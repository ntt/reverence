"""EVE path location discovery functions.

Copyright (c) 2003-2015 Jamie "Entity" van den Berge <jamie@hlekkir.com>

This code is free software; you can redistribute it and/or modify
it under the terms of the BSD license (see the file LICENSE.txt
included with the distribution).
"""

import os
import glob


def _SHGetFolderPath(folderID):
	from ctypes import wintypes, windll, c_int
	path_buf = wintypes.create_unicode_buffer(wintypes.MAX_PATH)
	result = windll.shell32.SHGetFolderPathW(0, folderID, 0, 0, path_buf)
	if result:
		if result < 0:
			result += 0x100000000
		raise RuntimeError("SHGetFolderPath failed, error code 0x%08x" % result)
	return path_buf.value


def _mangle_evepath(path, server):
	path = path.lower().replace(":", "").replace("\\", "_").replace(" ", "_")
	path += "_"+server.lower()
	return path




def _get_protocol(machopath, bulkpath):
	protocol = -1
	for scandir in (machopath, bulkpath):
		for dirName in glob.glob(os.path.join(scandir, "*")):
			candidate = os.path.basename(dirName)
			if candidate.isdigit():
				protocol = max(protocol, int(candidate))
	if protocol > -1:
		return protocol


class _Paths(object):

	def __init__(self, root):
		if root is None:
			# I -was- going to put auto path discovery here but EVE's install
			# folder(s) can be pretty elusive :)
			raise ValueError("No EVE install root path specified")

		root = os.path.abspath(root)

		# below are EVE paths used by Reverence and an example location

		# EVE installation root
		# - G:\EVE
		self.root = root

		# ResFiles cache parent
		# - C:\ProgramData\CCP\EVE\SharedCache
		self.sharedcache = None

		# per-install-per-server cache location
		# - C:\Users\Entity\AppData\Local\CCP\EVE\g_eve_tranquility\cache
		self.instancecache = None

		# "settings" folder inside instancecache
		# - C:\Users\Entity\AppData\Local\CCP\EVE\g_eve_tranquility\settings
		self.settings = None

		# "cache" folder inside instancecache
		# - C:\Users\Entity\AppData\Local\CCP\EVE\g_eve_tranquility\cache
		self.cache = None

		# machonet folder for specified/discovered protocol version and server
		# - C:\Users\Entity\AppData\Local\CCP\EVE\g_eve_tranquility\cache\MachoNet\87.237.38.200\409
		self.machocache = None

		# folder for bulkdata updates (files here take priority over bulkdata)
		# - C:\Users\Entity\AppData\Local\CCP\EVE\g_eve_tranquility\cache\bulkdata\409
		self.bulkdata_updates = None

		# "bulkdata" folder in root
		# - G:\EVE\bulkdata
		self.bulkdata = None

		# needed for accessing linux installs
		self.wineprefix = None


	def _set_known_paths(self, cache=None, sharedcache=None, wineprefix=None):
		self.cache = cache
		self.sharedcache = sharedcache
		self.wineprefix = wineprefix


	def _discover(self, server_name, server_ip, protocol):
		# figure out paths based on information provided
		# returns discovered or specified machonet protocol version.

		# Check EVE root for sharedcache and cache folders:
		# This provides a way to run reverence on a host that does not have
		# a proper EVE install by just making sure the right folder/file
		# hierarchy is present in the specified installation folder.
		if self.cache is None:
			_path = os.path.join(self.root, "cache")
			if os.path.exists(_path):
				self.instancecache = self.root

		if self.sharedcache is None:
			_path = os.path.join(self.root, "SharedCache")
			if os.path.exists(_path):
				self.sharedcache = _path

		# do platform specific discovery
		if os.name == "nt":
			self.__discover_windows(server_name)
		elif sys.platform == "darwin" or os.name == "mac":
			self.__discover_mac(server_name)
		elif os.name in ("posix", "linux2"):
			self.__discover_linux()


		self.bulkdata = os.path.join(self.root, 'bulkdata')


		# instancecache is optional for Reverence, it does not require this
		# path unless eve.RemoteSvc() calls are used or access to settings is
		# needed.
		if self.instancecache is not None:
			self.cache = os.path.join(self.instancecache, 'cache')
			self.settings = os.path.join(self.instancecache, 'settings')

			_bulkdata_updates = os.path.join(self.instancecache, 'cache', 'bulkdata')
			_machocache = os.path.join(self.cache, "MachoNet", server_ip)

			# discover protocol version if not set
			if protocol is None:
				protocol = _get_protocol(_machocache, _bulkdata_updates)
				#if self._protocol is None:
				#	raise RuntimeError("Could not determine MachoNet protocol version.")

			# these folders can only be known if we have a protocol version.
			# if a protocol version was specified, the relevant folders *MUST*
			# exist.
			if protocol is not None:
				self.machocache = os.path.join(_machocache, str(protocol))
				self.bulkdata_updates = os.path.join(_bulkdata_updates, str(protocol))

				if not os.path.exists(self.machocache):
					raise RuntimeError("Specified protocol version (%d) not found in %s" % (protocol, _machocache))

		return protocol


	def __discover_windows(self, server_name):
		self.root = os.path.abspath(self.root)

		_localappdata = _SHGetFolderPath(28)  # CSIDL_LOCAL_APPDATA
		_programdata = _SHGetFolderPath(35)  # CSIDL_COMMON_APPDATA
		_programdata = os.getenv("ProgramData", _programdata)

		# find shared cache path
		if self.sharedcache is None:
			import _winreg
			_winreg.aReg = _winreg.ConnectRegistry(None, _winreg.HKEY_CURRENT_USER)
			try:
				key = _winreg.OpenKey(_winreg.aReg, 'SOFTWARE\\CCP\\EVEONLINE')
				self.sharedcache, _ = _winreg.QueryValueEx(key, 'CACHEFOLDER')
			except OSError:
				pass

			if self.sharedcache is None:
				self.sharedcache = os.path.join(_programdata, 'CCP', 'EVE', 'SharedCache')

			if not (self.sharedcache and os.path.exists(self.sharedcache)):
				raise RuntimeError("Unable to locate SharedCache folder")

		if self.instancecache is None:
			self.instancecache = os.path.join(_localappdata, "CCP", "EVE", _mangle_evepath(self.root, server_name))
	

	def __discover_mac(root, server_name):
		home = os.path.expanduser('~')
		_localappdata = os.path.join(home, "Library/Application Support/EVE Online/p_drive/Local Settings/Application Data")
		if not _exists(path):
			_localappdata = os.path.join(home, "Library/Preferences/EVE Online Preferences/p_drive/Local Settings/Application Data")

		_programdata = _localappdata  # apparently....?!

		actualroot = os.path.join(root, "Contents/Resources/transgaming/c_drive/Program Files/CCP/EVE")
		if os.path.exists(actualroot):
			self.root = actualroot

		self.sharedcache = os.path.join(_programdata, "CCP", "EVE", "SharedCache")
		self.instancecache = os.path.join(_localappdata, "CCP", "EVE", "c_program_files_ccp_eve_"+server_name.lower())


	def __discover_linux(self, sever_name):
		import pwd

		# Assuming a WINE install, we are now going to have to do
		# some black magic to figure out where the cache folder is.

		# get the name of the owner of this EVE folder. This is
		# quite likely to be the user used in WINE as well.
		stat_info = os.stat(self.root)
		user = pwd.getpwuid(stat_info.st_uid).pw_name

		if None in (self.instancecache, self.sharedcache):
			if self.wineprefix is None:
				raise RuntimeError("wineprefix must be specified if cache and sharedcache paths are not specified")

			# get the filesystem root for WINE
			x = self.root.find(os.path.join(wineprefix, "drive_"))
			if x == -1:
				raise RuntimeError("specified wineprefix does not appear in EVE root path")

			wineroot = self.root[:x+len(wineprefix)]  # all drive_ folders be here

		def _scan_folders(paths, pattern):
			for path in paths:
				for path in glob.iglob(_join(path, pattern)):
					if exists(path):
						return path

		# locate that cache folder. the names of the folders here
		# depend on the locale of the Windows version used, so we
		# cheat past that with a glob match.
		if self.instancecache is None: 
			candidates = (
				os.path.join(wineroot, "drive_c/users", user),
				os.path.join(wineroot, "drive_c/windows/profile", user),
				os.path.join(wineroot, "drive_c/windows/profiles", user),
			)
			cachefoldername = _mangle_evepath(self.root[x+len(wineprefix)+7:], server_name)
			self.instancecache = _scan_folders(candidates, "*/*/CCP/EVE/"+cacheFolderName)

		if self.sharedcache is None:
			self.sharedcache = _scan_folders((os.path.join(wineroot, "drive_c")), "*/CCP/EVE/SharedCache")



if __name__ == "__main__":
	paths = _Paths("G:/EVE")
	paths._discover("tranquility", "87.237.38.200", None)
	for k, v in paths.__dict__.iteritems():
		print "%s = %s" % (k, v)

