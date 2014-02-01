/*
// fsd.c - FileStaticData classes and functions
//
// - FsdUnsignedIntegerKeyMap
//     efficient binary blob keymap class for FSD indices/dicts
//
// - _uint32_from / _int32_from
//     faster integer unpacking functions.
//
// Copyright (c) 2003-2013 Jamie "Entity" van den Berge <jamie@hlekkir.com>
//
// This code is free software; you can redistribute it and/or modify
// it under the terms of the BSD license (see the file LICENSE.txt
// included with the distribution).
*/

#include "Python.h"
#include "fsd.h"

#include <stdio.h>
#include <stdlib.h>


//----------------------------------------------------------------------------
// FsdUnsignedIntegerKeyMap Iterator
//

static PyKeyMapIteratorObject *
_iter(PyKeyMapObject *keymap, int mode)
{
	PyKeyMapIteratorObject *iter = (PyKeyMapIteratorObject *)PyType_GenericAlloc(&PyKeyMapIterator_Type, 0);

	if(!iter)
		return NULL;

	iter->kmi_keymap = keymap;
	iter->kmi_mode = mode;

	Py_INCREF(keymap);
	return iter;
}


static void
keymapiter_dealloc(PyKeyMapIteratorObject *self)
{
	Py_XDECREF(self->kmi_keymap);
	self->ob_type->tp_free((PyObject *)self);
}


#define ITERKEYS 0
#define ITERVALUES 1
#define ITERITEMS 2
#define ITERVALUES_NS 3
#define ITERITEMS_NS 4

PyObject *
keymapiter_next(PyKeyMapIteratorObject *self)
{
	keymap_entry *entry;
	int size;

	if(self->kmi_index < 0 || self->kmi_index >= self->kmi_keymap->km_map->count)
		return NULL;

	entry = (keymap_entry *)&(((char *)self->kmi_keymap->km_map->entry)[self->kmi_keymap->km_entrysize * self->kmi_index++]);
	size = (self->kmi_keymap->km_entrysize == 12) ? entry->size : 0;

	switch(self->kmi_mode)
	{
		case ITERKEYS     :
			if (self->kmi_keymap->km_signed)
				return PyLong_FromLong(entry->key);
			else
				return PyLong_FromUnsignedLong(entry->key);

		case ITERVALUES   : return Py_BuildValue("ii", entry->offset, size);
		case ITERITEMS    : return Py_BuildValue((self->kmi_keymap->km_signed ? "i(ii)" : "I(ii)"), entry->key, entry->offset, size);
		case ITERVALUES_NS: return PyLong_FromLong(entry->offset);
		case ITERITEMS_NS : return Py_BuildValue("ii", entry->key, entry->offset);

		default:
			PyErr_Format(PyExc_RuntimeError, "Invalid mode for KeyMapIterator: %d", self->kmi_mode);
			return NULL;
	}

}


PyTypeObject PyKeyMapIterator_Type = {
	PyObject_HEAD_INIT(NULL)
	0,
    "KeyMapIterator",               /* tp_name */
    sizeof(PyKeyMapIteratorObject), /* tp_basicsize */
    0,                              /* tp_itemsize */
    (destructor)keymapiter_dealloc, /* tp_dealloc */
    0,                              /* tp_print */
    0,                              /* tp_getattr */
    0,                              /* tp_setattr */
    0,                              /* tp_reserved */
    0,                              /* tp_repr */
    0,                              /* tp_as_number */
    0,                              /* tp_as_sequence */
    0,                              /* tp_as_mapping */
    0,                              /* tp_hash */
    0,                              /* tp_call */
    0,                              /* tp_str */
    0,                              /* tp_getattro */
    0,                              /* tp_setattro */
    0,                              /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,             /* tp_flags */
    0,                              /* tp_doc */
    0,                              /* tp_traverse */
    0,                              /* tp_clear */
    0,                              /* tp_richcompare */
    0,                              /* tp_weaklistoffset */
    PyObject_SelfIter,              /* tp_iter */
    (iternextfunc)keymapiter_next,  /* tp_iternext */
    0,                              /* tp_methods */
    0,                              /* tp_members */
    0,                              /* tp_getset */
    0,                              /* tp_base */
    0,                              /* tp_dict */
    0,                              /* tp_descr_get */
    0,                              /* tp_descr_set */
    0,                              /* tp_dictoffset */
    0,                              /* tp_init */
    0,            					/* tp_alloc */
    0,                              /* tp_new */
};



//----------------------------------------------------------------------------
// FsdUnsignedIntegerKeyMap
//

static PyObject *
keymap_initialize(PyKeyMapObject *self, PyObject *args)
{
	PyStringObject *pydata = NULL;
	char *data = NULL;
	Py_ssize_t size;
	int offset = 0;
	int hassize = 1;
	int issigned = 0;

	if(!PyArg_ParseTuple(args, "S|iii:Initialize", &pydata, &offset, &hassize, &issigned))
		return NULL;

	PyString_AsStringAndSize((PyObject *)pydata, &data, &size);

	if(offset < 0)
	{
		PyErr_Format(PyExc_ValueError, "Initialize received bogus offset: %d", offset);
		return NULL;
	}

	if(offset > (size-4))
	{
		PyErr_SetString(PyExc_ValueError, "Initialize requires a buffer of at least 4 bytes");
		return NULL;
	}

	self->km_signed = !!issigned;
	self->km_entrysize = hassize ? 12 : 8;
	self->km_map = (keymap *)&data[offset];
	size -= (offset+4);

	if((int32_t)size < self->km_map->count*self->km_entrysize)
	{
		PyErr_Format(PyExc_ValueError, "Not enough data in buffer, expected %d bytes", self->km_map->count*self->km_entrysize);
		return NULL;
	}

	// keep safety reference to string object
	self->km_ref = (PyObject *)pydata;
	Py_INCREF(pydata);

	Py_INCREF(Py_None);

	return Py_None;
}


static PyObject *
keymap_getattr(PyKeyMapObject *self, PyObject *name)
{
	return PyObject_GenericGetAttr((PyObject *)self, name);
}


static int _keycmp(keymap_entry *a, keymap_entry *b)
{
	return a->key - b->key;
}


__inline static PyObject *
_internal_get(PyKeyMapObject *self, PyObject *key, int raise)
{
	// finds and returns value pair associated with key.

	uint32_t k;
	keymap_entry *entry;
	int size;

	if(!PyInt_Check(key) && !PyLong_Check(key))
	{
		PyErr_SetString(PyExc_ValueError, "get called with non-integer key");
		return NULL;
	}

	k = PyInt_AsLong(key);

	/* note: using &k as a keymap_entry* parameter to the _keycmp function.
	   this works because only the first member of it (key) is accessed. */
	entry = bsearch(&k, self->km_map->entry, self->km_map->count, self->km_entrysize, (void *)_keycmp);
	if(!entry)
	{
		if(raise)
		{
			PyErr_Format(PyExc_KeyError, "%d", k);
			return NULL;
		}
		Py_INCREF(Py_None);
		return Py_None;
	}

	size = (self->km_entrysize == 12) ? entry->size : 0;

	return Py_BuildValue("ii", entry->offset, size);
}

static PyObject *
keymap_get(PyKeyMapObject *self, PyObject *key)
{
	return _internal_get(self, key, 0);
}

static PyObject *
keymap_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	PyObject *self;
	self = (PyObject *)type->tp_alloc(type, 0);
	if(!self)
		return NULL;
	return self;
}

static void
keymap_dealloc(PyKeyMapObject *self)
{
	Py_XDECREF(self->km_ref);
	self->ob_type->tp_free((PyObject *)self);
}

static int
keymap_obj_length(PyKeyMapObject *self)
{
	return self->km_map->count;
}

static PyObject *
keymap_mp_subscript(PyKeyMapObject *self, PyObject *key)
{
	return _internal_get(self, key, 1);
}

static PyObject *
keymap_iterkeys(PyKeyMapObject *self)
{
	return (PyObject *)_iter(self, 0);
}

static PyObject *
keymap_itervalues(PyKeyMapObject *self)
{
	return (PyObject *)_iter(self, 1);
}

static PyObject *
keymap_iteritems(PyKeyMapObject *self)
{
	return (PyObject *)_iter(self, 2);
}

static PyObject *
keymap_iterspecial(PyKeyMapObject *self, PyObject *pymode)
{
	int mode = -1;
	mode = PyInt_AsLong(pymode);  // nope, no safety check.
	return (PyObject *)_iter(self, mode);
}



static PySequenceMethods keymap_as_sequence = {
	(lenfunc)keymap_obj_length,		/* sq_length */
	0,								/* sq_concat */
	0,								/* sq_repeat */
	0,  //(ssizeargfunc)keymap_sq_item,	/* sq_item */
	0,								/* sq_slice */
	0, //(ssizeobjargproc)keymap_sq_ass_item,	/* sq_ass_item */
	0,								/* sq_ass_slice */
	0,								/* sq_contains */
};


static PyMappingMethods keymap_as_mapping = {
	(lenfunc)keymap_obj_length,			/*mp_length*/
	(binaryfunc)keymap_mp_subscript,		/*mp_subscript*/
	0, //(objobjargproc)keymap_ass_sub,	/*mp_ass_subscript*/
};

static struct PyMethodDef keymap_methods[] = {
	{"Initialize", (PyCFunction)keymap_initialize, METH_VARARGS, NULL},
	{"Get", (PyCFunction)keymap_get, METH_O, NULL},
	{"iteritems", (PyCFunction)keymap_iteritems, METH_NOARGS, NULL},
	{"itervalues", (PyCFunction)keymap_itervalues, METH_NOARGS, NULL},
	{"iterkeys", (PyCFunction)keymap_iterkeys, METH_NOARGS, NULL},

	{"_iterspecial", (PyCFunction)keymap_iterspecial, METH_O, NULL},
	{NULL,	 NULL}		/* sentinel */
};


PyTypeObject PyKeyMap_Type = {
	PyObject_HEAD_INIT(NULL)
	0,
	"FsdUnsignedIntegerKeyMap",
	sizeof(PyKeyMapObject),
	0,
	(destructor)keymap_dealloc,	/* tp_dealloc */
	0,					/* tp_print */
	0,					/* tp_getattr */
	0,					/* tp_setattr */
	0,					/* tp_compare */
	0,					/* tp_repr */
	0,					/* tp_as_number */
	0, //&keymap_as_sequence,	/* tp_as_sequence */
	&keymap_as_mapping,	/* tp_as_mapping */
	0,					/* tp_hash */
	0,					/* tp_call */
	0, //(reprfunc)&keymap_str,			/* tp_str */
	(getattrofunc)keymap_getattr,	/* tp_getattro */
	0,					/* tp_setattro */
	0,					/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,/* tp_flags */
	0,					/* tp_doc */
	0,					/* tp_traverse */
	0,					/* tp_clear */
	0,					/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	(getiterfunc)keymap_iterkeys,	/* tp_iter */
	0,					/* tp_iternext */
	keymap_methods,		/* tp_methods */
	0,					/* tp_members */
	0,					/* tp_getset */
	0,					/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	0,					/* tp_init */
	0,					/* tp_alloc */
	keymap_new,			/* tp_new */
	0,					/* tp_free */
};


//----------------------------------------------------------------------------
// unpacking functions for (unsigned) ints.
// these are slightly faster than an aliased struct.Struct().unpack_from
//

PyObject *
fsd_uint32_from(PyObject *self, PyObject *args)
{
	char *s;
	int size, offset=0;
	PyObject *dummy;  // used by fsd.py
	if(!PyArg_ParseTuple(args, "s#|iO:_uint32", &s, &size, &offset, &dummy))
		return NULL;
	if(offset >= 0 && offset <= size-4)
		return PyLong_FromUnsignedLong(*(uint32_t *)&s[offset]);
	PyErr_SetString(PyExc_ValueError, "_uint32_from requires a buffer of at least 4 bytes");
	return NULL;
}

PyObject *
fsd_int32_from(PyObject *self, PyObject *args)
{
	char *s;
	int size, offset=0;
	PyObject *dummy;  // used by fsd.py
	if(!PyArg_ParseTuple(args, "s#|iO:_int32", &s, &size, &offset, &dummy))
		return NULL;
	if(offset >= 0 && offset <= size-4)
		return PyInt_FromLong(*(int32_t *)&s[offset]);
	PyErr_SetString(PyExc_ValueError, "_int32_from requires a buffer of at least 4 bytes");
	return NULL;
}

PyObject *
fsd_string_from(PyObject *self, PyObject *args)
{
	char *s;
	int size, offset=0, length;
	PyObject *dummy;  // used by fsd.py
	if(!PyArg_ParseTuple(args, "s#|iO:_int32", &s, &size, &offset, &dummy))
		return NULL;

	size -= offset;
	if(size < 4)
		goto fail;

	length = *(int32_t *)&s[offset];
	size -= 4;
	if(length <= size)
		return PyString_FromStringAndSize(&s[offset+4], length);
fail:
	PyErr_SetString(PyExc_ValueError, "_int32_from requires a buffer of at least 4 bytes");
	return NULL;
}

// offset table generator for FSD_Object instances
PyObject *
fsd_make_offsets_table(PyObject *self, PyObject *args)
{
	char *data;
	int size, data_offset, relative_offset;
	int num;
	int i;

	PyObject *names;
	PyObject *result, *v;

	if(!PyArg_ParseTuple(args, "Os#ii:_fsd_make_offsets_table", &names, &data, &size, &data_offset, &relative_offset))
		return NULL;

	if(!(result = PyDict_New()))
		return NULL;

	names = PySequence_Fast(names, "Expected sequence of attribute names");
	num = PySequence_Size(names);

	data += (data_offset + relative_offset);
	relative_offset += (4*num);

	if (PyList_Check(names))
	{
		for(i=0; i<num; i++)
		{
			PyDict_SetItem(result, PyList_GET_ITEM(names, i), v = PyInt_FromLong(relative_offset + ((int32_t *)data)[i]));
			Py_DECREF(v);
		}
	}
	else
	{
		for(i=0; i<num; i++)
		{
			PyDict_SetItem(result, PyTuple_GET_ITEM(names, i),  v = PyInt_FromLong(relative_offset + ((int32_t *)data)[i]));
			Py_DECREF(v);
		}
	}
	Py_DECREF(names);

	return result;
}

//----------------------------------------------------------------------------
// _pyFSD module init
//

static struct PyMethodDef fsd_methods[] = {
	{"_uint32_from", (PyCFunction)fsd_uint32_from, METH_VARARGS, NULL},
	{"_int32_from", (PyCFunction)fsd_int32_from, METH_VARARGS, NULL},
	{"_string_from", (PyCFunction)fsd_string_from, METH_VARARGS, NULL},
	{"_make_offsets_table", (PyCFunction)fsd_make_offsets_table, METH_VARARGS, NULL},
	{ NULL, NULL }
};


PyObject *
init_pyFSD(void)
{
	PyObject *m;

	PyKeyMap_Type.ob_type = &PyType_Type;
	PyKeyMap_Type.tp_alloc = PyType_GenericAlloc;
	PyKeyMap_Type.tp_free = PyObject_Del;

	if (PyType_Ready(&PyKeyMap_Type) < 0)
		return NULL;

	PyKeyMapIterator_Type.ob_type = &PyType_Type;
	PyKeyMapIterator_Type.tp_alloc = PyType_GenericAlloc;
	PyKeyMapIterator_Type.tp_free = PyObject_Del;

	if (PyType_Ready(&PyKeyMapIterator_Type) < 0)
		return NULL;


	m = Py_InitModule("reverence._pyFSD", fsd_methods);
	if(!m)
		return NULL;

	Py_INCREF(m);
	Py_INCREF((PyObject*)&PyKeyMap_Type);
	PyModule_AddObject(m, "FsdUnsignedIntegerKeyMap", (PyObject*)&PyKeyMap_Type);

	return m;
}


