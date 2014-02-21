"""CCP Exception containers

This code is free software; you can redistribute it and/or modify
it under the terms of the BSD license (see the file LICENSE.txt
included with the distribution).

Parts of code inspired by or based on EVE Online, with permission from CCP.
"""

import types

from reverence import _blue as blue

class GPSException(StandardError):
	__guid__ = 'exceptions.GPSException'
	def __init__(self, reason):
		self.reason = reason

	def __str__(self):
		return repr(self)

	def __repr__(self):
		return "<%s: reason=%s>" % (self.__class__.__name__, self.reason)


class GPSTransportClosed(GPSException):
	__guid__ = 'exceptions.GPSTransportClosed'
	def __init__(self, reason):
		bootver = reason.rfind("bootver=")
		if bootver > 0:
			self.version, self.build, self.codename = blue.marshal.Load(reason[bootver+8:].decode("hex"))
			reason = reason[:bootver]
		GPSException.__init__(self,reason)


class GPSBadAddress(GPSException):
	__guid__ = 'exceptions.GPSBadAddress'
	def __init__(self, reason):
		GPSException.__init__(self, reason)


class GPSAddressOccupied(GPSException):
	__guid__ = 'exceptions.GPSAddressOccupied'
	def __init__(self, reason):
		GPSException.__init__(self, reason)

__all__ = [
	"GPSException",
	"GPSTransportClosed",
	"GPSBadAddress",
	"GPSAddressOccupied",
]

