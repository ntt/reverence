/*
// __init__.c - _blue module namespace
//
// Copyright (c) 2003-2010 Jamie "Entity" van den Berge <jamie@hlekkir.com>
//
// This code is free software; you can redistribute it and/or modify
// it under the terms of the BSD license (see the file LICENSE.txt
// included with the distribution).
*/


#include "Python.h"
#include "dbrow.h"
#include "marshal.h"

PyMODINIT_FUNC
init_blue(void)
{
	PyObject *m, *marshal;

	m = Py_InitModule("_blue", NULL);
	if (m == NULL)
		return;

	if(!init_dbrow(m))
		return;

	marshal = init_marshal();
	if(marshal)
		PyModule_AddObject(m, "marshal", marshal);

}

