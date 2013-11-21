"""Data container classes, text formatting and item type checking functions

Copyright (c) 2003-2013 Jamie "Entity" van den Berge <jamie@hlekkir.com>

This code is free software; you can redistribute it and/or modify
it under the terms of the BSD license (see the file LICENSE.txt
included with the distribution).

Parts of code inspired by or based on EVE Online, with permission from CCP.
"""

import __builtin__
import types
import os
import time
import math
import cPickle
import _weakref

from . import _os


DECIMAL = "."  # decimal point for currency. 
DIGIT = ","	# thousands separator

#-----------------------------------------------------------------------------
# Data containers
#-----------------------------------------------------------------------------

class Object:
	pass


#-----------------------------------------------------------------------------
# Formatting and stuff
#-----------------------------------------------------------------------------

def FmtDate(blueTime):
	sec = _os.FileTimeToSystemTime(blueTime)
	return time.strftime("%Y.%m.%d %H:%M:%S", time.gmtime(sec))

def FmtTimeInterval(interval, breakAt=None):
	if interval < 10000L:
		return "a short amount of time"

	year, month, wd, day, hour, min, sec, ms = _os.GetTimeParts(interval + _os.epoch_offset)
	year -= 1970
	month -= 1
	day -= 1
	items = []

	_s = ['','s']

	while 1:

		if year:
			items.append(str(year) + " year" + _s[year>1])
		if breakAt == "year":
			break

		if month:
			items.append(str(month) + " month" + _s[month>1])
		if breakAt == "month":
			break

		if day:
			items.append(str(day) + " day" + _s[day>1])
		if breakAt == "day":
			break

		if hour:
			items.append(str(hour) + " hour" + _s[hour>1])
		if breakAt == "hour":
			break

		if min:
			items.append(str(min) + " minute" + _s[min>1])
		if breakAt == "min":
			break

		if sec:
			items.append(str(sec) + " second" + _s[sec>1])
		if breakAt == "sec":
			break

		if ms:
			items.append(str(ms) + " millisecond" + _s[ms>1])
		break

	if items:
		if len(items) == 1:
			return items[0]
		else:
			lastItem = items.pop()
			return ", ".join(items) + " and " + lastItem
	else:
		if breakAt == "sec":
			return "less than a second"
		elif breakAt == "min":
			return "less than a minute"
		else:
			return "less than a " + breakAt


# todo, translation stuff.
_fmtOrder = {
	3: ("K", (" thousand", " thousands")),
	6: ("M", (" million" , " millions")),
	9: ("B", (" billion" , " billions")),
   12: ("T", (" trillion", " trillions")),
}
	

def FmtAmt(amount, fmt="ln", showFraction=0, fillWithZero=0):
	if amount == None:
		amount = 0
	else:
		try:
			long(amount)
		except:
			raise RuntimeError("AmountMustBeInteger", (amount))

	sign = "-" if float(amount) < 0.0 else ""
	amount = abs(amount)

	if fmt[0] == "l":
		amount, fraction = str(float(amount)).split(".")
		amount = amount.rjust((len(amount)+2)//3*3)
		amount = DIGIT.join((amount[x:x+3] for x in xrange(0, len(amount), 3))).strip()
		if fillWithZero:
			fraction = fraction.ljust(showFraction, "0")
		fraction = fraction[:showFraction]
		if fraction:
			amount += DECIMAL + fraction

	elif fmt[0] == "s":
		if amount >= 10000:
			order = min(len(str(long(amount)))//3*3, 12)
			symbol, canonical = _fmtOrder[order]
			amount = TruncateAmt(amount, 10**order) + (symbol if (fmt[1]!="l") else canonical[str(amount)[0]!="1"])

	else:
		amount = long(amount)

	return sign + str(amount)


def TruncateAmt(val, unit):
	rest = (val % unit) / (unit/100L)
	ret = str(val / unit)
	if rest > 0:
		ret += DECIMAL + ('%02d' % rest).rstrip("0")
	return ret

def TruncateDecimals(s, maxdecimals):
	ix = s.rfind(DECIMAL)
	if ix == -1 or maxdecimals is None:
		return s
	return s[:ix+max(0, maxdecimals)+1]


def FmtDist(dist, maxdecimals=3):
	dist = max(0, dist)
	if dist < 1.0:
		return TruncateDecimals(str(dist)[:5], maxdecimals) + " m"
	if dist < 10000.0:
		return TruncateDecimals(FmtAmt(long(dist)), maxdecimals) + " m"
	elif dist < 10000000000.0:
		return TruncateDecimals(FmtAmt(long(dist/1000.0)), maxdecimals) + " km"
	else:
		dist /= 149597870700.0
		if dist > 1000.0:
			return TruncateDecimals(FmtAmt(long(dist)), maxdecimals) + " AU"
		else:
			return TruncateDecimals((str(dist)[:5]).replace(".", DECIMAL), maxdecimals) + " AU"


def FmtISK(isk, showAurarAlways=1, sign=" ISK"):
	if not showAurarAlways:
		if long(isk) == isk:
			return FmtAmt(long(isk)) + sign
	return FmtAmt(round(isk, 2), showFraction=2, fillWithZero=True) + sign


_roman = {}
class preproman:
	for i in xrange(1, 40):
		n = i
		result = ""
		for (numeral, length, integer,) in (('X', 1, 10),('IX', 2, 9),('V', 1, 5),('IV', 2, 4),('I', 1, 1)):
			while i >= integer:
				result += numeral
				i -= integer
		_roman[n] = result
del preproman

def IntToRoman(n):
	return _roman.get(int(n), str(n))



#-----------------------------------------------------------------------------
# Type checking functions
#-----------------------------------------------------------------------------

def IsSystem(ownerID):
	return ownerID <= 10000

def IsNPC(ownerID):
	return (ownerID < 100000000) and (ownerID > 10000)

def IsSystemOrNPC(ownerID):
	return (ownerID < 100000000)

def IsFaction(ownerID):
	if (ownerID >= 500000) and (ownerID < 1000000):
		return 1
	else:
		return 0

def IsCorporation(ownerID):
	if (ownerID >= 1000000) and (ownerID < 2000000):
		return 1
	elif ownerID < 100000000:
		return 0
	else:
		return cfg.eveowners.Get(ownerID).IsCorporation()

def IsCharacter(ownerID):
	if (ownerID >= 3000000) and (ownerID < 4000000):
		return 1
	elif ownerID < 100000000:
		return 0
	else:
		return cfg.eveowners.Get(ownerID).IsCharacter()

def IsOwner(ownerID, fetch=0):
	if ((ownerID >=  500000) and (ownerID < 1000000))\
	or ((ownerID >= 1000000) and (ownerID < 2000000))\
	or ((ownerID >= 3000000) and (ownerID < 4000000)):
		return 1
	if IsNPC(ownerID):
		return 0
	if fetch:
		return cfg.eveowners.Get(ownerID).groupID in (const.groupCharacter, const.groupCorporation)
	return 0

def IsAlliance(ownerID):
	if ownerID < 100000000:
		return 0
	else:
		return cfg.eveowners.Get(ownerID).IsAlliance()

def IsRegion(itemID):
	return (itemID >= 10000000) and (itemID < 20000000)

def IsConstellation(itemID):
	return (itemID >= 20000000) and (itemID < 30000000)

def IsSolarSystem(itemID):
	return (itemID >= 30000000) and (itemID < 40000000)

def IsWormholeSystem(itemID):
	return (itemID >= const.mapWormholeSystemMin) and (itemID < const.mapWormholeSystemMax)
	
def IsWormholeConstellation(constellationID):
	return (constellationID >= const.mapWormholeConstellationMin) and (constellationID < const.mapWormholeConstellationMax)
	
def IsWormholeRegion(regionID):
	return (regionID >= const.mapWormholeRegionMin) and (regionID < const.mapWormholeRegionMax)

def IsUniverseCelestial(itemID):
	return (itemID >= const.minUniverseCelestial) and (itemID <= const.maxUniverseCelestial)
	
def IsStargate(itemID):
	return (itemID >= 50000000) and (itemID < 60000000)

def IsStation(itemID):
	return (itemID >= 60000000) and (itemID < 64000000)

def IsOutpost(itemID):
	return (itemID >= 61000000) and (itemID < 64000000)

def IsTrading(itemID):
	return (itemID >= 64000000) and (itemID < 66000000)

def IsOfficeFolder(itemID):
	return (itemID >= 66000000) and (itemID < 68000000)

def IsFactoryFolder(itemID):
	return (itemID >= 68000000) and (itemID < 70000000)

def IsUniverseAsteroid(itemID):
	return (itemID >= 70000000) and (itemID < 80000000)

def IsJunkLocation(locationID):
	if locationID >= 2000:
		return 0
	elif locationID in [6, 8, 10, 23, 25]:
		return 1
	elif locationID > 1000 and locationID < 2000:
		return 1
	else:
		return 0

def IsControlBunker(itemID):
	return (itemID >= 80000000) and (itemID < 80100000)

def IsPlayerItem(itemID):
	return (itemID >= const.minPlayerItem and itemID < const.maxPlayerItem)

def IsNewbieSystem(itemID):
	default = [
		30002547, 30001392, 30002715,
		30003489, 30005305, 30004971,
		30001672, 30002505, 30000141,
		30003410, 30005042, 30001407,
	]

#	   
#	optional = [
#		30001722, 30002518, 30003388, 30003524,
#		30005015, 30010141, 30011392, 30011407,
#		30011672, 30012505, 30012547, 30012715,
#		30013410, 30013489, 30014971, 30015042,
#		30015305, 30020141, 30021392, 30021407,
#		30021672, 30022505, 30022547, 30022715,
#		30023410, 30023489, 30024971, 30025042,
#		30025305, 30030141, 30031392, 30031407,
#		30031672, 30032505, 30032547, 30032715,
#		30033410, 30033489, 30034971, 30035042,
#		30035305, 30040141, 30041392, 30041407,
#		30041672, 30042505, 30042547, 30042715,
#		30043410, 30043489, 30044971, 30045042,
#		30045305,
#	]
#
#	if boot.region == "optic":
#		return itemID in (default + optional)

	return itemID in default

