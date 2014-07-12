"""Interface to bulkdata

- loads and prepares the bulkdata for use (on demand)
- provides container classes for record and row data.
- provides interface to the database tables

Copyright (c) 2003-2013 Jamie "Entity" van den Berge <jamie@hlekkir.com>

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
from . import const, util
from . import localization, fsd

# custom row containers are imported from this
from .eve.common.script.sys.eveCfg import *
from .eve.common.script.sys.rowset import IndexRowset, FilterRowset, IndexedRowLists



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
			return self._loadfsddata(staticName, schemaName, cacheNum, optimize=optimize)

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
		const.groupSpewContainer,
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
		const.groupMissileLauncherFestival,
		const.groupBubbleProbeLauncher,
		const.groupSensorBooster,
		const.groupRemoteSensorBooster,
		const.groupRemoteSensorDamper,
		const.groupTrackingComputer,
		const.groupTrackingDisruptor,
		const.groupTrackingLink,
		const.groupWarpDisruptFieldGenerator,
		const.groupFueledShieldBooster,
		const.groupFueledArmorRepairer,
		const.groupSurveyProbeLauncher,
		const.groupMissileLauncherRapidHeavy,
		const.groupDroneTrackingModules,
	)


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
		("invcategories"              , (  0,   0, IndexRowset         , InvCategory       , "categoryID"        , const.cacheInvCategories)),
		("invgroups"                  , (  0,   0, IndexRowset         , InvGroup          , "groupID"           , const.cacheInvGroups)),
		("invtypes"                   , (  0,   0, IndexRowset         , InvType           , "typeID"            , const.cacheInvTypes)),
		("invmetagroups"              , (  0,   0, IndexRowset         , InvMetaGroup      , "metaGroupID"       , const.cacheInvMetaGroups)),
		("invbptypes"                 , (  0,   0, IndexRowset         , Row               , "blueprintTypeID"   , const.cacheInvBlueprintTypes)),
		("invreactiontypes"           , (  0,   0, FilterRowset        , Row               , "reactionTypeID"    , const.cacheInvTypeReactions)),
		("shiptypes"                  , (  0,   0, IndexRowset         , Row               , "shipTypeID"        , const.cacheShipTypes)),

		("dgmattribs"                 , (  0,   0, IndexRowset         , DgmAttribute      , "attributeID"       , const.cacheDogmaAttributes)),
		("dgmeffects"                 , (  0,   0, IndexRowset         , DgmEffect         , "effectID"          , const.cacheDogmaEffects)),
		("dgmtypeattribs"             , (  0,   0, IndexedRowLists     , None              , ('typeID',)         , const.cacheDogmaTypeAttributes)),
		("dgmtypeeffects"             , (  0,   0, IndexedRowLists     , None              , ('typeID',)         , const.cacheDogmaTypeEffects)),
		("dgmexpressions"             , (297,   0, IndexRowset         , Row               , 'expressionID'      , const.cacheDogmaExpressions)),
		("dgmunits"                   , (299,   0, IndexRowset         , DgmUnit           , "unitID"            , const.cacheDogmaUnits)),

		("ramaltypes"                 , (  0,   0, IndexRowset         , Row               , "assemblyLineTypeID", const.cacheRamAssemblyLineTypes)),
		("ramactivities"              , (  0,   0, IndexRowset         , RamActivity       , "activityID"        , const.cacheRamActivities)),
		("ramcompletedstatuses"       , (276,   0, IndexRowset         , RamCompletedStatus, "completedStatus"   , const.cacheRamCompletedStatuses)),
		("ramaltypesdetailpercategory", (  0,   0, FilterRowset        , RamDetail         , "assemblyLineTypeID", const.cacheRamAssemblyLineTypesCategory)),
		("ramaltypesdetailpergroup"   , (  0,   0, FilterRowset        , RamDetail         , "assemblyLineTypeID", const.cacheRamAssemblyLineTypesGroup)),

		("billtypes"                  , (  0,   0, IndexRowset         , Billtype          , 'billTypeID'        , const.cacheActBillTypes)),

		("schematics"                 , (242,   0, IndexRowset         , Schematic         , 'schematicID'       , const.cachePlanetSchematics)),
		("ramtyperequirements"        , (242,   0, dict                , None              , ('typeID', 'activityID'), const.cacheRamTypeRequirements)),
		("invtypematerials"           , (254,   0, dict                , None              , 'typeID'            , const.cacheInvTypeMaterials)),

		# location/owner stuff.
		("factions"                   , (276,   0, IndexRowset         , Row               , "factionID"         , const.cacheChrFactions)),
		("npccorporations"            , (276,   0, IndexRowset         , Row               , "corporationID"     , const.cacheCrpNpcCorporations)),
		("corptickernames"            , (  0,   0, IndexRowset         , CrpTickerNames    , "corporationID"     , const.cacheCrpTickerNamesStatic)),

		("staoperationtypes"          , (299,   0, IndexRowset         , Row               , "operationID"       , const.cacheStaOperations)),
		("mapcelestialdescriptions"   , (276,   0, IndexRowset         , MapCelestialDescription, "itemID"       , const.cacheMapCelestialDescriptions)),
		("locationwormholeclasses"    , (  0,   0, IndexRowset         , Row               , "locationID"        , const.cacheMapLocationWormholeClasses)),

		("stations"                   , (299,   0, IndexRowset         , Row               , "stationID"         , const.cacheStaStationsStatic)),

		("nebulas"                    , (299,   0, IndexRowset         , Row               , "locationID"        , const.cacheMapNebulas)),

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

		# FSD stuff ------------------- (ver, del,  static name       , schema name       , optimize   cache size)
		("messages"                   , (378,   0, ("dialogs"         , "dialogs"         , False)   , None)),

		("fsdTypeOverrides"           , (324,   0, ("typeIDs"         , "typeIDs"         , False)   , None)),

		("graphics"                   , (324,   0, ("graphicIDs"      , "graphicIDs"      , True)    , 100 )),
		("sounds"                     , (332,   0, ("soundIDs"        , "soundIDs"        , True)    , 100 )),
		("icons"                      , (332,   0, ("iconIDs"         , "iconIDs"         , True)    , 100 )),
		("fsdDustIcons"               , (378,   0, ("dustIcons"       , None              , None )   , None)),

		("certificates"               , (391,   0, ("certificates"    , "certificates"    , False)   , None)),

		("mapRegionCache"             , (393,   0, ("regions"         , "regions"         , False)   , None)),
		("mapConstellationCache"      , (393,   0, ("constellations"  , "constellations"  , False)   , None)),
		("mapSystemCache"             , (393,   0, ("systems"         , "systems"         , False)   , None)),

		("mapJumpCache"               , (393,   0, ("jumps"           , "jumps"           , False)   , None)),

		("mapFactionsOwningSolarSystems",(393,  0, ("factionsOwningSolarSystems", "factionsOwningSolarSystems", False), None)),
		("mapCelestialLocationCache"  , (393,   0, ("locationCache"   , None              , None )   , None)),

		("mapSolarSystemContentCache" , (393,   0, ("solarSystemContent", None            , None )   , None)),
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

		rs = IndexRowset(['ownerID', 'ownerName', 'typeID', 'gender', 'ownerNameID'], None, key="ownerID", RowClass=EveOwners, cfgInstance=self)
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

		for row in self.cache.LoadBulk(const.cacheChrNpcCharacters):
			id_ = row.characterID
			npcName = self._localization.GetImportantByMessageID(id_) or row.characterName
			d[id_] = DBRow(rd, [id_, row.characterName, bloodlinesToTypes[row.bloodlineID], row.gender, row.characterNameID])

		auraName = self._localization.GetImportantByLabel(_OWNER_NAME_OVERRIDES[_OWNER_AURA_IDENTIFIER])
		sysName = self._localization.GetByLabel(_OWNER_NAME_OVERRIDES[_OWNER_SYSTEM_IDENTIFIER])

		d[1] = blue.DBRow(rd, [1, sysName, 0, None, None])

		rs.lines = rs.items.values()
		return rs


	@_memoize
	def evelocations(self):
		rs = IndexRowset(['locationID', 'locationName', 'x', 'y', 'z', 'locationNameID'], None, key="locationID", RowClass=EveLocations, cfgInstance=self)

		rd = blue.DBRowDescriptor((
			('locationID', const.DBTYPE_I4),
			('locationName', const.DBTYPE_WSTR),
			('x', const.DBTYPE_R8),
			('y', const.DBTYPE_R8),
			('z', const.DBTYPE_R8),
			('locationNameID', const.DBTYPE_I4),
		))

		DBRow = blue.DBRow

		_trans = self._localization.GetImportantByMessageID
		d = rs.items
		for fsdtable in (self.mapRegionCache, self.mapConstellationCache, self.mapSystemCache):
			for itemID, item in fsdtable.iteritems():
				c = item.center
				d[itemID] = DBRow(rd, [itemID, _trans(item.nameID), c.x, c.y, c.z, item.nameID])

		# code below requires the partially completed table.
		self.evelocations = rs

#		# This stuff below takes 12 seconds on my i7.
#		# TODO: find solution (dynamic lookup, I suppose ...)
#
#		# get stars, planets, belts and moons.
#		for row in self.localdb.execute("SELECT * FROM celestials"):
#			celestialName = self.GetCelestialNameFromLocalRow(row)
#			cid = row["celestialID"]
#			d[cid] = blue.DBRow(rd, [cid, celestialName, row["x"], row["y"], row["z"], 0])
#
#		# stations
#		_gbm = self._localization.GetByMessageID
#		_gbl = self._localization.GetByLabel
#		_sot = self.staoperationtypes.Get
#		for row in self.localdb.execute("SELECT * FROM npcStations"):
#			if row["isConquerable"]:
#				continue
#			stationID = row["stationID"]
#			operationName = _gbm(_sot(row["operationID"]).operationNameID) if row["useOperationName"] else ""
#			stationName = _gbl('UI/Locations/LocationNPCStationFormatter', orbitID=row["orbitID"], corporationID=row["ownerID"], operationName=operationName)
#			d[stationID] = DBRow(rd, [stationID, stationName, row["x"], row["y"], row["z"], 0])

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
		self.schematicstypemap = FilterRowset(header, obj, "schematicID")
		self.schematicsByType = FilterRowset(header, obj, "typeID")

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
		self.schematicspinmap = FilterRowset(header, obj, "schematicID")
		self.schematicsByPin = FilterRowset(header, obj, "pinTypeID")

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
		self.invmetatypes = FilterRowset(header, obj, "parentTypeID")
		self.invmetatypesByTypeID = FilterRowset(header, obj, "typeID")

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
		return localization.Localization(self.cache.root, self._languageID, cfgInstance=self)

	@_memoize
	def _averageMarketPrice(self):
		return self._eve.RemoteSvc("config").GetAverageMarketPricesForClient()

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

		self.localdb = sqlite3.connect(os.path.join(self.cache.root, "bin", "staticdata", "mapObjects.db"))
		self.localdb.row_factory = sqlite3.Row


		# DEPRECATED: look for fsd library in EVE install
		ccplibpath = os.path.join(self.cache.root, "lib")

		for fsdlib in glob.glob(os.path.join(ccplibpath, "fsdSchemas-*.zip")):
			break
		else:
			fsdlib = ccplibpath if os.path.exists(os.path.join(ccplibpath, "fsdCommon")) else None
		
		if fsdlib:
			sys.path.append(fsdlib)

			# import the important function!
			import fsdSchemas.binaryLoader as fsdBinaryLoader
			self._fsdBinaryLoader = fsdBinaryLoader

			fsdBinaryLoader.log.setLevel(-1)  # shut logging up

			# All set to use EVE's FSD code directly.
			# (patch the instance to use the alternative loader)
			self._loadfsddata = self._loadfsddata_usingccplib
		

	def release(self):
		# purge all loaded tables

		for tableList in (self.tables, ("_averageMarketPrice",)):
			for tableName in tableList:
				try:
					delattr(self, tableName)
				except AttributeError:
					pass

		self.cache._time_load = 0.0
		self._attrCache = {}


	def _loadfsddata_usingccplib(self, staticName, schemaName, cacheNum, optimize):
		# odyssey fsd loader (uses CCP code directly)
		# deprecated in ody1.1, but still works if fsd lib is present
		from . import blue as bloo

		# must patch our ResFile temporarily for CCP code to work.
		_rf = bloo.ResFile
		bloo.ResFile = self._eve.ResFile

		try:
			if optimize is None:
				optimize = True
			staticName = 'res:/staticdata/%s.static' % staticName
			schemaName = 'res:/staticdata/%s.schema' % schemaName if schemaName else None
			return self._fsdBinaryLoader.LoadFSDDataForCFG(staticName, schemaName, optimize=optimize)
		finally:
			bloo.ResFile = _rf


	def _loadfsddata(self, staticName, schemaName, cacheNum, optimize):
		# Custom FileStaticData loader.
		# Grabs schema and binary blob from .stuff file.
		res = self._eve.ResFile()

		schema = None
		if staticName:
			resFileName = "res:/staticdata/%s.schema" % schemaName
			if res.Open(resFileName):
				schema = fsd.LoadSchema(res.Read())
				if optimize:
					schema = fsd.OptimizeSchema(schema)

		resFileName = "res:/staticdata/%s.static" % staticName
		if not res.Open(resFileName):
			raise RuntimeError("Could not load FSD static data '%s'" % resFileName)

		try:
			# This will throw an error if there is no embedded schema.
			# As it is hardcoded in EVE whether a static data file comes
			# with an embedded schema, we just try to load it anyway.
			# if it fails, the previously loaded schema should still be there.
			schema, offset = fsd.LoadEmbeddedSchema(res.fh)
		except RuntimeError:
			offset = 0

		if schema is None:
			raise RuntimeError("No schema found for %s" % tableName)

		fsd.PrepareSchema(schema)

		if schema.get('multiIndex'):
			# Disk-based access for multi index tables because only the
			# FSD_MultiIndex class can handle them properly.
			return fsd.LoadIndexFromFile(res.fh, schema, cacheNum, offset=offset)

		# any other table will use memory-based access because they are pretty
		# small anyway, and they are considerably faster when used like this.
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
		
		if issubclass(storageClass, IndexRowset):
			rs = storageClass(obj.header.Keys(), obj, key=primaryKey, RowClass=rowClass, cfgInstance=self)

		elif issubclass(storageClass, FilterRowset):
			rs = storageClass(obj.header.Keys(), obj, primaryKey, RowClass=rowClass)

		elif issubclass(storageClass, IndexedRowLists):
			rs = storageClass(obj, keys=primaryKey)

		elif issubclass(storageClass, dict):
			rs = {}
			if type(primaryKey) is tuple:
				# composite key
				getkey = lambda r, k: tuple(map(r.__getitem__, k))
			else:
				getkey = getattr

			_get = rs.get
			for row in obj:
				key = getkey(row, primaryKey)
				li = _get(key)
				if li is None:
					rs[key] = [row]
				else:
					li.append(row)
		else:
			raise RuntimeError("Invalid storageClass: %s" % storageClass)

		return rs


	def prime(self, tables=None, callback=None, debug=False, onlyFSD=False):
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
				if onlyFSD and len(self._tables[tableName]) != 4:
					continue

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

		rec = self.invtypes.Get(typeID)
		volume = rec.volume
		if not singleton and typeID != const.typeBHMegaCargoShip:
			volume = const.shipPackagedVolumesPerGroup.get(rec.groupID, volume)

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


	def GetCelestialNameFromLocalRow(self, row):
		# row keys:
		# ['celestialID', 'celestialNameID', 'solarSystemID', 'typeID', 'groupID', 'radius', 'x', 'y', 'z', 'orbitID', 'orbitIndex', 'celestialIndex']

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

		return self._localization.GetByLabel(label, **param)


	def GetNPCStationNameFromLocalRow(self, row):
		operationName = self._localization.GetByMessageID(self.staoperationtypes.Get(row['operationID']).operationNameID) if row['useOperationName'] else ""
		return self._localization.GetByLabel('UI/Locations/LocationNPCStationFormatter', orbitID=row['orbitID'], corporationID=row['ownerID'], operationName=operationName)


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
