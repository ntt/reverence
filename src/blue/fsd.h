#ifndef _FSD_H
#define _FSD_H
#ifdef __cplusplus
extern "C" {
#endif

#include "Python.h"
#include "marshal.h"  // for uint32_t
#include "fsd.h"

typedef struct {
	uint32_t key;
	uint32_t value1;
	uint32_t value2;
} keymap_entry;


typedef struct {
    PyObject_HEAD
	PyObject *km_ref;   // safety ref to string object containing keymap blob
    keymap_entry *km_data;  // pointer to keymap
	int km_length; // number of entries in keymap
} PyKeyMapObject;

typedef struct {
	PyObject_HEAD
	PyKeyMapObject *kmi_keymap;
	int kmi_index;
	int kmi_mode;   // 0 = keys, 1 = values, 2 = (key,value)
} PyKeyMapIteratorObject;


extern PyTypeObject PyKeyMap_Type;
extern PyTypeObject PyKeyMapIterator_Type;

extern PyObject *init_fsd(void);

#ifdef __cplusplus
}
#endif
#endif // _FSD_H

