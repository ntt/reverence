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


class Rowset:
	__passbyvalue__ = 1
	__guid__ = "util.Rowset"

	cfg = None

	def __init__(self, header=None, lines=None, rowclass=Row, cfgInstance=None):
		self.header = header or []
		self.lines = lines or []
		self.RowClass = rowclass
		self.cfg = cfgInstance

	def __nonzero__(self):
		return True

	def __getitem__(self, index):
		if type(index) is slice:
			return Rowset(self.header, self.lines[index], self.RowClass, cfgInstance=self.cfg)
		return self.RowClass(self.header, self.lines[index], cfgInstance=self.cfg)

	def __len__(self):
		return len(self.lines)

	def sort(self, *args, **kw):
		self.lines.sort(*args, **kw)

	def GroupedBy(self, column):
		"""Returns new FilterRowset grouped on specified column."""
		return FilterRowset(self.header, self.lines, idName=column, RowClass=self.RowClass, cfgInstance=self.cfg)

	def IndexedBy(self, column):
		"""Returns new IndexRowset indexed on specified column."""
		return IndexRowset(self.header, self.lines, key=column, RowClass=self.RowClass, cfgInstance=self.cfg)

	def SortBy(self, column, reverse=False):
		"""Sorts the rowset in place."""
		ix = self.header.index(column)
		self.sort(key=lambda e: e[ix], reverse=reverse)

	def SortedBy(self, column, reverse=False):
		"""Returns a sorted shallow copy of the rowset."""
		rs = Rowset(header=self.header, lines=self.lines[:], rowclass=self.RowClass, cfgInstance=self.cfg)
		rs.SortBy(column, reverse)
		return rs

	def Select(self, *columns, **options):
		if len(columns) == 1:
			i = self.header.index(columns[0])
			if options.get("line", False):
				for line in self.lines:
					yield (line, line[i])
			else:
				for line in self.lines:
					yield line[i]
		else:
			i = map(self.header.index, columns)
			if options.get("line", False):
				for line in self.lines:
					yield line, [line[x] for x in i]
			else:
				for line in self.lines:
					yield [line[x] for x in i]


	def Sort(self, column, asc=1):
		"""Provided for compatibility. do not use in new code."""
		return self.SortedBy(column, not asc)

	def Index(self, column):
		"""Provided for compatibility. do not use in new code."""
		return self.IndexedBy(column)

	def Filter(self, column):
		"""Provided for compatibility. do not use in new code."""
		return self.GroupedBy(column)


class IndexRowset(Rowset):
	__guid__ = "util.IndexRowset"

	def __init__(self, header=None, lines=None, key=None, RowClass=Row, dict=None, cfgInstance=None, fetcher=None):
		if not key:
			raise ValueError, "Crap key"
		ki = header.index(key)

		Rowset.__init__(self, header, lines, RowClass, cfgInstance=cfgInstance)
		if dict is None:
			self.items = d = {}
			self.key = ki
			for line in self.lines:
				d[line[ki]] = line
		else:
			self.items = dict

		self._fetcher = fetcher

	def has_key(self, key):
		return key in self.items

	def __contains__(self, key):
		return key in self.items

	def values(self):
		return self  #Rowset(self.header,self.items.values(),self.RowClass)

	def itervalues(self):
		return self

	def Get(self, *args):
		row = self.items.get(*args)
		if row:
			return self.RowClass(self.header, row, cfgInstance=self.cfg)
		return None

	def GetIfExists(self, *args):
		row = self.items.get(args[0], None)
		if row is None:
			return None
		return self.RowClass(self.header, row, cfgInstance=self.cfg)

	def SortedBy(self, column, reverse=False):
		"""Returns a sorted shallow copy of the rowset."""
		rs = self.IndexedBy(column)
		rs.SortBy(column, reverse)
		return rs

	def Prime(self, keys):
		wanted = set(keys) - set(self.items)
		lines = self._fetcher(wanted)
		self.lines.extend(lines)
		d = self.items
		ki = self.key
		for line in lines:
			d[line[ki]] = line

	get = Get  # compatibility


class FilterRowset:
	__guid__ = "util.FilterRowset"
	__passbyvalue__ = 1

	RowClass = Row

	cfg = None

	def __init__(self,header=None, li=None, idName=None, RowClass=Row, idName2=None, dict=None, cfgInstance=None):
		self.cfg = cfgInstance

		self.RowClass = RowClass

		if dict is not None:
			items = dict
		elif header is not None:
			items = {}
			_get = items.get
			idfield = header.index(idName)
			if idName2:
				idfield2 = header.index(idName2)
				for i in li:
					id = i[idfield]
					_items = _get(id)
					if _items is None:
						items[id] = {i[idfield2]:i}
					else:
						_items[i[idfield2]] = i
			else:
				for i in li:
					id = i[idfield]
					_items = _get(id)
					if _items is None:
						items[id] = [i]
					else:
						_items.append(i)
		else:
			items = {}

		self.items = items
		self.header = header
		self.idName = idName
		self.idName2 = idName2

	def Clone(self):
		return FilterRowset(copy.copy(self.header), None, self.idName, self.RowClass, self.idName2, dict=copy.deepcopy(self.items))

	def __contains__(self, key):
		return key in self.items

	def has_key(self, key):
		return key in self.items

	def get(self, key, val):
		try:
			return self[key]
		except:
			sys.exc_clear()
			return val

	def keys(self):
		return self.items.keys()

	def iterkeys(self):
		return self.items.iterkeys()

	def __getitem__(self, i):
		if self.idName2:
			return IndexRowset(self.header, None, self.idName2, self.RowClass, self.items.get(i, {}), cfgInstance=self.cfg)
		return Rowset(self.header, self.items.get(i, []), self.RowClass, cfgInstance=self.cfg)

	def __len__(self):
		return len(self.items)

	def Sort(self, colname):
		ret = Rowset(self.header, self.items.values(), self.RowClass)
		return ret.Sort(colname)

	def __iter__(self):
		return (self[key] for key in self.iterkeys())



class IndexedRowLists(dict):
	__guid__ = 'util.IndexedRowLists'
	__passbyvalue__ = 1
	__slots__ = ("header",)

	def __init__(self, rows=[], keys=None):
		if rows:
			self.header = rows[0].__header__.Keys()
		self.InsertMany(keys, rows)

	def Insert(self, keys, row):
		self.InsertMany(keys, [row])

	def InsertMany(self, keys, rows):
		rkeys = keys[1:]
		k = keys[0]
		_get = dict.get
		if rkeys:
			for row in rows:
				key = row[k]
				grp = _get(self, key)
				if grp is None:
					grp = self[key] = self.__class__()
				grp.InsertMany(rkeys, [row])
		else:
			for row in rows:
				key = row[k]
				grp = _get(self, key)
				if grp is None:
					self[key] = [row]
				else:
					grp.append(row)


	def __getitem__(self, key):
		return dict.get(self, key) or []


class IndexedRows(IndexedRowLists):
	__guid__ = 'util.IndexedRows'




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

