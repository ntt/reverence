"""
FileStaticData loader stuff

This code is free software; you can redistribute it and/or modify
it under the terms of the BSD license (see the file LICENSE.txt
included with the distribution).

Part of this code is inspired by or based on EVE Online.
Used with permission from CCP.
"""
#
# So apparently CCP added yet another static data format, using YAML for the
# schema and binary blobs for data. CCP's uses ctypes, which I don't really
# like, as it slows down access considerably.
#
# I've used precompiled structs instead.
#
# Also, this stuff should totally be implemented in C.
#

import ctypes
import struct
import collections

try:
	import yaml
except ImportError:
	raise RuntimeError("Reverence requires the PyYAML library")

_byte = struct.Struct("b").unpack_from
_ubyte = struct.Struct("B").unpack_from
_int32 = struct.Struct("i").unpack_from
_uint32 = struct.Struct("I").unpack_from
_float = struct.Struct("f").unpack_from


#-----------------------------------------------------------------------------
# Persistence
#-----------------------------------------------------------------------------

def orderedDict_constructor(loader, node):
	value = collections.OrderedDict()
	f = loader.construct_object
	for k, v in node.value:
		value[f(k)] = f(v)
	return value


class SafeSchemaLoader(yaml.SafeLoader):
	pass


SafeSchemaLoader.add_constructor(u'tag:yaml.org,2002:map', orderedDict_constructor)

def LoadSchema(fileStream):
	return yaml.load(fileStream, Loader=SafeSchemaLoader)


def GetEditorSchema(schema):
	editorSchema = schema['editorFileSchema']
	return schema['schemas'][editorSchema]


def GetUnOptimizedRuntimeSchema(schema):
	runtimeSchema = schema['runtimeSchema']
	return schema['schemas'][runtimeSchema]


def GetNewIDForSchemaObject(schemaNode):
	return None


#-----------------------------------------------------------------------------
# SchemaOptimizer
#-----------------------------------------------------------------------------



def IsUsedInTarget(schema, target):
	usage = schema.get('usage', None)
	return usage is None or usage == target or target == 'Editor'


def GetLargeEnoughUnsignedTypeForMaxValue(i):
	if i <= 255:
		return struct.Struct("B")
	if i <= 65536:
		return struct.Struct("H")
	return struct.Struct("I")


def GetAttributesForTarget(schema, target):
	orderedAttributeList = []
	attributes = schema.get('attributes')
	for attr in attributes:
		if IsUsedInTarget(attributes[attr], target):
			orderedAttributeList.append(attr)

	return orderedAttributeList


def GetOptionalAttributesForTarget(schema, target):
	attributes = GetAttributesForTarget(schema, target)
	for attr in attributes:
		if not schema['attributes'][attr].get('isOptional', False):
			attributes.remove(attr)

	return attributes


fixedSizeTypes = set(['float', 'int', 'typeID', 'vector2', 'vector3', 'vector4', 'enum', 'bool'])

def IsFixedSize(schema, target):
	schemaType = schema['type']
	if schemaType in fixedSizeTypes:
		return True
	if schemaType == 'object':
		attributes = schema['attributes']
		for attr in attributes:
			if not IsUsedInTarget(attrributes[attr]):
				continue
			if attributes[attr].get('isOptional', False) or not IsFixedSize(attributes[attr]):
				return False
		return True
	return False


def OptimizeDictSchema(schema, target):
	newSchema = {'type': 'dict'}
	if 'isOptional' in schema:
		newSchema['isOptional'] = schema['isOptional']
	newSchema['keyTypes'] = OptimizeSchema(schema['keyTypes'], target)
	newSchema['valueTypes'] = OptimizeSchema(schema['valueTypes'], target)
	keyHeaderSchema = {
		'type': 'list',
		'itemTypes': {
			'type': 'object',
			'attributes': {
				'key': schema['keyTypes'],
				'offset': {
					'type': 'int',
					'min': 0
				}
			}
		}
	}
	if schema.get('buildIndex', False):
		newSchema['buildIndex'] = True
		keyHeaderSchema['itemTypes']['attributes']['size'] = {'type': 'int', 'min': 0}
	newSchema['keyHeader'] = OptimizeSchema(keyHeaderSchema, target)
	return newSchema


def OptimizeListSchema(schema, target):
	newSchema = {'type': 'list'}
	newSchema['itemTypes'] = OptimizeSchema(schema['itemTypes'], target)
	if 'size' in newSchema['itemTypes']:
		newSchema['fixedItemSize'] = newSchema['itemTypes']['size']
	if 'length' in schema:
		newSchema['length'] = schema['length']
	if 'isOptional' in schema:
		newSchema['isOptional'] = schema['isOptional']
	return newSchema


def OptimizeObjectSchema(schema, target):
	newSchema = {'type': 'object'}
	if 'isOptional' in schema:
		newSchema['isOptional'] = schema['isOptional']

	allAttributesForTarget = GetAttributesForTarget(schema, target)
	optionalAttributes = []
	variableSizedAttributes = []
	for attr in allAttributesForTarget:
		if schema['attributes'][attr].get('isOptional', False):
			optionalAttributes.append(attr)

	optionalAttributes = set(optionalAttributes)
	numOptionalAttributes = len(optionalAttributes)
	optionalAttributeValue = 1
	newSchema['optionalValueLookups'] = {}
	if numOptionalAttributes > 0:
		for attr in optionalAttributes:
			newSchema['optionalValueLookups'][attr] = optionalAttributeValue
			optionalAttributeValue <<= 1
		newSchema['optionalValueLookupType'] = GetLargeEnoughUnsignedTypeForMaxValue(optionalAttributeValue >> 1)  # this isnt used?

	requiredFixedSizeAttributes = [ attr for attr in allAttributesForTarget if attr not in optionalAttributes and attr not in variableSizedAttributes ]
	newSchema['attributes'] = collections.OrderedDict()
	currentOffset = 0
	newSchema['attributeOffsets'] = {}
	newSchema['size'] = 0
	resolvedAttributes = set()
	for attr in allAttributesForTarget:
		attrOptimizedSchema = OptimizeSchema(schema['attributes'][attr], target)
		newSchema['attributes'][attr] = attrOptimizedSchema
		if 'size' in attrOptimizedSchema:
			if 'size' in newSchema:
				newSchema['size'] += newSchema['attributes'][attr]['size']
			if attr not in optionalAttributes:
				newSchema['attributeOffsets'][attr] = currentOffset
				currentOffset += newSchema['attributes'][attr]['size']
				resolvedAttributes.add(attr)
			elif 'size' in newSchema:
				del newSchema['size']
		elif 'size' in newSchema:
			del newSchema['size']

	newSchema['endOfFixedSizeData'] = currentOffset
	attributesWithOffsets = [ attr for attr in allAttributesForTarget if attr not in resolvedAttributes ]
	newSchema['attributesWithOffsets'] = attributesWithOffsets
	return newSchema


def OptimizeEnumSchema(schema, target):
	newSchema = {'type': 'enum'}
	maxEnumValue = max(schema['values'].values())
	_type = newSchema['enumType'] = GetLargeEnoughUnsignedTypeForMaxValue(maxEnumValue)
	newSchema['size'] = _type.size
	newSchema['values'] = schema['values']
	if 'isOptional' in schema:
		newSchema['isOptional'] = schema['isOptional']
	return newSchema


def OptimizeIntSchema(schema, target):
	newSchema = {'type': 'int'}
	if 'min' in schema:
		newSchema['min'] = schema['min']
	newSchema['size'] = struct.calcsize("i")
	if 'isOptional' in schema:
		newSchema['isOptional'] = schema['isOptional']
	return newSchema


def OptimizeVectorSchema(schema, target):
	newSchema = {'type': schema['type']}
	if 'aliases' in schema:
		newSchema['aliases'] = schema['aliases']
	if 'isOptional' in schema:
		newSchema['isOptional'] = schema['isOptional']
	return newSchema


def OptimizeBinarySchema(schema, target):
	newSchema = {'type': schema['type']}
	if 'schema' in schema:
		newSchema['schema'] = schema['schema']
		dataSchema = OptimizeSchema(schema['schema'], target)
		if 'size' in dataSchema:
			newSchema['size'] = dataSchema['size']
		if 'isOptional' in dataSchema:
			newSchema['isOptional'] = dataSchema['isOptional']
	return newSchema


_builtInSchemaOptimizationFunctions = {
 'dict'   : OptimizeDictSchema,
 'list'   : OptimizeListSchema,
 'object' : OptimizeObjectSchema,
 'enum'   : OptimizeEnumSchema,
 'int'    : OptimizeIntSchema,
 'vector2': OptimizeVectorSchema,
 'vector3': OptimizeVectorSchema,
 'vector4': OptimizeVectorSchema,
 'binary' : OptimizeBinarySchema
}

_typeSizes = {
 'typeID' : struct.calcsize("I"),
 'float'  : struct.calcsize("f"),
 'vector2': struct.calcsize("ff"),
 'vector3': struct.calcsize("fff"),
 'vector4': struct.calcsize("ffff"),
 'bool'   : struct.calcsize("B"),
}

def OptimizeSchema(schema, target):
	schemaType = schema.get('type')
	optfunc = _builtInSchemaOptimizationFunctions.get(schemaType)
	if optfunc:
		return optfunc(schema, target)

	newSchema = {'type': schemaType}
	if 'isOptional' in schema:
		newSchema['isOptional'] = schema['isOptional']
	size = _typeSizes.get(schemaType)
	if size:
		newSchema['size'] = size
	return newSchema


#-----------------------------------------------------------------------------
# Loaders
#-----------------------------------------------------------------------------



class VectorLoader(object):
	def __init__(self, data, offset, schema, extraState):
		self.data = data
		self.offset = offset
		self.schema = schema
		schemaType = schema['type']
		self.itemCount = int(schemaType[-1])  # vector2, vector3 or vector4

	def __getitem__(self, key):
		if 'aliases' in self.schema:
			idx = self.schema['aliases'].get(key)
			if idx is not None:
				return _float(self.data, self.offset + 4*idx)[0]

		if type(key) is int and key >= 0 and key <= self.itemCount:
			return _float(self.data, self.offset + 4*key)[0]

		raise IndexError('Invalid index %s' % key)

	def __getattr__(self, name):
		try:
			return self.__getitem__(name)
		except IndexError as e:
			raise AttributeError(str(e))

_vector4 = struct.Struct("ffff")
def Vector4FromBinaryString(data, offset, schema, extraState):
	if 'aliases' in schema:
		return VectorLoader(data, offset, schema, extraState)
	return _vector4(data, offset)

_vector3 = struct.Struct("fff")
def Vector3FromBinaryString(data, offset, schema, extraState):
	if 'aliases' in schema:
		return VectorLoader(data, offset, schema, extraState)
	return _vector3(data, offset)

_vector2 = struct.Struct("ff")
def Vector2FromBinaryString(data, offset, schema, extraState):
	if 'aliases' in schema:
		return VectorLoader(data, offset, schema, extraState)
	return _vector2(data, offset)

def StringFromBinaryString(data, offset, schema, extraState):
	return data[4+offset:4+offset+_int32(data, offset)[0]]

def EnumFromBinaryString(data, offset, schema, extraState):
	dataValue = schema['enumType'].unpack_from(data, offset)[0]
	for k, v in schema['values'].iteritems():
		if v == dataValue:
			return k

def BoolFromBinaryString(data, offset, schema, extraState):
	return data[offset] == "\xff"

def IntFromBinaryString(data, offset, schema, extraState):
	if 'min' in schema and schema['min'] >= 0:
		return _uint32(data, offset)[0]
	return _int32(data, offset)[0]

def FloatFromBinaryString(data, offset, schema, extraState):
	return _float(data, offset)[0]



class FixedSizeListRepresentation(object):

	def __init__(self, data, offset, itemSchema, knownLength = None):
		self.data = data
		self.offset = offset
		self.itemSchema = itemSchema
		if knownLength is None:
			self.count = _uint32(data, offset)
			self.fixedLength = False
		else:
			self.count = knownLength
			self.fixedLength = True
		self.itemSize = itemSchema['size']

	def __iter__(self):
		offset = self.offset if self.fixedLength else (self.offset+4)
		return (RepresentSchemaNode(self.data, itemOffset, self.itemSchema) for itemOffset in xrange(offset, offset + self.count * self.itemSize, self.itemSize))

	def __len__(self):
		return self.count

	def __getitem__(self, key):
		if type(key) not in (int, long):
			raise TypeError('Invalid key type')
		if key < 0 or key >= self.count:
			raise IndexError('Invalid item index %i for list of length %i' % (key, self.count))
		offset = self.offset if self.fixedLength else (self.offset+4)
		return RepresentSchemaNode(self.data, offset + self.itemSize * key, self.itemSchema)


class VariableSizedListRepresentation(object):

	def __init__(self, data, offset, itemSchema, knownLength = None):
		self.data = data
		self.offset = offset
		self.itemSchema = itemSchema
		if knownLength is None:
			self.count = _uint32(data, offset)
			self.fixedLength = False
		else:
			self.count = knownLength
			self.fixedLength = True

	def __len__(self):
		return self.count

	def __getitem__(self, key):
		if type(key) not in (int, long):
			raise TypeError('Invalid key type')
		if key < 0 or key >= self.count:
			raise IndexError('Invalid item index %i for list of length %i' % (key, self.count))
		offset = (self.offset if self.fixedLength else (self.offset+4)) + 4*key
		return RepresentSchemaNode(self.data, self.offset + _uint32(data, offset)[0], self.itemSchema)


def ListFromBinaryString(data, offset, schema, knownLength = None):
	knownLength = schema.get('length', knownLength)
	if 'fixedItemSize' in schema:
		return FixedSizeListRepresentation(data, offset, schema['itemTypes'], knownLength)
	else:
		return VariableSizedListRepresentation(data, offset, schema['itemTypes'], knownLength)

		



########################
# dictLoader

def BinarySearch(key, headerDataList):
	minIndex = 0
	maxIndex = len(headerDataList) - 1
	while 1:
		if maxIndex < minIndex:
			return None
		meanIndex = (minIndex + maxIndex) / 2
		headerDataIndex = headerDataList[meanIndex]
		if headerDataIndex['key'] < key:
			minIndex = meanIndex + 1
		elif headerDataIndex['key'] > key:
			maxIndex = meanIndex - 1
		else:
			return headerDataIndex


class DictLoader(object):

	def __init__(self, data, offset, schema, extraState):
		self.data = data
		self.offset = offset
		self.schema = schema
		self.offsetToData = _uint32(data, offset)[0]
		self.__extraState__ = extraState
		self.index = {}
		ListFromBinaryString = self.__extraState__.factories['list']
		self.headerData = ListFromBinaryString(data, offset + 4, self.schema['keyHeader'], self.__extraState__)

	def __getitem__(self, key):
		self._Search(key)
		if self.__extraState__.cfgObject is not None:
			cfgObject = self.__extraState__.cfgObject.GetIfExists(key)
			newState = self.__extraState__.CreateNewStateWithCfgObject(cfgObject)
			if self.index[key] is not None:
				return newState.RepresentSchemaNode(self.data, self.offset + 4 + self.offsetToData + self.index[key], self.schema['valueTypes'])
			if cfgObject is None:
				raise IndexError('key is not in BSD or FSD table - %s' % str(key))
			else:
				return cfgObject
		else:
			if self.index[key] is None:
				raise IndexError('key is not in BSD or FSD table - %s' % str(key))
			return self.__extraState__.RepresentSchemaNode(self.data, self.offset + 4 + self.offsetToData + self.index[key], self.schema['valueTypes'])

	def __len__(self):
		return len(self.headerData)

	def __contains__(self, item):
		return self._Search(item) is not None

	def _Search(self, key):
		if key not in self.index:
			searchResult = BinarySearch(key, self.headerData)
			if searchResult is None:
				self.index[key] = None
			else:
				self.index[key] = searchResult['offset']
		return self.index[key]

	def Get(self, key):
		return self.__getitem__(key)

	def get(self, key, default):
		self._Search(key)
		if self.index[key] is None:
			return default
		return self.__getitem__(key)

	def GetIfExists(self, key):
		return self.get(key, None)


class IndexLoader(object):

	def __init__(self, fileObject, cacheSize, schema, extraState, offset = 0):
		self.fileObject = fileObject
		self.cacheSize = cacheSize
		self.schema = schema
		self.offset = offset
		self.__extraState__ = extraState
		self.index = {}
		fileObject.seek(offset)
		self.headerDataSize = headerSize = _uint32(fileObject.read(4), 0)[0]
		dictHeader = fileObject.read(headerSize)
		ListFromBinaryString = extraState.factories['list']
		self.headerData = ListFromBinaryString(dictHeader, 0, self.schema['keyHeader'], extraState)
		self.cache = collections.OrderedDict()

	def _Search(self, key):
		if key not in self.index:
			searchResult = BinarySearch(key, self.headerData)
			if searchResult != None:
				self.index[key] = (searchResult['offset'], searchResult['size'])
			else:
				self.index[key] = None
		return self.index[key]

	def __getitem__(self, key):
		v = self.cache.pop(key, type)
		if v is not type:
			self.cache[key] = v
			if isinstance(v, IndexLoader):
				return v
			return self.__extraState__.RepresentSchemaNode(v, 0, self.schema['valueTypes'])

		isSubObjectAnIndex = self.schema['valueTypes'].get('buildIndex', False) and self.schema['valueTypes']['type'] == 'dict'
		dataInfo = self._Search(key)
		if dataInfo == None:
			raise KeyError(str(key))
		newOffset = self.offset + 4 + self.headerDataSize + dataInfo[0]
		if isSubObjectAnIndex:
			result = self.cache[key] = IndexLoader(self.fileObject, self.cacheSize, self.schema['valueTypes'], self.__extraState__, offset=newOffset)
			return result
		self.fileObject.seek(newOffset)
		itemData = self.fileObject.read(dataInfo[1])
		self.cache[key] = itemData
		if len(self.cache) > self.cacheSize:
			self.cache.popitem(last=False)
		if self.__extraState__.cfgObject is not None:
			newState = self.__extraState__.CreateNewStateWithCfgObject(self.__extraState__.cfgObject.GetIfExists(key))
			newState.RepresentSchemaNode(itemData, 0, self.schema['valueTypes'])
		else:
			return self.__extraState__.RepresentSchemaNode(itemData, 0, self.schema['valueTypes'])

	def __contains__(self, item):
		return self._Search(item) is not None

	def __len__(self):
		return len(self.headerData)

	def Get(self, key):
		return self.__getitem__(key)

	def GetIfExists(self, key):
		return self.get(key, None)

	def get(self, key, default):
		self._Search(key)
		if self.index[key] is not None:
			return self.__getitem__(key)
		else:
			return default


#################
# listLoader.py

class FixedSizeListRepresentation(object):

	def __init__(self, data, offset, itemSchema, extraState, knownLength = None):
		self.data = data
		self.offset = offset
		self.itemSchema = itemSchema
		self.__extraState__ = extraState
		if knownLength is None:
			self.count = _uint32(data, offset)[0]
			self.fixedLength = False
		else:
			self.count = knownLength
			self.fixedLength = True
		self.itemSize = itemSchema['size']

	def __iter__(self):
		offset = self.offset if self.fixedLength else self.offset+4
		RSN = self.__extraState__.RepresentSchemaNode
		return (RSN(self.data, itemOffset, self.itemSchema) for itemOffset in xrange(offset, offset + self.count*self.itemSize, self.itemSize))

	def __len__(self):
		return self.count

	def __getitem__(self, key):
		if type(key) not in (int, long):
			raise TypeError('Invalid key type')
		if key < 0 or key >= self.count:
			raise IndexError('Invalid item index %i for list of length %i' % (key, self.count))
		countOffset = 0 if self.fixedLength else 4
		itemOffset = self.offset + countOffset + self.itemSize * key
		return self.__extraState__.RepresentSchemaNode(self.data, itemOffset, self.itemSchema)


class VariableSizedListRepresentation(object):

	def __init__(self, data, offset, itemSchema, extraState, knownLength = None):
		self.data = data
		self.offset = offset
		self.itemSchema = itemSchema
		self.__extraState__ = extraState
		if knownLength is None:
			self.count = _uint32(data, offset)[0]
			self.fixedLength = False
		else:
			self.count = knownLength
			self.fixedLength = True

	def __len__(self):
		return self.count

	def __getitem__(self, key):
		if type(key) not in (int, long):
			raise TypeError('Invalid key type')
		if key < 0 or key >= self.count:
			raise IndexError('Invalid item index %i for list of length %i' % (key, self.count))
		countOffset = 0 if self.fixedLength else 4
		offset = self.offset + countOffset + 4 * key
		dataOffsetFromObjectStart = _uint32(data, offset)[0]
		return self.__extraState__.RepresentSchemaNode(self.data, self.offset + dataOffsetFromObjectStart, self.itemSchema)


def ListFromBinaryString(data, offset, schema, extraState, knownLength = None):
	knownLength = schema.get('length', knownLength)
	if 'fixedItemSize' in schema:
		return FixedSizeListRepresentation(data, offset, schema['itemTypes'], extraState, knownLength)
	else:
		return VariableSizedListRepresentation(data, offset, schema['itemTypes'], extraState, knownLength)


#######################
# objectLoader

class ObjectLoader(object):

	def __init__(self, data, offset, schema, extraState):
		self.__data__ = data
		self.__offset__ = offset
		self.__schema__ = schema
		self.__extraState__ = extraState
		self.__hasOptionalAttributes__ = False
		if 'size' not in schema:
			self.__offsetAttributes__ = schema['attributesWithOffsets'][:]
			if self.__schema__['optionalValueLookups']:
				self.__hasOptionalAttributes__ = True
				optionalAttributesField = _uint32(data, offset + schema['endOfFixedSizeData'])[0]
				for attr, i in schema['optionalValueLookups'].iteritems():
					if not optionalAttributesField & i:
						self.__offsetAttributes__.remove(attr)
			_num = len(self.__offsetAttributes__)
			_off = self.__offset__ + schema.get('endOfFixedSizeData', 0) + 4
			self.__variableDataOffsetBase__ = _off + 4*_num
			self.__offsetAttributesOffsetLookupTable__ = struct.unpack_from("I"*_num, data, _off)

	def __getitem__(self, key):
		if key not in self.__schema__['attributes']:
			if self.__extraState__.cfgObject is None:
				raise KeyError("Schema does not contain this attribute '%s'. It may not be present under the current environment." % key)
			else:
				return getattr(self.__extraState__.cfgObject, key)
		attributeSchema = self.__schema__['attributes'][key]
		if key in self.__schema__['attributeOffsets']:
			return self.__extraState__.RepresentSchemaNode(self.__data__, self.__offset__ + self.__schema__['attributeOffsets'][key], attributeSchema)
		else:
			try:
				index = self.__offsetAttributes__.index(key)
			except ValueError:
				if self.__extraState__.cfgObject is not None:
					return getattr(self.__extraState__.cfgObject, key)
				if 'default' in attributeSchema:
					return attributeSchema['default']
				raise KeyError("Object instance does not have this attribute '%s'" % key)

			return self.__extraState__.RepresentSchemaNode(self.__data__, self.__variableDataOffsetBase__ + self.__offsetAttributesOffsetLookupTable__[index], attributeSchema)

	def __getattr__(self, name):
		try:
			return self.__getitem__(name)
		except KeyError as e:
			raise AttributeError(str(e))


#-----------------------------------------------------------------------------
# Binary Loader
#-----------------------------------------------------------------------------

_defaultLoaderFactories = {
 'float': FloatFromBinaryString,
 'vector4': Vector4FromBinaryString,
 'vector3': Vector3FromBinaryString,
 'vector2': Vector2FromBinaryString,
 'string': StringFromBinaryString,
 'resPath': StringFromBinaryString,
 'enum': EnumFromBinaryString,
 'bool': BoolFromBinaryString,
 'int': IntFromBinaryString,
 'typeID': IntFromBinaryString,
 'list': ListFromBinaryString,
 'object': ObjectLoader,
 'dict': DictLoader
}


class LoaderState(object):

	def __init__(self, factories, logger = None, cfgObject = None):
		self.factories = factories
		self.logger = logger
		self.cfgObject = cfgObject

	def RepresentSchemaNode(self, data, offset, schemaNode):
		schemaType = schemaNode.get('type')
		factory = self.factories.get(schemaType)
		if factory:
			return factory(data, offset, schemaNode, self)
		raise NotImplementedError("Unknown type not supported in binary loader '%s'" % str(schemaType))

	def CreateNewStateWithCfgObject(self, cfgObject):
		return LoaderState(self.factories, self.logger, cfgObject)


def RepresentSchemaNode(data, offset, schemaNode, extraState = None):
	schemaType = schemaNode.get('type')
	if extraState is None:
		extraState = LoaderState(_defaultLoaderFactories, None)
	factory = extraState.factories.get(schemaType)
	if factory:
		return factory(data, offset, schemaNode, extraState)
	raise NotImplementedError("Unknown type not supported in binary loader '%s'" % str(schemaType))


def LoadFromString(dataString, optimizedSchema, extraState = None):
	return RepresentSchemaNode(dataString, 0, optimizedSchema, extraState)


def LoadIndexFromFile(fileObject, optimizedSchema, cacheItems, extraState = None):
	if extraState is None:
		extraState = LoaderState(_defaultLoaderFactories, None)
	return IndexLoader(fileObject, cacheItems, optimizedSchema, extraState)





