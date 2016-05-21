"""Main interface to all the goodies.

Copyright (c) 2003-2015 Jamie "Entity" van den Berge <jamie@hlekkir.com>

This code is free software; you can redistribute it and/or modify
it under the terms of the BSD license (see the file LICENSE.txt
included with the distribution).
"""

import __builtin__
import sys
from time import sleep as _sleep

from ._blue import marshal, DBRow, DBRowDescriptor
from . import exceptions
from . import cache
from . import _os as os
from . import _blue
from . import pyFSD
from . import discover
from . import rescache

from reverence.carbon.common.lib.utillib import KeyVal

def set_user_agent(useragent):
	rescache._useragent = useragent


_serveraliases = {
	"tranquility": "87.237.34.200",
	"singularity": "87.237.33.2",
	"duality"    : "87.237.38.60",
	"serenity"   : "211.144.214.68",
}

def _getserver(server):
	if server.replace(".","").isdigit():
		serverip = server or None
	else:
		serverip = _serveraliases.get(server.lower(), None)

	if serverip is None:
		raise ValueError("Invalid server name '%s'. Valid names are '%s' or an IP address." %\
			(server, "', '".join((x.capitalize() for x in _serveraliases))))

	if serverip == "87.237.34.200":
		servername = "Tranquility"
	elif serverip == "87.237.33.2":
		servername = "Singularity"
	elif serverip == "211.144.214.68":
		servername = "211.144.214.68"
	else:
		servername = serverip

	return servername, serverip



__all__ = ["EVE", "marshal", "os", "pyos", "DBRow", "DBRowDescriptor"]


# Little hack to have our exceptions look pretty when raised; instead of
#   "reverence.blue.marshal.UnmarshalError: not enough kittens!"
# it will look like
#   "UnmarshalError: not enough kittens!"
# Yes I know this is naughty, but EVE presents them like this as well ;)
marshal.UnmarshalError.__module__ = None

# and because the exception class is accessible like this in EVE ...
exceptions.UnmarshalError = exceptions.SQLError = __builtin__.UnmarshalError = marshal.UnmarshalError

class boot:
	role = "client"

class pyos:
	class synchro:
		@staticmethod
		def Sleep(msec):
			_sleep(msec / 1000.0)


class statistics(object):
	# dummy for compatibility with CCP libs

	@staticmethod
	def EnterZone(*args):
		pass

	@staticmethod
	def LeaveZone():
		pass


class _ResFile(object):
	# read-only resource file handler.

	def __init__(self, rescache):
		self.fh = None
		self.rescache = rescache

	def Open(self, filename):
		self.Close()
		try:
			if filename.startswith("res:"):
				try:
					self.fh = self.rescache.open(filename)
				except IndexError, e:
					return None
#			elif filename.startswith("cache:"):
#				self.fh = open(os.path.join(self.eve.paths.root, "cache", filename[7:]), "rb") 
			else:
				self.fh = open(filename, "rb")
		except IOError:
			pass

		return self.fh

	def Read(self, *args):
		return self.fh.read(*args)

	def Close(self):
		if self.fh:
			self.fh.close()
			self.fh = None

	# ---- custom additions ----

	def resolvepath(self, filename):
		if filename.startswith("res:"):
			return self.rescache.prime(filename)
		else:
			return filename
	
	def read(self, *args):
		return self.fh.read(*args)

	def readline(self):
		return self.fh.readline()

	def seek(self, *args, **kw):
		return self.fh.seek(*args, **kw)


# offline RemoteSvc wrappers

class _RemoteSvcWrap(object):
	def __init__(self, eve, name):
		self.eve = eve
		self.svcName = name

	def __getattr__(self, methodName):
		return _RemoteSvcMethod(self.eve, self.svcName, methodName)


class _RemoteSvcMethod(object):
	def __init__(self, eve, svcName, methodName):
		self.eve = eve
		self.svcName = svcName
		self.methodName = methodName

	def __call__(self, *args, **kw):
		key = (self.svcName, self.methodName) + args
		obj = self.eve.cache.LoadCachedMethodCall(key)
		return obj['lret']


ResFile = None

class EVE(object):
	"""Interface to an EVE installation's related data.

	provides the following methods:
	getconfigmgr() - creates interface to bulkdata. see config.ConfigMgr.
	getcachemgr() - creates interface to cache. see cache.CacheMgr.
	readstuff(name) - reads the specified file from EVE's resource cache.
	RemoteSvc(service) - creates offline RemoteSvc wrapper for given service.
	"""

	def __init__(self, root, server="Tranquility", protocol=None, languageID="en-us", cachepath=None, sharedcachepath=None, wineprefix=None):
		self.server = server
		self.languageID = languageID

		self.server_name, self.server_ip = _getserver(server)

		self.paths = discover._Paths(root)
		self.paths._set_known_paths(cache=cachepath, sharedcache=sharedcachepath, wineprefix=wineprefix)
		self.protocol = self.paths._discover(self.server_name, self.server_ip, protocol)

		# default cache
		self.cache = cache.CacheMgr(self)

		# shared resource cache
		self.rescache = rescache.ResourceCache(self.paths.root, self.paths.sharedcache)

		self.cfg = self.cache.getconfigmgr(self)
		__builtin__.cfg = self.cfg

		# hack to make blue.ResFile() work. This obviously means that
		# when using multiple EVE versions, only the latest will be accessible
		# in that manner.
		global ResFile
		ResFile = lambda: _ResFile(self.rescache)

	def RemoteSvc(self, service):
		"""Creates a wrapper through which offline remote service methods can be called"""
		return _RemoteSvcWrap(self, service)

	# --- custom additions ---

	def ResFile(self):
		return _ResFile(self.rescache)

	def getcachemgr(self):
		"""Return CacheMgr instance through which this EVE's cache can be manually accessed"""
		return self.cache

	def getconfigmgr(self):
		"""Return ConfigMgr instance through which this EVE's bulkdata can be accessed"""
		return self.cfg

	def readstuff(self, name):
		"""Reads specified file in the virtual filesystem"""
		f = _ResFile(self.rescache)
		f.Open(name)
		return f.read()




def _readstringstable():
	from . import strings

	marshal._stringtable[:] = strings.stringTable
	#marshal._stringtable_rev.clear()

	#c = 1
	#for line in strings.stringsTable:
	#	marshal._stringtable_rev[line] = c
	#	c+=1




def _find_global(module, name):
	# locates a global. used by marshal.Load and integrated unpickler

	# compatibility
	if module in ("util", "utillib") and name == "KeyVal":
		return KeyVal
	try:
		m = __import__(module, globals(), locals(), (), -1)
	except ImportError:
		raise RuntimeError("Unable to locate object: " + module + "." + name + " (import failed)")

	try:
		return getattr(m, name)
	except AttributeError:
		raise RuntimeError("Unable to locate object: " + module + "." + name + " (not in module)")


def _debug(*args):
	print >>sys.stderr, args[0].Keys(), args


# __str__ function for DBRow objects. This is done in python because it would
# take considerably more effort to implement in C. It's not the most efficient
# way to display DBRows, but quite useful for debugging or inspection.
_fmt = u"%s:%s".__mod__
def dbrow_str(row):
	return "DBRow(" + ','.join(map(_fmt, zip(row.__keys__, row))) + ")"
_blue.dbrow_str = dbrow_str


# set the helper functions in the marshaller and init strings table
marshal._set_find_global_func(_find_global)
marshal._set_debug_func(_debug)
_readstringstable()

# hack to make CCP zip libs accept our not-exactly-the-same environment
sys.modules["blue"] = sys.modules["reverence.blue"]

# and this one to make CCP's FSD loader import pyFSD succesfully
sys.modules["pyFSD"] = pyFSD

__builtin__.boot = boot

