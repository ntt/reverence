class CIndexedRowset(dict):
	__guid__ = "dbutil.CIndexedRowset"
    
	def __init__(self, header, columnName):
		self.header = header
		self.columnName = columnName


class CFilterRowset(dict):
	__guid__ = "dbutil.CFilterRowset"

	def __setstate__(self, data):
		self.__dict__.update(data)  # header and columnName

	def __getstate__(self):
		return {"header": self.header, "columnName": self.columnName}


class CRowset(list):
	__guid__ = "dbutil.CRowset"
	__passbyvalue__	 = 1
	
	def __init__(self, header, rows):
		list.__init__(self, rows)
		self.header = header

	def Sort(self, columnName, caseInsensitive = False):
		ix = self.header.Keys().index(columnName)
		if caseInsensitive:
			self.sort(key=lambda x: x[ix].upper())
		else:			
			self.sort(key=lambda x: x[ix])

	def Index(self, columnName):
		d = CIndexedRowset(self.header, columnName)

		if "." in columnName:		
			keys = columnName.split(".")
			c = 0

			for row in self:
				combinedKey = []
				for key in keys:
					combinedKey.append(row[key])
				d[tuple(combinedKey)] = row
	
			return d
		else:
			pass

	def Filter(self, columnName, indexName=None):
		fr = CFilterRowset(self.header, columnName)

		c = 0
		keyIdx = fr.header.Keys().index(columnName)
		_get = dict.get
		if indexName is None:
			for row in self:
				key = row[keyIdx]
				grp = _get(fr, key)
				if grp is None:
					fr[key] = [row]
				else:
					grp.append(row)
		else:
			key2Idx = fr.header.Keys().index(indexName)
			for row in self:
				key = row[keyIdx]
				key2 = row[key2Idx]
				if key not in fr:
					fr[key] = {}
				fr[key][key2] = row

		return  fr

