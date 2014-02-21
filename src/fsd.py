"""
FileStaticData decoder stuff

Copyright (c) 2003-2014 Jamie "Entity" van den Berge <jamie@hlekkir.com

This code is free software; you can redistribute it and/or modify
it under the terms of the BSD license (see the file LICENSE.txt
included with the distribution).

Part of this code is inspired by or based on EVE Online.
Used with permission from CCP.
"""
#
# So apparently CCP added yet another static data format, using YAML for the
# schema and binary blobs for data.
#
# Also, this stuff should totally be implemented in C.
#

import struct
import collections
import os
import cPickle
import itertools

try:
	import yaml
except ImportError:
	raise RuntimeError("Reverence requires the PyYAML library")

import pyFSD

from reverence import _pyFSD
_uint32 = _pyFSD._uint32_from  # used for decoding in the various containers
_make_offsets_table = _pyFSD._make_offsets_table
_unpack_from = struct.unpack_from

FLOAT_PRECISION_DEFAULT = 'single'


#-----------------------------------------------------------------------------
# Schema Loaders
#-----------------------------------------------------------------------------

class _SchemaLoader(yaml.SafeLoader):
	pass

_SchemaLoader.add_constructor(u'tag:yaml.org,2002:map',
	lambda loader, node: collections.OrderedDict(map(loader.construct_object, kv) for kv in node.value))

def LoadSchema(f):
	return yaml.load(f, Loader=_SchemaLoader)

def LoadEmbeddedSchema(f):
	pos = f.tell()
	size = _uint32(f.read(4))
	try:
		# there's a possibility this blind unpickle goes spectacularly wrong.
		return cPickle.load(f), size
	except cPickle.UnpicklingError:
		# it is not a pickle, restore position in file.
		f.seek(pos)
		raise RuntimeError("LoadEmbeddedSchema called on file without embedded schema")
	finally:
		# update filehandle state after cPickle.load() (see virtualfile.c)
		f.tell()


#-----------------------------------------------------------------------------
# Schema Optimizer
#-----------------------------------------------------------------------------

_typeSizes = {
 'int'     : struct.calcsize("I"),
 'typeID'  : struct.calcsize("I"),
 'localizationID' : struct.calcsize("I"),
 'float'   : struct.calcsize("f"),
 'single'  : struct.calcsize("f"),
 'vector2' : struct.calcsize("ff"),
 'vector3' : struct.calcsize("fff"),
 'vector4' : struct.calcsize("ffff"),
 'double'  : struct.calcsize("d"),
 'vector2d': struct.calcsize("dd"),
 'vector3d': struct.calcsize("ddd"),
 'vector4d': struct.calcsize("dddd"),
 'bool'    : struct.calcsize("B"),
}


def IsFixedSize(schema):
	t = schema['type']
	if t in _typeSizes:
		return True
	if t == 'object':
		attributes = schema['attributes']
		for attr in attributes:
			sa = attributes[attr]
			if sa.get('usage', "Client") == "Client":
				if sa.get('isOptional', False) or not IsFixedSize(sa):
					return False
		return True
	return False


class _SchemaOptimizer:
	@classmethod
	def optimize(cls, schema):
		schemaType = schema['type']
		optimizefunc = getattr(cls, "_"+schemaType, None)
		if optimizefunc:
			newSchema = optimizefunc(schema)
			newSchema['type'] = schemaType
		else:
			size = _typeSizes.get(schemaType)
			if size:
				newSchema = {'type': schemaType, 'size': size}
			else:
				newSchema = {'type': schemaType}

		if 'isOptional' not in newSchema:
			newSchema['isOptional'] = schema.get('isOptional', False)

		if 'default' in schema:
			newSchema['default'] = schema['default']

		return newSchema

	@staticmethod
	def _generic(schema):

		return {}

	@staticmethod
	def _dict(schema):
		newSchema = {
			'keyTypes': _OptimizeSchema(schema['keyTypes']),
			'valueTypes': _OptimizeSchema(schema['valueTypes']),
			'buildIndex': schema.get('buildIndex', False),
		}

		if 'multiIndex' in schema:
#			newSchema['multiIndex'] = schema['multiIndex']
#			newSchema['subIndexOffsetLookup'] = _OptimizeSchema(_subIndexOffsetLookupSchema)
#			SetNestedIndexIdInformationToRootSchema(newSchema)
			raise RuntimeError("fsd.py is not equipped to handle unoptimized multi-index schemas.")

		return newSchema

	@staticmethod
	def _list(schema):
		newSchema = {'itemTypes': _OptimizeSchema(schema['itemTypes'])}
		if 'size' in newSchema['itemTypes']:
			newSchema['fixedItemSize'] = newSchema['itemTypes']['size']
		if 'length' in schema:
			newSchema['length'] = schema['length']
		return newSchema

	@staticmethod
	def _object(schema):
		newSchema = {'attributes': collections.OrderedDict()}
		_constantAttributeOffsets = newSchema['constantAttributeOffsets'] = {}
		_attributesWithVariableOffsets = newSchema['attributesWithVariableOffsets'] = []
		_optionalValueLookups = newSchema['optionalValueLookups'] = {}

		offset = 0
		attr_bit = 1
		fixedsize = True

		attributes = schema["attributes"]
		for attr in attributes:
			sa = attributes[attr]
			if not sa.get('usage', "Client") == "Client":
				continue
			oschema = _OptimizeSchema(sa)
			newSchema['attributes'][attr] = oschema
			if sa.get('isOptional', False):
				fixedsize = False
				_optionalValueLookups[attr] = attr_bit
				_attributesWithVariableOffsets.append(attr)
				attr_bit <<= 1
			elif not IsFixedSize(sa):
				fixedsize = False
				_attributesWithVariableOffsets.append(attr)
			else:
				_constantAttributeOffsets[attr] = offset
				offset += oschema['size']

		if fixedsize:
			newSchema['endOfFixedSizeData'] = newSchema['size'] = offset
		else:
			newSchema['endOfFixedSizeData'] = offset

		return newSchema

	@staticmethod
	def _enum(schema):
		return {
			'readEnumValue': schema.get('readEnumValue', False),
			'values': schema['values'],
		}

	@staticmethod
	def _int(schema):
		newSchema = {'size': struct.calcsize("i")}
		if 'min' in schema:
			newSchema['min'] = schema['min']
		if 'exclusiveMin' in schema:
			newSchema['exclusiveMin'] = schema['exclusiveMin']
		return newSchema

	@staticmethod
	def _vector(schema, size=None):
		newSchema = {}
		if 'aliases' in schema:
			newSchema['aliases'] = schema['aliases']
		if 'precision' in schema:
			prec = newSchema['precision'] = schema['precision']
		else:
			prec = FLOAT_PRECISION_DEFAULT
		newSchema['size'] = _typeSizes[prec] * size
		return newSchema

	@staticmethod
	def _vector2(schema):
		return _SchemaOptimizer._vector(schema, 2)

	@staticmethod
	def _vector3(schema):
		return _SchemaOptimizer._vector(schema, 3)

	@staticmethod
	def _vector4(schema):
		return _SchemaOptimizer._vector(schema, 4)

	@staticmethod
	def _union(schema):
		newSchema = {'optionTypes': []}
		for unionType in schema['optionTypes']:
			newSchema['optionTypes'].append(_OptimizeSchema(unionType))
		return newSchema

	@staticmethod
	def _float(schema):
		newSchema = {}
		if 'precision' in schema:
			prec = newSchema['precision'] = schema['precision']
		else:
			prec = FLOAT_PRECISION_DEFAULT
		newSchema['size'] = _typeSizes[prec]
		return newSchema

_OptimizeSchema = _SchemaOptimizer.optimize


#-----------------------------------------------------------------------------
# Deserialization stuff
#-----------------------------------------------------------------------------

_vectorUnpackers = {}
_vectorUnpackers["vector4"] = _vector4 = struct.Struct("ffff").unpack_from
_vectorUnpackers["vector3"] = _vector3 = struct.Struct("fff").unpack_from
_vectorUnpackers["vector2"] = _vector2 = struct.Struct("ff").unpack_from
_vectorUnpackers["vector4d"] = _vector4d = struct.Struct("dddd").unpack_from
_vectorUnpackers["vector3d"] = _vector3d = struct.Struct("ddd").unpack_from
_vectorUnpackers["vector2d"] = _vector2d = struct.Struct("dd").unpack_from

class _FixedSizeList(object):

	def __init__(self, data, offset, itemSchema, knownLength = None):
		self.data = data
		self.itemSchema = itemSchema

		if knownLength is None:
			self.count = _uint32(data, offset)
			self.offset = offset + 4
		else:
			self.count = knownLength
			self.offset = offset
		self.itemSize = itemSchema['size']

	def __iter__(self):
		d = self.data; s = self.itemSchema; loader = self.itemSchema['loader']
		return (loader(d, offset, s) for offset in xrange(self.offset, self.offset + self.count*self.itemSize, self.itemSize))

	def __len__(self):
		return self.count

	def __getitem__(self, idx):
		if type(idx) not in (int, long):
			raise TypeError('Invalid key type')
		if idx < 0 or idx >= self.count:
			raise IndexError('Invalid item index %i for list of length %i' % (idx, self.count))
		return self.itemSchema['loader'](self.data, self.offset + self.itemSize * idx, self.itemSchema)

	def __repr__(self):
		return "<FixedSizeList(values:%s,size:%d)>" % (self.itemSchema['type'], self.count)


class _VariableSizedList(object):

	def __init__(self, data, offset, itemSchema, knownLength = None):
		self.data = data
		self.itemSchema = itemSchema

		if knownLength is None:
			self.count = _uint32(data, offset)
			self.start = offset
			self.offset = offset + 4
		else:
			self.count = knownLength
			self.start = self.offset = offset

	def __iter__(self):
		d = self.data; s = self.itemSchema; loader = self.itemSchema['loader']
		start = self.start; offset = self.offset
		return (loader(d, start + _uint32(d, offset + idx*4), s) for idx in xrange(self.count))

	def __len__(self):
		return self.count

	def __getitem__(self, idx):
		if type(idx) not in (int, long):
			raise TypeError('Invalid key type')
		if idx < 0 or idx >= self.count:
			raise IndexError('Invalid item index %i for list of length %i' % (idx, self.count))
		return self.itemSchema['loader'](self.data, self.start + _uint32(self.data, self.offset + idx*4), self.itemSchema)

	def __repr__(self):
		return "<VariableSizedList(values:%s,size:%d)>" % (self.itemSchema['type'], self.count)

def FSD_List(data, offset, schema):
	return (_FixedSizeList if 'fixedItemSize' in schema else _VariableSizedList)(data, offset, schema['itemTypes'], schema.get('length'))


class FSD_NamedVector(object):
	def __init__(self, data, offset, schema):
		self.data = data
		self.offset = offset
		self.schema = schema
		self.data = schema['unpacker'](data, offset)
		self._getKeyIndex = self.schema['aliases'].get

	def __getitem__(self, key):
		return self.data[self._getKeyIndex(key, key)]

	def __getattr__(self, name):
		try:
			return self.data[self._getKeyIndex(name)]
		except (KeyError, IndexError) as e:
			raise AttributeError(str(e))

	def __repr__(self):
		return "FSD_NamedVector(" + ",".join(map("%s:%s".__mod__, zip(self.schema['aliases'], self.data))) + ")"


def Load_Enum(data, offset, schema):
	dataValue = schema['unpacker'](data, offset)[0]
	if schema['readEnumValue']:
		return dataValue
	for k, v in schema['values'].iteritems():
		if v == dataValue:
			return k


class _DictFooter(object):
	def __init__(self, data, offset, schema):
		self.footer = FSD_List(data, offset, schema)

	def Get(self, key):
		minIndex = 0
		maxIndex = len(self.footer) - 1
		while 1:
			if maxIndex < minIndex:
				return None
			meanIndex = (minIndex + maxIndex) / 2
			item = self.footer[meanIndex]
			if item.key < key:
				minIndex = meanIndex + 1
			elif item.key > key:
				maxIndex = meanIndex - 1
			else:
				return (item.offset, getattr(item, 'size', 0))

	def _iterspecial(self, mode):
		if mode == 4: return ((item.key, item.offset) for item in self.footer)
		if mode == 3: return (item.offset for item in self.footer)
		raise RuntimeError("iterspecial mode has to be 3 or 4")

	def keys(self)      : return [item.key for item in self.footer]
	def iterkeys(self)  : return (item.key for item in self.footer)
	def itervalues(self): return ((item.offset, getattr(item, 'size', 0)) for item in self.footer)
	def iteritems(self) : return ((item.key, (item.offset, getattr(item, 'size', 0))) for item in self.footer)
	def __len__(self)   : return len(self.footer)


class FSD_Dict(object):

	def __init__(self, data, offset, schema):
		self.data = data
		self.offset = offset + 4
		endOfFooter = offset + _uint32(data, offset)
		footerOffset = endOfFooter - _uint32(data, endOfFooter)
		self.schema = schema
		if schema['keyTypes']['type'] in 'int':
			hassize = ('size' in schema['keyFooter']['itemTypes']['attributes']) if ('keyFooter' in schema) else True
			self.footer = pyFSD.FsdUnsignedIntegerKeyMap()
			self.footer.Initialize(data, footerOffset, hassize, True)
		else:
			self.footer = _DictFooter(data, footerOffset, schema['keyFooter'])
		self.valueSchema = schema['valueTypes']
		self.loader = self.valueSchema['loader']
		self.header = schema['header']
		self.index = {}

	def __GetItem__(self, offset):
		return self.valueSchema["loader"](self.data, self.offset + offset, self.valueSchema)

	def __len__(self):
		return len(self.footer)

	def __contains__(self, item):
		try:
			return self._Search(item) is not None
		except TypeError:
			return False

	def _Search(self, key):
		v = self.index.get(key, self)  # abusing self
		if v is self:
			v = self.index[key] = self.footer.Get(key)
		return v

	def __getitem__(self, key):
		v = self._Search(key)
		if v is None:
			raise KeyError('key (%s) not found' % (str(key)))
		return self.loader(self.data, self.offset + v[0], self.valueSchema)

	def get(self, key, default=None):
		v = self._Search(key)
		if v is None:
			return default
		return self.loader(self.data, self.offset + v[0], self.valueSchema)

	def keys(self):
		return list(self.footer.iterkeys())

	def iteritems(self):
		d = self.data; a = self.offset; s = self.valueSchema; loader = s["loader"]
		return ((key, loader(d, a+offset, s)) for key, offset in self.footer._iterspecial(4))

	def itervalues(self):
		d = self.data; a = self.offset; s = self.valueSchema; loader = s["loader"]
		return (loader(d, a+offset, s) for offset in self.footer._iterspecial(3))

	def iterkeys(self):
		return self.footer.iterkeys()

	def __repr__(self):
		return "<FSD_Dict(keys:%s,values:%s,size:%d)>" % (self.schema['keyTypes']['type'], self.valueSchema['type'], len(self.footer))

	__iter__ = iterkeys

	Get = __getitem__
	GetIfExists = get


class FSD_Index(object):

	def __init__(self, f, cacheSize, schema, offset=0, offsetToFooter=0):
		self.file = f
		self.cacheSize = cacheSize
		self.offset = offset = offset+4 if offset else 0
		self.index = {}
		self.header = schema['header']

		# read the footer blob and put it in an appropriate container
		f.seek(offset)
		self.fileSize = _uint32(f.read(4))

		f.seek(offset + self.fileSize)
		footerSize = self.footerSize = _uint32(f.read(4))

		f.seek(-(4+footerSize), os.SEEK_CUR)
		if schema['keyTypes']['type'] == 'int':
			self.footer = pyFSD.FsdUnsignedIntegerKeyMap()
			self.footer.Initialize(f.read(footerSize))
		else:
			self.footer = _DictFooter(f.read(footerSize), 0, schema['keyFooter'])

		self.cache = collections.OrderedDict()

		s = self.valueSchema = schema['valueTypes']
		self._load = s['loader']
		if (s.get('buildIndex', False)) and (s['type'] == 'dict'):
			self._getitem = self.__GetIndex__ 
		else:
			self._getitem = self.__GetItem__

	def keys(self):
		return list(self.footer.iterkeys())

	def iterkeys(self):
		return self.footer.iterkeys()

	def iteritems(self):
		_get = self._getitem
		return ((key, _get(offset, size)) for key, (offset, size) in self.footer.iteritems())

	def itervalues(self):
		_get = self._getitem
		return (_get(offset, size) for (offset, size) in self.footer.itervalues())

	def _Search(self, key):
		v = self.index.get(key, self)  # abusing self
		if v is self:
			v = self.index[key] = self.footer.Get(key)
		return v

	def __getitem__(self, key):
		v = self.cache.pop(key, self)  # abusing self
		if v is self:
			# item wasnt cached. grab it and do so.
			try:
				itemOffset, itemSize = self._Search(key)
			except TypeError:
				# can be thrown by _Search returning None or being passed wrong type
				raise KeyError('Key (%s) not found' % str(key))

			v = self._getitem(itemOffset, itemSize)

			if len(self.cache) > self.cacheSize:
				self.cache.popitem(last=False)

		self.cache[key] = v
		return v

	def __GetItem__(self, offset, size):
		self.file.seek(self.offset+offset)
		return self._load(self.file.read(size), 0, self.valueSchema)

	def __GetIndex__(self, offset, size):
		return FSD_Index(self.file, self.cacheSize, self.valueSchema, offset=self.offset+offset)

	def __contains__(self, item):
		try:
			return self._Search(item) is not None
		except TypeError:
			return False

	def __len__(self):
		return len(self.footer)

	def get(self, key, default=None):
		try:
			return self.__getitem__(key)
		except (KeyError, IndexError):
			return default

	def __repr__(self):
		return "<FSD_Index(type:%s,size:%s)" % (self.valueSchema['type'], len(self.footer))

	__iter__ = iterkeys

	Get = __getitem__
	GetIfExists = get


class _subindex(object):
	# one index in a multiindex table

	def __init__(self, f, indexedOffsetTable, valueSchema):
		self.file = f
		self.offsetTable = indexedOffsetTable
		self.valueSchema = valueSchema
		self.fsdindex = self.valueSchema.get("buildIndex", False)
		self.loader = self.valueSchema["loader"]

		# aliases for speed
		self._getkey = self.offsetTable.Get
		self._seek = self.file.seek
		self._read = self.file.read

	def __getitem__(self, key):
		offsetAndSize = self._getkey(key)
		if offsetAndSize is None:
			raise KeyError('Key (%s) not found in subindex' % str(key))
		if self.fsdindex:
			return FSD_Index(self.file, 100, self.valueSchema, offset=offsetAndSize[0], offsetToFooter=offsetAndSize[0]+offsetAndSize[1])
		self._seek(offsetAndSize[0])
		return self.loader(self._read(offsetAndSize[1]), 0, self.valueSchema)

	def get(self, key, default=None):
		offsetAndSize = self._getkey(key)
		if offsetAndSize is None:
			return default
		if self.fsdindex:
			return FSD_Index(self.file, 100, self.valueSchema, offset=offsetAndSize[0], offsetToFooter=offsetAndSize[0]+offsetAndSize[1])
		self._seek(offsetAndSize[0])
		return self.loader(self._read(offsetAndSize[1]), 0, self.valueSchema)

	def iterkeys(self)    : return self.offsetTable.iterkeys()
	def itervalues(self)  : return (self[key] for key in self.offsetTable.iterkeys())
	def iteritems(self)   : return ((key, self[key]) for key in self.offsetTable.iterkeys())
	def __len__(self)     : return len(self.offsetTable)
	def __contains__(self): return key in self.offsetTable

	__iter__ = iterkeys

	Get = __getitem__
	GetIfExists = get


_chain = itertools.chain.from_iterable

class _indexgroup(object):
	# a group of subindex instances treated as one index.
	__slots__ = ("indices",)

	def __init__(self, indices):
		self.indices = indices

	def __getitem__(self, key):
		for index in self.indices:
			if key in index:
				return index[key]
		raise KeyError('Key (%s) not found in indexgroup' % str(key))

	def get(self, key, default=None):
		for index in self.indices:
			if key in index:
				return index[key]
		return default

	def iterkeys(self)  : return _chain(self.indices)
	def itervalues(self): return (v for index in self.indices for v in index.itervalues())
	def iteritems(self) : return (kv for index in self.indices for kv in index.iteritems())
	def __len__(self)   : return sum(len(index) for index in self.indices)
	
	def __contains__(self, item):
		for index in self.indices:
			if key in index:
				return True
		return False

	__iter__ = iterkeys

	Get = __getitem__
	GetIfExists = get


class FSD_MultiIndex(FSD_Index):
	# clever multiple indices on the same collection of data

	def __init__(self, f, cacheSize, schema, offset=0, offsetToFooter=0):
		FSD_Index.__init__(self, f, cacheSize, schema, offset, offsetToFooter)

		f.seek(offset + self.fileSize - self.footerSize)
		attributeLookupTableSize = _uint32(f.read(4))

		f.seek(-(4+attributeLookupTableSize), os.SEEK_CUR)
		attributeLookupTable = f.read(attributeLookupTableSize)

		# create the subindices
		subindices = {}
		for index, offsetAndSize in load(attributeLookupTable, 0, schema['subIndexOffsetLookup']).iteritems():
			f.seek(offset + 4 + offsetAndSize.offset)
			offsetTable = pyFSD.FsdUnsignedIntegerKeyMap()
			offsetTable.Initialize(f.read(offsetAndSize.size), 0, True, False, offset+8)
			subindices[index] = _subindex(f, offsetTable, schema['indexableSchemas'][index]['valueTypes'])

		# assign either indexgroup or subindex to relevant attributes.
		for indexName, indices in schema['indexNameToIds'].iteritems():
			index = _indexgroup(map(subindices.__getitem__, indices)) if len(indices)>1 else subindices[indices[0]]
			setattr(self, indexName, index)

		self._indices = schema['indexNameToIds'].keys()

	def __repr__(self):
		indexsummary = map("%s:%d".__mod__, ((name, len(getattr(self, name))) for name in self._indices))
		return "<FSD_MultiIndex(type:%s,size:%d,indices:{%s})>" % (self.valueSchema['type'], len(self.footer), ','.join(indexsummary))


class FSD_Object(object):

	def __init__(self, data, offset, schema):
		self.__data__ = data
		self.__offset__ = offset
		self.attributes = schema['attributes']
		self._get_schema = schema['attributes'].get

		if 'size' in schema:
			# fixed size object. skip all the scary stuff.
			self._get_offset = schema['constantAttributeOffsets'].get
		else:
			# variable sized object. figure out what optional attributes we have.
			if schema['optionalValueLookups']:
				attr_bits = _uint32(data, offset + schema['endOfFixedSizeData'])
				if attr_bits:
					# some attribute bits are set. figure out what attributes are actually there ...
					_oa = schema.get(attr_bits)
					if not _oa:
						lookup = schema['optionalValueLookups'].get
						# filter out optional attributes that are not given
						_oa = schema[attr_bits] = \
							[attr for attr in schema['attributesWithVariableOffsets'] if lookup(attr, -1) & attr_bits]
				else:
					# no attribute bits set, so this set is going to be empty anyway.
					_oa = ()

			else:
				# looks like there's just the required attributes.
				_oa = schema['attributesWithVariableOffsets']

			if _oa:
				_offsets = _make_offsets_table(_oa, data, offset, schema['endOfFixedSizeData'] + 4)
				_offsets.update(schema['constantAttributeOffsets'])
				self._get_offset = _offsets.get
			else:
				self._get_offset = schema['constantAttributeOffsets'].get


	def __getitem__(self, key):
		schema = self._get_schema(key)
		if schema is None:
			raise KeyError("Attribute '%s' is not in the schema for this object." % key)

		off = self._get_offset(key)
		if off is None:
			if 'default' in schema:
				return schema['default']
			raise schema['KeyError']
		return schema['loader'](self.__data__, self.__offset__ + off, schema)

	def __getattr__(self, key):
		schema = self._get_schema(key)
		if schema is None:
			raise AttributeError("Attribute '%s' is not in the schema for this object." % key)

		off = self._get_offset(key)
		if off is None:
			if 'default' in schema:
				return schema['default']
			raise schema['AttributeError']
		return schema['loader'](self.__data__, self.__offset__ + off, schema)


	def __str__(self):
		# detailed representation
		header = self.attributes
		_getoffset = self._get_offset
		stuff = []
		_a = stuff.append
		for attr, schema in header.iteritems():
			offset = _getoffset(attr)
			if offset is None:
				v = schema.get("default", self)
				v = "NULL" if v is self else repr(v)
			else:
				v = repr(schema['loader'](self.__data__, self.__offset__ + offset, schema))
			_a(v)

		return "FSD_Object(" + ','.join(map(u"%s:%s".__mod__, zip(header, stuff))) + ")"

	def __repr__(self):
		# lightweight representation that doesn't decode any information
		return "<FSD_Object(" + ','.join(map(u"%s:%s".__mod__, ((k, v['type']) for k,v in self.attributes.iteritems()) )) + ")>"



_loaders = {
	# scalars
	'int'     : _pyFSD._int32_from,
	'typeID'  : _pyFSD._int32_from,
	'bool'    : _pyFSD._bool_from,
	'float'   : _pyFSD._float_from,
	'double'  : _pyFSD._double_from,
	'string'  : _pyFSD._string_from,
	'resPath' : _pyFSD._string_from,
	'unicode' : lambda data, offset, schema: _string(data, offset).decode('utf-8'),
	'enum'    : Load_Enum,

	'localizationID' : _pyFSD._int32_from,  # rubicon 1.1
	
	# compounds
	'vector4' : lambda data, offset, schema: _vector4(data, offset),
	'vector3' : lambda data, offset, schema: _vector3(data, offset),
	'vector2' : lambda data, offset, schema: _vector2(data, offset),
	'vector4d': lambda data, offset, schema: _vector4d(data, offset),
	'vector3d': lambda data, offset, schema: _vector3d(data, offset),
	'vector2d': lambda data, offset, schema: _vector2d(data, offset),
	'union'   : lambda data, offset, schema: load(data, offset+4, schema['optionTypes'][_uint32(data, offset)]),
	
	# containers
	'list'   : FSD_List,
	'dict'   : FSD_Dict,
	'object' : FSD_Object,
}


def load(data, offset, schema):
	return schema['loader'](data, offset, schema)


#-----------------------------------------------------------------------------
# Exposed stuff
#-----------------------------------------------------------------------------

def OptimizeSchema(schema):
	return _OptimizeSchema(schema['schemas'][schema['runtimeSchema']])


def PrepareSchema(schema):
	# Adds required decoding information to a schema
	# THIS -MUST- BE USED ON EVERY SCHEMA (AFTER OPTIMIZING, IF ANY)

	t = schema.get('type')
	schema['loader'] = _loaders[t]

	if t in _typeSizes:
		schema['size'] = _typeSizes[t]

	if t.startswith("vector"):
		if schema.get('precision') == 'double':
			t = schema['type']+"d"

		# figure out correct loader.
		if schema.get('aliases'):
			schema['loader'] = FSD_NamedVector
			schema['unpacker'] = _vectorUnpackers[t]
		else:
			schema['loader'] = _loaders[t]

	elif t == 'list':
		PrepareSchema(schema['itemTypes'])

	elif t == 'dict':
		PrepareSchema(schema['keyTypes'])
		PrepareSchema(schema['valueTypes'])

		if 'subIndexOffsetLookup' in schema:
			PrepareSchema(schema['subIndexOffsetLookup'])

		if "keyFooter" in schema:
			PrepareSchema(schema['keyFooter'])
		try:
			schema['header'] = schema['valueTypes']['attributes'].keys()
		except KeyError:
			# apparently this info is gone from some fsd dicts in Rubicon
			schema['header'] = ()

	elif t == 'object':
		if "endOfFixedSizeData" not in schema:
			schema["endOfFixedSizeData"] = 0

		for key, attrschema in schema["attributes"].iteritems():
			PrepareSchema(attrschema)
			attrschema['AttributeError'] = AttributeError("Object instance does not have attribute '%s'" % key)
			attrschema['KeyError'] = KeyError("Object instance does not have attribute '%s'" % key)

	elif t == 'binary':
		PrepareSchema(schema["schema"])

	elif t == 'int':
		if schema.get("min", -1) >= 0 or schema.get("exclusiveMin", -2) >= -1:
			schema['loader'] = _uint32

	elif t == 'union':
		for s in newSchema['optionTypes'].itervalues():
			PrepareSchema(s)

	elif t == 'float':
		if schema.get('precision') == 'double':
			schema['loader'] = _loaders['double']

	elif t == 'enum':
		_max = max(schema['values'].values())
		if _max <= 255:
			_type = struct.Struct("B")
		elif _max <= 65536:
			_type = struct.Struct("H")
		else:
			_type = struct.Struct("I")

		schema['unpacker'] = _type.unpack_from
		schema['size'] = _type.size
		if 'readEnumValue' not in schema:
			schema['readEnumValue'] = False


def LoadFromString(dataString, optimizedSchema=None):
	if optimizedSchema is None:
		size = uint32(dataString, 0)
		optimizedSchema = cPickle.loads(dataString[4:size+4])
		PrepareSchema(optimizedSchema)
		return load(dataString, size+4, optimizedSchema)
	else:
		return load(dataString, 0, optimizedSchema)


def LoadIndexFromFile(f, optimizedSchema, cacheItems=None, offset=0):
	if optimizedSchema.get("multiIndex", False):
		return FSD_MultiIndex(f, cacheItems, optimizedSchema, offset=offset)
	return FSD_Index(f, cacheItems, optimizedSchema, offset=offset)



