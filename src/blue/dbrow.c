/*
// dbrow.c - DBRow decoder
//
// Copyright (c) 2003-2011 Jamie "Entity" van den Berge <jamie@hlekkir.com>
//
// This code is free software; you can redistribute it and/or modify
// it under the terms of the BSD license (see the file LICENSE.txt
// included with the distribution).
*/


#include "Python.h"
#include "structmember.h"
#include "dbrow.h"
#include "marshal.h"

#define PTRSIZE sizeof(void *)
#define ALIGNED(x) (((x) + PTRSIZE-1) & ~(PTRSIZE-1))

static PyObject *blue, *py_dbrow_str;

__inline static void rle_pack(char *in, int in_size, char *out, int *out_size)
{
	int nibble = 0;
	int nibble_ix = 0;
	int in_ix = 0;
	int out_ix = 0;
	int start, end, count;
	int zerochains = 0;

	while(in_ix < in_size)
	{
		if(!nibble)
		{
			nibble_ix = out_ix++;
			out[nibble_ix] = 0;
		}

		start = in_ix;
		end = in_ix+8;
		if(end > in_size)
			end = in_size;

		if(in[in_ix])
		{
			zerochains = 0;
			do {
				out[out_ix++] = in[in_ix++];
			} while(in_ix<end && in[in_ix]);
			count = start - in_ix + 8;
		}
		else
		{
			zerochains++;
			while(in_ix<end && !in[in_ix])
				in_ix++;
			count = in_ix - start + 7;
		}

		if(nibble)
			out[nibble_ix] |= (count << 4);
		else
			out[nibble_ix] = count;
		nibble = !nibble;
	}

	if(nibble && zerochains)
		zerochains++;

	while(zerochains>1)
	{
		zerochains -= 2;
		out_ix -= 1;
	}

	*out_size = out_ix;
}

__inline static int rle_unpack(char *in, int in_size, char *out, int out_size)
{
	int in_ix = 0;
	int out_ix = 0;
	int count;
	int run = 0;
	int nibble = 0;

	while(in_ix < in_size)
	{
		nibble = !nibble;
		if(nibble)
		{
			run = (unsigned char)in[in_ix++];
			count = (run & 0x0f) - 8;
		}
		else
			count = (run >> 4) - 8;

		if(count >= 0)
		{
			if (out_ix + count + 1 > out_size)
				return 0;

			while(count-- >= 0)
				out[out_ix++] = 0;
		}
		else
		{
			if (out_ix - count > out_size)
				return 0;

			while(count++ && in_ix < in_size)
				out[out_ix++] = in[in_ix++];
		}
	}

	while(out_ix < out_size)
		out[out_ix++] = 0;

	return 1;
}


//============================================================================
// Column Descriptor
//============================================================================


__inline static PyObject *
getFromCD(PyDBRowObject *row, ColumnDescriptor *cd)
{
	char *data = &row->dbrow_data[cd->cd_offset];

	switch (cd->cd_type) {
		case DBTYPE_I1       : return PyInt_FromLong(*(int8_t*)data);
		case DBTYPE_UI1      : return PyInt_FromLong(*(uint8_t*)data);
		case DBTYPE_I2       : return PyInt_FromLong(*(int16_t*)data);
		case DBTYPE_UI2      : return PyInt_FromLong(*(uint16_t*)data);
		case DBTYPE_I4       : return PyInt_FromLong(*(int32_t*)data);
		case DBTYPE_UI4      : return PyInt_FromLong(*(uint32_t*)data);
		case DBTYPE_I8       : return PyLong_FromLongLong(*(int64_t *)data);
		case DBTYPE_UI8      : return PyLong_FromUnsignedLongLong(*(uint64_t *)data);
		case DBTYPE_FILETIME : return PyLong_FromUnsignedLongLong(*(uint64_t *)data);
		case DBTYPE_R4       : return PyFloat_FromDouble(*(float*)data);
		case DBTYPE_R8       : return PyFloat_FromDouble(*(double*)data);
		case DBTYPE_CY       : return PyFloat_FromDouble((double)(*(int64_t *)data) / 10000.0);

		case DBTYPE_BOOL:
		{
			PyObject *obj = (row->dbrow_data[cd->cd_offset >> 3] & (1<<(cd->cd_offset & 0x7))) ? Py_True : Py_False;
			Py_INCREF(obj);
			return obj;
		}

		case DBTYPE_STR:
		case DBTYPE_WSTR:
		case DBTYPE_BYTES:
		{
			PyObject *obj = *(PyObject**)data;
			if(!obj)
				obj = Py_None;
			Py_INCREF(obj);
			return obj;
		}

		case DBTYPE_EMPTY:
			// we dont support virtuals...
		default:
			PyErr_Format(PyExc_RuntimeError, "Unexpected db column type encountered: %d", cd->cd_type);
			return NULL;
	}
}


// This macro saves a lot of copypasta below (but at what price...)
#define SET(_stype, _pycast, _sobj, _ttype, _tdata, _tmodify, _pyconv)\
{\
	PyObject *converted;\
	_stype temp;\
	if(!(converted = _pycast(_sobj))) {\
		PyErr_Format(PyExc_TypeError, "column of type %s expects numeric value", #_ttype);\
		return -1;\
	}\
	temp = _pyconv(converted) _tmodify;\
	*(_ttype *)_tdata = (_ttype)temp;\
	if(temp != (*(_ttype *)_tdata))\
		PyErr_Warn(PyExc_RuntimeWarning, "numeric value was truncated to " #_ttype);\
	return 0;\
}


static int
setToCD(PyDBRowObject *row, ColumnDescriptor *cd, PyObject *obj)
{
	// returns -1 for failure, 0 for success.
	char *data = &row->dbrow_data[cd->cd_offset];

	switch (cd->cd_type) {
		// note to self: cases in this switch are supposed to return, not break.

		//                         /-------- precast ---------\  /- store as -\ /modify\ /--- convert from
		case DBTYPE_I1       : SET(int64_t, PyNumber_Long , obj, int8_t  , data,        , PyLong_AsLongLong);
		case DBTYPE_UI1      : SET(int64_t, PyNumber_Long , obj, uint8_t , data,        , PyLong_AsUnsignedLongLong);
		case DBTYPE_I2       : SET(int64_t, PyNumber_Long , obj, int16_t , data,        , PyLong_AsLongLong);
		case DBTYPE_UI2      : SET(int64_t, PyNumber_Long , obj, uint16_t, data,        , PyLong_AsUnsignedLongLong);
		case DBTYPE_I4       : SET(int64_t, PyNumber_Long , obj, int32_t , data,        , PyLong_AsLongLong);
		case DBTYPE_UI4      : SET(int64_t, PyNumber_Long , obj, uint32_t, data,        , PyLong_AsUnsignedLongLong);
		case DBTYPE_I8       : SET(int64_t, PyNumber_Long , obj, int64_t , data,        , PyLong_AsLongLong);
		case DBTYPE_UI8      : SET(int64_t, PyNumber_Long , obj, uint64_t, data,        , PyLong_AsUnsignedLongLong);
		case DBTYPE_FILETIME : SET(int64_t, PyNumber_Long , obj, uint64_t, data,        , PyLong_AsUnsignedLongLong);
		case DBTYPE_R4       : SET(double , PyNumber_Float, obj, float   , data,        , PyFloat_AsDouble);
		case DBTYPE_R8       : SET(double , PyNumber_Float, obj, double  , data,        , PyFloat_AsDouble);
		case DBTYPE_CY       : SET(double , PyNumber_Float, obj, int64_t , data,*10000.0, PyFloat_AsDouble);

		case DBTYPE_BOOL:
			if(PyObject_IsTrue(obj) == 1)
				row->dbrow_data[cd->cd_offset >> 3] |= (1<<(cd->cd_offset & 0x7));
			else
				row->dbrow_data[cd->cd_offset >> 3] &= ~(1<<(cd->cd_offset & 0x7));
			return 0;

		case DBTYPE_STR:
		case DBTYPE_WSTR:
		case DBTYPE_BYTES:
			Py_XDECREF(*(PyObject**)data);
			Py_INCREF(obj);
			*(PyObject**)data = obj;
			return 0;

		case DBTYPE_EMPTY:
			// we dont support virtuals...
		default:
			PyErr_Format(PyExc_RuntimeError, "Unexpected db column type encountered: %d", cd->cd_type);
			return -1;
	}

	PyErr_Format(PyExc_RuntimeError, "Oops! control is reaching places it shouldn't");
	return -1;
}


__inline ColumnDescriptor *
findCD(PyDBRowObject *self, char *name)
{
	ColumnDescriptor *cd;
	int i;

	// find named column in the list...
	for(i=0; i<self->dbrow_header->ob_size; i++)
	{
		cd = &self->dbrow_header->rd_cd[i];
		if(!strcmp(cd->cd_name, name))
			return cd;
	}
	return NULL;
}



//============================================================================
// DBRowDescriptor
//============================================================================
 

static PyObject *
rd_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	PyDBRowDescriptorObject *self;
	int i;
	ColumnDescriptor *cd;
	PyObject *initarg;
	PyObject *item;

	int sizes[5] = {0};

	assert(type != NULL && type->tp_alloc != NULL);


	if(!(initarg = PyTuple_GetItem(args, 0)))
		goto rdfail;
	if(!initarg || !PyTuple_Check(initarg))
		goto rdfail;

	// get number of columns
	i = PyTuple_GET_SIZE(initarg);
	self = (PyDBRowDescriptorObject *)type->tp_alloc(type, i);
	if(!self)
		return NULL;

	// init some shite
	self->rd_initarg = initarg;
	Py_INCREF(self->rd_initarg);

	// don't have to zero these as tp_alloc already does that, but w/e.
	self->rd_num_objects = 0;
	self->rd_header = NULL;
	self->rd_unpacked_size = 0;
	self->rd_properties = NULL;
	self->rd_prop_size = 0;

	// fill the descriptors
	for(i=0; i<self->ob_size; i++)
	{
		cd = &self->rd_cd[i];

		item = PyTuple_GET_ITEM(self->rd_initarg, i);

		if (!PyArg_ParseTuple(item, "si:DBRowDescriptor", &cd->cd_name, &cd->cd_type))
			goto rdfail;

		switch(cd->cd_type) {
			case DBTYPE_BOOL:
				cd->cd_size = 0;
				break;
			case DBTYPE_I1:
			case DBTYPE_UI1:
				cd->cd_size = 1;
				break;
			case DBTYPE_I2:
			case DBTYPE_UI2:
				cd->cd_size = 2;
				break;
			case DBTYPE_I4:
			case DBTYPE_UI4:
			case DBTYPE_R4:
				cd->cd_size = 3;
				break;
			case DBTYPE_I8:
			case DBTYPE_UI8:
			case DBTYPE_R8:
			case DBTYPE_CY:
			case DBTYPE_FILETIME:
			case DBTYPE_DBTIMESTAMP:
				cd->cd_size = 4;
				break;

			case DBTYPE_EMPTY:
				cd->cd_size = 0;
				// don't count this in size array
				continue;

			case DBTYPE_STR:
			case DBTYPE_WSTR:
			case DBTYPE_BYTES:
				cd->cd_size = 4;
				cd->cd_offset = self->rd_num_objects++;
				// don't count this in size array
 				continue;

			default:
				PyErr_Format(PyExc_TypeError, "DBRowDescriptor doesn't support data type %d", cd->cd_type);
				return NULL;
		}

		if(cd->cd_type != DBTYPE_EMPTY)
			sizes[cd->cd_size]++;
	}

	{
		int offsets[5] = {0};
		int offset = 0;
		int virtuals = 0;
		int msize = 0;

		for(i=4; i; i--)
		{
			offsets[i] = offset;
			offset += sizes[i] * (1<<(i-1));
		}

		offset <<= 3;
		offsets[0] = offset;
		offset += sizes[0] + self->ob_size;
		offset = (offset+7) >> 3;

		self->rd_unpacked_size = offset;

		if(self->rd_num_objects)
		{
			offset = ALIGNED(offset);  // align to 32bit
			self->rd_total_size = offset + self->rd_num_objects * PTRSIZE;
		}
		else {
			self->rd_total_size = offset;
		}


		self->rd_num_objects = 0;

		for(i=0; i<self->ob_size; i++)
		{
			cd = &self->rd_cd[i];
			switch(cd->cd_type) {
				case DBTYPE_STR:
				case DBTYPE_WSTR:
				case DBTYPE_BYTES:
					cd->cd_offset = offset + (self->rd_num_objects++) * PTRSIZE;
					break;
				case DBTYPE_EMPTY:
					cd->cd_offset = virtuals++;
					break;
				case DBTYPE_BOOL:
					cd->cd_offset = offsets[0]++;
					break;
				default:
					cd->cd_offset = offsets[cd->cd_size];
					msize = 1<<(cd->cd_size-1);
					offsets[cd->cd_size] += msize;
			}
		}
	}

	return (PyObject *)self;

rdfail:
	PyErr_SetString(PyExc_TypeError, "DBRowDescriptor expected a tuple of 2-element tuples");
	return NULL;
}


static PyObject *
rd_reduce_ex(PyDBRowDescriptorObject *self, PyObject *arg)
{
	return Py_BuildValue("O(O)", self->ob_type, self->rd_initarg);
}



static void
rd_dealloc(PyDBRowDescriptorObject *self)
{
/*
	extern void DEBUG(char *text);

	{
		char buf[200];
		DEBUG("Dealloc RD");
		sprintf(buf, "0x%08x 0x%08x", self->rd_initarg, self->rd_header);
		DEBUG(buf);
//		sprintf(buf, "%d %d", self->rd_initarg->ob_refcnt, self->rd_header->ob_refcnt);
//		DEBUG(buf);
	}
*/

	Py_XDECREF(self->rd_header);
	Py_XDECREF(self->rd_initarg);
	Py_XDECREF(self->rd_properties);

	self->rd_header = self->rd_initarg = NULL;
	self->ob_type->tp_free((PyObject *)self);

}

static PyObject *
rd_getattr(PyDBRowDescriptorObject *self, PyObject *key)
{
	char *attr;

	if(!PyString_Check(key))
		return NULL;

	attr = PyString_AS_STRING(key);
	if(!strcmp(attr, "length"))
		return (PyObject *)PyInt_FromLong(self->rd_unpacked_size);

	if(!strcmp(attr, "_objects"))
		return (PyObject *)PyInt_FromLong(self->rd_num_objects);

	if(!strcmp(attr, "__guid__"))
		return (PyObject *)PyString_FromString("blue.DBRowDescriptor");

	return PyObject_GenericGetAttr((PyObject *)self, key);
}


static PyObject *
rd_setstate(PyDBRowDescriptorObject *self, PyObject *state)
{
	// this method doesn't "set state" as expected, but rather adds property
	// functions that will be called if the relevant attribute is requested
	// of a DBRow using this descriptor.

	int i;
	PyObject *item;

	if(self->rd_properties)
	{
		PyErr_SetString(PyExc_RuntimeError, "DBRowDescriptor.__setstate__ may only be called once");
		return NULL;
	}

	if(!PyList_Check(state))
	{
		PyErr_SetString(PyExc_TypeError, "DBRowDescriptor.__setstate__ first arg must be a list");
		return NULL;
	}

	// verify state contents
	self->rd_prop_size = PyList_GET_SIZE(state);

	for(i=0; i<self->rd_prop_size; i++)
	{
		item = PyList_GET_ITEM(state, i);
		if(PyTuple_Check(item) && PyTuple_GET_SIZE(item) == 2)
			if(PyString_Check(PyTuple_GET_ITEM(item, 0)) && PyCallable_Check(PyTuple_GET_ITEM(item, 1)))
				continue;

		PyErr_SetString(PyExc_TypeError, "expected a list of tuples -> (string, callable)");
		return NULL;
	}

	self->rd_properties = state;
	Py_INCREF(self->rd_properties);

	Py_INCREF(Py_None);
	return Py_None;
}


static PyObject *
rd_Keys(PyDBRowDescriptorObject *self)
{
	if(!self->rd_header)
	{
		int i;
		PyObject *column;

		if(!(self->rd_header = PyList_New(self->ob_size+self->rd_prop_size)))
			return NULL;

		for(i=0; i < self->ob_size; i++)
			PyList_SET_ITEM(self->rd_header, i, PyString_FromString(self->rd_cd[i].cd_name));

		for(i=0; i < self->rd_prop_size; i++)
		{
			column = PyTuple_GET_ITEM(PyList_GET_ITEM(self->rd_properties, i), 0);
			Py_INCREF(column);  // ugh.
			PyList_SET_ITEM(self->rd_header, i+self->ob_size, column);
		}
	}

	Py_INCREF(self->rd_header);

	return self->rd_header;
}


static struct PyMethodDef rd_methods[] = {
	{"Keys", (PyCFunction)rd_Keys, METH_NOARGS, NULL},
	{"__reduce_ex__", (PyCFunction)rd_reduce_ex, METH_O, NULL},
	{"__setstate__", (PyCFunction)rd_setstate, METH_O, NULL},
	{NULL,	 NULL}		/* sentinel */
};

PyTypeObject PyDBRowDescriptor_Type = {
	PyObject_HEAD_INIT(NULL)
	0,
	"blue.DBRowDescriptor",
	sizeof(PyDBRowDescriptorObject),
	sizeof(ColumnDescriptor),
	(destructor)rd_dealloc,	/* tp_dealloc */
	0,					/* tp_print */
	0,					/* tp_getattr */
	0,					/* tp_setattr */
	0,					/* tp_compare */
	0,					/* tp_repr */
	0,					/* tp_as_number */
	0,					/* tp_as_sequence */
	0,					/* tp_as_mapping */
	0,					/* tp_hash */
	0,					/* tp_call */
	0,					/* tp_str */
	(getattrofunc)rd_getattr,	/* tp_getattro */
	0,					/* tp_setattro */
	0,					/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,/* tp_flags */
	0,					/* tp_doc */
	0,					/* tp_traverse */
	0,					/* tp_clear */
	0,					/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	0,					/* tp_iter */
	0,					/* tp_iternext */
	rd_methods,			/* tp_methods */
	NULL,				/* tp_members */
	0,					/* tp_getset */
	0,					/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	0,					/* tp_init */
	0,					/* tp_alloc */
	rd_new,				/* tp_new */
	0,					/* tp_free */
};





//============================================================================
// DBRow
//============================================================================

static PyObject *
dbrow_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	int i, offset;
	PyDBRowObject *row;
	PyDBRowDescriptorObject *header;

	if(PyTuple_GET_SIZE(args) != 2)
	{
		PyErr_SetString(PyExc_TypeError, "expected 2 arguments");
		return NULL;
	}

	header = (PyDBRowDescriptorObject *)PyTuple_GetItem(args, 0);
	row = (PyDBRowObject *)PyDBRow_New(header, "", 0);

	// WARNING: DBRows are not intended to be instantiated by users. There
	// is no validation on the initialization params, nor are their types
	// checked against the column descriptors. Incorrect use will likely
	// result in a crash.

	args = PyTuple_GetItem(args, 1);  // assumed to be a list or tuple.

	// zero out the objects array, otherwise setToCD will bomb on it.
	offset = ALIGNED(header->rd_unpacked_size);
	row->ob_size = header->rd_num_objects;
	for(i=0; i<row->ob_size; i++)
		*(PyObject **)(&row->dbrow_data[offset + i * PTRSIZE]) = NULL;

	// now populate the row data with the init args
	for(i=0; i < header->ob_size; i++)
		setToCD(row, &header->rd_cd[i], PyList_GET_ITEM(args, i));

	return (PyObject *)row;
}


static PyObject *
dbrow_setstate(PyDBRowObject *self, PyObject *state)
{
	PyObject *data = NULL;
	PyObject *objects = NULL;
	char *in;
	Py_ssize_t in_size;


	if(PyTuple_Check(state))
	{
		if(PyTuple_GET_SIZE(state) < 2
		|| !PyString_Check(data = PyTuple_GET_ITEM(state, 0))
		|| !PyList_Check(objects = PyTuple_GET_ITEM(state, 1))
		){
			PyErr_SetString(PyExc_TypeError, "expected a 2-element tuple -> (string, list)");
			return NULL;
		}
	}
	else if(PyString_Check(state))
		data = state;
	else if(PyList_Check(state))
		objects = state;
	else
	{
		PyErr_SetString(PyExc_TypeError, "expected a string, list or 2-element tuple");
		return NULL;
	}

	if(data)
	{
		if(PyString_AsStringAndSize(data, &in, &in_size))
			return NULL;

		if(!rle_unpack(in, in_size, self->dbrow_data, self->dbrow_header->rd_unpacked_size))
		{
			PyErr_SetString(PyExc_RuntimeError, "Invalid RLE string");
			return NULL;
		}
	}

	if(objects)
	{
		int i, numobjects;
		numobjects = PyList_GET_SIZE(objects);
		for(i=0; i<numobjects; i++)
		{
			data = PyList_GET_ITEM(objects, i);  // re-use data.
			dbrow_append_internal(self, data);
			Py_INCREF(data);
		}
	}

	Py_INCREF(Py_None);
	return Py_None;
}


PyObject *
PyDBRow_New(PyDBRowDescriptorObject *header, char *in, int in_size)
{
	PyDBRowObject *self;

	if(!header || !PyDBRowDescriptor_Check(header))
	{
		PyErr_SetString(PyExc_SystemError, "expected a DBRowDescriptorObject");
		return NULL;
	}

	if(!in)
	{
		PyErr_SetString(PyExc_SystemError, "expected row data");
		return NULL;
	}

	if(!(self = (PyDBRowObject *)PyObject_NewVar(PyDBRowObject, &PyDBRow_Type, header->rd_total_size)))
		return NULL;

	if(!rle_unpack(in, in_size, self->dbrow_data, header->rd_unpacked_size))
	{
		PyErr_SetString(PyExc_RuntimeError, "Invalid RLE string");
		return NULL;
	}


/*	{
		char buf[500];
		int size;

		rle_pack(self->dbrow_data, header->rd_unpacked_size, buf, &size);

		if(memcmp(buf, in, in_size))
		{
			PyErr_SetString(PyExc_SystemError, "encode error");
			return NULL;
		}
	}
*/
	self->ob_size = 0;
	self->dbrow_header = header;
	Py_INCREF(header);

	return (PyObject *)self;
}


static PyObject *
dbrow_pack(PyDBRowObject *self)
{
	char packed[256];
	int packed_size = 0;

	rle_pack(self->dbrow_data, self->dbrow_header->rd_unpacked_size, packed, &packed_size);

	return (PyObject *)PyString_FromStringAndSize(packed, packed_size);
}


PyObject *
dbrow_append(PyDBRowObject *self, PyObject *item)
{
	if(!dbrow_append_internal(self, item))
		return NULL;
	Py_INCREF(item);
	Py_INCREF(Py_None);
	return Py_None;
}


int dbrow_append_internal(PyDBRowObject *self, PyObject *item)
{
	int offset;

	if(self->ob_size >= self->dbrow_header->rd_num_objects)
	{
		PyErr_SetString(PyExc_RuntimeError, "DBRow object table full");
		return 0;
	}

	offset = ALIGNED(self->dbrow_header->rd_unpacked_size);
	offset += (self->ob_size++) * PTRSIZE;

	// NO INCREF, we're stealing this reference.
	*(PyObject **)(&self->dbrow_data[offset]) = item;
	return 1;
}



static PyObject *
dbrow_getobject(PyDBRowObject *self, PyObject *key)
{
	int ix, offset;
	PyObject *item;

	if(!PyInt_Check(key))
	{
		PyErr_SetString(PyExc_TypeError, "integer expected");
		return NULL;
	}

	ix = PyInt_AS_LONG(key);

	if(ix < 0 || ix >= self->ob_size)
	{
		PyErr_SetString(PyExc_IndexError, "Index out of range");
		return NULL;
	}

	offset = ALIGNED(self->dbrow_header->rd_unpacked_size) + ix * PTRSIZE;
	item = *(PyObject **)(&self->dbrow_data[offset]);
	if(!item)
		item = Py_None;

	Py_INCREF(item);
	return item;
}



static void
dbrow_dealloc(PyDBRowObject *self)
{
	int i;
	int offset = ALIGNED(self->dbrow_header->rd_unpacked_size);

	Py_XDECREF(self->dbrow_header);

	for(i=0; i<self->ob_size; i++)
		Py_XDECREF(*(PyObject **)(&self->dbrow_data[offset + i * PTRSIZE]));

	PyObject_Del(self);
}






int
dbrow_setattr(PyDBRowObject *self, PyObject *name, PyObject *value)
{
	int i;
	PyObject *item;

	if(PyString_Check(name))
	{
		char *attr = PyString_AsString(name);
		ColumnDescriptor *cd = findCD(self, attr);

		if(cd)
			return setToCD(self, cd, value);

		if(self->dbrow_header->rd_properties)
		{
			for(i=0; i<self->dbrow_header->rd_prop_size; i++)
			{
				item = PyList_GET_ITEM(self->dbrow_header->rd_properties, i);
				if(!strcmp(attr, PyString_AS_STRING(PyTuple_GET_ITEM(item, 0))))
				{
					PyErr_SetString(PyExc_AttributeError, "read only attribute");
					return -1;
				}
			}
		}
	}
	return PyObject_GenericSetAttr((PyObject *)self, name, value);
}


static PyObject *
dbrow_getattr(PyDBRowObject *self, PyObject *name)
{
	ColumnDescriptor *cd = NULL;

	if(PyString_Check(name))
	{
		int i;
		const char *attr = PyString_AsString(name);
		ColumnDescriptor *cdi;
		PyObject *item;

		if(!strcmp("__header__", attr))
		{
			Py_INCREF(self->dbrow_header);
			return (PyObject *)self->dbrow_header;
		}

		if(!strcmp("__keys__", attr))
		{
			return rd_Keys(self->dbrow_header);
		}

		if(!strcmp("__guid__", attr))
		{
			return (PyObject *)PyString_FromString("blue.DBRow");
		}

		// find named column in the list...
		for(i=0; i<self->dbrow_header->ob_size; i++)
		{
			cdi = &self->dbrow_header->rd_cd[i];
			if(!strcmp(cdi->cd_name, attr))
			{
				cd = cdi;
				break;
			}
		}

		// see if we have properties
		if(!cd && self->dbrow_header->rd_properties)
		{
			for(i=0; i<self->dbrow_header->rd_prop_size; i++)
			{
				item = PyList_GET_ITEM(self->dbrow_header->rd_properties, i);
				if(!strcmp(attr, PyString_AS_STRING(PyTuple_GET_ITEM(item, 0))))
				{
					return PyObject_CallFunction(PyTuple_GET_ITEM(item, 1), "O", self);
				}
			}
		}
	}
	else if(PyInt_Check(name))
	{
		int i = PyInt_AS_LONG(name);
		if(i >= 0 && i < self->dbrow_header->ob_size)
			cd = &self->dbrow_header->rd_cd[i];
		else
		{
			i -= self->dbrow_header->ob_size;
			if(i >= 0 && i < self->dbrow_header->rd_prop_size)
				return PyObject_CallFunction(PyTuple_GET_ITEM(PyList_GET_ITEM(self->dbrow_header->rd_properties, i), 1), "O", self);

			PyErr_SetString(PyExc_IndexError, "Index out of range");
			return NULL;
		}
	}


	if(!cd)
		return PyObject_GenericGetAttr((PyObject *)self, name);

	return getFromCD(self, cd);
}


static PyObject *
dbrow_str(PyDBRowObject *self)
{
	PyObject *result = NULL, *str;
	if(str = PyObject_GetAttr((PyObject *)blue, py_dbrow_str))
	{
		result = PyObject_CallFunction(str, "O", self);
		Py_DECREF(str);
	}
	return result;
}


static int
dbrow_obj_length(PyDBRowObject *self)
{
	// number of columns
	return self->dbrow_header->ob_size;
}

static PyObject *
dbrow_sq_item(PyDBRowObject *self, int i)
{
	if(i >= 0 && i < self->dbrow_header->ob_size)
		// see if index refers to normal column
		return getFromCD(self, &self->dbrow_header->rd_cd[i]);
	else
	{
		// see if index refers to a property column
		i -= self->dbrow_header->ob_size;
		if(i >= 0 && i < self->dbrow_header->rd_prop_size)
			return PyObject_CallFunction(PyTuple_GET_ITEM(PyList_GET_ITEM(self->dbrow_header->rd_properties, i), 1), "O", self);
	}

	PyErr_SetString(PyExc_IndexError, "Index out of range");
	return NULL;
}

static int
dbrow_sq_ass_item(PyDBRowObject *self, Py_ssize_t i, PyObject *obj)
{
	if(i >= 0 && i < self->dbrow_header->ob_size)
		return setToCD(self, &self->dbrow_header->rd_cd[i], obj);

	i -= self->dbrow_header->ob_size;
	if(i >= 0 && i < self->dbrow_header->rd_prop_size)
	{
		PyErr_SetString(PyExc_AttributeError, "read only attribute");
		return -1;
	}

	PyErr_SetString(PyExc_IndexError, "Index out of range");
	return -1;
}


static PyObject *
dbrow_mp_subscript(PyDBRowObject *self, PyObject *key)
{
	return dbrow_getattr(self, key);
}



static PySequenceMethods dbrow_as_sequence = {
	(lenfunc)dbrow_obj_length,		/* sq_length */
	0,								/* sq_concat */
	0,								/* sq_repeat */
	(ssizeargfunc)dbrow_sq_item,	/* sq_item */
	0,								/* sq_slice */
	(ssizeobjargproc)dbrow_sq_ass_item,	/* sq_ass_item */
	0,								/* sq_ass_slice */
	0,								/* sq_contains */
};


static PyMappingMethods dbrow_as_mapping = {
	(lenfunc)dbrow_obj_length,			/*mp_length*/
	(binaryfunc)dbrow_mp_subscript,		/*mp_subscript*/
	0, //(objobjargproc)dbrow_ass_sub,	/*mp_ass_subscript*/
};


static struct PyMethodDef dbrow_methods[] = {
	{"append", (PyCFunction)dbrow_append, METH_O, NULL},
	{"pack", (PyCFunction)dbrow_pack, METH_NOARGS, NULL},
	{"getobject", (PyCFunction)dbrow_getobject, METH_O, NULL},
	{"__setstate__", (PyCFunction)dbrow_setstate, METH_O, NULL},
	{NULL,	 NULL}		/* sentinel */
};


#define OFF(x) offsetof(PyDBRowObject, x)



PyTypeObject PyDBRow_Type = {
	PyObject_HEAD_INIT(NULL)
	0,
	"blue.DBRow",
	sizeof(PyDBRowObject),
	sizeof(char),
	(destructor)dbrow_dealloc,	/* tp_dealloc */
	0,					/* tp_print */
	0,					/* tp_getattr */
	0,					/* tp_setattr */
	0,					/* tp_compare */
	0,					/* tp_repr */
	0,					/* tp_as_number */
	&dbrow_as_sequence,	/* tp_as_sequence */
	&dbrow_as_mapping,	/* tp_as_mapping */
	0,					/* tp_hash */
	0,					/* tp_call */
	(reprfunc)&dbrow_str,			/* tp_str */
	(getattrofunc)dbrow_getattr,	/* tp_getattro */
	(setattrofunc)dbrow_setattr,	/* tp_setattro */
	0,					/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,/* tp_flags */
	0,					/* tp_doc */
	0,					/* tp_traverse */
	0,					/* tp_clear */
	0,					/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	0,					/* tp_iter */
	0,					/* tp_iternext */
	dbrow_methods,		/* tp_methods */
	0,					/* tp_members */
	0,					/* tp_getset */
	0,					/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	0,					/* tp_init */
	0,					/* tp_alloc */
	dbrow_new,			/* tp_new */
	0,					/* tp_free */
};




int init_dbrow(PyObject *m)
{
	// prep DBRow type

	PyDBRow_Type.ob_type = &PyType_Type;
	PyDBRow_Type.tp_alloc = PyType_GenericAlloc;
	PyDBRow_Type.tp_free = PyObject_Del;
	if (PyType_Ready(&PyDBRow_Type) < 0)
		return 0;

	// prep DBRowDescriptor type

	PyDBRowDescriptor_Type.ob_type = &PyType_Type;
	PyDBRowDescriptor_Type.tp_alloc = PyType_GenericAlloc;
	PyDBRowDescriptor_Type.tp_free = PyObject_Del;
	if (PyType_Ready(&PyDBRowDescriptor_Type) < 0)
		return 0;

	Py_INCREF((PyObject*)&PyDBRow_Type);
	PyModule_AddObject(m, "DBRow", (PyObject*)&PyDBRow_Type);

	Py_INCREF((PyObject*)&PyDBRowDescriptor_Type);
	PyModule_AddObject(m, "DBRowDescriptor", (PyObject*)&PyDBRowDescriptor_Type);

	py_dbrow_str = PyString_FromString("dbrow_str");
	blue = m;

	return 1;
}

