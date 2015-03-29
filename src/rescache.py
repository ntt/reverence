"""Resource cache manager (handles EVE shared resource cache).

Copyright (c) 2003-2015 Jamie "Entity" van den Berge <jamie@hlekkir.com>
Copyright (c) 2015 Anton "DarkPhoenix" Vorobyov <phoenix@mail.ru>

This code is free software; you can redistribute it and/or modify
it under the terms of the BSD license (see the file LICENSE.txt
included with the distribution).
"""


import csv
import os.path
import urllib2
import zlib

from .config import _memoize

# Servers for Download-on-Demand.
_DOWNLOAD_SERVERS = (
	"http://res.eveprobe.ccpgames.com/",
	"http://eve-probe-res.s3-website-eu-west-1.amazonaws.com/",
)

_BLOCKSIZE = 8192

_useragent = None

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
		
		if _useragent is None:
			return open(fullPath, mode='rb')
		else:
			try:
				return open(fullPath, mode='rb')
			except IOError:
				# file not present. download it.
				if not os.path.exists(fullPath):
					self._download(resPath, fullPath)
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

		
	def _download(self, resPath, fullPath):
		# make sure the folder exists.
		folder = os.path.dirname(fullPath)
		if not os.path.exists(folder):
			os.makedirs(folder)

		# now try all download servers.
		for server in _DOWNLOAD_SERVERS:
			try:
				req = urllib2.Request(server+resPath, None, headers={"User-Agent": _useragent})
				response = urllib2.urlopen(req)
				
				with open(fullPath, "wb") as f:
					d = zlib.decompressobj(zlib.MAX_WBITS|32)  # gzip mode
					while True:
						buffer = response.read(_BLOCKSIZE)
						if not buffer:
							break
						f.write(d.decompress(buffer))
				return

			except Exception, e:
				pass
			raise e


				