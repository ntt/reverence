"""Resource cache manager (handles EVE shared resource cache).

Copyright (c) 2003-2015 Jamie "Entity" van den Berge <jamie@hlekkir.com>
Copyright (c) 2015 Anton "DarkPhoenix" Vorobyov <phoenix@mail.ru>

This code is free software; you can redistribute it and/or modify
it under the terms of the BSD license (see the file LICENSE.txt
included with the distribution).
"""


import csv
import os.path

from .config import _memoize


class ResourceCache(object):
	"""Manages folder with cached resources"""

	def __init__(self, evePath, sharedCachePath):
		self._evePath = evePath
		self._sharedCachePath = sharedCachePath

	def open(self, name):
		name = name.lower()
		try:
			resPath = self._nameMap[name.lower()]
		except KeyError:
			raise IndexError("File not in resfileindex: '%s'" % name)

		fullPath = os.path.join(self._sharedCachePath, 'ResFiles', resPath)
		return open(fullPath, mode='rb')

	@_memoize
	def _nameMap(self):
		# Format:
		# {resource file name: path name relative to res cache root}
		nameMap = {}
		indexPath = os.path.join(self._evePath, 'resfileindex.txt')
		with open(indexPath) as csvFile:
			for row in csv.reader(csvFile):
				resPath = row[0].lower()
				filePath = row[1]
				nameMap[resPath] = filePath
		return nameMap

