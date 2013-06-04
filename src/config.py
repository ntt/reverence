"""Interface to bulkdata

- loads and prepares the bulkdata for use (on demand)
- provides container classes for record and row data.
- provides interface to the database tables

Copyright (c) 2003-2012 Jamie "Entity" van den Berge <jamie@hlekkir.com>

This code is free software; you can redistribute it and/or modify
it under the terms of the BSD license (see the file LICENSE.txt
included with the distribution).

Parts of code inspired by or based on EVE Online, with permission from CCP.
"""

import sys
import os
import time
import sqlite3
import glob
import logging

from . import _blue as blue
from . import const, util, dbutil
from . import localization, fsd


_get = util.Row.__getattr__

def _localized(row, attr, messageID):
	_cfg = (row.cfg or cfg)
	if _cfg._languageID:
		return _cfg._localized.GetByMessageID(messageID)
	return _get(row, attr)

def _localized_important(row, attr, messageID):
	_cfg = (row.cfg or cfg)
	if _cfg._languageID:
		return _cfg._localized.GetImportantByMessageID(messageID)
	return _get(row, attr)


OWNER_AURA_IDENTIFIER = -1
OWNER_SYSTEM_IDENTIFIER = -2
OWNER_NAME_OVERRIDES = {
	OWNER_AURA_IDENTIFIER: 'UI/Agents/AuraAgentName',
	OWNER_SYSTEM_IDENTIFIER: 'UI/Chat/ChatEngine/EveSystem'
}

# used by GetLocationsLocalBySystem method
_solarSystemObjectRowDescriptor = blue.DBRowDescriptor((
	('groupID', const.DBTYPE_I4),
	('typeID', const.DBTYPE_I4),
	('itemID', const.DBTYPE_I4),
	('itemName', const.DBTYPE_WSTR),
	('locationID', const.DBTYPE_I4),
	('orbitID', const.DBTYPE_I4),
	('connector', const.DBTYPE_BOOL),
	('x', const.DBTYPE_R8),
	('y', const.DBTYPE_R8),
	('z', const.DBTYPE_R8),
))


class Billtype(util.Row):
	__guid__ = 'cfg.Billtype'

	def __getattr__(self, name):
		value = _get(self, name)
#		if name == 'billTypeName':
#			value = Tr(value, 'dbo.actBillTypes.billTypeName', self.billTypeID)
		return value

	def __str__(self):
		return 'Billtype ID: %d' % self.billTypeID


class InvType(util.Row):
	__guid__ = "sys.InvType"

	def Group(self):
		return (self.cfg or cfg).invgroups.Get(self.groupID)

	def Graphic(self):
		if self.graphicID is not None:
			return (self.cfg or cfg).evegraphics.Get(self.graphicID)
		else:
			return None

	def __getattr__(self, attr):
		if attr in ("name", "typeName"):
			return _localized_important(self, "typeName", self.typeNameID)
		if attr == 'categoryID':
			return (self.cfg or cfg).invgroups.Get(self.groupID).categoryID
		if attr == "description":
			return _localized(self, "description", self.descriptionID)
		return _get(self, attr)

	def GetRawName(self, languageID):
		return (self.cfg or cfg)._localization.GetByMessageID(self.typeNameID, languageID)


	# ---- custom additions ----

	def GetRequiredSkills(self):
		return (self.cfg or cfg).GetRequiredSkills(self.typeID)

	def GetTypeAttrDict(self):
		return (self.cfg or cfg).GetTypeAttrDict(self.typeID)

	def GetTypeAttribute(self, attributeID, defaultValue=None):
		return (self.cfg or cfg).GetTypeAttribute(self.typeID, attributeID, defaultValue)

	def GetTypeAttribute2(self, attributeID):
		return (self.cfg or cfg).GetTypeAttribute2(self.typeID, attributeID)


class InvGroup(util.Row):
	__guid__ = "sys.InvGroup"

	def Category(self):
		return (self.cfg or cfg).invcategories.Get(self.categoryID)

	def __getattr__(self, attr):
		if attr in ("name", "groupName", "description"):
			return _localized(self, "groupName", self.groupNameID)
		if attr == "id":
			return _get(self, "groupID")
		return _get(self, attr)


class InvCategory(util.Row):
	__guid__ = "sys.InvCategory"

	def __getattr__(self, attr):
		if attr in ("name", "categoryName", "description"):
			return _localized(self, "categoryName", self.categoryNameID)
		if attr == "id":
			return _get(self, "categoryID")
		return _get(self, attr)

	def IsHardware(self):
		return self.categoryID == const.categoryModule


class InvMetaGroup(util.Row):
	__guid__ = "cfg.InvMetaGroup"

	def __getattr__(self, name):
		if name == "_metaGroupName":
			return _get(self, "metaGroupName")

		if name == "name":
			name = "metaGroupName"

		return _get(self, name)


class DgmAttribute(util.Row):
	__guid__ = "cfg.DgmAttribute"

	def __getattr__(self, name):
		if name == 'displayName':
			return _localized(self, "displayName", self.displayNameID)
		return _get(self, name)


class DgmEffect(util.Row):
	__guid__ = "cfg.DgmEffect"

	def __getattr__(self, name):
		if name == "displayName":
			return _localized(self, "displayName", self.displayNameID)
		if name == "description":
			return _localized(self, "description", self.descriptionID)
		return _get(self, name)


class EveOwners(util.Row):
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


class EveLocations(util.Row):
	__guid__ = "dbrow.Location"

	def __getattr__(self, name):
		if name in ("name", "description", "locationName"):
			locationName = _get(self, 'locationName')
			_cfg = (self.cfg or cfg)
			if _cfg._languageID:
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


class RamCompletedStatus(util.Row):
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


class RamActivity(util.Row):
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


class RamDetail(util.Row):
	def __getattr__(self, name):
   		if name == "activityID":
			return self.cfg.ramaltypes.Get(self.assemblyLineTypeID).activityID
   		return _get(self, name)


class MapCelestialDescription(util.Row):
	def __getattr__(self, name):
		if name == "description":
			return _localized(self, "description", self.descriptionID)
		return _get(self, name)

	def __str__(self):
		return "MapCelestialDescriptions ID: %d" % (self.itemID)


class CrpTickerNames(util.Row):
	def __getattr__(self, name):
		if name in ("name", "description"):
			return _get(self, "tickerName")
		return _get(self, name)

	def __str__(self):
		return "CorpTicker ID: %d, \"%s\"" % (self.corporationID, self.tickerName)


class AllShortNames(util.Row):
	__guid__ = 'cfg.AllShortNames'

	def __getattr__(self, name):
		if name in ("name", "description"):
			return _get(self, "shortName")
		return _get(self, name)

	def __str__(self):
		return "AllianceShortName ID: %d, \"%s\"" % (self.allianceID, self.shortName)


class Certificate(util.Row):
	__guid__ = 'cfg.Schematic'

	def __getattr__(self, name):
		if name == "description":
			return _localized(self, "description", self.descriptionID)
		return _get(self, name)

	def __str__(self):
		return "Certificate ID: %d" % (self.certificateID)


class Schematic(util.Row):
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
			return util.Row.__cmp__(self, other)


# Warning: Code below may accidentally your whole brain.

class _memoize(object):
	# This class is a getter. On attribute access, it will call the method it
	# decorates and replace the attribute value (which is the getter instance)
	# with the value returned by that method. Used to implement the
	# load-on-access mechanism 

	__slots__ = ["method"]

	def __init__(self, func):
		self.method = func

	def __get__(self, obj, type=None):
		if obj is None:
			# class attribute (descriptor itself)
			return self
		else:
			# instance attribute (replaced by value)
			value = self.method(obj)
			setattr(obj, self.method.func_name, value)
			return value


def _loader(attrName):
	# Creates a closure used as a method in Config class (to be decorated with
	# _memoize) that loads a specific bulkdata table.
	def method(self):
		entry = self._tables[attrName]
		if len(entry) == 6:
			# bulkID loader
			ver, rem, storageClass, rowClass, primaryKey, bulkID = entry
			return self._loadbulkdata(tableName=attrName, storageClass=storageClass, rowClass=rowClass, primaryKey=primaryKey, bulkID=bulkID)

		if len(entry) == 4:
			# FSD loader
			ver, rem, (staticName, schemaName, optimize), cacheNum = entry
			if self.useCCPlibs:
				# odyssey fsd loader (uses CCP code directly)
				from . import blue as bloo
				_rf = bloo.ResFile
				try:
					bloo.ResFile = self._eve.ResFile
					if optimize is None:
						optimize = True
					staticName = 'res:/staticdata/%s.static' % staticName
					schemaName = 'res:/staticdata/%s.schema' % schemaName if schemaName else None
					return self._fsdBinaryLoader.LoadFSDDataForCFG(staticName, schemaName, optimize=optimize)
				finally:
					bloo.ResFile = _rf
			else:
				# pre-odyssey loader
				return self._loadfsddata(attrName, staticName, cacheNum)

	method.func_name = attrName
	return method


class _tablemgr(type):
	# Creates decorated methods in the Config class that handle loading of
	# bulkdata tables on accessing the attributes those methods are bound as.
	# Note: tables that require non-standard handling will need methods for
	# that (decorated with @_memoize) in Config class.

	def __init__(cls, name, bases, dict):
		type.__init__(cls, name, bases, dict)
		for attrName, x in cls.__tables__:
			if hasattr(cls, attrName):
				# specialized loader method exists.
				continue
			setattr(cls, attrName, _memoize(_loader(attrName)))


class Config(object):
	__metaclass__ = _tablemgr

	"""Interface to bulkdata.

	EVE's database is available as attributes of instances of this class.
    Tables are transparently loaded from bulkdata/cache upon accessing such an
    attribute. Because this automatic loading scheme is NOT thread-safe, the
    prime() method should be called prior to allowing other threads access to
    the instance.
    """

	__containercategories__ = (
		const.categoryStation,
		const.categoryShip,
		const.categoryTrading,
		const.categoryStructure,
		)

	__containergroups__ = (
		const.groupCargoContainer,
		const.groupSecureCargoContainer,
		const.groupAuditLogSecureContainer,
		const.groupFreightContainer,
		const.groupConstellation,
		const.groupRegion,
		const.groupSolarSystem,
		const.groupMissionContainer,            
		)

	__chargecompatiblegroups__ = (
		const.groupFrequencyMiningLaser,
		const.groupEnergyWeapon,
		const.groupProjectileWeapon,
		const.groupMissileLauncher,
		const.groupCapacitorBooster,
		const.groupHybridWeapon,
		const.groupScanProbeLauncher,
		const.groupComputerInterfaceNode,
		const.groupMissileLauncherBomb,
		const.groupMissileLauncherCruise,
		const.groupMissileLauncherDefender,
		const.groupMissileLauncherAssault,
		const.groupMissileLauncherSiege,
		const.groupMissileLauncherHeavy,
		const.groupMissileLauncherHeavyAssault,
		const.groupMissileLauncherRocket,
		const.groupMissileLauncherStandard,
		const.groupMissileLauncherCitadel,
		const.groupMissileLauncherSnowball,
		const.groupBubbleProbeLauncher,
		const.groupSensorBooster,
		const.groupRemoteSensorBooster,
		const.groupRemoteSensorDamper,
		const.groupTrackingComputer,
		const.groupTrackingDisruptor,
		const.groupTrackingLink,
		const.groupWarpDisruptFieldGenerator,
		)

	__containerVolumes__ = {
		const.groupAssaultShip: 2500.0,
		const.groupBattlecruiser: 15000.0,
		const.groupBattleship: 50000.0,
		const.groupBlackOps: 50000.0,
		const.groupCapitalIndustrialShip: 1000000.0,
		const.groupCapsule: 500.0,
		const.groupCarrier: 1000000.0,
		const.groupCombatReconShip: 10000.0,
		const.groupCommandShip: 15000.0,
		const.groupCovertOps: 2500.0,
		const.groupCruiser: 10000.0,
		const.groupStrategicCruiser: 10000.0,
		const.groupDestroyer: 5000.0,
		const.groupDreadnought: 1000000.0,
		const.groupElectronicAttackShips: 2500.0,
		const.groupEliteBattleship: 50000.0,
		const.groupExhumer: 3750.0,
		const.groupForceReconShip: 10000.0,
		const.groupFreighter: 1000000.0,
		const.groupFrigate: 2500.0,
		const.groupHeavyAssaultShip: 10000.0,
		const.groupHeavyInterdictors: 10000.0,
		const.groupIndustrial: 20000.0,
		const.groupIndustrialCommandShip: 500000.0,
		const.groupInterceptor: 2500.0,
		const.groupInterdictor: 5000.0,
		const.groupJumpFreighter: 1000000.0,
		const.groupLogistics: 10000.0,
		const.groupMarauders: 50000.0,
		const.groupMiningBarge: 3750.0,
		const.groupSupercarrier: 1000000.0,
		const.groupRookieship: 2500.0,
		const.groupShuttle: 500.0,
		const.groupStealthBomber: 2500.0,
		const.groupTitan: 10000000.0,
		const.groupTransportShip: 20000.0,
		const.groupCargoContainer: 1000.0,
		const.groupMissionContainer: 1000.0,
		const.groupSecureCargoContainer: 1000.0,
		const.groupAuditLogSecureContainer: 1000.0,
		const.groupFreightContainer: 1000.0,
		const.groupStrategicCruiser: 5000.0,
		const.groupPrototypeExplorationShip: 500.0,
		}


	#-------------------------------------------------------------------------------------------------------------------
	# BulkData Table Definitions.
	# ver            - minimum machoNet version required to load this table with prime() method
	# del            - starting from this machoNet version the table no longer exists
	# cfg attrib     - name the table is accessed with in cfg.* (e.g. cfg.invtypes)
	# bulkdata name  - name of the bulkdata in the cache file if not same as cfg attrib, else None.
	# storage class  - container class for the table data. can be string to generate FilterRowset from named table.
	# row class      - the class used to wrap rows with when they are requested.
	# primary key    - primary key
	# bulkID         - bulkdata file ID
	#
	# this table is filtered for every instance to create a table dict containing only those entries relevant
	# to its protocol version.
	__tables__ = (

#		( cfg attrib                  , (ver, del, storage class       , row class         , primary key           bulkID)),
		("icons"                      , (242, 332, util.IndexRowset    , util.Row          , 'iconID'            , const.cacheResIcons)),
		("sounds"                     , (242, 332, util.IndexRowset    , util.Row          , 'soundID'           , const.cacheResSounds)),

		("invcategories"              , (  0,   0, util.IndexRowset    , InvCategory       , "categoryID"        , const.cacheInvCategories)),
		("invgroups"                  , (  0,   0, util.IndexRowset    , InvGroup          , "groupID"           , const.cacheInvGroups)),
		("invtypes"                   , (  0,   0, util.IndexRowset    , InvType           , "typeID"            , const.cacheInvTypes)),
		("invmetagroups"              , (  0,   0, util.IndexRowset    , InvMetaGroup      , "metaGroupID"       , const.cacheInvMetaGroups)),
		("invbptypes"                 , (  0,   0, util.IndexRowset    , util.Row          , "blueprintTypeID"   , const.cacheInvBlueprintTypes)),
		("invreactiontypes"           , (  0,   0, util.FilterRowset   , util.Row          , "reactionTypeID"    , const.cacheInvTypeReactions)),
		("shiptypes"                  , (  0,   0, util.IndexRowset    , util.Row          , "shipTypeID"        , const.cacheShipTypes)),

		("dgmattribs"                 , (  0,   0, util.IndexRowset    , DgmAttribute      , "attributeID"       , const.cacheDogmaAttributes)),
		("dgmeffects"                 , (  0,   0, util.IndexRowset    , DgmEffect         , "effectID"          , const.cacheDogmaEffects)),
		("dgmtypeattribs"             , (  0,   0, util.IndexedRowLists, None              , ('typeID',)         , const.cacheDogmaTypeAttributes)),
		("dgmtypeeffects"             , (  0,   0, util.IndexedRowLists, None              , ('typeID',)         , const.cacheDogmaTypeEffects)),
		("dgmexpressions"             , (297,   0, util.IndexRowset    , util.Row          , 'expressionID'      , const.cacheDogmaExpressions)),
		("dgmunits"                   , (299,   0, util.IndexRowset    , util.Row          , "unitID"            , const.cacheDogmaUnits)),

		("ramaltypes"                 , (  0,   0, util.IndexRowset    , util.Row          , "assemblyLineTypeID", const.cacheRamAssemblyLineTypes)),
		("ramactivities"              , (  0,   0, util.IndexRowset    , RamActivity       , "activityID"        , const.cacheRamActivities)),
		("ramcompletedstatuses"       , (276,   0, util.IndexRowset    , RamCompletedStatus, "completedStatus"   , const.cacheRamCompletedStatuses)),
		("ramaltypesdetailpercategory", (  0,   0, util.FilterRowset   , RamDetail         , "assemblyLineTypeID", const.cacheRamAssemblyLineTypesCategory)),
		("ramaltypesdetailpergroup"   , (  0,   0, util.FilterRowset   , RamDetail         , "assemblyLineTypeID", const.cacheRamAssemblyLineTypesGroup)),

		("billtypes"                  , (  0,   0, util.IndexRowset    , Billtype          , 'billTypeID'        , const.cacheActBillTypes)),
		("certificates"               , (  0,   0, util.IndexRowset    , Certificate       , "certificateID"     , const.cacheCertificates)),
		("certificaterelationships"   , (  0,   0, util.IndexRowset    , util.Row          , "relationshipID"    , const.cacheCertificateRelationships)),

		("schematics"                 , (242,   0, util.IndexRowset    , Schematic         , 'schematicID'       , const.cachePlanetSchematics)),
		("ramtyperequirements"        , (242,   0, dict                , None          , ('typeID', 'activityID'), const.cacheRamTypeRequirements)),
		("invtypematerials"           , (254,   0, dict                , None              , 'typeID'            , const.cacheInvTypeMaterials)),

		# location/owner stuff.
		("factions"                   , (276,   0, util.IndexRowset    , util.Row          , "factionID"         , const.cacheChrFactions)),
		("npccorporations"            , (276,   0, util.IndexRowset    , util.Row          , "corporationID"     , const.cacheCrpNpcCorporations)),
		("corptickernames"            , (  0,   0, util.IndexRowset    , CrpTickerNames    , "corporationID"     , const.cacheCrpTickerNamesStatic)),

		("staoperationtypes"          , (299,   0, util.IndexRowset    , util.Row          , "operationID"       , const.cacheStaOperations)),
		("mapcelestialdescriptions"   , (276,   0, util.IndexRowset    , MapCelestialDescription, "itemID"       , const.cacheMapCelestialDescriptions)),
		("locationwormholeclasses"    , (  0,   0, util.IndexRowset    , util.Row          , "locationID"        , const.cacheMapLocationWormholeClasses)),

		("regions"                    , (299,   0, util.IndexRowset    , util.Row          , "regionID"          , const.cacheMapRegionsTable)),
		("constellations"             , (299,   0, util.IndexRowset    , util.Row          , "constellationID"   , const.cacheMapConstellationsTable)),
		("solarsystems"               , (299,   0, util.IndexRowset    , util.Row          , "solarSystemID"     , const.cacheMapSolarSystemsTable)),
		("stations"                   , (299,   0, util.IndexRowset    , util.Row          , "stationID"         , const.cacheStaStationsStatic)),

		("nebulas"                    , (299,   0, util.IndexRowset    , util.Row          , "locationID"        , const.cacheMapNebulas)),

		# autogenerated FilterRowsets from some of the above tables
		("groupsByCategories"         , (  0,   0, "invgroups"         , None              , "categoryID"        , None)),
		("typesByGroups"              , (  0,   0, "invtypes"          , None              , "groupID"           , None)),
		("typesByMarketGroups"        , (  0,   0, "invtypes"          , None              , "marketGroupID"     , None)),

		# tables that have custom loaders
		("eveowners"                  , (299,   0)),
		("evelocations"               , (299,   0)),
		("invmetatypes"               , (  0,   0)),
		("invmetatypesByTypeID"       , (  0,   0)),
		("invcontrabandTypesByFaction", (  0,   0)),
		("invcontrabandTypesByType"   , (  0,   0)),
		("schematicstypemap"          , (242,   0)),
		("schematicsByType"           , (242,   0)),
		("schematicspinmap"           , (242,   0)),
		("schematicsByPin"            , (242,   0)),

		# new FSD stuff --------------- (ver, del,  static name       , schema name       , optimize   cache size)
		("fsdTypeOverrides"           , (324,   0, ("typeIDs"         , "typeIDs"         , False)   , None)),
		("fsdPlanetAttributes"        , (324,   0, ("planetAttributes", "planetAttributes", False)   , 100 )),
#		("fsdDustIcons"               , (XXX,   0, ("dustIcons"       , None              , None )   , None)),  # FIXME (@ Odyssey release?)
		("graphics"                   , (324,   0, ("graphicIDs"      , "graphicIDs"      , None )   , 100 )),
		("sounds"                     , (332,   0, ("soundIDs"        , "soundIDs"        , None )   , 100 )),
		("icons"                      , (332,   0, ("iconIDs"         , "iconIDs"         , None )   , 100 )),

	)


	# Custom table loader methods follow

	@_memoize
	def eveowners(self):
		bloodlinesToTypes = {
			const.bloodlineDeteis   : const.typeCharacterDeteis,
			const.bloodlineCivire   : const.typeCharacterCivire,
			const.bloodlineSebiestor: const.typeCharacterSebiestor,
			const.bloodlineBrutor   : const.typeCharacterBrutor,
			const.bloodlineAmarr    : const.typeCharacterAmarr,
			const.bloodlineNiKunni  : const.typeCharacterNiKunni,
			const.bloodlineGallente : const.typeCharacterGallente,
			const.bloodlineIntaki   : const.typeCharacterIntaki,
			const.bloodlineStatic   : const.typeCharacterStatic,
			const.bloodlineModifier : const.typeCharacterModifier,
			const.bloodlineAchura   : const.typeCharacterAchura,
			const.bloodlineJinMei   : const.typeCharacterJinMei,
			const.bloodlineKhanid   : const.typeCharacterKhanid,
			const.bloodlineVherokior: const.typeCharacterVherokior
		}

		rs = util.IndexRowset(['ownerID', 'ownerName', 'typeID', 'gender', 'ownerNameID'], None, key="ownerID", RowClass=EveOwners, cfgInstance=self)
		d = rs.items

		rd = blue.DBRowDescriptor((
			('ownerID', const.DBTYPE_I4),
			('ownerName', const.DBTYPE_WSTR),
			('typeID', const.DBTYPE_I2),
			('gender', const.DBTYPE_I2),
			('ownerNameID', const.DBTYPE_I4),
		))

		DBRow = blue.DBRow
		for row in self.factions:
			id_ = row.factionID
			d[id_] = DBRow(rd, [id_, row.factionName, const.typeFaction, 0, row.factionNameID])

		for row in self.npccorporations:
			id_ = row.corporationID
			d[id_] = DBRow(rd, [id_, row.corporationName, const.typeCorporation, 0, row.corporationNameID])

		if self._languageID:
			# cerberus version
			for row in self.cache.LoadBulk(const.cacheChrNpcCharacters):
				id_ = row.characterID
				npcName = self._localization.GetImportantByMessageID(id_) or row.characterName
				d[id_] = DBRow(rd, [id_, row.characterName, bloodlinesToTypes[row.bloodlineID], row.gender, row.characterNameID])

			auraName = self._localization.GetImportantByLabel(_OWNER_NAME_OVERRIDES[OWNER_AURA_IDENTIFIER])
			sysName = self._localization.GetByLabel(_OWNER_NAME_OVERRIDES[OWNER_SYSTEM_IDENTIFIER])
		else:
			# non-cerberus version
			for row in self.cache.LoadBulk(const.cacheChrNpcCharacters):
				id_ = row.characterID
				npcName = row.characterName
				d[id_] = DBRow(rd, [id_, row.characterName, bloodlinesToTypes[row.bloodlineID], row.gender, row.characterNameID])

			auraName = "Aura"
			sysName = "EVE System"

		for id_ in const.auraAgentIDs:
			d[id_].ownerName = auraName
		d[1] = blue.DBRow(rd, [1, sysName, 0, None, None])

		rs.lines = rs.items.values()
		return rs


	@_memoize
	def evelocations(self):
		rs = util.IndexRowset(['locationID', 'locationName', 'x', 'y', 'z', 'locationNameID'], None, key="locationID", RowClass=EveLocations, cfgInstance=self)
		d = rs.items

		rd = blue.DBRowDescriptor((
			('locationID', const.DBTYPE_I4),
			('locationName', const.DBTYPE_WSTR),
			('x', const.DBTYPE_R8),
			('y', const.DBTYPE_R8),
			('z', const.DBTYPE_R8),
			('locationNameID', const.DBTYPE_I4),
		))

		DBRow = blue.DBRow

		if self._languageID:
			getname = self._localization.GetImportantByMessageID

		for table, name in (
			(self.regions, "region"),  # 1xxxxxxx
			(self.constellations, "constellation"),  # 2xxxxxxx
			(self.solarsystems, "solarSystem"),  # 3xxxxxxx
			(self.stations, "station"),  # 6xxxxxxx
		):
			hdr = table.header
			id_ix = hdr.index(name + "ID")

			try:
				nameid_ix = hdr.index(name + "NameID")
				if self._languageID:
					for row in table.lines:
						id_ = row[id_ix]
						nameID = row[nameid_ix]
						d[id_] = DBRow(rd, [id_, getname(nameID), row.x, row.y, -row.z, nameID])
				else:
					name_ix = hdr.index(name + "Name")
					for row in table.lines:
						id_ = row[id_ix]
						d[id_] = DBRow(rd, [id_, row[name_ix], row.x, row.y, -row.z, row[nameid_ix]])

			except ValueError:
				# no nameID.
				name_ix = hdr.index(name + "Name")
				for row in table.lines:
					id_ = row[id_ix]
					d[id_] = DBRow(rd, [id_, row[name_ix], row.x, row.y, -row.z, None])


		# set evelocations attr here, because the following code needs
		# to access the table to generate the planet names.
		self.evelocations = rs

#		# get stars, planets, belts and moons.
#		sql = 'SELECT * FROM celestials WHERE celestialID >= 40000000 AND celestialID < 60000000'
#		for row in self.localdb.execute(sql):
#			celestialName = self.GetCelestialNameFromLocalRow(row)
#			#self.rawCelestialCache[row['celestialID']] = celestialNameData
#			d[row['celestialID']] = blue.DBRow(rd, [row['celestialID'], celestialName, row['x'], row['y'], row['z'], 0])


		rs.lines = rs.items.values()
		return rs


	#--

	def _invcontrabandtypes_load(self):
		byFaction = self.invcontrabandTypesByFaction = {}
		byType = self.invcontrabandFactionsByType = {}

		obj = self.cache.LoadBulk(const.cacheInvContrabandTypes)

		for each in obj:
			typeID = each.typeID
			factionID = each.factionID

			if factionID in byFaction:
				byFaction[factionID][typeID] = each
			else:
				byFaction[factionID] = {typeID:each}

			if typeID in byType:
				byType[typeID][factionID] = each
			else:
				byType[typeID] = {factionID: each}

	@_memoize
	def invcontrabandTypesByFaction(self):
		self._invcontrabandtypes_load()
		return self.invcontrabandTypesByFaction

	@_memoize
	def invcontrabandTypesByType(self):
		self._invcontrabandtypes_load()
		return self.invcontrabandFactionsByType


	#--

	def _schematicstypemap_load(self):
		obj = self.cache.LoadBulk(const.cachePlanetSchematicsTypeMap)
		header = obj.header.Keys()
		self.schematicstypemap = util.FilterRowset(header, obj, "schematicID")
		self.schematicsByType = util.FilterRowset(header, obj, "typeID")

	@_memoize
	def schematicstypemap(self):
		self._schematicstypemap_load()
		return self.schematicstypemap

	@_memoize
	def schematicsByType(self):
		self._schematicstypemap_load()
		return self.schematicsByType

	#--

	def _schematicspinmap_load(self):
		obj = self.cache.LoadBulk(const.cachePlanetSchematicsPinMap)
		header = obj.header.Keys()
		self.schematicspinmap = util.FilterRowset(header, obj, "schematicID")
		self.schematicsByPin = util.FilterRowset(header, obj, "pinTypeID")

	@_memoize
	def schematicspinmap(self):
		self._schematicspinmap_load()
		return self.schematicspinmap

	@_memoize
	def schematicsByPin(self):
		self._schematicspinmap_load()
		return self.schematicsByPin

	#--

	def _invmetatypes_load(self):
		obj = self.cache.LoadBulk(const.cacheInvMetaTypes)
		header = obj.header.Keys()
		self.invmetatypes = util.FilterRowset(header, obj, "parentTypeID")
		self.invmetatypesByTypeID = util.FilterRowset(header, obj, "typeID")

	@_memoize
	def invmetatypes(self):
		self._invmetatypes_load()
		return self.invmetatypes

	@_memoize
	def invmetatypesByTypeID(self):
		self._invmetatypes_load()
		return self.invmetatypesByTypeID

	#--

	@_memoize
	def _localization(self):
		if not self._languageID:
			raise RuntimeError("Cerberus started without languageID set")
		return localization.Localization(self.cache.root, self._languageID, cfgInstance=self)

	#--

	def __init__(self, cache, languageID=None):
		self.cache = cache
		self.callback = None
		protocol = self.protocol = self.cache.machoVersion
		self._languageID = languageID

		# Figure out the set of tables managed by this instance.
		# Only tables that are available for this instance's particular
		# machoNet version will be in this set, and are the only tables loaded
		# when prime() is called.
		self._tables = dict(((k, v) for k, v in self.__tables__ if protocol >= v[0] and protocol < (v[1] or 2147483647)))
		self.tables = frozenset(( \
			attrName for attrName in dir(self.__class__) \
			if attrName[0] != "_" \
			and attrName in self._tables \
			and isinstance(getattr(self.__class__, attrName), _memoize) \
			and protocol >= self._tables[attrName][0] \
			and protocol < (self._tables[attrName][1] or 2147483647) \
		))
		self._attrCache = {}

		self.localdb = sqlite3.connect(os.path.join(self.cache.BULK_SYSTEM_PATH, "mapbulk.db"))
		self.localdb.row_factory = sqlite3.Row


		# look for fsd library in EVE install
		for fsdlib in glob.glob(os.path.join(self.cache.root, "lib", "fsdSchemas-*.zip")):
			# add zip library to module search path
			sys.path.append(fsdlib)

			# needed to make logger work, and shut it up
			logging.basicConfig()
			self._logger = logging.getLogger("fsdSchemas")
			self._logger.setLevel(-1)

			# import the important function!
			import fsdSchemas.binaryLoader as fsdBinaryLoader
			self._fsdBinaryLoader = fsdBinaryLoader

			# All set to use EVE's FSD code directly.
			# Yep, now we're basically gambling on that code to be compatible
			# with whatever other EVE installs are accessed with this process.
			# (This is obviously only an issue if you are using this process
			# to access multiple EVE installs)

			self.useCCPlibs = True
			break
		else:
			self.useCCPlibs = False


	def release(self):
		# purge all loaded tables

		for tableName in self.tables:
			try:
				delattr(self, tableName)
			except AttributeError:
				pass

		self.cache._time_load = 0.0
		self._attrCache = {}


	def _loadfsddata(self, tableName, resName, cacheNum):
		# pre-Odyssey FileStaticData loader.
		# Grabs schema and binary blob from .stuff file.
		res = self._eve.ResFile()
		resFileName = "res:/staticdata/%s.schema" % resName
		if not res.Open(resFileName):
			raise RuntimeError("Could not load FSD data schema '%s'" % resFileName)

		schema = fsd.LoadSchema(res.Read())
		schema = fsd.GetUnOptimizedRuntimeSchema(schema)
		schema = fsd.OptimizeSchema(schema, "Client")

		resFileName = "res:/staticdata/%s.static" % resName
		if not res.Open(resFileName):
			raise RuntimeError("Could not load FSD static data '%s'" % resFileName)

		if cacheNum:
			return fsd.LoadIndexFromFile(res.fh, schema, cacheNum)

		return fsd.LoadFromString(res.Read(), schema)


	def _loadbulkdata(self, tableName=None, storageClass=None, rowClass=None, primaryKey=None, bulkID=None):

		if type(storageClass) is str:
			# create a FilterRowset from existing table named by storageClass.
			table = getattr(self, storageClass)
			rs = table.GroupedBy(primaryKey)
			return rs

		obj = self.cache.LoadBulk(bulkID)
		if obj is None:
			raise RuntimeError("Unable to load '%s' (bulkID:%d)" % (tableName, bulkID))
		
		if issubclass(storageClass, util.IndexRowset):
			rs = util.IndexRowset(obj.header.Keys(), obj, key=primaryKey, RowClass=rowClass, cfgInstance=self)

		elif issubclass(storageClass, util.FilterRowset):
			rs = storageClass(obj.header.Keys(), obj, primaryKey, RowClass=rowClass)

		elif issubclass(storageClass, util.IndexedRowLists):
			rs = storageClass(obj, keys=primaryKey)

		elif issubclass(storageClass, dict):
			rs = {}
			if type(primaryKey) is tuple:
				# composite key
				getkey = lambda row: tuple(map(row.__getitem__, primaryKey))
			else:
				getkey = lambda row: getattr(row, primaryKey)

			for row in obj:
				key = getkey(row)
				li = rs.get(key)
				if li is None:
					rs[key] = [row]
				else:
					li.append(row)
		else:
			raise RuntimeError("Invalid storageClass: %s" % storageClass)

		return rs


	def prime(self, tables=None, callback=None, debug=False):
		"""Loads the tables named in the tables sequence. If no tables are
specified, it will load all supported ones. A callback function can be provided
which will be called as func(current, total, tableName).

		This method should be used in the following situations:
		- The ConfigMgr instance is going to be used in a multi-threaded app.
		- The Application wants to load all data at once instead of on access.
		"""

		if debug:
			self._debug = True
			start = time.clock()
			print >>sys.stderr, "LOADING STATIC DATABASE"
			print >>sys.stderr, "  machoCachePath:", self.cache.machocachepath
			print >>sys.stderr, "  machoVersion:", self.cache.machoVersion
			print >>sys.stderr, "  bulk system path:", self.cache.BULK_SYSTEM_PATH
			print >>sys.stderr, "  bulk cache path:", self.cache.BULK_CACHE_PATH
		try:
			if tables is None:
				# preload everything.
				tables = self.tables
			else:
				# preload specified only.
				tables = frozenset(tables)
				invalid = tables - self.tables
				if invalid:
					raise ValueError("Unknown table(s): %s" % ", ".join(invalid))

			current = 0
			total = len(tables)
		
			for tableName in tables:

				if callback:
					callback(current, total, tableName)
					current += 1

				if debug:
					print >>sys.stderr, "  priming:", tableName
				# now simply trigger the property's getters
				getattr(self, tableName)

		finally:
			if debug:
				self._debug = False

		if debug:
			t = time.clock() - start
			print >>sys.stderr, "Priming took %ss (of which %.4f decoding)" % (t, self.cache._time_load)


	def GetTypeVolume(self, typeID, singleton=1, qty=1):
		"""Returns total volume of qty units of typeID. 
		Uses packaged volume if singleton is non-zero.
		"""
		if typeID == const.typePlasticWrap:
			raise RuntimeError("GetTypeVolume: cannot determine volume of plastic from type alone")

		rec = cfg.invtypes.Get(typeID)
		if rec.Group().categoryID == const.categoryShip and not singleton and rec.groupID in self.__containerVolumes__ and typeID != const.typeBHMegaCargoShip:
			volume = self.__containerVolumes__[rec.groupID]
		else:
			volume = rec.volume

		if volume != -1:
			return volume * qty

		return volume


	def GetTypeAttrDict(self, typeID):
		"""Returns (cached) dictionary of attributes for specified type."""
		attr = self._attrCache.get(typeID, None)
		if attr is None:
			self._attrCache[typeID] = attr = {}
			for row in self.dgmtypeattribs[typeID]:
				attr[row.attributeID] = row.value
		return attr


	def GetRequiredSkills(self, typeID):
		"""Returns list of (requiredSkillTypeID, requiredLevel) tuples."""
		attr = self.GetTypeAttrDict(typeID)
		reqs = []
		for i in xrange(1, 7):
			skillID = attr.get(getattr(const, "attributeRequiredSkill%s" % i), False)
			if skillID:
				lvl = attr.get(getattr(const, "attributeRequiredSkill%sLevel" % i), None)
				if lvl is not None:
					reqs.append((skillID, lvl))
		return reqs


	def GetTypeAttribute(self, typeID, attributeID, defaultValue=None):
		"""Return specified dogma attribute for given type, or custom default value."""
		attr = self.GetTypeAttrDict(typeID)
		return attr.get(attributeID, defaultValue)


	def GetTypeAttribute2(self, typeID, attributeID):
		"""Return specified dogma attribute for given type, or default attribute value."""
		attr = self.GetTypeAttrDict(typeID)
		value = attr.get(attributeID)
		if value is None:
			return self.dgmattribs.Get(attributeID).defaultValue
		return value


	def GetLocationWormholeClass(self, solarSystemID, constellationID, regionID):
		get = self.locationwormholeclasses.Get
		rec = get(solarSystemID) or get(constellationID) or get(regionID)
		if rec:
			return rec.wormholeClassID
		return 0


	@staticmethod
	def _GetCelestialNameDataFromLocalRow(row):
		celestialGroupID = row['groupID']
		celestialNameID = row['celestialNameID']

		if celestialNameID is not None and celestialGroupID != const.groupStargate:
			label = 'UI/Util/GenericText'
			param = {'text': celestialNameID}
		elif celestialGroupID == const.groupAsteroidBelt:
			label = 'UI/Locations/LocationAsteroidBeltFormatter'
			param = {'solarSystemID': row['solarSystemID'], 'romanCelestialIndex': util.IntToRoman(row['celestialIndex']), 'typeID': row['typeID'], 'orbitIndex': row['orbitIndex']}
		elif celestialGroupID == const.groupMoon:
			label = 'UI/Locations/LocationMoonFormatter'
			param = {'solarSystemID': row['solarSystemID'], 'romanCelestialIndex': util.IntToRoman(row['celestialIndex']), 'orbitIndex': row['orbitIndex']}
		elif celestialGroupID == const.groupPlanet:
			label = 'UI/Locations/LocationPlanetFormatter'
			param = {'solarSystemID': row['solarSystemID'], 'romanCelestialIndex': util.IntToRoman(row['celestialIndex'])}
		elif celestialGroupID == const.groupStargate:
			label = 'UI/Locations/LocationStargateFormatter'
			param = {'destinationSystemID': row['celestialNameID']}
		elif celestialGroupID == const.groupSun:
			label = 'UI/Locations/LocationStarFormatter'
			param = {'solarSystemID': row['solarSystemID']}
		else:
			label = None
			param = None

		return label, param


	def GetCelestialNameFromLocalRow(self, row):
		# row keys:
		# ['celestialID', 'celestialNameID', 'solarSystemID', 'typeID', 'groupID', 'radius', 'x', 'y', 'z', 'orbitID', 'orbitIndex', 'celestialIndex']

		if self._languageID:
			# Fetch name through cerberus
			label, param = self._GetCelestialNameDataFromLocalRow(row)
			return self._localization.GetByLabel(label, **param)

		celestialGroupID = row['groupID']
		celestialNameID = row['celestialNameID']

		if celestialNameID is not None and celestialGroupID != const.groupStargate:
			try:
				return const._NAMED_CELESTIALS[row['celestialID']]
			except KeyError:
				raise RuntimeError("Hardcoded celestial names table incomplete.")

		if celestialGroupID == const.groupAsteroidBelt:
			return "%s %s - %s %d" % (
				self.solarsystems.Get(row['solarSystemID']).solarSystemName, util.IntToRoman(row['celestialIndex']), self.invtypes.Get(row['typeID']).name, row['orbitIndex'])
		elif celestialGroupID == const.groupMoon:
			return "%s %s - Moon %d" % (
				self.solarsystems.Get(row['solarSystemID']).solarSystemName, util.IntToRoman(row['celestialIndex']), row['orbitIndex'])
		elif celestialGroupID == const.groupPlanet:
			return "%s %s" % (
				self.solarsystems.Get(row['solarSystemID']).solarSystemName, util.IntToRoman(row['celestialIndex']))
		elif celestialGroupID == const.groupStargate:
			return self.solarsystems.Get(row['celestialNameID']).solarSystemName
		elif celestialGroupID == const.groupSun:
			return "%s - Star" % self.solarsystems.Get(row['solarSystemID']).solarSystemName
		else:
			return ""


	def GetNPCStationNameFromLocalRow(self, row):
		if self._languageID:
			if row['useOperationName']:
				operationNameID = self.staoperationtypes.Get(row['operationID']).operationNameID
				operationName = self._localization.GetByMessageID(operationNameID)
				#operationNameEN = self._localization.GetByMessageID(operationNameID, "en-us")
			else:
				operationName = ''
				#operationNameEN = ''
			locName = self._localization.GetByLabel('UI/Locations/LocationNPCStationFormatter', orbitID=row['orbitID'], corporationID=row['ownerID'], operationName=operationName)
			#locNameEN = localization.GetByLabel('UI/Locations/LocationNPCStationFormatter', "en-us", orbitID=row['orbitID'], corporationID=row['ownerID'], operationName=operationNameEN)
			#return localization.FormatImportantString(locName, locNameEN)
			return locName

		# non-cerberus version
		return self.stations.Get(row['stationID']).stationName


	def GetLocationsLocalBySystem(self, solarSystemID):
		data = []

		# local aliasing ftw.
		append = data.append
		DBRow = blue.DBRow
		get = self.invtypes.Get

		sql = 'SELECT * FROM celestials WHERE solarSystemID=%d' % solarSystemID
		rs = self.localdb.execute(sql)
		for row in rs:
			celestialName = self.GetCelestialNameFromLocalRow(row)
			append(DBRow(_solarSystemObjectRowDescriptor, [
				row['groupID'], row['typeID'], row['celestialID'],
				celestialName, solarSystemID, row['orbitID'], None,
				row['x'], row['y'], row['z']
			]))

		sql = 'SELECT * FROM npcStations WHERE solarSystemID=%d' % solarSystemID
		rs = self.localdb.execute(sql)
		for row in rs:
			celestialName = self.GetNPCStationNameFromLocalRow(row)
			append(DBRow(_solarSystemObjectRowDescriptor, [
				get(row['typeID']).groupID, row['typeID'], row['stationID'],
				celestialName, solarSystemID, row['orbitID'], None,
				row['x'], row['y'], row['z']
			]))

		return dbutil.CRowset(_solarSystemObjectRowDescriptor, data)
