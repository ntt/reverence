"""
FileStaticData decoder stuff

Copyright (c) 2003-2013 Jamie "Entity" van den Berge <jamie@hlekkir.com

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

try:
	import yaml
except ImportError:
	raise RuntimeError("Reverence requires the PyYAML library")

import pyFSD

from reverence import _pyFSD
_uint32 = _pyFSD._uint32_from
_int32 = _pyFSD._int32_from
_string = _pyFSD._string_from

_unpack_from = struct.unpack_from
_float = struct.Struct("f").unpack_from
_double = struct.Struct("d").unpack_from

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
	size = _uint32(f.read(4))
	return cPickle.loads(f.read(size)), size



#-----------------------------------------------------------------------------
# Schema Optimizer
#-----------------------------------------------------------------------------

_typeSizes = {
 'typeID'  : struct.calcsize("I"),
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
	if t in ('float', 'int', 'typeID', 'vector2', 'vector3', 'vector4', 'enum', 'bool'):
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
		return {
			'keyTypes': _OptimizeSchema(schema['keyTypes']),
			'valueTypes': _OptimizeSchema(schema['valueTypes']),
			'buildIndex': schema.get('buildIndex', False),
		}

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

	def __len__(self):
		return len(self.footer)

	def iteritems(self):
		return ((item.key, (item.offset, getattr(item, 'size', 0))) for item in self.footer)

	def _iterspecial(self, mode):
		if mode == 4:
			return ((item.key, item.offset) for item in self.footer)
		if mode == 3:
			return (item.offset for item in self.footer)
		raise RuntimeError("iterspecial mode has to be 3 or 4")

	def itervalues(self):
		return ((item.offset, getattr(item, 'size', 0)) for item in self.footer)

	def iterkeys(self):
		return (item.key for item in self.footer)

	def keys(self):
		return [item.key for item in self.footer]


class FSD_Dict(object):

	def __init__(self, data, offset, schema):
		self.data = data
		self.offset = offset + 4
		endOfFooter = offset + _uint32(data, offset)
		footerOffset = endOfFooter - _uint32(data, endOfFooter)
		if schema['keyTypes']['type'] == 'int':
			self.footer = pyFSD.FsdUnsignedIntegerKeyMap()
			self.footer.Initialize(data, footerOffset)
		else:
			self.footer = _DictFooter(data, footerOffset, schema['keyFooter'])
		self.valueSchema = schema['valueTypes']
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
		return self.valueSchema["loader"](self.data, self.offset + v[0], self.valueSchema)

	def get(self, key, default=None):
		v = self._Search(key)
		if v is None:
			return default
		return self.valueSchema["loader"](self.data, self.offset + v[0], self.valueSchema)

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

	Get = __getitem__
	GetIfExists = get
	__iter__ = iterkeys


class FSD_Index(object):

	def __init__(self, f, cacheSize, schema, offset=0, offsetToFooter=0):
		self.file = f
		self.cacheSize = cacheSize
		self.offset = offset + 4
		self.index = {}
		self.header = schema['header']

		# read the footer blob and put it in an appropriate container
		f.seek(offset)
		f.seek((offsetToFooter - 4) if offsetToFooter else (offset + _uint32(f.read(4))))
		footerSize = _uint32(f.read(4))
		f.seek(-(4+footerSize), os.SEEK_CUR)
		if schema['keyTypes']['type'] == 'int':
			self.footer = pyFSD.FsdUnsignedIntegerKeyMap()
			self.footer.Initialize(f.read(footerSize))
		else:
			self.footer = _DictFooter(f.read(footerSize), 0, schema['keyFooter'])

		self.cache = collections.OrderedDict()

		s = self.valueSchema = schema['valueSchema']
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

	Get = __getitem__
	GetIfExists = get
	__iter__ = iterkeys


_vectorunpackers = []
for i in xrange(32):
	_vectorunpackers.append(struct.Struct("I"*i).unpack_from)


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
							[attr for attr in schema['attributesWithVariableOffsets'] if lookup(attr, attr_bits) & attr_bits]
				else:
					# no attribute bits set, so this set is going to be empty anyway.
					_oa = ()

			else:
				# looks like there's just the required attributes.
				_oa = schema['attributesWithVariableOffsets']

			if _oa: 
				_num = len(_oa)
				_off = schema['endOfFixedSizeData'] + 4
				if _num == 1:
					_offsets = {
						_oa[0]: _off + 4 + _uint32(data, offset + _off)
					}
				elif _num == 2:
					_offsets = {
						_oa[0]: _off + 8 + _uint32(data, offset + _off),
						_oa[1]: _off + 8 + _uint32(data, offset + 4 + _off),
					}
				else:
					_offsets = dict(zip(_oa, map((_off + 4*_num).__add__, _vectorunpackers[_num](data, offset + _off))))

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
		header = self.attributes
		_getoffset = self._get_offset
		stuff = []
		for attr, schema in header.iteritems():
			offset = _getoffset(attr)
			if offset is None:
				if 'default' in schema:
					v = schema['default']
				else:
					v = "NULL"
			else:
				v = schema['loader'](self.__data__, self.__offset__ + offset, schema)
			stuff.append(v)

		return "FSD_Object(" + ','.join(map(u"%s:%s".__mod__, zip(header, stuff))) + ")"


_loaders = {
	# scalars
	'int'     : _int32,
	'typeID'  : _int32,
	'bool'    : lambda data, offset, schema: data[offset] == "\xff",
	'float'   : lambda data, offset, schema: _float(data, offset)[0],
	'double'  : lambda data, offset, schema: _double(data, offset)[0],
	'string'  : _string,
	'resPath' : _string,
	'unicode' : lambda data, offset, schema: _string(data, offset).decode('utf-8'),
	'enum'    : Load_Enum,
	
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
	return FSD_Index(f, cacheItems, optimizedSchema, offset=offset)





