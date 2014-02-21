import types

from reverence.carbon.common.script.net.GPSExceptions import *

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

		self.msg = msg or "<NO MESSAGE>"
		if len(args) and type(args[0]) == dict:
			self.dict = args[0]
			self.args = (self.msg or self.dict)
		else:
			self.dict = None
			self.args = (self.msg,) + args


	def __str__(self):
		try:
			msg = cfg.GetMessage(self.msg, self.dict)
			return "[%s] %s - %s" % (msg.type, msg.title, msg.text)
		except:
			return "User error, msg=%s, dict=%s" % (self.msg, self.dict)
