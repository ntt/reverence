#-----------------------------------------------------------------------------
# Magic Hat - Cache dumping utility by Entity
# Freeware, use at your own risk.
#-----------------------------------------------------------------------------
# Make your own EVE SQL or XML data dump!
#
# Usage:
#
# - Edit the MODE below to XML or SQL depending on what you want
# - Edit the path to the correct location
# - Edit the output path to where you want the dumped data
# - Run script.
#
# Note that the SQL dumps produced are fairly simple and do not include the
# tables.
#-----------------------------------------------------------------------------

# want XML or SQL?
MODE = "XML"

# where is EVE?
EVEPATH = "E:/EVE"

# where to output the dump?
OUTPATH = "N:/temp"

#-----------------------------------------------------------------------------

from reverence import blue
import os

MODE = MODE.upper()
if MODE not in ("SQL", "XML"):
	raise RuntimeError("Unknown Mode:", MODE)

eve = blue.EVE(EVEPATH)
c = eve.getcachemgr()

cachedObjects = c.LoadCacheFolder("BulkData")
cachedObjects2 = c.LoadCacheFolder("CachedObjects")

# bulkdata updates may exist in cache folder. do version check and
# update when necessary.
while cachedObjects2:
	objID, obj = cachedObjects2.popitem()
	if objID in cachedObjects:
		if obj.version < cachedObjects[objID].version:
			continue  # skip, the object is an older version
	cachedObjects[objID] = obj
	
cachedObjects.update()

#-----------------------------------------------------------------------------

def xmlstr(value):
	# returns string that is safe to use in XML
	t = type(value)
	if t in (list, tuple, dict):
		raise ValueError("Unsupported type")
	if t is str:
		return repr(value.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;').replace("'",'&apos;'))[1:-1]
	elif t is unicode:
		return repr(value.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;').replace("'",'&apos;'))[2:-1]
	elif t == float:
		return value
	return repr(value)

def sqlstr(x):
	t = type(x)
	if t in (list, tuple, dict):
		raise ValueError("Unsupported type")
	if t is unicode:
		return repr(x)[1:]
	if t is str:
		return repr(x)
	if t is bool:
		return repr(x).lower()
	else:
		r = str(x)
		r = r.replace("e+", "E").replace("e-", "E-")
		if r.endswith(".0"):
			r = r[:-2]
		if r == "None":
			return "null"
		return r

#-----------------------------------------------------------------------------

# see what we can pull out of the hat...
for obj in cachedObjects.itervalues():

	name = filter(lambda x: x not in "()'\" ", str(obj.objectID).replace(",",".").replace('u"', "").replace("u'", ""))
	item = name.split(".")[-1]
	if item.isdigit():
		# stuff ending in numbers is pretty much irrelevant.
		continue

	if item.startswith("Get"):
		item = item[3:]

	print name, "...", 

	thing = obj.GetObject()

	# try to get "universal" header and lines lists by checking what
	# type the object is and grabbing the needed bits.
	header = lines = None
	guid = getattr(thing, "__guid__", None)
	if guid:
		if guid.startswith("util.Row"):
			header, lines = thing.header, thing.lines
		elif guid.startswith("util.IndexRow"):
			header, lines = thing.header, thing.items.values()
		elif guid == "dbutil.CRowset":
			header, lines = thing.header, thing
		elif guid == "dbutil.CIndexedRowset":
			header, lines = thing.header, thing.values()
		elif guid == "util.FilterRowset":
			header = thing.header
			lines = []	
			for stuff in thing.items.itervalues():  # bad way to do this.
				lines += stuff
		else:
			print "UNSUPPORTED (%s)" % guid

	elif type(thing) == tuple:
		if len(thing) == 2:
			header, lines = thing

	elif type(thing) == list:
		row = thing[0]
		if hasattr(row, "__guid__"):
			if row.__guid__ == "blue.DBRow":
				header = row.__header__
				lines = thing
	else:
		print "UNKNOWN (%s)" % type(thing)
		continue

	if not header:
		print "NO HEADER (%s)" % type(thing)
		continue

	if type(header) is blue.DBRowDescriptor:
		header = header.Keys()

	f = []

	# create XML file and dump the lines.
	try:
		if MODE == "XML":
			f.append("<?xml version='1.0' encoding='utf-8'?>\r\n<data>")
			for line in lines:
				f.append("\t<%s>" % item)
				for key,value in zip(header, line):
					if type(key) == tuple:
						key = key[0]
					f.append("\t\t<%s>%s</%s>" % (key, xmlstr(value), key))
				f.append("\t</%s>" % item)
			f.append("</data>")

		elif MODE == "SQL":
			f.append("-- ObjectID: %s" % str(obj.objectID))
			f.append("")
			for line in lines:
				line = ','.join([sqlstr(x) for x in line])
				f.append("INSERT INTO %s (%s) VALUES(%s)" % (item, ','.join(header), line))

		# dump to file
		f2 = open( os.path.join(OUTPATH, name) + "." + MODE.lower(), "w")
		for line in f:
			print >>f2, line
		del f
		f2.close()

		print "OK"
	except:
		print "FAILED"



