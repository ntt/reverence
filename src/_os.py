"""Miscellaneous time functions for blue module.

Copyright (c) 2003-2010 Jamie "Entity" van den Berge <jamie@hlekkir.com>

This code is free software; you can redistribute it and/or modify
it under the terms of the BSD license (see the file LICENSE.txt
included with the distribution).
"""

from time import time, gmtime
import operator

_offset = 0L

epoch_offset = 116444736000000000L

def GetTime():
	return long((time() * 10000000L) + epoch_offset) - _offset

def FileTimeToSystemTime(t):
    return (t-epoch_offset) / 10000000L

def SyncTime(list):
	global _offset
	_offset = 0
	deltas = [(localTime-remoteTime) for localTime, remoteTime in list]
	_offset = long(reduce(operator.add, deltas) / len(deltas))

def GetTimeParts(date):
	assert date >= epoch_offset
	date -= epoch_offset
	# date==0 should yield [1970, 1, 4, 1, 0, 0, 0, 0]
	seconds, ms = divmod(date/10000, 1000)
	s = gmtime(seconds)
	return [s.tm_year, s.tm_mon, s.tm_wday+1, s.tm_mday, s.tm_hour, s.tm_min, s.tm_sec, int(ms)]


