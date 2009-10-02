# Implant summary HTML dump - by Entity
# Spits out neat page for the EVE IGB showing implant hardwirings.
#
# usage: python implants.py >implants.html
#
# This script is freeware. Do whatever you want with it
# Disclaimer: Use at your own risk

evePath = "E:/EVE"

import sys

from reverence import blue, const
from collections import defaultdict

eve = blue.EVE(evePath)
cfg = eve.getconfigmgr()

cats = defaultdict(list)

ignoreGroups = (300, const.groupBooster)

for rec in cfg.invtypes:
	g = rec.Group()
	if g.categoryID == const.categoryImplant and rec.groupID not in ignoreGroups:
		slot = rec.GetTypeAttribute(const.attributeImplantness, 0)
		if slot >= 6 and slot <= 10:
			if rec.name.endswith("I"):
				continue
			if "test " in rec.description.lower():
				continue
			l = cats[g.id].append((slot, rec.name, rec))

print "<html><body>"
print "<H1><u>Entity's Nifty Implant Lookup Page</u></H1><br>"

def mangle(s, c):
	return s\
	.replace("0", "%")\
	.replace("1", "%")\
	.replace("2", "%")\
	.replace("3", "%")\
	.replace("4", "%")\
	.replace("5", "%")\
	.replace("6", "%")\
	.replace("7", "%")\
	.replace("8", "%")\
	.replace("9", "%")\
	.replace("%%", "%")\
	.replace("%%", "%")\
	.replace("%", c)


def sortkey(s):
	t = mangle(s[1], "%04d")
	if "%" in t:
		return (s[0], t % int(filter("0123456789".__contains__, s[1])))
	return s

def desc(rec, fltr=False):
	d = rec.description
	i = d.rfind("%")
	if i == -1:
		i = d.rfind("0", 0, i)

	if i > -1:
		i = d.rfind(".", 0, i)

	if i > -1:
		d = d[i+1:].strip()

	if fltr:
		for i in range(10):
			d = d.replace(str(i), "x")
		for s in ["x.x ", "+x% ", " x ", "-x%", "x%"]:
			d = d.replace(s, "")

	return d.strip().capitalize()


for groupID in sorted(cats, key=lambda id: cfg.invgroups.Get(id)):
	print "<h2>%s</h2>" % cfg.invgroups.Get(groupID).groupName
	print "<table>"

	last = -1
	lastPrefix = None
	models = []

	all = sorted(cats[groupID], key=sortkey)
	for slot, name, rec in all + [all[0]]:

		prefix = mangle(name, "")

		if lastPrefix and ((lastPrefix != prefix) or (last != -1 and last != slot)):
			models.reverse()

			if models[0].name[-2] != " ":
				print "<tr><td>%d</td><td><b>" % last
				print '<a href="showinfo:%d">%s</a>' % (models[0].typeID, models[0].name),
				if len(models)>1:
					links = [('<a href="showinfo:%d">%s</a>' % (rec2.typeID, rec2.name.rsplit(" ", 1)[1])) for rec2 in models[1:]]
					print " / " + " / ".join(links)

				print "</b><br>"

				print desc(models[0], len(models)>1)

				print "</td></tr>"


			models = []

		models.append(rec)

		if slot != last and last != -1:
			print "<tr><td><br></td><td><br></td></tr>"
		last = slot

		lastPrefix = prefix

	print "<tr><td><br></td><td><br></td></tr>"

	print "</table>"

print "</body></html>"
