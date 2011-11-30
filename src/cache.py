"""Interface to cache and bulkdata. Primarily used by ConfigMgr.

Copyright (c) 2003-2011 Jamie "Entity" van den Berge <jamie@hlekkir.com>

This code is free software; you can redistribute it and/or modify
it under the terms of the BSD license (see the file LICENSE.txt
included with the distribution).
"""

import sys
import os
import glob
import platform
import time
import cPickle
import binascii

from . import config

# can't simply import blue (circular import). only using marshal anyway.
from . import _blue as blue


def GetCacheFileName(key, machoVersion=99999):
	"""Returns filename for specified object name."""

	if machoVersion >= 213:
		return "%x.cache" % binascii.crc_hqx(cPickle.dumps(key), 0)
# Legacy stuff. Deprecated. Here for historical reasons :)
	#elif machoVersion >= 151:
	#	return "%x.cache" % binascii.crc_hqx((blue.marshal.Save(key, machoVersion=machoVersion)), 0)
	#elif machoVersion >= 136:
	#	return blue.marshal.Save(key).encode("base64").replace('=', '').replace('/', '-').replace('\n', '') + ".cache"
	#else:
	#	return blue.marshal.Save(key).encode("hex") + ".cache"
	else:
		raise RuntimeError("machoNet version 213 or higher required")


def _findcachepath(root, servername, wineprefix):
	# returns (root, cachepath) tuple where eve stuff may be found.

	if os.name == "nt":
		cacheFolderName = root.lower().replace(":", "").replace("\\", "_").replace(" ", "_")
		cacheFolderName += "_"+servername.lower()

		from ctypes import wintypes, windll, c_int
		CSIDL_LOCAL_APPDATA = 28
		path_buf = wintypes.create_unicode_buffer(wintypes.MAX_PATH)
		result = windll.shell32.SHGetFolderPathW(0, CSIDL_LOCAL_APPDATA, 0, 0, path_buf)
		if result:
			raise RuntimeError("SHGetFolderPath failed, error code 0x%08x" % result)
		cachepath = os.path.join(path_buf.value, "CCP", "EVE", cacheFolderName, "cache")

	elif sys.platform == "darwin" or os.name == "mac":
		# slightly less untested. might still be wrong.
		home = os.path.expanduser('~')
		cacheFolderName = "c_program_files_ccp_eve_" + servername.lower()
		cachepath = os.path.join(home, "Library/Preferences/EVE Online Preferences/p_drive/Local Settings/Application Data/CCP/EVE", cacheFolderName, "cache")
		actualroot = os.path.join(root, "Contents/Resources/transgaming/c_drive/Program Files/CCP/EVE")
		if os.path.exists(actualroot):
			root = actualroot

	elif os.name == "posix":
		import pwd

		# Assuming a WINE install, we are now going to have to do
		# some black magic to figure out where the cache folder is.

		# get the name of the owner of this EVE folder. This is
		# quite likely to be the user used in WINE as well.
		stat_info = os.stat(root)
		user = pwd.getpwuid(stat_info.st_uid).pw_name

		# get the filesystem root for WINE
		x = root.find(os.path.join(wineprefix, "drive_"))
		if x == -1:
			return (None, None)

		wineroot = root[:x+len(wineprefix)]  # all drive_ folders be here

		# now we can get the cache folder name (as produced by EVE
		# from the install path by mangling separators and spaces)
		cacheFolderName = root[x+len(wineprefix)+7:].replace("/", "_").replace(" ", "_")
		cacheFolderName += "_" + servername
		cacheFolderName = cacheFolderName.lower()

		# locate that cache folder. the names of the folders here
		# depend on the locale of the Windows version used, so we
		# cheat past that with a glob match.
		for settingsroot in [
			os.path.join(wineroot, "drive_c/users", user),
			os.path.join(wineroot, "drive_c/windows/profile", user),
			os.path.join(wineroot, "drive_c/windows/profiles", user),
		]:
			if not os.path.exists(settingsroot):
				continue

			for cachepath in glob.iglob(os.path.join(settingsroot, "*/*/CCP/EVE/" + cacheFolderName, "cache")):
				# this should only ever give one folder.
				break
			else:
				# no cache folder found? user must have a really
				# freakin' bizarre install. screw that!
				continue

			# cache folder found, no need to continue.
			break

	else:
		return (None, None)

	return (root, cachepath)



class CacheMgr:
	"""Interface to an EVE Installation's cache and bulkdata."""

	def __init__(self, root, servername="Tranquility", machoversion=-1, cachepath=None, wineprefix=".wine"):
		self.cfg = None
		self._time_load = 0.0

		# get cache folder servername and machonet server ip.
		# the servername should be equal to what was used in the /server option
		# of the EVE shortcut, even if it's an IP address.

		serveraliases = {
			"tranquility": "87.237.38.200",
			"singularity": "87.237.38.50",
			"duality": "87.237.38.60",
		}

		if servername.replace(".","").isdigit():
			serverip = servername
		else:
			serverip = serveraliases.get(servername.lower(), None)

		if serverip is None:
			raise ValueError("Invalid server name '%s'. Valid names are '%s' or an IP address." %\
				(servername, "', '".join((x.capitalize() for x in serveraliases))))

		if serverip == "87.237.38.200":
			servername = "Tranquility"

		#---------------------

		if root is None:
			# I -was- going to put auto path discovery here but EVE's install
			# folder(s) can be pretty elusive :)
			raise ValueError("No EVE install root path specified")

		root = os.path.abspath(root)

		candidates = []
		guess = cachepath is None
		if guess:
			# auto-discovery of cachepath. try a few places...
			guess = True
			candidates = [
				(root, os.path.join(root, "cache")),
				_findcachepath(root, servername, wineprefix),
			]
		else:
			# manually specified cachepath! only look there.
			candidates.append((root, cachepath))

		#---------------------

		self.machoVersion = -1

		cachenotfound = machonotfound = False

		for root, cachepath in candidates:
			if root is None:
				continue

			if not os.path.exists(cachepath):
				cachenotfound = True
				continue

			machopath = os.path.join(cachepath, "MachoNet", serverip)
			bulkcpath = os.path.join(cachepath, "bulkdata")

			if machoversion > -1:
				# machoversion was specified, so look for just that.
				machocachepath = os.path.join(machopath, str(machoversion))
				bulkdatapath = os.path.join(bulkcpath, str(machoversion))
				if os.path.exists(machocachepath) or os.path.exists(bulkdatapath):
					protocol = machoversion
				else:
					machonotfound = True
					continue
			else:
				# machoversion not specified, find highest.
				protocol = -1

				# look in cache/MachoNet as well as cache/bulkdata
				for scandir in (machopath, bulkcpath):
					for dirName in glob.glob(os.path.join(scandir, "*")):
						candidate = os.path.basename(dirName)
						if candidate.isdigit():
							protocol = max(protocol, int(candidate))

				if protocol == -1:
					machonotfound = True

			if protocol > self.machoVersion:
				self.root = root
				self.bulkdatapath = os.path.join(root, "bulkdata")
				self.cachepath = cachepath
				self.machoVersion = protocol
				self.machocachepath = os.path.join(machopath, str(protocol))
				self.BULK_SYSTEM_PATH = os.path.join(root, 'bulkdata')
				self.BULK_CACHE_PATH = os.path.join(cachepath, 'bulkdata', str(protocol))
				return

		if self.machoVersion == -1:
			if machonotfound:
				if machoversion == -1:
					raise RuntimeError("Could not determine MachoNet protocol version.")
				else:
					raise RuntimeError("Specified protocol version (%d) not found in MachoNet cache." % machoversion)

			if cachenotfound:
				if guess:
					raise RuntimeError("Could not determine EVE cache folder location.")
				else:
					raise RuntimeError("Specified cache folder does not exist: '%s'" % cachepath)


	def LoadCacheFolder(self, name, filter="*.cache"):
		"""Loads all .cache files from specified folder. Returns a dict keyed on object name."""
		crap = {}
		if self.machoVersion > 181 and name.lower() == "bulkdata":
			name = self.bulkdatapath
		else:
			name = os.path.join(self.machocachepath, name)
		for filename in glob.glob(os.path.join(name, filter)):
			try:
				what, obj = blue.marshal.Load(open(filename,"rb").read())
				crap[what] = obj
			except RuntimeError:  # todo: make proper UnmarshalError exception class
				# ignore files that cannot be decoded.
				pass

		return crap


	def LoadCachedMethodCall(self, key):
		"""Loads a named object from EVE's CachedMethodCalls folder."""
		name = os.path.join(self.machocachepath, "CachedMethodCalls", self.GetCacheFileName(key))
		what, obj = blue.marshal.Load(open(name, "rb").read())
		if what != key:
			# Oops. We did not get what we asked for...
			raise RuntimeError("Hash collision: Wanted '%s' but got '%s'" % (key, what))
		return obj


	def LoadCachedObject(self, key):
		"""Loads a named object from EVE's CachedObjects folder."""
		fileName = self.GetCacheFileName(key)
		name = os.path.join(self.machocachepath, "CachedObjects", fileName)
		what, obj = blue.marshal.Load(open(name, "rb").read())
		if what != key:
			# Oops. We did not get what we asked for...
			raise RuntimeError("Hash collision: Wanted '%s' but got '%s'" % (key, what))
		return obj


	def LoadBulk(self, bulkID):
		"""Loads bulkdata for the specified bulkID"""
		# This is a protocol 276+ feature.
		for folder in [self.BULK_CACHE_PATH, self.BULK_SYSTEM_PATH]:
			cacheName = os.path.join(folder, str(bulkID)+".cache2")
			if os.path.exists(cacheName):
				# No version check required with CCP's new system.
				return blue.marshal.Load(open(cacheName, "rb").read())


	def LoadObject(self, key):
		"""Load named object from cache or builkdata, whichever is the higher version."""

		fileName = self.GetCacheFileName(key)

		src = None
		what = None

		obj = None
		version = (0L, 0)

		# Check both cache locations and pick whichever has the higher version

		for cacheName in [
			os.path.join(self.machocachepath, "CachedObjects", fileName),
			os.path.join(self.bulkdatapath, fileName),
		]:
			if os.path.exists(cacheName):
				blurb = open(cacheName, "rb").read()
				_t = time.clock()
				what, obj2 = blue.marshal.Load(blurb)
				self._time_load += (time.clock() - _t)

			if what == key:
				if obj2.version > version:
					obj = obj2
					version = obj.version

		if obj is None:
			raise RuntimeError("cache file not found: %s" % fileName)

		obj = obj.GetCachedObject()
		return obj


	def GetCacheFileName(self, key):
		"""Returns the filename for specified object name."""
		return GetCacheFileName(key, self.machoVersion)


	def FindCacheFile(self, key):
		"""Attempts to locate a cache file in any of the cache locations.

		Note: does no version/content check, so do not use for bulkdata.
		"""
		fileName = self.GetCacheFileName(key)
		for cacheName in [
			os.path.join(self.machocachepath, "CachedObjects", fileName),
			os.path.join(self.bulkdatapath, fileName),
			os.path.join(self.machocachepath, "CachedMethodCalls", fileName),
			os.path.join(self.machocachepath, "MethodCallCachingDetails", fileName),
		]:
			if os.path.exists(cacheName):
				return cacheName
		return None


	def find(self, key):
		"""Locates and loads a cache object. will check version and contents."""
		fileName = self.GetCacheFileName(key)
		obj = (key, None)
		version = (0L, 0)
		for cacheName in [
			os.path.join(self.machocachepath, "CachedObjects", fileName),
			os.path.join(self.bulkdatapath, fileName),
			os.path.join(self.machocachepath, "CachedMethodCalls", fileName),
			os.path.join(self.machocachepath, "MethodCallCachingDetails", fileName),
		]:
			if os.path.exists(cacheName):
				blurb = open(cacheName, "rb").read()
				_t = time.clock()
				what, obj2 = blue.marshal.Load(blurb)
				self._time_load += (time.clock() - _t)

				if what == key:
					if obj2.version > version:
						obj = (what, obj2)
						version = obj2.version

		return fileName, obj


	def GetConfigMgr(self, *args, **kw):
		"""Returns a ConfigMgr instance associated with this CacheMgr."""
		if not self.cfg:
			self.cfg = config.Config(self, *args, **kw)

		return self.cfg



__all__ = ["GetCacheFileName", "CacheMgr"]

