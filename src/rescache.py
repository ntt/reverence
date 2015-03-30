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
import hashlib

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
		try:
			_, resPath, file_hash, file_size, compressed_size = self._index[name.lower()]
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
					self._download(resPath, fullPath, file_hash, file_size, compressed_size)
					return open(fullPath, mode='rb')


	@_memoize
	def _index(self):
		d = {}
		indexPath = os.path.join(self._evePath, 'resfileindex.txt')
		with open(indexPath) as csvFile:
			for row in csv.reader(csvFile):
				d[row[0].lower()] = row
		return d

		
	def _download(self, resPath, fullPath, file_hash, file_size, compressed_size):
		# make sure the folder exists.
		folder = os.path.dirname(fullPath)
		if not os.path.exists(folder):
			os.makedirs(folder)

		tempfilename = fullPath + ".part"
			
		# now try all download servers.
		for server in _DOWNLOAD_SERVERS:
			try:
				req = urllib2.Request(server+resPath, None, headers={"User-Agent": _useragent})
				response = urllib2.urlopen(req)
				with open(tempfilename, "wb") as f:
					d = zlib.decompressobj(zlib.MAX_WBITS|32)  # gzip mode
					m = hashlib.md5()
					csize = 0
					while True:
						buffer = response.read(_BLOCKSIZE)
						if not buffer:
							break
						csize += len(buffer)
						buffer = d.decompress(buffer)
						m.update(buffer)
						f.write(buffer)
					fsize = f.tell()
					
				# as we might be downloading directly to EVE's shared
				# cache, do strict tests to see if what we asked for is
				# what we actually got.
				if str(csize) != compressed_size or str(fsize) != file_size or m.hexdigest() != file_hash:
					raise RuntimeError("Download failed - file %s does not match index." % fullPath)

				# rename file to its proper cache name.
				os.rename(tempfilename, fullPath)
				return

			except Exception, e:
				# delete the temporary file, it's probably useless anyway.
				if os.path.exists(tempfilename):
					os.unlink(tempfilename)

		raise e


