/*
// dbrow.h
//
// Copyright (c) 2003-2010 Jamie "Entity" van den Berge <jamie@hlekkir.com>
//
// This code is free software; you can redistribute it and/or modify
// it under the terms of the BSD license (see the file LICENSE.txt
// included with the distribution).
*/

#ifndef _DBROW_H
#define _DBROW_H
#ifdef __cplusplus
extern "C" {
#endif

#include "Python.h"

#define DBTYPE_EMPTY         0
#define DBTYPE_NULL          1
#define DBTYPE_I2            2
#define DBTYPE_I4            3
#define DBTYPE_R4            4
#define DBTYPE_R8            5
#define DBTYPE_CY            6
#define DBTYPE_DATE          7
#define DBTYPE_BSTR          8
#define DBTYPE_IDISPATCH     9
#define DBTYPE_ERROR        10
#define DBTYPE_BOOL         11
#define DBTYPE_VARIANT      12
#define DBTYPE_IUNKNOWN     13
#define DBTYPE_DECIMAL      14
#define DBTYPE_UI1          17
#define DBTYPE_I1           16
#define DBTYPE_UI2          18
#define DBTYPE_UI4          19
#define DBTYPE_I8           20
#define DBTYPE_UI8          21
#define DBTYPE_FILETIME     64
#define DBTYPE_GUID         72
#define DBTYPE_BYTES       128
#define DBTYPE_STR         129
#define DBTYPE_WSTR        130
#define DBTYPE_NUMERIC     131
#define DBTYPE_UDT         132
#define DBTYPE_DBDATE      133
#define DBTYPE_DBTIME      134
#define DBTYPE_DBTIMESTAMP 135
#define DBTYPE_HCHAPTER    136
#define DBTYPE_DBFILETIME  137
#define DBTYPE_PROPVARIANT 138
#define DBTYPE_VARNUMERIC  139

#define DBTYPE_VECTOR      0x1000
#define DBTYPE_ARRAY       0x2000
#define DBTYPE_BYREF       0x4000
#define DBTYPE_RESERVED    0x8000


typedef struct {
	int cd_size;			// size class
	int cd_type;			// DBTYPE_* value
	int cd_offset;			// offset into data blurb
	char *cd_name;			// column name (hard reference to string in columns data)
} ColumnDescriptor;


extern PyTypeObject PyDBRowDescriptor_Type;

typedef struct {
	PyObject_VAR_HEAD
	PyObject *rd_initarg;				// tuple of columns/types
	PyObject *rd_header;				// List with header.

	// ob_size will be the number of columns.
	int rd_num_objects;					// number of non-scalar entries

	int rd_unpacked_size;				// length of decoded RLE blurbs
	int rd_total_size;					// length of decoded RLE blurb PLUS space for objects

	// object gets enough space allocated for rd_num_columns ColumnDescriptors
	ColumnDescriptor rd_cd[1];

} PyDBRowDescriptorObject;

#define PyDBRowDescriptor_Check(op) PyObject_TypeCheck(op, (void *)&PyDBRowDescriptor_Type)
#define PyDBRowDescriptor_CheckExact(op) ((op)->ob_type == &PyDBRowDescriptor_Type)


typedef struct {
	PyObject_VAR_HEAD
	PyDBRowDescriptorObject *dbrow_header;
	// after initialization, ob_size will be used as object counter.
	char dbrow_data[1]; // decoded binary blurb + objects
} PyDBRowObject;

extern PyTypeObject PyDBRow_Type;

#define PyDBRow_Check(op) PyObject_TypeCheck(op, (void *)&PyDBRow_Type)
#define PyDBRow_CheckExact(op) ((op)->ob_type == &PyDBRow_Type)

// used by marshal.Load
extern PyObject *PyDBRow_New(PyDBRowDescriptorObject *header, char *in, int in_size);

extern int dbrow_append_internal(PyDBRowObject *self, PyObject *item);

extern int init_dbrow(PyObject *);

#ifdef __cplusplus
}
#endif
#endif // _DBROW_H
