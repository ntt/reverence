"""Container classes for DBRow/DBRowset

Copyright (c) 2003-2013 Jamie "Entity" van den Berge <jamie@hlekkir.com>

This code is free software; you can redistribute it and/or modify
it under the terms of the BSD license (see the file LICENSE.txt
included with the distribution).

Part of this code is inspired by or based on EVE Online.
Used with permission from CCP.
"""

from reverence import _blue as blue

from reverence.carbon.common.script.sys.row import Row

def RowsInit(rows, columns):
	header = None
	if type(rows) is types.TupleType:
		header = rows[0]
		rows = rows[1]

	if rows:
		first = rows[0]
		if type(first) != blue.DBRow:
			raise AttributeError('Not DBRow. Initialization requires a non-empty list of DBRows')
		header = first.__header__
	elif header:
		if type(header) != blue.DBRowDescriptor:
			raise AttributeError('expected (DBRowDesciptor, [])')
	if header:
		columns = header.Keys()
	return rows, columns, header


class RowDict(dict):
	__guid__ = 'dbutil.RowDict'
	__passbyvalue__ = 1
	slots = ["columns", "header", "key"]

	def __init__(self, rowList, key, columns = None):
		dict.__init__(self)

		rows, self.columns, self.header = RowsInit(rowList, columns)

		if key not in self.columns:
			raise AttributeError('Indexing key not found in row')

		self.key = key
		for row in rows:
			self[row[key]] = row


	def ReIndex(self, key):
		if key not in self.columns:
			raise AttributeError('Indexing key not found in columns')

		vals = self.values()

		self.clear()

		self.key = key
		for row in vals:
			self[row[self.key]] = row

	def Add(self, row):

		if type(row) != blue.DBRow:
			raise AttributeError('Not DBRow')

		if row.__keys__ != self.columns:
			raise ValueError('Incompatible rows')

		if self.header is None:
			self.header = row.__header__

		self[row[self.key]] = row


class RowList(list):
	__guid__ = 'dbutil.RowList'
	__passbyvalue__ = 1
	slots = ["header", "columns"]

	def __init__(self, rowList, columns = None):
		list.__init__(self)
		rows, self.columns, self.header = RowsInit(rowList, columns)
		self[:] = rows

	def append(self, row):
		if not isinstance(row, blue.DBRow):
			raise ValueError('Not DBRow: %s' % row )

		if row.__header__ is not self.header:
			raise ValueError('Incompatible headers')

		if self.header is None:
			self.header = row.__header__

		list.append(self, row)


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



__all__ = [
	"RowDict",
	"RowList",
	"Rowset",
	"IndexedRowLists",
	"IndexRowset",
	"FilterRowset",
]

