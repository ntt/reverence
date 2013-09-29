"""Interface to cache and bulkdata. Primarily used by ConfigMgr.

Copyright (c) 2003-2012 Jamie "Entity" van den Berge <jamie@hlekkir.com>

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


def GetCacheFileName(key, machoVersion=99999):
	"""Returns filename for specified object name."""
	if machoVersion >= 213:
		return "%x.cache" % binascii.crc_hqx(cPickle.dumps(key), 0)
	else:
		raise RuntimeError("machoNet version 213 or higher required")


def _readfile(filename):
	with open(filename, "rb") as f:
		return f.read()


_localappdata = None

def _find_appdata_path(root, servername, wineprefix):
	# returns (root, appdatapath) tuple where eve stuff may be found.
	global _localappdata

	if os.name == "nt":
		cacheFolderName = root.lower().replace(":", "").replace("\\", "_").replace(" ", "_")
		cacheFolderName += "_"+servername.lower()

		if _localappdata is None:
			from ctypes import wintypes, windll, c_int
			CSIDL_LOCAL_APPDATA = 28
			path_buf = wintypes.create_unicode_buffer(wintypes.MAX_PATH)
			result = windll.shell32.SHGetFolderPathW(0, CSIDL_LOCAL_APPDATA, 0, 0, path_buf)
			if result:
				if result < 0:
					result += 0x100000000
				raise RuntimeError("SHGetFolderPath failed, error code 0x%08x" % result)
			_localappdata = path_buf.value

		appdatapath = _join(_localappdata, "CCP", "EVE", cacheFolderName)

	elif sys.platform == "darwin" or os.name == "mac":
		# slightly less untested. might still be wrong.
		home = os.path.expanduser('~')
		cacheFolderName = "c_program_files_ccp_eve_" + servername.lower()
		appdatapath = _join(home, "Library/Application Support/EVE Online/p_drive/Local Settings/Application Data/CCP/EVE", cacheFolderName)
		if not _exists(appdatapath):
			appdatapath = _join(home, "Library/Preferences/EVE Online Preferences/p_drive/Local Settings/Application Data/CCP/EVE", cacheFolderName)
		actualroot = _join(root, "Contents/Resources/transgaming/c_drive/Program Files/CCP/EVE")
		if _exists(actualroot):
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
		x = root.find(_join(wineprefix, "drive_"))
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
		for appdataroot in [
			_join(wineroot, "drive_c/users", user),
			_join(wineroot, "drive_c/windows/profile", user),
			_join(wineroot, "drive_c/windows/profiles", user),
		]:
			if not _exists(appdataroot):
				continue

			for appdatapath in glob.iglob(_join(appdataroot, "*/*/CCP/EVE/" + cacheFolderName)):
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

	return (root, appdatapath)



class CacheMgr:
	"""Interface to an EVE Installation's cache and bulkdata."""

	def __init__(self, root, servername="Tranquility", machoversion=-1, appdatapath=None, wineprefix=".wine"):
		self.cfg = None
		self._time_load = 0.0

		# get cache folder servername and machonet server ip.
		# the servername should be equal to what was used in the /server option
		# of the EVE shortcut, even if it's an IP address.

		serveraliases = {
			"tranquility": "87.237.38.200",
			"singularity": "87.237.38.50",
			"duality": "87.237.38.60",
			"serenity":"211.144.214.68",
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
		elif serverip == "211.144.214.68":
			servername = "211.144.214.68"

		#---------------------

		if root is None:
			# I -was- going to put auto path discovery here but EVE's install
			# folder(s) can be pretty elusive :)
			raise ValueError("No EVE install root path specified")

		root = os.path.abspath(root)

		candidates = []
		discover = appdatapath is None  # used further down too.
		if discover:
			# auto-discovery of appdata path. try a few places...
			candidates = [
				(root, _join(root, "cache")),
				_find_appdata_path(root, servername, wineprefix),
			]
		else:
			# manually specified cachepath! only look there.
			candidates.append((root, appdatapath))

		#---------------------

		self.machoVersion = -1

		cachenotfound = machonotfound = False

		for root, appdatapath in candidates:
			if root is None:
				continue

			if not _exists(appdatapath):
				cachenotfound = True
				continue

			machopath = _join(appdatapath, "cache", "MachoNet", serverip)
			bulkcpath = _join(appdatapath, "cache", "bulkdata")

			if machoversion > -1:
				# machoversion was specified, so look for just that.
				machocachepath = _join(machopath, str(machoversion))
				bulkdatapath = _join(bulkcpath, str(machoversion))
				if _exists(machocachepath) or _exists(bulkdatapath):
					protocol = machoversion
				else:
					machonotfound = True
					continue
			else:
				# machoversion not specified, find highest.
				protocol = -1

				# look in cache/MachoNet as well as cache/bulkdata
				for scandir in (machopath, bulkcpath):
					for dirName in glob.glob(_join(scandir, "*")):
						candidate = os.path.basename(dirName)
						if candidate.isdigit():
							protocol = max(protocol, int(candidate))

				if protocol == -1:
					machonotfound = True

			if protocol > self.machoVersion:
				self.machoVersion = protocol
				self.root = root
				self.appdatapath = appdatapath
				self.cachepath = _join(appdatapath, "cache")
				self.settingspath = _join(appdatapath, "settings")
				self.machocachepath = _join(machopath, str(protocol))
				self.BULK_SYSTEM_PATH = _join(root, 'bulkdata')
				self.BULK_CACHE_PATH = _join(appdatapath, 'cache', 'bulkdata', str(protocol))
				return

		if self.machoVersion == -1:
			if machonotfound:
				if machoversion == -1:
					raise RuntimeError("Could not determine MachoNet protocol version.")
				else:
					raise RuntimeError("Specified protocol version (%d) not found in MachoNet cache." % machoversion)

			if cachenotfound:
				if discover:
					raise RuntimeError("Could not determine EVE cache folder location.")
				else:
					raise RuntimeError("Specified cache folder does not exist: '%s'" % cachepath)


	def GetCacheFileName(self, key):
		"""Returns the filename for specified object name."""
		return GetCacheFileName(key, self.machoVersion)


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
		name = _join(self.machocachepath, folder, self.GetCacheFileName(key))
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
		for folder in (self.BULK_CACHE_PATH, self.BULK_SYSTEM_PATH):
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
		for cacheName in [
			_join(self.machocachepath, "CachedObjects", fileName),
			_join(self.machocachepath, "CachedMethodCalls", fileName),
			_join(self.machocachepath, "MethodCallCachingDetails", fileName),
		]:
			if _exists(cacheName):
				return cacheName
		return None


	def find(self, key):
		"""Locates and loads a cache object. will check version and contents."""
		fileName = self.GetCacheFileName(key)
		obj = (key, None)
		version = (0L, 0)
		for cacheName in [
			_join(self.machocachepath, "CachedObjects", fileName),
			_join(self.machocachepath, "CachedMethodCalls", fileName),
			_join(self.machocachepath, "MethodCallCachingDetails", fileName),
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
		for folder in (self.BULK_CACHE_PATH, self.BULK_SYSTEM_PATH):
			cacheName = _join(folder, str(bulkID)+".cache2")
			if _exists(cacheName):
				return cacheName


	def getconfigmgr(self, *args, **kw):
		"""Returns a ConfigMgr instance associated with this CacheMgr."""
		if not self.cfg:
			self.cfg = config.Config(self, *args, **kw)

		return self.cfg

