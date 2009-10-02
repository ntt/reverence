/*
// marshal.h
//
// Copyright (c) 2003-2009 Jamie "Entity" van den Berge <jamie@hlekkir.com>
//
// This code is free software; you can redistribute it and/or modify
// it under the terms of the BSD license (see the file LICENSE.txt
// included with the distribution).
*/

#ifndef _MARSHAL_H
#define _MARSHAL_H
#ifdef __cplusplus
extern "C" {
#endif


#ifdef _WIN32
// thanks MSVC++ for not including a stdint.h. Who needs standards anyway.
typedef __int8 int8_t;
typedef __int16 int16_t;
typedef __int32 int32_t;
typedef __int64 int64_t;

typedef unsigned __int8  uint8_t;
typedef unsigned __int16 uint16_t;
typedef unsigned __int32 uint32_t;
typedef unsigned __int64 uint64_t;
#else
#include <stdint.h>
#endif // _WIN32

#include "Python.h"

#define PROTOCOL_ID    0x7e

#define TYPE_NONE      0x01  //  1: None
#define TYPE_GLOBAL    0x02  //  2: usually a type, function or class object, but just the name,
                             //     so it has to exist for this to decode properly.

#define TYPE_INT64     0x03  //  3: 8 byte signed int
#define TYPE_INT32     0x04  //  4: 4 byte signed int
#define TYPE_INT16     0x05  //  5: 2 byte signed int
#define TYPE_INT8      0x06  //  6: 1 byte signed int
#define TYPE_MINUSONE  0x07  //  7: the value of -1
#define TYPE_ZERO      0x08  //  8: the value of 0
#define TYPE_ONE       0x09  //  9: the value of 1
#define TYPE_FLOAT     0x0a  // 10: 8 byte float
#define TYPE_FLOAT0    0x0b  // 11: the value of 0.0
//#define TYPE_COMPLEX   0x0c  // 12: (not used, complex number)
#define TYPE_STRINGL   0x0d  // 13: string, longer than 255 characters using normal count*
#define TYPE_STRING0   0x0e  // 14: string, empty
#define TYPE_STRING1   0x0f  // 15: string, 1 character
#define TYPE_STRING    0x10  // 16: string, next byte is 0x00 - 0xff being the count.
#define TYPE_STRINGR   0x11  // 17: string, reference to line in strings.txt (stringTable)
#define TYPE_UNICODE   0x12  // 18: unicode string, next byte is count*
#define TYPE_BUFFER    0x13  // 19: buffer object... hmmm
#define TYPE_TUPLE     0x14  // 20: tuple, next byte is count*
#define TYPE_LIST      0x15  // 21: list, next byte is count*
#define TYPE_DICT      0x16  // 22: dict, next byte is count*
#define TYPE_INSTANCE  0x17  // 23: class instance, name of the class follows (as string, probably)
#define TYPE_BLUE      0x18  // 24: blue object.
#define TYPE_CALLBACK  0x19  // 25: callback
//#define TYPE_PICKLE    0x1a  // 26: (not used, old pickle method)
#define TYPE_REF       0x1b  // 27: shared object reference
#define TYPE_CHECKSUM  0x1c  // 28: checksum of rest of stream
//#define TYPE_COMPRESS  0x1d  // 29: (not used)
//#define TYPE_UNUSED    0x1e  // 30: (not used)
#define TYPE_TRUE      0x1f  // 31: True
#define TYPE_FALSE     0x20  // 32: False
#define TYPE_PICKLER   0x21  // 33: standard pickle of undetermined size
#define TYPE_REDUCE    0x22  // 34: reduce protocol
#define TYPE_NEWOBJ    0x23  // 35: new style class object
#define TYPE_TUPLE0    0x24  // 36: tuple, empty
#define TYPE_TUPLE1    0x25  // 37: tuple, single element
#define TYPE_LIST0     0x26  // 38: list, empty
#define TYPE_LIST1     0x27  // 39: list, single element
#define TYPE_UNICODE0  0x28  // 40: unicode string, empty
#define TYPE_UNICODE1  0x29  // 41: unicode string, 1 character

#define TYPE_DBROW     0x2a  // 42: database row (quite hard, custom data format)
#define TYPE_STREAM    0x2b  // 43: embedded marshal stream
#define TYPE_TUPLE2    0x2c  // 44: tuple, 2 elements
#define TYPE_MARK      0x2d  // 45: marker (for the NEWOBJ/REDUCE iterators that follow them)
#define TYPE_UTF8      0x2e  // 46: UTF8 unicode string, buffer size count follows*

#define TYPE_LONG      0x2f  // 47: big int, byte count follows.

#define SHARED_FLAG    0x40

extern PyObject *marshal_Load(PyObject *self, PyObject *args, PyObject *kwds);
extern PyObject *marshal_Save(PyObject *self, PyObject *args, PyObject *kwds);
extern PyObject *marshal_set_find_global_func(PyObject *self, PyObject *callable);
extern PyObject *marshal_set_debug_func(PyObject *self, PyObject *callable);

extern PyObject *string_table;

extern PyObject *init_marshal(void);

#ifdef __cplusplus
}
#endif
#endif // _MARSHAL_H

