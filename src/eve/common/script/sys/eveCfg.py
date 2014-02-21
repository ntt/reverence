"""Bulk Static Data container classes

Copyright (c) 2003-2014 Jamie "Entity" van den Berge <jamie@hlekkir.com>

This code is free software; you can redistribute it and/or modify
it under the terms of the BSD license (see the file LICENSE.txt
included with the distribution).

Parts of code inspired by or based on EVE Online, with permission from CCP.
"""

import reverence.carbon.common.script.sys.crowset as dbutil
from reverence.carbon.common.script.sys.row import Row
import reverence.eve.common.script.sys.rowset as util

_get = Row.__getattr__

def _localized(row, attr, messageID):
	_cfg = (row.cfg or cfg)
	return _cfg._localization.GetByMessageID(messageID)

def _localized_important(row, attr, messageID):
	_cfg = (row.cfg or cfg)
	return _cfg._localization.GetImportantByMessageID(messageID)


def Singleton(dbrow):
	# used as property getter by certain cache objects
	if dbrow.quantity < 0:
		return 1
	else:
		if 30000000 <= dbrow.locationID < 40000000:
			return 1
	return 0


def StackSize(dbrow):
	# used as property getter by certain cache objects
	qty = dbrow.quantity
	return qty if qty >= 0 else 1


def RamActivityVirtualColumn(dbrow):
# this does not work because the dbrow does not have a cfg attrib and we don't have a global one.
# the RamDetail class will handle it.
#   return cfg.ramaltypes.Get(dbrow.assemblyLineTypeID).activityID
	return None




class Billtype(Row):
	__guid__ = 'cfg.Billtype'

	def __getattr__(self, name):
		value = _get(self, name)
#		if name == 'billTypeName':
#			value = Tr(value, 'dbo.actBillTypes.billTypeName', self.billTypeID)
		return value

	def __str__(self):
		return 'Billtype ID: %d' % self.billTypeID


class InvType(Row):
	__guid__ = "sys.InvType"

	def __getattr__(self, attr):
		if attr in ("name", "typeName"):
			return _localized_important(self, "typeName", self.typeNameID)
		if attr == 'categoryID':
			return (self.cfg or cfg).invgroups.Get(self.groupID).categoryID
		if attr == "description":
			return _localized(self, "description", self.descriptionID)

		# check overrides
		if attr in ('graphicID', 'soundID', 'iconID', 'radius'):
			try:
				fsd = (self.cfg or cfg).fsdTypeOverrides
				return getattr(fsd.Get(self.typeID), attr)
			except (AttributeError, KeyError):
				pass

		return _get(self, attr)

	def Group(self):
		return (self.cfg or cfg).invgroups.Get(self.groupID)

	def GetRawName(self, languageID):
		return (self.cfg or cfg)._localization.GetByMessageID(self.typeNameID, languageID)

	def Icon(self):
		if self.typeID >= const.minDustTypeID:
			return (self.cfg or cfg).fsdDustIcons.get(self.typeID, None)
		elif self.iconID is not None:
			return (self.cfg or cfg).icons.GetIfExists(self.iconID)
		return

	def IconFile(self):
		return getattr((self.cfg or cfg).icons.Get(self.iconID), "iconFile", "")

	def Graphic(self):
		gid = self.graphicID
		if gid is not None:
			return (self.cfg or cfg).graphics.Get(gid)
		return None

	def GraphicFile(self):
		return getattr((self.cfg or cfg).Graphic(), "graphicFile", "")

	def Sound(self):
		sid = self.soundID
		if sid is not None:
			print (self.cfg or cfg).sounds.keys()
			return (self.cfg or cfg).sounds.GetIfExists(sid)

	@property
	def averagePrice(self):
		try:
			return (self.cfg or cfg)._averageMarketPrice[self.typeID].averagePrice
		except KeyError:
			return None

	# ---- custom additions ----

	@property
	def packagedvolume(self):
		return (self.cfg or cfg).GetTypeVolume(self.typeID)

	def GetRequiredSkills(self):
		return (self.cfg or cfg).GetRequiredSkills(self.typeID)

	def GetTypeAttrDict(self):
		return (self.cfg or cfg).GetTypeAttrDict(self.typeID)

	def GetTypeAttribute(self, attributeID, defaultValue=None):
		return (self.cfg or cfg).GetTypeAttribute(self.typeID, attributeID, defaultValue)

	def GetTypeAttribute2(self, attributeID):
		return (self.cfg or cfg).GetTypeAttribute2(self.typeID, attributeID)


class InvGroup(Row):
	__guid__ = "sys.InvGroup"

	def Category(self):
		return (self.cfg or cfg).invcategories.Get(self.categoryID)

	def __getattr__(self, attr):
		if attr in ("name", "groupName", "description"):
			return _localized(self, "groupName", self.groupNameID)
		if attr == "id":
			return _get(self, "groupID")
		return _get(self, attr)


class InvCategory(Row):
	__guid__ = "sys.InvCategory"

	def __getattr__(self, attr):
		if attr in ("name", "categoryName", "description"):
			return _localized(self, "categoryName", self.categoryNameID)
		if attr == "id":
			return _get(self, "categoryID")
		return _get(self, attr)

	def IsHardware(self):
		return self.categoryID == const.categoryModule


class InvMetaGroup(Row):
	__guid__ = "cfg.InvMetaGroup"

	def __getattr__(self, name):
		if name == "_metaGroupName":
			return _get(self, "metaGroupName")

		if name == "name":
			name = "metaGroupName"

		return _get(self, name)


class DgmAttribute(Row):
	__guid__ = "cfg.DgmAttribute"

	def __getattr__(self, name):
		if name == 'displayName':
			return _localized(self, "displayName", self.displayNameID)
		return _get(self, name)


class DgmEffect(Row):
	__guid__ = "cfg.DgmEffect"

	def __getattr__(self, name):
		if name == "displayName":
			return _localized(self, "displayName", self.displayNameID)
		if name == "description":
			return _localized(self, "description", self.descriptionID)
		return _get(self, name)


class DgmUnit(Row):
	__guid__ = 'cfg.DgmUnit'

	def __getattr__(self, name):
		if name == 'displayName':
			return _localized(self, "displayName", self.displayNameID)
		if name == 'description':
			return _localized(self, "description", self.descriptionID)
		return _get(self, name)


class EveOwners(Row):
	__guid__ = "cfg.EveOwners"

	def __getattr__(self, name):
		if name in ("name", "description", "ownerName"):
			return _get(self, "ownerName")
		if name == "groupID":
			return self.cfg.invtypes.Get(self.typeID).groupID
		return _get(self, name)

	def GetRawName(self, languageID):
		if self.ownerNameID:
			if self.ownerNameID in _OWNER_NAME_OVERRIDES:
				return (self.cfg or cfg)._localization.GetByLabel(_OWNER_NAME_OVERRIDES[self.ownerNameID], languageID)
			return (self.cfg or cfg)._localization.GetByMessageID(self.ownerNameID, languageID)
		return self.name

	def __str__(self):
		return 'EveOwner ID: %d, "%s"' % (self.ownerID, self.ownerName)

	def Type(self):
		return self.cfg.invtypes.Get(self.typeID)

	def Group(self):
		return self.cfg.invgroups.Get(self.groupID)


class EveLocations(Row):
	__guid__ = "dbrow.Location"

	def __getattr__(self, name):
		if name in ("name", "description", "locationName"):
			locationName = _get(self, 'locationName')
			_cfg = (self.cfg or cfg)
			if (not locationName) and self.locationNameID is not None:
				if isinstance(self.locationNameID, (int, long)):
					locationName = _cfg._localization.GetByMessageID(self.locationNameID)
				elif isinstance(self.locationNameID, tuple):
					locationName = _cfg._localization.GetByLabel(self.locationNameID[0], **self.locationNameID[1])
				setattr(self, 'locationName', locationName)
			return locationName

		return _get(self, name)

	def __str__(self):
		return 'EveLocation ID: %d, "%s"' % (self.locationID, self.locationName)

	def GetRawName(self, languageID):
		if self.locationNameID:
			return (self.cfg or cfg)._localization.GetByMessageID(self.locationNameID, languageID)
#		if self.locationID in cfg.rawCelestialCache:
#			(lbl, kwargs,) = cfg.rawCelestialCache[self.locationID]
#			return self.cfg._localization.GetByLabel(lbl, languageID, **kwargs)
		return _get(self, name)

#	def Station(self):
#		return self.cfg.GetSvc("stationSvc").GetStation(self.id)


class RamCompletedStatus(Row):
	def __getattr__(self, name):
		if name in ("name", "completedStatusName"):
			return _localized(self, "completedStatusName", self.completedStatusTextID)
		if name == "description":
			return _localized(self, "description", self.descriptionID)
		return _get(self, name)

	def __str__(self):
		try:
			return 'RamCompletedStatus ID: %d, "%s"' % (self.completedStatus, self.completedStatusName)
		except:
			sys.exc_clear()
			return "RamCompletedStatus containing crappy data"


class RamActivity(Row):
	def __getattr__(self, name):
		if name in ("name", "activityName"):
			return _localized(self, "activityName", self.activityNameID)
		if name == "description":
			return _localized(self, "description", self.descriptionID)
		return _get(self, name)

	def __str__(self):
		try:
			return 'RamActivity ID: %d, "%s"' % (self.activityID, self.activityName)
		except:
			sys.exc_clear()
			return "RamActivity containing crappy data"


class RamDetail(Row):
	def __getattr__(self, name):
   		if name == "activityID":
			return self.cfg.ramaltypes.Get(self.assemblyLineTypeID).activityID
   		return _get(self, name)


class MapCelestialDescription(Row):
	def __getattr__(self, name):
		if name == "description":
			return _localized(self, "description", self.descriptionID)
		return _get(self, name)

	def __str__(self):
		return "MapCelestialDescriptions ID: %d" % (self.itemID)


class CrpTickerNames(Row):
	def __getattr__(self, name):
		if name in ("name", "description"):
			return _get(self, "tickerName")
		return _get(self, name)

	def __str__(self):
		return "CorpTicker ID: %d, \"%s\"" % (self.corporationID, self.tickerName)


class AllShortNames(Row):
	__guid__ = 'cfg.AllShortNames'

	def __getattr__(self, name):
		if name in ("name", "description"):
			return _get(self, "shortName")
		return _get(self, name)

	def __str__(self):
		return "AllianceShortName ID: %d, \"%s\"" % (self.allianceID, self.shortName)


class Certificate(Row):
	__guid__ = 'cfg.Schematic'

	def __getattr__(self, name):
		if name == "description":
			return _localized(self, "description", self.descriptionID)
		return _get(self, name)

	def __str__(self):
		return "Certificate ID: %d" % (self.certificateID)


class Schematic(Row):
	__guid__ = 'cfg.Schematic'

	def __getattr__(self, name):
		if name == "schematicName":
			return _localized(self, "schematicName", self.schematicNameID)
		return _get(self, name)

	def __str__(self):
		return 'Schematic: %s (%d)' % (self.schematicName, self.schematicID)

	def __cmp__(self, other):
		if type(other) is int:
			return int.__cmp__(self.schematicID, other)
		else:
			return Row.__cmp__(self, other)

