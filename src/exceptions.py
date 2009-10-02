"""CCP Exception containers

This code is free software; you can redistribute it and/or modify
it under the terms of the BSD license (see the file LICENSE.txt
included with the distribution).

Parts of code inspired by or based on EVE Online, with permission from CCP.
"""

import types

from . import _blue as blue


class UserError(StandardError):
	__guid__ = 'exceptions.UserError'

	def __init__(self, msg=None, *args):
		if type(msg) == types.InstanceType and msg.__class__ == UserError:
			self.msg = msg.msg
			self.dict = msg.dict
			self.args = (self.msg, self.dict)
			return

		if type(msg) not in [types.StringType, types.NoneType]:
			raise RuntimeError("Invalid argument, msg must be a string", msg)

		self.msg = msg
		if len(args) and type(args[0]) == dict:
			self.dict = args[0]
			self.args = (self.msg, self.dict)
		else:
			self.dict = None
			self.args = (self.msg,) + args


	def __str__(self):
		try:
			msg = cfg.GetMessage(self.msg, self.dict)
			return "[%s] %s - %s" % (msg.type, msg.title, msg.text)
		except:
			return "User error, msg=%s, dict=%s" % (self.msg, self.dict)


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




