"""Odyssey pyFSD module

- implements the functionality of bin\pyFSD.pyd in the EVE install.

Copyright (c) 2003-2013 Jamie "Entity" van den Berge <jamie@hlekkir.com>

This code is free software; you can redistribute it and/or modify
it under the terms of the BSD license (see the file LICENSE.txt
included with the distribution).
"""

try:
	# Try importing the uber efficient keymap class
	from reverence import _pyFSD
	FsdUnsignedIntegerKeyMap = _pyFSD.FsdUnsignedIntegerKeyMap

except ImportError:
	# Crappy pure python fallback keymap class.
	# Note that this thing uses a great deal of ram to get
	# performance similar to the C-based class.
	import struct

	_unpack_from = struct.Struct("<III").unpack_from

	class FsdUnsignedIntegerKeyMap(dict):

		def Initialize(self, data):
			length = struct.unpack_from("<I", data, 0)[0]
			for offset in xrange(4, 4+length*12, 12):
				key, off, value = _unpack_from(data, offset)
				self[key] = (off, value)
		length = dict.__len__
		Get = dict.get




