"""Interface to cache and bulkdata. Primarily used by ConfigMgr.

Copyright (c) 2003-2009 Jamie "Entity" van den Berge <jamie@hlekkir.com>

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


def GetCacheFileName(this, machoVersion=99999):
	"""Returns filename for specified object name."""

	if machoVersion >= 213:
		return "%x.cache" % binascii.crc_hqx(cPickle.dumps(this), 0)
# Legacy stuff. Deprecated. Here for historical reasons :)
	#elif machoVersion >= 151:
	#	return "%x.cache" % binascii.crc_hqx((blue.marshal.Save(this, machoVersion=machoVersion)), 0)
	#elif machoVersion >= 136:
	#	return blue.marshal.Save(this).encode("base64").replace('=', '').replace('/', '-').replace('\n', '') + ".cache"
	#else:
	#	return blue.marshal.Save(this).encode("hex") + ".cache"
	else:
		raise RuntimeError("machoNet version 213 or higher required")



class CacheMgr:
	"""Interface to an EVE Installation's cache and bulkdata."""

	def __init__(self, root, servername="Tranquility", machoversion=-1, cachepath=None):
		self.cfg = None
		self._time_load = 0.0

		# get cache folder servername and machonet server ip.
		# the servername should be equal to what was used in the /server option
		# of the EVE shortcut, even if it's an IP address.

		serveraliases = {
			"tranquility": "87.237.38.200",
			"singularity": "87.237.38.50",
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

		if root is None:
			# I -was- going to put auto path discovery here but EVE's install
			# folder(s) can be pretty elusive :)
			raise ValueError("No EVE install root path specified")

		root = os.path.abspath(root)

		# now the cache could be either in EVE's own install folder (LUA:OFF),
		# or in Local Appdata....

		if cachepath is None:
			cachepath = os.path.join(root, "cache")
			if not os.path.exists(cachepath):

				# the cache folder is not in install folder. this means it's
				# in Application Data, however where that one is located varies
				# per platform, windows version and locale.

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
					root = os.path.join(root, "Contents/Resources/transgaming/c_drive/Program Files/CCP/EVE")

				elif os.name == "posix":
					import pwd

					# Assuming a WINE install, we are now going to have to do
					# some black magic to figure out where the cache folder is.

					# get the name of the owner of this EVE folder. This is
					# quite likely to be the user used in WINE as well.
					stat_info = os.stat(root)
					user = pwd.getpwuid(stat_info.st_uid).pw_name

					# get the filesystem root for WINE
					x = root.find(".wine/drive_")
					if x == -1:
						raise RuntimeError("Must specify cachepath manually on this platform for non-WINE installs.")
					wineroot = root[:x+5]  # all drive_ folders be here

					# now we can get the cache folder name (as produced by EVE
					# from the install path by mangling separators and spaces)
					cacheFolderName = root[x+12:].replace("/", "_").replace(" ", "_")
					cacheFolderName += "_" + servername
					cacheFolderName = cacheFolderName.lower()

					# locate that cache folder. the names of the folders here
					# depend on the locale of the Windows version used, so we
					# cheat past that with a glob match.
					for settingsroot in [
						os.path.join(wineroot, "drive_c/users", user),
						os.path.join(wineroot, "drive_c/windows/profile", user),
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
					raise RuntimeError("Must specify cachepath manually on this platform if the cache folder is not in EVE root")

		if not os.path.exists(cachepath):
			raise RuntimeError("Could not determine EVE cache folder location.")

		machoCachePath = os.path.join(cachepath, "MachoNet", serverip)
		if machoversion == -1:
			# find highest macho version...
			for dirName in glob.glob(os.path.join(machoCachePath, "*")):
				try:
					machoversion = max(machoversion, int(os.path.basename(dirName)))
				except ValueError:
					pass
				except TypeError:
					pass

		if machoversion == -1:
			raise RuntimeError("Could not determine machoNet version from cache folder %s" % machoCachePath)

		self.machoVersion = machoversion

		self.root = root
		self.cachepath = cachepath
		self.machocachepath = os.path.join(machoCachePath, str(machoversion))
		self.bulkdatapath = os.path.join(root, "bulkdata")


	def LoadCacheFolder(self, name, filter="*.cache"):
		"""Loads all .cache files from specified folder. Returns a dict keyed on object name."""
		crap = {}
		if self.machoVersion > 181 and name.lower() == "bulkdata":
			name = self.bulkdatapath
		else:
			name = os.path.join(self.machocachepath, name)
		for filename in glob.glob(os.path.join(name, filter)):
			what, obj = blue.marshal.Load(open(filename,"rb").read())
			crap[what] = obj
		return crap


	def LoadCachedMethodCall(self, this):
		"""Loads a named object from EVE's CachedMethodCalls folder."""
		name = os.path.join(self.machocachepath, "CachedMethodCalls", self.GetCacheFileName(this))
		what, obj = blue.marshal.Load(open(name, "rb").read())
		if what != this:
			# Oops. We did not get what we asked for...
			raise RuntimeError("Hash collision: Wanted '%s' but got '%s'" % (this, what))
		return obj


	def LoadCachedObject(self, this):
		"""Loads a named object from EVE's CachedObjects folder."""
		fileName = self.GetCacheFileName(this)
		name = os.path.join(self.machocachepath, "CachedObjects", fileName)
		what, obj = blue.marshal.Load(open(name, "rb").read())
		if what != this:
			# Oops. We did not get what we asked for...
			raise RuntimeError("Hash collision: Wanted '%s' but got '%s'" % (this, what))
		return obj

	def LoadObject(self, this):
		"""Load named object from cache or builkdata, whichever is the higher version."""

		fileName = self.GetCacheFileName(this)

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

			if what == this:
				if obj2.version > version:
					obj = obj2
					version = obj.version

		if obj is None:
			raise RuntimeError("cache file not found: %s" % fileName)

		obj = obj.GetCachedObject()
		return obj


	def GetCacheFileName(self, this):
		"""Returns the filename for specified object name."""
		return GetCacheFileName(this, self.machoVersion)


	def FindCacheFile(self, this):
		"""Attempts to locate a cache file in any of the cache locations.

		Note: does no version/content check, so do not use for bulkdata.
		"""
		fileName = self.GetCacheFileName(this)
		for cacheName in [
			os.path.join(self.machocachepath, "CachedObjects", fileName),
			os.path.join(self.bulkdatapath, fileName),
			os.path.join(self.machocachepath, "CachedMethodCalls", fileName),
			os.path.join(self.machocachepath, "MethodCallCachingDetails", fileName),
		]:
			if os.path.exists(cacheName):
				return cacheName
		return None


	def find(self, this):
		"""Locates and loads a cache object. will check version and contents."""
		fileName = self.GetCacheFileName(this)
		obj = (this, None)
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

				if what == this:
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

