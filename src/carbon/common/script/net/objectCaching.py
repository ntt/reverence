"""Cached object envelope classes.

This code is free software; you can redistribute it and/or modify
it under the terms of the BSD license (see the file LICENSE.txt
included with the distribution).

Parts of code inspired by or based on EVE Online, with permission from CCP.
"""

import zlib

from reverence import blue, util

class CachedMethodCallResult:
	__guid__ = "objectCaching.CachedMethodCallResult"
	__passbyvalue__ = 1

	def __setstate__(self, state):
		self.details, self.result, self.version = state

	def GetResult(self):
		if isinstance(self.result, util.CachedObject):
			return self.result.GetCachedObject()
		else:
			return blue.marshal.Load(self.result)

class CachedObject:
	__guid__ = "objectCaching.CachedObject"

	def __getstate__(self):
		if self.pickle is None:
			import blue
			if self.isCompressed:
				self.pickle = zlib.compress(blue.marshal.Save(self.object), 1)
			else:
				self.pickle = blue.marshal.Save(self.object)

		return (self.version, None, self.nodeID, self.shared, self.pickle, self.isCompressed, self.objectID,)

	def __setstate__(self,state):
		self.version, self.object, self.nodeID, self.shared, self.pickle, self.isCompressed, self.objectID = state

	def GetCachedObject(self):
		if self.object is None:
			if self.pickle is None:
				raise RuntimeError, "Wtf? no object?"
			if self.isCompressed:
				self.object = blue.marshal.Load(zlib.decompress(self.pickle))
			else:
				self.object = blue.marshal.Load(self.pickle)
			self.pickle = None
		return self.object

	GetObject = GetCachedObject

