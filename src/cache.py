"""Interface to cache and bulkdata. Primarily used by ConfigMgr.

Copyright (c) 2003-2015 Jamie "Entity" van den Berge <jamie@hlekkir.com>

This code is free software; you can redistribute it and/or modify
it under the terms of the BSD license (see the file LICENSE.txt
included with the distribution).
"""

from __future__ import with_statement

import sys
import os
import glob
import platform
import time
import cPickle
import binascii

from . import config
from . import _blue as blue  # can't simply import blue (circular import). only using marshal anyway.

__all__ = ["GetCacheFileName", "CacheMgr"]

_join = os.path.join
_exists = os.path.exists


def GetCacheFileName(key):
	"""Returns filename for specified object name."""

	# BEGIN UGLY HACK ----------------------------------------------------
	# CCP is relying on pickle to produce consistent output, which it does
	# not because pickle's output depends on the refcount of objects; an
	# object referenced only once will not get memoized. Cache keys are
	# seemingly always created by EVE with refcounts >1. When Reverence
	# decodes them, they only have a refcount of 1. This code ensures that
	# those refcounts are increased so cPickle produces the correct output
	# when you feed a decoded object's key to this function.
	# (and no, copy.deepcopy doesn't work as expected on tuples)
	memoize = [].append
	def increase_refcounts(k):
		if type(k) is tuple:
			for element in k:
				increase_refcounts(element)
		memoize(k)
	increase_refcounts(key)
	# END UGLY HACK ------------------------------------------------------

	return "%x.cache" % binascii.crc_hqx(cPickle.dumps(key), 0)


def _readfile(filename):
	with open(filename, "rb") as f:
		return f.read()



class CacheMgr:
	"""Interface to an EVE Installation's cache and bulkdata."""

	def __init__(self, eve):
		self.eve = eve
		self.cfg = None
		self._time_load = 0.0

		self.machocache = eve.paths.machocache
		
		# search order for bulkdata
		self.bulkdata_paths = [folder for folder in (eve.paths.bulkdata_updates, eve.paths.bulkdata) if folder is not None]


	def GetCacheFileName(self, key):
		"""Returns the filename for specified object name."""
		return GetCacheFileName(key)


	def LoadCacheFolder(self, name, filter="*.cache"):
		"""Loads all .cache files from specified folder. Returns a dict keyed on object name."""

		# Note that this method is used mainly for debugging and testing,
		# and is subject to change without notice.
		crap = {}
		for filename in glob.glob(_join(name, filter)):
			what, obj = blue.marshal.Load(_readfile(filename))
			crap[what] = obj
		return crap


	def _loadobject(self, key, canraise=False, folder=None):
		name = _join(self.machocache, folder, self.GetCacheFileName(key))
		if not canraise:
			if not _exists(name):
				return None

		what, obj = blue.marshal.Load(_readfile(name))
		if what != key:
			# Oops. We did not get what we asked for...
			if canraise:
				raise RuntimeError("Hash collision: Wanted '%s' but got '%s'" % (key, what))
			return None

		return obj


	def LoadCachedMethodCall(self, key):
		"""Loads a named object from EVE's CachedMethodCalls folder."""
		return self._loadobject(key, True, "CachedMethodCalls")

	def LoadCachedObject(self, key):
		"""Loads a named object from EVE's CachedObjects folder."""
		return self._loadobject(key, True, "CachedObjects")

	def LoadObject(self, key):
		"""Load named object from cache, or None if it is not available."""
		return self._loadobject(key, False, "CachedObjects")


	def LoadBulk(self, bulkID):
		"""Loads bulkdata for the specified bulkID"""
		for folder in self.bulkdata_paths:
			if folder is not None:
				cacheName = _join(folder, str(bulkID)+".cache2")
				if _exists(cacheName):
					# No version check required.
					_t = time.clock()
					obj = blue.marshal.Load(_readfile(cacheName))
					self._time_load += (time.clock() - _t)
					return obj


	def FindCacheFile(self, key):
		"""Attempts to locate a cache file in any of the cache locations."""
		fileName = self.GetCacheFileName(key)
		_machocache = self.machocache
		for cacheName in [
			_join(_machocache, "CachedObjects", fileName),
			_join(_machocache, "CachedMethodCalls", fileName),
			_join(_machocache, "MethodCallCachingDetails", fileName),
		]:
			if _exists(cacheName):
				return cacheName
		return None


	def find(self, key):
		"""Locates and loads a cache object. will check version and contents."""
		fileName = self.GetCacheFileName(key)
		obj = (key, None)
		version = (0L, 0)
		_machocache = self.machocache
		for cacheName in [
			_join(_machocache, "CachedObjects", fileName),
			_join(_machocache, "CachedMethodCalls", fileName),
			_join(_machocache, "MethodCallCachingDetails", fileName),
		]:
			if _exists(cacheName):
				blurb = _readfile(cacheName)
				_t = time.clock()
				what, obj2 = blue.marshal.Load(blurb)
				self._time_load += (time.clock() - _t)

				if what == key:
					if obj2.version > version:
						obj = (what, obj2)
						version = obj2.version

		return fileName, obj


	def findbulk(self, bulkID):
		"""Locates bulkdata file by ID."""
		for folder in self.bulkdata_paths:
			cacheName = _join(folder, str(bulkID)+".cache2")
			if _exists(cacheName):
				return cacheName


	def getconfigmgr(self, *args, **kw):
		"""Returns a ConfigMgr instance associated with this CacheMgr."""
		if not self.cfg:
			self.cfg = config.Config(*args, **kw)

		return self.cfg

