/*
// virtualfile.c - file object that treats a section of a file as a real one.
//
// Copyright (c) 2012 Jamie "Entity" van den Berge <jamie@hlekkir.com>
//
// This code is free software; you can redistribute it and/or modify
// it under the terms of the BSD license (see the file LICENSE.txt
// included with the distribution).
*/

/*
// This read-only PyFile_Type subclass limits I/O to a specific offset and
// size in a file, and fools seek() and tell(). Instances of it can be
// used in almost all places expecting a regular file object.
//
// Used by the EmbedFS module.
//
// Caveat: feeding an object of this kind to cPickle.load() works, but after
// that you -MUST- do a tell() or seek() if you want to keep using the file!
// This is because cPickle cheats for performance; When the object is
// (a subclass of) the builtin file type, it accesses the file using stdio
// instead of going through the object's read() and readline() methods, which
// in turn means this class never gets an opportunity to update its own state.
*/

#include <stdio.h>

#include "Python.h"
#include "virtualfile.h"

static PyObject *(*file_read)(PyFileObject *, PyObject *);
static PyObject *(*file_readline)(PyFileObject *, PyObject *);
static PyObject *(*file_readlines)(PyFileObject *, PyObject *);
static PyObject *(*file_tell)(PyFileObject *);
static PyObject *(*file_seek)(PyFileObject *, PyObject *);


#define READLINE_INITIALBUFFERSIZE 100
static PyObject *rlarg;  // used for file.readline().
static PyObject *one;  // 1!

typedef struct {
	PyFileObject file;
	long vf_start;      // offset in real file of beginning of virtual file.
	long vf_end;        // offset in real file of the EOF of virtual file.
	long vf_remaining;  // bytes remaining until virtual EOF
} PyVirtualFileObject;


__inline static PyObject *
tuple(long value)
{
	// makes a single element tuple containing an int of specified value.
	PyObject *tuple;
	tuple = PyTuple_New(1);
	PyTuple_SET_ITEM(tuple, 0, PyInt_FromLong(value));
	return tuple;
}

static int
virtualfile_init(PyVirtualFileObject *self, PyObject *args, PyObject *kwds)
{
	// _VirtualFile(filename, mode, buffering, offset, size)
	int ret;

	PyObject *oargs = args, *py_filename, *py_buffering = NULL;
	char *mode = NULL;

	self->vf_start = 0;
	self->vf_end = LONG_MAX;

	// validate args
	if(!PyArg_ParseTuple(args, "O|sOll:_VirtualFile", &py_filename, &mode, &py_buffering, &self->vf_start, &self->vf_end))
		return -1;

	if(mode)
	{
		if(strchr(mode, 'w') || strchr(mode, 'a') || strchr(mode, '+')) {
			PyErr_SetString(PyExc_ValueError, "file mode must be read-only");
			return -1;
		}
	}

	// make new args tuple for initializing super.
	ret = (int)PyTuple_GET_SIZE(args);
	if(!(args = PyTuple_New(ret>3?3:ret)))
		return -1;
	Py_INCREF(py_filename);
	PyTuple_SET_ITEM(args, 0, py_filename);
	if(mode)
	{
		oargs = PyTuple_GET_ITEM(oargs, 1);
		Py_INCREF(oargs);
		PyTuple_SET_ITEM(args, 1, oargs);
	}
	if(py_buffering)
	{
		Py_INCREF(py_buffering);
		PyTuple_SET_ITEM(args, 2, py_buffering);
	}

	// do super().__init__()
	ret = PyFile_Type.tp_init((PyObject *)self, args, kwds);

	Py_DECREF(args);

	if(!ret)
	{
		self->vf_remaining = self->vf_end;
		self->vf_end += self->vf_start;
		args = tuple(self->vf_start);  // reuse args again
		file_seek((PyFileObject *)self, args);
		Py_DECREF(args);
	}

	return ret;
}


static PyObject *
virtualfile_read(PyVirtualFileObject *self, PyObject *args)
{
	// Wrapper around file.read(). Enforces seek limits.
	PyObject *result;
	int bytesrequested = -1;

	if(!PyArg_ParseTuple(args, "|i:read", &bytesrequested))
		return NULL;

	if(!self->vf_remaining)
		return PyString_FromString("");

	if(bytesrequested == 1)
		return file_read((PyFileObject *)self, one);

	if(bytesrequested < 0 || bytesrequested > self->vf_remaining)
		bytesrequested = self->vf_remaining;

	args = tuple(bytesrequested);  // reusing args
	result = file_read((PyFileObject *)self, args);
	Py_DECREF(args);
	return result;
}


#define UPDATE_POS(bytes) \
{                                                                            \
	if(univ_newline)                                                         \
	{                                                                        \
		/* in universal newline mode, bytesread might not equal the actual   \
		   number of bytes processed in the file (because it strips \r).     \
		   use tell() to see where we are. */                                \
		PyObject *t = file_tell((PyFileObject *)self);                       \
		if(!t)                                                               \
			goto fail;                                                       \
		self->vf_remaining = self->vf_end-PyLong_AsLong(t);                  \
		Py_DECREF(t);                                                        \
		if(self->vf_remaining < 0)                                           \
			self->vf_remaining = 0;                                          \
	}                                                                        \
	else                                                                     \
		self->vf_remaining -= (long)(bytes);                                 \
}


static PyObject *
virtualfile_readline(PyVirtualFileObject *self, PyObject *args)
{
	// Wrapper around file.readline().
	// Slightly trickier because the size argument makes it allocate that
	// much ram, so we can't just set it to the remaining size.

	PyObject *result = NULL;
	PyObject *temp = NULL;
	PyObject *string;

	int eol = 0;
	long bytesread;
	long limit = -1;
	int univ_newline = self->file.f_univ_newline;

	int buffer_size = READLINE_INITIALBUFFERSIZE;
	int buffer_incr = 200;

	if(args)
	{
		if(!PyArg_ParseTuple(args, "|i:read", &limit))
			return NULL;
	}

	if(!limit || !self->vf_remaining)
		return PyString_FromString("");

	if(limit > 0)
	{
		// Positive size; Read this much or until EOF, whichever comes first.
		// easy. just limit the given size to what's remaining.
		if(limit > self->vf_remaining)
			limit = self->vf_remaining;

		args = tuple(limit);  // reusing args
		result = file_read((PyFileObject *)self, args);
		Py_DECREF(args);

		UPDATE_POS(((PyStringObject *)result)->ob_size);
		return result;
	}

	// Negative size; Read until EOL or EOF.
	// Not so easy because we don't know the length of the next line.

	while(!eol && self->vf_remaining)
	{
		// reuses args.
		if(buffer_size >= self->vf_remaining)
		{
			args = tuple(self->vf_remaining);
			string = file_readline((PyFileObject *)self, args);
			Py_DECREF(args);
		}
		else
		{
			if(buffer_size == READLINE_INITIALBUFFERSIZE)
				string = file_readline((PyFileObject *)self, rlarg);
			else
			{
				args = tuple(buffer_size);
				string = file_readline((PyFileObject *)self, args);
				Py_DECREF(args);
			}
		}

		if(!string)
			goto fail;

		bytesread = (long)((PyStringObject *)string)->ob_size;

		UPDATE_POS(bytesread);

		if(bytesread == buffer_size)
		{
			if(!(eol = (PyString_AS_STRING(string)[buffer_size-1] == '\n')))
			{
				// increase buffer size for next pass
				if(buffer_size < 1000000)
				{
					buffer_size += buffer_incr;
					buffer_incr = buffer_size >> 2;
				}
			}
		}
		else
			eol = 1;

		if(result)
		{
			// already had partial line. concat the data read.
			PyString_ConcatAndDel(&result, string);
			if(!result)
				goto fail;
		}
		else
			result = string;
	}

	return result;

fail:
	Py_XDECREF(result);
	return NULL;
}

static PyObject *
virtualfile_readlines(PyVirtualFileObject *self, PyObject *args)
{
	PyErr_SetString(PyExc_RuntimeError, "readlines not implemented");
	return NULL;
}

static PyObject *
virtualfile_tell(PyVirtualFileObject *self)
{
	long pos;
	PyObject *t = file_tell((PyFileObject *)self);
	if(!t)
		return NULL;
	pos = PyLong_AsLong(t);
	Py_DECREF(t);
	self->vf_remaining = self->vf_end - pos;
	return PyLong_FromLong(pos - self->vf_start);
}

static PyObject *
virtualfile_seek(PyVirtualFileObject *self, PyObject *args)
{
	long pos;
	int whence = 0;
	PyObject *ret;

    if (!PyArg_ParseTuple(args, "l|i:seek", &pos, &whence))
        return NULL;

	// figure out the absolute position to seek() to.
	if(whence == 2)
		pos += self->vf_end;
	else if(whence == 1)
	{
		PyObject *t = file_tell((PyFileObject *)self);
		if(!t)
			return NULL;
		pos += PyLong_AsLong(t);
		Py_DECREF(t);
	}
	else
		pos += self->vf_start;

	// limit seek position
	if(pos < self->vf_start)
		pos = self->vf_start;
	else if(pos > self->vf_end)
		pos = self->vf_end;

	// update remaining bytes count
	self->vf_remaining = self->vf_end - pos;

	args = tuple(pos); // reuse args
	ret = file_seek((PyFileObject *)self, args);
	Py_DECREF(args);

	return ret;
}

static PyObject *
virtualfile_iternext(PyVirtualFileObject *self)
{
	if(self->vf_remaining)
		return virtualfile_readline(self, NULL);
	return NULL;
}



static PyMethodDef virtualfile_methods[] = {
    {"read",      (PyCFunction)virtualfile_read,      METH_VARARGS, NULL},
    {"readline",  (PyCFunction)virtualfile_readline,  METH_VARARGS, NULL},
    {"readlines", (PyCFunction)virtualfile_readlines, METH_VARARGS, NULL},
    {"seek",      (PyCFunction)virtualfile_seek,      METH_VARARGS, NULL},
    {"tell",      (PyCFunction)virtualfile_tell,      METH_NOARGS,  NULL},
    {NULL,            NULL}             /* sentinel */
};


PyTypeObject PyVirtualFile_Type = {
    PyObject_HEAD_INIT(NULL)
	0,
    "_VirtualFile",
    sizeof(PyVirtualFileObject),
    0,
    0,                                          /* tp_dealloc */
    0,                                          /* tp_print */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
    0,                                          /* tp_compare */
    0,                                          /* tp_repr */
    0,                                          /* tp_as_number */
    0,                                          /* tp_as_sequence */
    0,                                          /* tp_as_mapping */
    0,                                          /* tp_hash */
    0,                                          /* tp_call */
    0,                                          /* tp_str */
    0,                                          /* tp_getattro */
    0,                                          /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,   /* tp_flags */
    0,                                          /* tp_doc */
    0,                                          /* tp_traverse */
    0,                                          /* tp_clear */
    0,                                          /* tp_richcompare */
    0,                                          /* tp_weaklistoffset */
    0,                                          /* tp_iter */
    (iternextfunc)virtualfile_iternext,         /* tp_iternext */
    virtualfile_methods,                        /* tp_methods */
    0,                                          /* tp_members */
    0,                                          /* tp_getset */
    0,                                          /* tp_base */
    0,                                          /* tp_dict */
    0,                                          /* tp_descr_get */
    0,                                          /* tp_descr_set */
    0,                                          /* tp_dictoffset */
    (void *)virtualfile_init,                   /* tp_init */
    0,                                          /* tp_alloc */
    0,                                          /* tp_new */
    0,                                          /* tp_free */
};


int init_virtualfile(PyObject *m)
{
	PyMethodDef *method;

	PyVirtualFile_Type.tp_base = &PyFile_Type;
	if (PyType_Ready(&PyVirtualFile_Type) < 0)
		return 0;

	Py_INCREF((PyObject*)&PyVirtualFile_Type);
	PyModule_AddObject(m, "_VirtualFile", (PyObject*)&PyVirtualFile_Type);

	rlarg = tuple(READLINE_INITIALBUFFERSIZE);
	one = tuple(1);

	// grab relevant methods from file object.
	for(method = PyFile_Type.tp_methods; method->ml_name; method++)
	{
		     if(!strcmp("read"     , method->ml_name)) file_read      = (void *)method->ml_meth;
		else if(!strcmp("readline" , method->ml_name)) file_readline  = (void *)method->ml_meth;
		else if(!strcmp("readlines", method->ml_name)) file_readlines = (void *)method->ml_meth;
		else if(!strcmp("seek"     , method->ml_name)) file_seek      = (void *)method->ml_meth;
		else if(!strcmp("tell"     , method->ml_name)) file_tell      = (void *)method->ml_meth;
	}
	

	return 1;
}




