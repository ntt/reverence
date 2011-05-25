/*
// marshal.c - high-performance iterative EVE cache/bulkdata decoder
//
// Copyright (c) 2003-2011 Jamie "Entity" van den Berge <jamie@hlekkir.com>
//
// This code is free software; you can redistribute it and/or modify
// it under the terms of the BSD license (see the file LICENSE.txt
// included with the distribution).
*/

#include "Python.h"
#include "cStringIO.h"

#include "dbrow.h"
#include "marshal.h"

extern unsigned long adler32(unsigned long adler, const char *buf, unsigned int len);


#define MARSHAL_DEBUG 0

#define MAX_DEPTH 64  // max object hierarchy depth

static PyObject *constants[256] = {NULL};
static int needlength[256] = {0};

static char *tokenname[256] = {"???"};


// module level objects
PyObject *global_cache = NULL;
PyObject *find_global_func = NULL;
PyObject *debug_func = NULL;
PyObject *string_table = NULL;

// some frequently used python strings
PyObject *py__new__ = NULL;
PyObject *py__setstate__ = NULL;
PyObject *py__dict__ = NULL;
PyObject *pyappend = NULL;


#if MARSHAL_DEBUG
void DEBUG(char *text)
{
	if(debug_func && !PyObject_CallFunction(debug_func, "s", text))
		PyErr_Clear();
}
#else
#define DEBUG(text)
#endif

#define TYPE_LIST_ITERATOR (TYPE_LIST|SHARED_FLAG)
#define TYPE_DICT_ITERATOR (TYPE_DICT|SHARED_FLAG)



// macro to read an object length/size value.
#define READ_LENGTH \
{\
	CHECK_SIZE(1);\
	length = *(unsigned char *)s++;\
	if(length == 255) {\
		CHECK_SIZE(4);\
		length = *(int32_t *)s;\
		s+=4;\
	}\
}

// immediately store object in shared object table
#define STORE(_obj)\
{\
	if(shared_count > shared_mapsize)\
	{\
		sprintf((error = errortext), "Shared object table overflow (size:%d)", shared_mapsize);\
		goto fail;\
	}\
	if(!(_obj))\
	{\
		sprintf((error = errortext), "Attempted store of NULL at shared position #%d", shared_map[shared_count]-1);\
		goto fail;\
	}\
	Py_INCREF(_obj);\
	shared_obj[shared_map[shared_count++]-1] = (_obj);\
}

// reserve an index in the shared object table, but only if needed.
#define RESERVE_SLOT(_store)\
{\
	if(shared) {\
		if(shared_count >= shared_mapsize) {\
			PyErr_Format(PyExc_RuntimeError, "Shared object table overflow, mapsize:%d", shared_mapsize);\
			goto cleanup;\
		}\
		_store = shared_map[shared_count++];\
	}\
	else\
		_store = 0;\
}

// update a previously reserved spot in shared object table with an object
// (only if it was a valid slot)
#define UPDATE_SLOT(_ix, _obj)\
	if(_ix) {\
		Py_INCREF(_obj);\
		shared_obj[_ix-1] = _obj;\
	}

// checks whether size of remaining data in stream is sufficient
#define CHECK_SIZE(x)\
if((s+x) > end)\
{\
	error = "Unexpected EOL";\
	goto fail;\
}\

// stores shared object if it was tagged as shared
#define CHECK_SHARED(_obj)\
{\
	if(shared)\
		STORE(_obj);\
}

// puts a new data container on the stack
#define PUSH_CONTAINER \
{\
	if(ct_ix >= MAX_DEPTH)\
	{\
		error = "object hierarchy too deep";\
		goto fail;\
	}\
	container = &ct_stack[++ct_ix];\
}

// pops current container off the stack (makes its parent active)
#define POP_CONTAINER \
	container = &ct_stack[--ct_ix]


// changes current container type to list iterator.
#define LIST_ITERATOR \
{\
	container->type = TYPE_LIST_ITERATOR;\
	container->obj2 = NULL;\
	container->free = -1;\
}\

// this structure tracks state of a container
struct Container {
	PyObject *obj;
	PyObject *obj2;
	int type;  // type as defined by the TYPE_ definitions.
	int free;  // typically the number of remaining slots in the container.
	int index; // reserved index into shared object map (if object is shared).
};


__inline static PyObject *
find_global(PyObject *pyname)
{
	// Return value: New Reference
	char *name, *dot;
	PyObject *m;
	PyObject *obj;

	char buffer[64];

	if(!PyString_Check(pyname))
	{
		PyErr_SetString(PyExc_RuntimeError, "expected string");
		return NULL;
	}

	// if the requested object is in cache, just return that.
	obj = PyDict_GetItem(global_cache, pyname);
	if(obj)
	{
		Py_INCREF(obj);
		return obj;
	}

	name = PyString_AS_STRING(pyname);

	dot = strchr(name, '.');
	if(dot)
	{
		// name is in "module.object" form

		*dot = 0;  // cut off object name

		// try importing it from reverence first
		if(strlen(name) < (64-11))
		{
			// FIXME: Should really use PyImport_ImportModuleEx here,
			// but this seems to work fine and is a lot simpler.
			sprintf(buffer, "reverence.%s", name);
			m = PyImport_ImportModule(buffer);
		}

		// otherwise try absolute import
		if(!m)
		{
			PyErr_Clear();
			m = PyImport_ImportModule(name);
		}

		*dot = '.';  // restore object name
	}
	else
	{
		// name is just a module name.
		m = PyImport_ImportModule("__builtin__");
	}

	if(m)
	{
		// we got a module handle, now get the object asked for.
		obj = PyObject_GetAttrString(m, dot ? dot+1 : name);
		Py_DECREF(m);
	}
	else
	{
		// oops, no module handle. use the python fallback function as a last
		// ditch effort to get the requested object.

		PyErr_Clear();
		if(!find_global_func)
		{
			PyErr_SetString(PyExc_RuntimeError, "No find_global function set. Use _set_find_global_func()");
			return NULL;
		}

		if(dot)
		{
			*dot = 0;
			obj = PyObject_CallFunction(find_global_func, "(ss)", name, dot+1, NULL);
			*dot = '.';
		}
		else
		{
			obj = PyObject_CallFunction(find_global_func, "(sO)", name, pyname, NULL);
		}
	}

	// we should have the requested object now. if not, tough luck.
	if(!obj)
		return NULL;

	// now store the result in cache so subsequent requests for this object are faster.
	if(PyDict_SetItem(global_cache, pyname, obj))
		return NULL;

	return obj;
}


__inline static int
set_state(PyObject *obj, PyObject *state)
{
	PyObject *__setstate__, *__dict__;

	if((__setstate__ = PyObject_GetAttr(obj, py__setstate__)))
	{
		// container has a __setstate__, invoke it!
		if(!PyObject_CallFunctionObjArgs(__setstate__, state, 0))
		{
			Py_DECREF(__setstate__);
			return 0;
		}
		Py_DECREF(__setstate__);
	}
	else
	{
		// container does not have __setstate__, see if it
		// has a __dict__ to update instead.
		PyErr_Clear();
		if(!(__dict__ = PyObject_GetAttr(obj, py__dict__)))
		{
			return 0;
		}

		if(PyDict_Update(__dict__, state))
		{
			Py_DECREF(__dict__);
			return 0;
		}
		Py_DECREF(__dict__);
	}

	return 1;
}


// Pickle support.
// FIXME: this is currently a single-use unpickler. make it return an unpickler
// instance instead, for TYPE_PICKLER support (with memo preservation)

PyObject *
unpickle(PyObject *obj, int *offset)
{
	// Return value: New Reference
	PyObject *input = NULL;
	PyObject *cPickle = NULL;
	PyObject *unpickler = NULL;
	PyObject *result = NULL;

	cPickle = PyImport_ImportModule("cPickle");
	if(!cPickle)
		return NULL;

	input = PycStringIO->NewInput(obj);
	if(!input)
		goto fail;

	unpickler = PyObject_CallMethod(cPickle, "Unpickler", "(O)", input);
	if(!unpickler)
		goto fail;

	if(!find_global_func)
	{
		PyErr_SetString(PyExc_RuntimeError, "No find_global function set. Use _set_find_global_func()");
		goto fail;
	}

	if(PyObject_SetAttrString(unpickler, "find_global", find_global_func) == -1)
	{
		PyErr_SetString(PyExc_RuntimeError, "Unpickler initialization failed");
		goto fail;
	}

	if(*offset)
	{
		// seek to desired position.
		Py_XDECREF(PyObject_CallMethod(cPickle, "seek", "(i)", *offset));
	}

	result = PyObject_CallMethod(unpickler, "load", NULL);

fail:
	Py_XDECREF(cPickle);
	Py_XDECREF(input);
	Py_XDECREF(unpickler);
	return result;
}


static PyObject *
marshal_Load_internal(PyObject *py_stream, PyObject *py_callback, int skipcrc)
{
	// Return value: New Reference

	char *stream;
	Py_ssize_t size;

	char *s;
	char *end;

	int type = -1;   // current object type
	int shared = -1; // indicates whether current object is shared
	int i;

	char *error = "NO ERROR SPECIFIED";
	char errortext[256];

	Py_ssize_t length = 0;  // generic length value.

	int shared_mapsize;
	int shared_count;  // shared object index counter
	int *shared_map;  // points to shared object mapping at end of stream
	PyObject **shared_obj = NULL;  // holds the shared objects

	PyObject *obj = NULL;  // currently decoded object
	PyObject *result = NULL;  // final result

	int ct_ix = 0;
	struct Container ct_stack[MAX_DEPTH];
	struct Container *container = &ct_stack[0];

	if(PyString_AsStringAndSize(py_stream, &stream, &size) == -1)
		return NULL;

	s = stream;

	container->obj = NULL;
	container->type = 0;
	container->free = -1;
	container->index = 0;

	if(size < 6 || *s++ != PROTOCOL_ID)
	{
		int offset = 0;
		result = unpickle(py_stream, &offset);
		if(!result)
			goto cleanup;

		return result;
	}

	// how many shared objects in this stream?
	shared_mapsize = *(int32_t *)s;
	s += 4;

	// Security Check: assert there is enough data for that many items.
	if((5 + shared_mapsize*4) > size) 
	{
		PyErr_Format(PyExc_RuntimeError, "Not enough room in stream for map. Wanted %d, but have only %d bytes remaining...", (shared_mapsize*4), ((int)size-5));
		goto cleanup;
	}

	// ok, we got the map data right here...
	shared_map = (int32_t *)&stream[size - shared_mapsize * 4];

	// Security Check #2: assert all map entries are between 1 and shared_mapsize
	for(i=0; i<shared_mapsize; i++)
	{
		if( (shared_map[i] > shared_mapsize) || (shared_map[i] < 1) )
		{
			PyErr_SetString(PyExc_RuntimeError, "Bogus map data in marshal stream");
			goto cleanup;
		}
	}

	// the start of which is incidentally also the end of the object data.
	end = (char *)shared_map;

	// create object table
	shared_obj = PyMem_MALLOC(shared_mapsize * sizeof(PyObject *));
	if(!shared_obj)
		goto cleanup;

	// zero out object table
	for(shared_count = 0; shared_count < shared_mapsize; shared_count++)
		shared_obj[shared_count] = NULL;
	shared_count = 0;


	// start decoding.

	while(s < end)
	{
		// This outer loop is responsible for reading and decoding the next
		// object from the stream. The object is then handed to the inner loop,
		// which adds it to the current container, or returns it to the caller.

		// get type of next object to decode and check shared flag
		type = *s++;
		shared = type & SHARED_FLAG;
		type &= ~SHARED_FLAG;

		// if token uses a normal length value, read it now.
		if(needlength[type])
		{
			READ_LENGTH;
		}
		else
			length = 0;


#if MARSHAL_DEBUG
//		if(shared)
		{
			char text[220];
			int i;
			for(i=0; i<ct_ix; i++)
				printf("  ");

			sprintf(text, "pos:%4d type:%s(0x%02x) shared:%d len:%4d map:[", s-stream, tokenname[type], type, shared?1:0, length);
			printf(text);
			for(i=0; i<shared_mapsize; i++)
				printf("%d(%d),", shared_obj[i], shared_obj[i] ? ((PyObject *)(shared_obj[i]))->ob_refcnt : 0);
			printf("]\r\n");
		}
#endif // MARSHAL_DEBUG

		switch(type) {

		//---------------------------------------------------------------------
		// SCALAR TYPES
		//---------------------------------------------------------------------

		case TYPE_INT8:
			CHECK_SIZE(1);
			obj = PyInt_FromLong(*(int8_t *)s);
			s++;
			break;

		case TYPE_INT16:
			CHECK_SIZE(2);
			obj = PyInt_FromLong(*(int16_t *)s);
			s += 2;
			break;

		case TYPE_INT32:
			CHECK_SIZE(4);
			obj = PyInt_FromLong(*(int32_t *)s);
			s += 4;
			break;

		case TYPE_INT64:
			CHECK_SIZE(8);
			obj = PyLong_FromLongLong(*(int64_t *)s);
			s += 8;
			break;

		case TYPE_LONG:
			CHECK_SIZE(length);
			if(!length)
				obj = PyLong_FromLong(0);
			else
			{
				obj = _PyLong_FromByteArray((unsigned char *)s, length, 1, 1);
				Py_INCREF(obj);
			}

			CHECK_SHARED(obj);
			s += length;
			break;

		case TYPE_FLOAT:
			CHECK_SIZE(8);
			obj = PyFloat_FromDouble(*(double *)s);
			s += 8;
			break;


		case TYPE_CHECKSUM:
			CHECK_SIZE(4);
			if(!skipcrc && (*(uint32_t *)s != (uint32_t)adler32(1, s, end-s)))
			{
				error = "checksum error";
				goto fail;
			}
			s += 4;
			// because this type does not yield an object, go grab another
			// object right away!
			continue;


		//---------------------------------------------------------------------
		// STRING TYPES
		//---------------------------------------------------------------------

		case TYPE_STRINGR:
			if (length < 1 || length >= PyList_GET_SIZE(string_table))
			{
				if(PyList_GET_SIZE(string_table))
					PyErr_Format(PyExc_RuntimeError, "Invalid string table index %d", (int)length);
				else
					PyErr_SetString(PyExc_RuntimeError, "_stringtable not initialized");
				goto cleanup;
			}
			obj = PyList_GET_ITEM(string_table, length);
			Py_INCREF(obj);
			break;

		case TYPE_STRING:
			// appears to be deprecated since machoVersion 213
			CHECK_SIZE(1);
			length = *(unsigned char *)s++;
			CHECK_SIZE(length);
			obj = PyString_FromStringAndSize(s, length);
			s += length;
			break;

		case TYPE_STRING1:
			CHECK_SIZE(1);
			obj = PyString_FromStringAndSize(s, 1);
			s++;
			break;

		case TYPE_STREAM:
			// fallthrough, can be treated as string.
		case TYPE_STRINGL:
			// fallthrough, deprecated since machoVersion 213
		case TYPE_BUFFER:
			// Type identifier re-used by CCP. treat as string.
			CHECK_SIZE(length);
			obj = PyString_FromStringAndSize(s, length);
			s += length;
			CHECK_SHARED(obj);
			break;

		case TYPE_UNICODE1:
			CHECK_SIZE(2);
			obj = PyUnicode_FromWideChar((wchar_t *)s, 0);
			s += 2;
			break;

		case TYPE_UNICODE:
			CHECK_SIZE(length*2);
			obj = PyUnicode_FromWideChar((wchar_t *)s, length);
			s += length*2;
			break;

		case TYPE_UTF8:
			CHECK_SIZE(length);
			obj = PyUnicode_DecodeUTF8(s, length, NULL);
			s += length;
			break;

		//---------------------------------------------------------------------
		// SEQUENCE/MAPPING TYPES
		//---------------------------------------------------------------------

		case TYPE_TUPLE1:
			length = 1;
			goto tuple;

		case TYPE_TUPLE2:
			length = 2;
			// fallthrough
tuple:
		case TYPE_TUPLE:
			// Security Check: we're forced to trust the stream to some extent
			// regarding the number of items to allocate for the sequence.
			// To reduce the effects of malicious or corrupted data, make sure
			// the stream has enough data to fill the list.

			CHECK_SIZE(length);

			PUSH_CONTAINER;
			container->obj = PyTuple_New(length);
			container->type = TYPE_TUPLE;
			container->free = length;
			container->index = 0;
			CHECK_SHARED(container->obj);
			continue;

		case TYPE_LIST0:
			obj = PyList_New(0);
			CHECK_SHARED(obj);
			break;

		case TYPE_LIST1:
			length = 1;
			// fallthrough
		case TYPE_LIST:
			// Security Check: see TYPE_TUPLE above.
			CHECK_SIZE(length);

			PUSH_CONTAINER;
			container->type = TYPE_LIST;
			container->free = length;
			container->obj = PyList_New(length);
			container->index = 0;
			CHECK_SHARED(container->obj);
			continue;

		case TYPE_DICT:
			if(length)
			{
				PUSH_CONTAINER;
				container->obj = PyDict_New();
				container->type = TYPE_DICT;
				container->free = length * 2;
				container->obj2 = NULL;
				container->index = 0;
				CHECK_SHARED(container->obj);
				continue;
			}
			else
			{
				obj = PyDict_New();
				CHECK_SHARED(obj);
				break;
			}


		//---------------------------------------------------------------------
		// OBJECT TYPES
		//---------------------------------------------------------------------

		case TYPE_REF:
			// length value is index in sharedobj array!
			if((length < 1 || length > shared_mapsize))
			{
				error = "Shared reference index out of range";
				goto fail;
			}

			if(!(obj = shared_obj[length-1]))
			{
				error = "Shared reference points to invalid object";
				goto fail;
			}

			Py_INCREF(obj);
			//printf("Getting object %d from %d (refs:%d)\r\n", (int)obj, length-1, obj->ob_refcnt);
			break;

		case TYPE_GLOBAL:
		{
			PyObject *name;
			CHECK_SIZE(length);
 			name = PyString_FromStringAndSize(s, length);
			if(!name)
				goto cleanup;
			s += length;
			obj = find_global(name);
			Py_DECREF(name);
			CHECK_SHARED(obj);
			break;
		}

		case TYPE_DBROW:
		case TYPE_INSTANCE:
		case TYPE_NEWOBJ:
		case TYPE_REDUCE:
			PUSH_CONTAINER;
			container->obj = NULL;
			container->type = type;
			container->free = -1;
			RESERVE_SLOT(container->index);
			continue;

		case TYPE_MARK:
			// this is a marker, not a real object. list/dict iterators check
			// for this type, but it can't be instantiated.
			break;

		default:
			if((obj = constants[type]))
			{
				Py_INCREF(obj);
			}
			else
			{
				error = "Unsupported type";
				goto fail;
			}
		}


		// object decoding and construction done!

		if(!obj && type != TYPE_MARK)
		{
			// if obj is somehow NULL, whatever caused it is expected to have
			// set an exception at this point.
			goto cleanup;
		}

#if MARSHAL_DEBUG
/*
if(obj && obj->ob_refcnt < 0)
{
	char b[200];
	sprintf(b, "type: %d, refcount: %d", type, obj->ob_refcnt);
	DEBUG(b);
}
*/
#endif // MARSHAL_DEBUG

		while(1)
		{
			// This inner loop does one of two things:
			//
			// - return the finished object to the caller if we're at the root
			//   container.
			//
			// - add the object to the current container in a container-
			//   specific manner. note that ownership of the reference is to be
			//   given to the container object.
/*
#ifdef DEBUG_LOAD
		{
			char text[220];
			sprintf(text, "container ix:%d type:0x%02x free:%d index:%d", ct_ix, container->type, container->free, container->index);
			DEBUG(text);
		}
#endif // DEBUG_LOAD
*/

			switch(container->type) {
				case TYPE_TUPLE:
					// tuples steal references.
					PyTuple_SET_ITEM(container->obj, container->index++, obj);
					break;

				case TYPE_LIST:
					// lists steal references.
					PyList_SET_ITEM(container->obj, container->index++, obj);
					break;


				case TYPE_DBROW:
					if(container->obj)
					{
						// we have an initialized DBRow. current object is a
						// non-scalar object for the row. append it.
						if(!dbrow_append_internal((PyDBRowObject *)container->obj, obj))
						{
							// append call will have set an exception here.
							goto cleanup;
						}
					}
					else
					{
						// we now have a DBRowDescriptor, and the header data
						// should follow. Pull it and create the DBRow.
						READ_LENGTH;
						CHECK_SIZE(length);
						container->obj = PyDBRow_New((PyDBRowDescriptorObject *)obj, s, length);
						container->free = 1+((PyDBRowDescriptorObject *)obj)->rd_num_objects;

						if(!container->obj)
							goto cleanup;
						Py_DECREF(obj);
						s += length;

						// add as shared object, if neccessary...
						UPDATE_SLOT(container->index, container->obj);

					}
					break;


				case TYPE_INSTANCE:
				{
					PyObject *cls;

					if(container->free == -1)
					{
						// create class instance
						if(!(cls = find_global(obj)))
							goto cleanup;
						container->obj = PyInstance_NewRaw(cls, 0);
						Py_DECREF(cls);
						if(!container->obj)
							goto cleanup;
						UPDATE_SLOT(container->index, container->obj);
						Py_DECREF(obj);
						break;
					}

					if(container->free == -2)
					{
						container->free = 1;
						// set state.
						if(!set_state(container->obj, obj))
							goto cleanup;

						Py_DECREF(obj);
						break;
					}

					error = "invalid container state";
					goto fail;
				}


				case TYPE_NEWOBJ:
				{
					PyObject *cls, *args, *__new__, *state;

					// instantiate the object...
					if(!(args = PyTuple_GetItem(obj, 0)))
						goto cleanup;
					if(!(cls = PyTuple_GetItem(args, 0)))
						goto cleanup;

					__new__ = PyObject_GetAttr(cls, py__new__);
					if(!__new__)
						goto cleanup;

					container->obj = PyObject_CallObject(__new__, args);
					Py_DECREF(__new__);
					if(!container->obj)
						goto cleanup;

					// add as shared object, if neccessary...
					UPDATE_SLOT(container->index, container->obj);

					// is there state data?
					if(PyTuple_GET_SIZE(obj) > 1)
					{
						state = PyTuple_GET_ITEM(obj, 1);
						if(!set_state(container->obj, state))
							goto cleanup;
					}

					Py_DECREF(obj);

					LIST_ITERATOR;
					break;
				}



				case TYPE_REDUCE:
				{
					PyObject *callable, *args, *state;


					if(!(args = PyTuple_GetItem(obj, 1)))
						goto cleanup;
					if(!(callable = PyTuple_GET_ITEM(obj, 0)))
						goto cleanup;

					if(!(container->obj = PyObject_CallObject(callable, args)))
						goto cleanup;

					UPDATE_SLOT(container->index, container->obj);

					if(PyTuple_GET_SIZE(obj) > 2)
					{
						state = PyTuple_GET_ITEM(obj, 2);

						if(!set_state(container->obj, state))
							goto cleanup;
					}

					Py_DECREF(obj);

					LIST_ITERATOR;

					break;
				}


				case TYPE_LIST_ITERATOR:
					if(type == TYPE_MARK)
					{
						// decref the append method
						Py_XDECREF(container->obj2);
						container->obj2 = NULL;

						// we're done with list iter, switch to dict iter.
						container->type = TYPE_DICT_ITERATOR;
						break;
					}

					if(!container->obj2)
					{
						// grab the append method from the container and keep
						// it around for speed.
						if(!(container->obj2 = PyObject_GetAttr(container->obj, pyappend)))
							goto cleanup;
					}

					if(!PyObject_CallFunctionObjArgs(container->obj2, obj, NULL))
						goto cleanup;

					Py_DECREF(obj);
					break;


				case TYPE_DICT_ITERATOR:
					if(type == TYPE_MARK)
					{
						// we're done with dict iter. container is finished.
						container->free = 1;
						break;
					}
					// fallthrough
				case TYPE_DICT:
					if(container->obj2)
					{
						PyDict_SetItem(container->obj, obj, container->obj2);

						// dicts don't steal references, decref the key & val.
						Py_DECREF(obj);
						Py_DECREF(container->obj2);
						container->obj2 = NULL;
					}
					else
					{
						// object is the value. next iteration's object will be
						// the key, so store it temporarily while waiting.
						container->obj2 = obj;
					}
					break;



				case 0:
					// we're at the root. return the object to caller.
					result = obj;

					// avoid decreffing this object.
					obj = NULL;
					goto cleanup;
			}

			container->free--;
			if(container->free)
				// still room in this container.
				// break out of container handling to get next object for it.
				break;

			// this container is done, it is the next object to put into the
			// container under it!
			obj = container->obj;

			// switch context to said older container
			POP_CONTAINER;
		}

		// we've processed the object. clear it for next one.
		obj = NULL;
	}

	// if we get here, we're out of data, but it's a "clean" eof; we ran out
	// of data while expecting a new object...
	error = "Not enough objects in stream";

fail:
	PyErr_Format(PyExc_RuntimeError, "%s - type:0x%02x ctype:0x%02x len:%d share:%d pos:%d size:%d", error, type, container->type, (int)length, shared, (int)(s-stream), (int)(size));

cleanup:
	// on any error the current object we were working on will be unassociated
	// with anything, decref it. if decode was succesful or an object failed to
	// be created, it will be NULL anyway.
	Py_XDECREF(obj);

	// same story for containers...
	while(container->type)
	{
		Py_XDECREF(container->obj);
		// possibly unassociated object for dict entry?
		if(container->type == TYPE_DICT || container->type == TYPE_DICT_ITERATOR)
		{
			Py_XDECREF(container->obj2);
		}

		POP_CONTAINER;
	}

	if(shared_obj)
	{
		/* shared object list held a safety ref to all objects, decref em */
		int i;
		for(i=0; i<shared_mapsize; i++)
			Py_XDECREF(shared_obj[i]);

		/* and free the list */
		PyMem_FREE(shared_obj);
	}
	return result;
}


PyObject *
marshal_Load(PyObject *self, PyObject *args, PyObject *kwds)
{
	PyObject *py_stream;
	PyObject *py_callback = NULL;
	PyObject *result;


	int skipcrc = 0;

	if(!PyArg_ParseTuple(args, "O|Oi:Load", &py_stream, &py_callback, &skipcrc))
		return NULL;

	if(!PyString_Check(py_stream))
	{
		PyErr_SetString(PyExc_TypeError, "expected string argument");
		return NULL;
	}

	if(py_callback == Py_None)
		py_callback = NULL;

	if(py_callback && !PyCallable_Check(py_callback))
	{
		PyErr_SetString(PyExc_TypeError, "callback argument must be callable");
		return NULL;
	}

	result = marshal_Load_internal(py_stream, py_callback, skipcrc);
	return result;
}


PyObject *marshal_Save_internal(PyObject *string)
{
	return NULL;	
}


PyObject *
marshal_set_find_global_func(PyObject *self, PyObject *callable)
{
	if(!PyCallable_Check(callable))
	{
		PyErr_SetString(PyExc_TypeError, "argument must be callable");
		return NULL;
	}

	Py_XDECREF(find_global_func);
	find_global_func = callable;
	Py_INCREF(find_global_func);
	Py_INCREF(Py_None);
	return Py_None;
}

PyObject *
marshal_set_debug_func(PyObject *self, PyObject *callable)
{
	if(!PyCallable_Check(callable))
	{
		PyErr_SetString(PyExc_TypeError, "argument must be callable");
		return NULL;
	}

	Py_XDECREF(debug_func);
	debug_func = callable;
	Py_INCREF(debug_func);
	Py_INCREF(Py_None);
	return Py_None;
}


static struct PyMethodDef marshal_methods[] = {
	{"Load", (PyCFunction)marshal_Load, METH_VARARGS|METH_KEYWORDS, NULL},
	{"_set_find_global_func", (PyCFunction)marshal_set_find_global_func, METH_O, NULL},
	{"_set_debug_func", (PyCFunction)marshal_set_debug_func, METH_O, NULL},
	{ NULL, NULL }
};



PyObject *
init_marshal(void)
{
	// init some stuff.
	// note that if any of this fails, we're probably horribly screwed.
	PyObject *m;

	int i, nl[] = {TYPE_TUPLE, TYPE_DICT, TYPE_LIST,
		TYPE_STRINGL, TYPE_STRINGR, TYPE_UNICODE, TYPE_GLOBAL,
		TYPE_STREAM, TYPE_UTF8,	TYPE_LONG,
		TYPE_REF, TYPE_BLUE, TYPE_BUFFER, 0};

	PycString_IMPORT;

	m = Py_InitModule("_blue.marshal", marshal_methods);
	if(!m)
		return NULL;

	Py_INCREF(m);

	for(i=0; nl[i]; i++)
		needlength[nl[i]] = 1;

	// populate constants table
	constants[TYPE_NONE] = (PyObject *)Py_None;
	constants[TYPE_TRUE] = (PyObject *)Py_True;
	constants[TYPE_FALSE] = (PyObject *)Py_False;
	constants[TYPE_MINUSONE] = (PyObject *)PyInt_FromLong(-1);
	constants[TYPE_ONE] = (PyObject *)PyInt_FromLong(1);
	constants[TYPE_ZERO] = (PyObject *)PyInt_FromLong(0);
	constants[TYPE_FLOAT0] = (PyObject *)PyFloat_FromDouble(0.0);
	constants[TYPE_STRING0] = (PyObject *)PyString_FromString("");
	constants[TYPE_TUPLE0] = (PyObject *)PyTuple_New(0);
	constants[TYPE_UNICODE0] = (PyObject *)PyUnicode_FromObject(constants[TYPE_STRING0]);

	if(!(py__new__ = PyString_FromString("__new__")))
		goto fail;
	if(!(py__setstate__ = PyString_FromString("__setstate__")))
		goto fail;
	if(!(py__dict__ = PyString_FromString("__dict__")))
		goto fail;
	if(!(pyappend = PyString_FromString("append")))
		goto fail;
	if(!(global_cache = PyDict_New()))
		goto fail;
	if(!(string_table = PyList_New(0)))
		goto fail;

	PyModule_AddObject(m, "_stringtable", (PyObject*)string_table);


#if MARSHAL_DEBUG
	tokenname[TYPE_NONE] = "NONE";
	tokenname[TYPE_GLOBAL] = "GLOBAL";
	tokenname[TYPE_INT64] = "INT64";
	tokenname[TYPE_INT32] = "INT32";
	tokenname[TYPE_INT16] = "INT16";
	tokenname[TYPE_INT8] = "INT8";
	tokenname[TYPE_MINUSONE] = "MINUSONE";
	tokenname[TYPE_ZERO] = "ZERO";
	tokenname[TYPE_ONE] = "ONE";
	tokenname[TYPE_FLOAT] = "FLOAT";
	tokenname[TYPE_FLOAT0] = "FLOAT0";
	tokenname[TYPE_STRINGL] = "STRINGL";
	tokenname[TYPE_STRING0] = "STRING0";
	tokenname[TYPE_STRING1] = "STRING1";
	tokenname[TYPE_STRING] = "STRING";
	tokenname[TYPE_STRINGR] = "STRINGR";
	tokenname[TYPE_UNICODE] = "UNICODE";
	tokenname[TYPE_BUFFER] = "BUFFER";
	tokenname[TYPE_TUPLE] = "TUPLE";
	tokenname[TYPE_LIST] = "LIST";
	tokenname[TYPE_DICT] = "DICT";
	tokenname[TYPE_INSTANCE] = "INSTANCE";
	tokenname[TYPE_BLUE] = "BLUE";
	tokenname[TYPE_CHECKSUM] = "CHECKSUM";
	tokenname[TYPE_TRUE] = "TRUE";
	tokenname[TYPE_FALSE] = "FALSE";
	tokenname[TYPE_PICKLER] = "PICKLER";
	tokenname[TYPE_REDUCE] = "REDUCE";
	tokenname[TYPE_NEWOBJ] = "NEWOBJ";
	tokenname[TYPE_TUPLE0] = "TUPLE0";
	tokenname[TYPE_TUPLE1] = "TUPLE1";
	tokenname[TYPE_LIST0] = "LIST0";
	tokenname[TYPE_LIST1] = "LIST1";
	tokenname[TYPE_UNICODE0] = "UNICODE0";
	tokenname[TYPE_UNICODE1] = "UNICODE1";
	tokenname[TYPE_DBROW] = "DBROW";
	tokenname[TYPE_STREAM] = "STREAM";
	tokenname[TYPE_TUPLE2] = "TUPLE2";
	tokenname[TYPE_MARK] = "MARK";
	tokenname[TYPE_UTF8] = "UTF8";
	tokenname[TYPE_LONG] = "LONG";
#endif // MARSHAL_DEBUG

	return m;
fail:
	Py_XDECREF(py__new__);
	Py_XDECREF(py__setstate__);
	Py_XDECREF(py__dict__);
	Py_XDECREF(pyappend);
	Py_XDECREF(global_cache);
	Py_XDECREF(string_table);
	return 0;
}
