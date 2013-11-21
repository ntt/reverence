"""Container classes for DBRow/DBRowset

Copyright (c) 2003-2013 Jamie "Entity" van den Berge <jamie@hlekkir.com>

This code is free software; you can redistribute it and/or modify
it under the terms of the BSD license (see the file LICENSE.txt
included with the distribution).

Part of this code is inspired by or based on EVE Online.
Used with permission from CCP.
"""

class Row:
	__guid__ = "util.Row"
	__passbyvalue__ = 1

	def __init__(self, header=None, line=None, cfgInstance=None):
		self.header = header or []
		self.line = line or []
		self.cfg = cfgInstance

	def __ne__(self, other):
		return self.__cmp__(other)

	def __eq__(self, other):
		return self.__cmp__(other) == 0

	def __cmp__(self, other):
		if not isinstance(other, Row):
			raise TypeError("Incompatible comparison type")
		return cmp(self.header, other.header) or cmp(self.line, other.line)

	def __str__(self):
		if self.__class__ is Row:
			# bare row class, use shortcut
			return "Row(" + ','.join(map(lambda k, v: "%s:%s" % (unicode(k), unicode(v)), self.header, self.line)) + ")"
		else:
			# assume it has custom attribute handling (e.g. invtypes)
			return "Row(" + ','.join(map(lambda k, v: "%s:%s" % (unicode(k), unicode(v)), self.header, map(self.__getattr__, self.header))) + ")"

	__repr__ = __str__

	def __nonzero__(self):
		return True

	def __getattr__(self, this):
		try:
			return self.line[self.header.index(this)]
		except ValueError:
			raise AttributeError, this

	def __getitem__(self, this):
		return self.line[self.header.index(this)]


