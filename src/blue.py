"""Main interface to all the goodies.

Copyright (c) 2003-2009 Jamie "Entity" van den Berge <jamie@hlekkir.com>

This code is free software; you can redistribute it and/or modify
it under the terms of the BSD license (see the file LICENSE.txt
included with the distribution).
"""

from ._blue import marshal, DBRow, DBRowDescriptor
from . import cache, _os as os

try:
	from . import marshal_writer
	marshal.Save = marshal_writer.Save
	del marshal_writer
except ImportError:
	def Oops(*arg, **kw):
		raise RuntimeError("Save function requires marshal_writer module")
	marshal.Save = Oops

try:
	from . import _dotblue
except ImportError:
	_dotblue = None


import sys
from time import sleep as _sleep

class pyos:
	class synchro:
		@staticmethod
		def Sleep(msec):
			_sleep(msec / 1000.0)


class _ResFile(object):
	# read-only resource file handler.

	def __init__(self, rot):
		self.fh = None
		self.rot = rot

	def Open(self, filename):
		self.fh = None
		if filename.startswith("res:"):
			# we gotta have to open a .stuff file...
			self.fh = self.rot.efs.open("res/" + filename[5:])
		elif filename.startswith("cache:"):
			self.fh = open(os.path.join(self.eve.root, "cache", filename[7:]), "rb") 
		else:
			self.fh = open(filename, "rb")
		return self.fh

	def Read(self, *args):
		return self.fh.read(*args)

	def Close(self):
		if fh:
			fh.close()
			fh = None

	# ---- custom additions ----

	def read(self, *args):
		return self.fh.read(*args)

	def readline(self):
		return self.fh.readline()


class _Rot(object):

	def __init__(self, eve):
		from . import embedfs
		self.eve = eve
		self.efs = embedfs.EmbedFSDirectory(eve.root)

	def GetCopy(self, filename):
		if _dotblue:
			f = _ResFile(self)
			f.Open(filename)
			return _dotblue.Load(f.fh)
		else:
			raise RuntimeError("GetCopy method requires _dotblue module")


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
	readstuff(name) - reads the specified file from EVE's virtual file system.
	RemoteSvc(service) - creates offline RemoteSvc wrapper for given service.
	"""

	def __init__(self, root, server="Tranquility", machoVersion=-1, languageID="EN", cachepath=None, compatibility=False):
		self.root = root
		self.server = server
		self.rot = _Rot(self)
		self.languageID = languageID

		from . import infosvc

		# default cache
		self.cache = cache.CacheMgr(self.root, self.server, machoVersion, cachepath)
		self.machoVersion = self.cache.machoVersion

		self.cfg = self.cache.GetConfigMgr(compatibility=compatibility)

		# hack to make blue.ResFile() work. This obviously means that
		# when using multiple EVE versions, only the latest will be accessible
		# in that manner.
		global ResFile
		ResFile = lambda: _ResFile(self.rot)

	def RemoteSvc(self, service):
		"""Creates a wrapper through which offline remote service methods can be called"""
		return RemoteSvcWrap(self, service)

	# --- custom additions ---

	def ResFile(self):
		return _ResFile(self.rot)

	def getcachemgr(self):
		"""Return CacheMgr instance through which this EVE's cache can be manually accessed"""
		return self.cache

	def getconfigmgr(self):
		"""Return ConfigMgr instance through which this EVE's bulkdata can be accessed"""
		return self.cfg

	def readstuff(self, name):
		"""Reads specified file in the virtual filesystem"""
		f = _ResFile(self.rot)
		f.Open(name)
		return f.read()




def _readstringstable():
	from os.path import join, dirname

	marshal._stringtable[:] = [None]
	#marshal._stringtable_rev.clear()

	f = open(join(dirname(__file__), "strings.txt"), "r")
	c = 1
	for line in f:
		line = line.replace("\r","\n").strip('\n')
		marshal._stringtable.append(line)
		#marshal._stringtable_rev[line] = c
		c+=1
	f.close()


def _find_global(module, name):
	# locates a global. used by marshal.Load and integrated unpickler
	try:
		m = __import__(module, globals(), locals(), (), -1)
	except ImportError:
		raise RuntimeError("Unable to locate object: " + module + "." + name + " (import failed)")

	try:
		return getattr(m, name)
	except AttributeError:
		raise RuntimeError("Unable to locate object: " + module + "." + name + " (not in module)")


def _debug(text):
	print >>sys.stderr, text


# set the helper functions in the marshaller and init strings table
marshal._set_find_global_func(_find_global)
marshal._set_debug_func(_debug)
_readstringstable()



__all__ = ["EVE", "marshal", "os", "pyos", "DBRow", "DBRowDescriptor"]

