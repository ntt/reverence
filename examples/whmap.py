#
# K and W space wormhole target class map renderer - by Entity
#
# Renders color-coded wormhole destination map of New Eden and Sleeper galaxy.
#
# Requires:
# - Python Imaging Library
# - Reverence
#
# This map render script is freeware. Do whatever you want with it
#
# Disclaimer: Use at your own risk
#

#-----------------------------------------------------------------------------
# Change the following settings to suit your needs:

EVEROOT = r"E:\EVE"
OUT = r"C:\whtcmap.png"

WIDTH = 1920
HEIGHT = 1200

MARGIN = 20

#-----------------------------------------------------------------------------

mapLeft = MARGIN
mapTop = MARGIN
mapWidth = (WIDTH/2)-(MARGIN*2)
mapHeight = (HEIGHT)-(MARGIN*2)

mapScaleFactor = min(mapWidth, mapHeight) / 2.0

print mapWidth, mapHeight

#-----------------------------------------------------------------------------
from PIL import Image, ImageDraw, ImageFont
from reverence import blue, const

import time

print "Setting up EVE resources..."

eve = blue.EVE(EVEROOT)
cfg = eve.getconfigmgr()

print "Loading map data..."

f = blue.ResFile()
f.Open("res:/UI/Shared/Maps/mapcache.dat")
mapcache = blue.marshal.Load(f.Read())


# first, separate the 2 galaxies...

print "Separating galaxies..."

class DecoDict(dict):
	pass

kspace = DecoDict()
kspace.name = "kspace"

wspace = DecoDict()
wspace.name = "wspace"

for system in mapcache["items"].itervalues():
	if system.item.typeID != const.typeSolarSystem:
		continue

	if str(system.item.itemID)[1] != "1":
		kspace[system.item.itemID] = system
	else:
		wspace[system.item.itemID] = system

print "- kspace has %d systems" % len(kspace)
print "- wspace has %d systems" % len(wspace)

# first, get galaxy widths of both galaxies!

print "Measuring coordinates..."

for galaxy in (kspace, wspace):
	xMin = zMin = None
	xMax = zMax = None
	for system in galaxy.itervalues():
		row = system.item
		xMin, xMax = min(row.x, xMin) if xMin else row.x, max(row.x, xMax) if xMax else row.x
		zMin, zMax = min(row.z, zMin) if zMin else row.z, max(row.z, zMax) if zMax else row.z

	galaxy.xMin, galaxy.xMax = xMin, xMax
	galaxy.zMin, galaxy.zMax = zMin, zMax

	galaxy.width = xMax - xMin
	galaxy.height = zMax - zMin

	print "- %s has dimensions (%s, %s)" % (galaxy.name, galaxy.width, galaxy.height)


frameWidth = max(kspace.width, wspace.width)
frameHeight = max(kspace.height, wspace.height)

# center the coordinates around 0,0

print "Transforming coordinates..."

for idx, galaxy in enumerate((kspace, wspace)):
	for system in galaxy.itervalues():
		# translate
		system.x = system.item.x - galaxy.xMin - (galaxy.width / 2.0)
		system.z = system.item.z - galaxy.zMin - (galaxy.height / 2.0)

		# normalize to -1 .. 1 range
		system.x /= frameWidth / 2.0
		system.z /= frameHeight / 2.0

		if max(abs(system.x), abs(system.z)) > 1:
			print system.x, system.z
			raise "FRACK"

		# scale
		system.x *= mapScaleFactor
		system.z *= mapScaleFactor

		# offset
		system.x += mapWidth / 2.0 + (idx * WIDTH * 0.5)
		system.z += mapHeight / 2.0

		system.coords = (system.x, system.z)


s = time.time()

print "Rendering map..."


#-----------------------------------------------------------------------------
# Init canvas
img = Image.new("RGB", (WIDTH, HEIGHT))
pix = img.load()
draw = ImageDraw.Draw(img)
font = ImageFont.truetype('cour.ttf', 13)


#-----------------------------------------------------------------------------
# Render lines

if 0:
	line = draw.line
	for galaxy in (kspace, wspace):
		seen = {}
		for itemID, system in galaxy.iteritems():
			row, loc, jumps = system.item, system.hierarchy, system.jumps

			fromCoord = system.coords
			# region jumps
			for itemID in (itemID for itemID in jumps[0] if itemID not in seen):
				line([fromCoord, galaxy[itemID].coords], fill=0x7f007f)

			# const jumps
			for itemID in (itemID for itemID in jumps[2] if itemID not in seen):
				line([fromCoord, galaxy[itemID].coords], fill=0x7f0000)

			# normal jumps
			for itemID in (itemID for itemID in jumps[1] if itemID not in seen):
				line([fromCoord, galaxy[itemID].coords], fill=0x00007f)

#-----------------------------------------------------------------------------

classColor = {

	1: (255, 255,   0), # yellow
	2: (  0, 255, 255), # cyan
	3: (  0, 128, 255), # blue
	4: (208,   0, 208), # pink
	5: (128,   0, 224), # purple
	6: ( 64,   0, 128), # darker purple

	7: (  0, 255,   0), # green
	8: (255, 128,  64), # orange
	9: (224,   0,   0), # red

}


wormholes = []
for typeID, groupID, name in cfg.invtypes.Select("typeID", "groupID", "typeName"):
	if groupID != const.groupWormhole:
		continue

	attr = cfg.GetTypeAttrDict(typeID)
	if const.attributeWormholeTargetDistribution in attr:
		whclass = attr[const.attributeWormholeTargetSystemClass]
		wormholes.append((name, whclass))

wormholes.sort()

for whClass in range(1,10):
	y = whClass*15 + 30
	draw.text((1,y), "Class %d:" % whClass , fill=classColor[whClass], font=font)

	# collect wormholes...
	names = []
	for name, whtypeclass in wormholes:
		if whtypeclass == whClass:
			names.append(name[-4:])

	draw.text((80,y), "  ".join(names), fill=0xaaaaaa, font=font)


count = 0
x = 700
y = 15 + 30

tabwidth = font.getsize("XXXX  ")[0]
wordwidth = font.getsize("XXXX")[0]


draw.text((x,y), "Alphabetical list:", fill=0xaaaaaa, font=font)
y += 15

for name, whtypeclass in wormholes:
	if count == 9:
		x = 700
		y += 15
		count = 0

	count += 1
	draw.text((x,y), name[-4:], fill=classColor[whtypeclass], font=font)

	x += tabwidth




draw.text((0,0), "Wormhole Target System Class Map by Entity", fill=0xffffff, font=font)
draw.text((0,15), "The destination wormhole (K162) appears in a system of the same class as the source wormhole (listed below).", fill=0xaaaaaa, font=font)


# Render systems
for galaxy in (kspace, wspace):
	for system in galaxy.itervalues():
		whClass = cfg.GetLocationWormholeClass(system.hierarchy[2], system.hierarchy[1], system.hierarchy[0])
		pix[system.coords] = classColor.get(whClass, 0xffffff)




#-----------------------------------------------------------------------------
# Save

print "Render took %.2f seconds" % (time.time() - s)

print "Saving image to %s..." % OUT

img.save(OUT)

print "All done"