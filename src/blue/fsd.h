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
	uint32_t offset;
	uint32_t size;
} keymap_entry;


typedef struct {
	int32_t count;
	keymap_entry entry[1];
} keymap;


typedef struct {
    PyObject_HEAD
	PyObject *km_ref;   // safety ref to string object containing keymap blob
    keymap *km_map;  // pointer to keymap
	int km_entrysize;
	int km_signed;  // signed keys anyway?
	int km_add;  // add this to every offset
} PyKeyMapObject;

typedef struct {
	PyObject_HEAD
	PyKeyMapObject *kmi_keymap;
	int kmi_index;
	int kmi_mode;   // 0 = iterkeys, 1 = itervalues, 2 = iteritems, 3 = itervalues(nosize), 4 = iteritems(nosize)
} PyKeyMapIteratorObject;


extern PyTypeObject PyKeyMap_Type;
extern PyTypeObject PyKeyMapIterator_Type;

extern PyObject *init_fsd(void);

#ifdef __cplusplus
}
#endif
#endif // _FSD_H

