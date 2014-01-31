# Traits printer - by Entity
#
# Lists traits of an item as they would appear ingame.
#
# This script is freeware. Do whatever you want with it
#
# Disclaimer: Use at your own risk
#

# Note: this code uses cfg._localization - this internal attr is subject to change without notice.

EVEROOT = "G:/EVE"  # change me.

import re
from reverence import blue

tags = re.compile("\<.+?\>")

ROLE_BONUS_TYPE = -1
MISC_BONUS_TYPE = -2


def striptags(text):
	return tags.sub("", text)

def printbonuses(bonusdata):
	for bla, data in bonusdata.iteritems():
		if hasattr(data, 'bonus'):
			value = round(data.bonus, 1)
			if int(data.bonus) == data.bonus:
				value = int(data.bonus)
			text = cfg._localization.GetByLabel('UI/InfoWindow/TraitWithNumber', color="", value=value, unit=cfg.dgmunits.Get(data.unitID).displayName, bonusText=cfg._localization.GetByMessageID(data.nameID))
		else:
			text = cfg._localization.GetByLabel('UI/InfoWindow/TraitWithoutNumber', color="", bonusText=cfg._localization.GetByMessageID(data.nameID))

		bonus, text = text.split("<t>")

		print "%8s %s" % (striptags(bonus), striptags(text))


def printtraits(typeID):
	fsdType = cfg.fsdTypeOverrides.Get(typeID)
	if hasattr(fsdType, 'infoBubbleTypeBonuses'):
		typeBonuses = fsdType.infoBubbleTypeBonuses
		for skillTypeID, skillData in typeBonuses.iteritems():
			if skillTypeID <= 0:
				continue

			print cfg._localization.GetByLabel('UI/ShipTree/SkillNameCaption', skillName=cfg.invtypes.Get(skillTypeID).name)
			printbonuses(skillData)

		if ROLE_BONUS_TYPE in typeBonuses:
			print cfg._localization.GetByLabel('UI/ShipTree/RoleBonus')
			printbonuses(typeBonuses[ROLE_BONUS_TYPE])

		elif MISC_BONUS_TYPE in typeBonuses:
			print cfg._localization.GetByLabel('UI/ShipTree/MiscBonus')
			printbonuses(typeBonuses[MISC_BONUS_TYPE])

		return True


if __name__ == "__main__":
	import sys

	if len(sys.argv) != 2:
		print "Usage: %s <typeName>"
		print "Note: typeName is case sensitive!"
		exit(1)

	what = sys.argv[1]

	eve = blue.EVE(EVEROOT, languageID="en-us")
	cfg = eve.getconfigmgr()

	typesByName = cfg.invtypes.IndexedBy("typeName")

	rec = typesByName.GetIfExists(what)
	if not rec:
		print "No such type found: %s" % what
		exit(1)

	if not printtraits(rec.typeID):
		print "No traits for %s" % rec.typeName
	
