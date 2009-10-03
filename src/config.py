"""Interface to bulkdata

- loads and prepares the bulkdata for use (on demand)
- provides container classes for record and row data.
- provides interface to the database tables

Copyright (c) 2003-2009 Jamie "Entity" van den Berge <jamie@hlekkir.com>

This code is free software; you can redistribute it and/or modify
it under the terms of the BSD license (see the file LICENSE.txt
included with the distribution).

Parts of code inspired by or based on EVE Online, with permission from CCP.
"""

# TODO:
# - multi language support :)

import os
import time
import sys

from . import const, util, dbutil

_urga = util.Row.__getattr__


class RecordsetIterator(object):
	def next(self):
		return self.rowset.rowclass(self.rowset, self.iter.next())

class Recordset(object):
	def __init__(self, rowclass, keycolumn):
		self.rowclass = rowclass
		self.keycolumn = keycolumn
		self.header = {}
		self.data = {}

	def Get(self, *args):
		return self.data.get(*args)

	def GetIfExists(self, *args):
		return self.data.get(*args)

	def __iter__(self):
		it = RecordsetIterator()
		it.rowset = self
		it.iter = self.data.iterkeys()
		return it

	def __contains__(self, key):
		return key in self.data


class ItemsRecordset(Recordset):
	pass



class Record(object):
	def Get(self, *args):
		return self.__dict__.get(*args)

	def Update(self, dict):
		if self.__primary__ in dict:
			raise ValueError, "Cannot update primary key '%s' of record" % self.__primary__

		for k in dict.iterkeys():
			if k not in self.__fields__:
				raise IndexError, "Record has no field '%s'" % k

		self.__dict__.update(dict)

class OwnerRecord(Record):
	__primary__ = "ownerID"
	__fields__ = ['ownerID', 'ownerName', 'typeID', 'allianceID', 'corpID', 'role', 'corpRole']

	def __init__(self, ownerID, dict=None):
		self.ownerID = ownerID
		self.ownerName = None
		if dict:
			self.Update(dict)

	def __getattr__(self, attr):
		if attr == "name":
			attr = "ownerName"
		return Record.__getattr__(self, attr)

	def __repr__(self):
		return "<OwnerRecord %s: '%s'>" % (self.ownerID, self.ownerName)


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
		if attr == "name":
			return _urga(self, "typeName")
		return _urga(self, attr)

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
		if attr == "name":
			return _urga(self, "groupName")
		if attr == "id":
			return _urga(self, "groupID")
		return _urga(self, attr)


class InvCategory(util.Row):
	__guid__ = "sys.InvCategory"

	def __getattr__(self, attr):
		if attr == "name":
			return _urga(self, "categoryName")
		if attr == "id":
			return _urga(self, "categoryID")
		return _urga(self, attr)

	def IsHardware(self):
		return self.categoryID == const.categoryModule


class InvMetaGroup(util.Row):
	def __getattr__(self, name):
		if name == "_metaGroupName":
			return _urga(self, "metaGroupName")

		if name == "name":
			name = "metaGroupName"

		value = _urga(self, name)
#		if name == "metaGroupName":
#			return self.cfg.Tr(value, "inventory.metaGroups.metaGroupName", self.dataID)
		return value


class DgmAttribute(util.Row):
	def __getattr__(self, name):
		value = _urga(self, name)
#		if name == "displayName":
#			return self.cfg.Tr(value, "dogma.attributes.displayName", self.dataID)
		return value


class DgmEffect(util.Row):
	def __getattr__(self, name):
		value = _urga(self, name)
#		if name == "displayName":
#			return self.cfg.Tr(value, "dogma.effects.displayName", self.dataID)
#		if name == "description":
#			return self.cfg.Tr(value, "dogma.effects.description", self.dataID)
		return value


class EveGraphics(util.Row):
	def __getattr__(self, name):
		if name == "name" or name == "description":
			return self.icon
		else:
			return _urga(self, name)

	def __str__(self):
		return "EveGraphic ID: %d, \"%s\"" % (self.graphicID, self.icon)


class EveOwners(util.Row):
	def __getattr__(self, name):
		if name == "name" or name == "description":
			name = "ownerName"
		elif name == "groupID":
			return self.cfg.invtypes.Get(self.typeID).groupID

		value = _urga(self, name)
#		if name == "ownerName" and IsSystemOrNPC(self.ownerID):
#			return self.cfg.Tr(value, "dbo.eveNames.itemName", self.ownerID)
		return value


	def __str__(self):
		return "EveOwner ID: %d, \"%s\"" % (self.ownerID, self.ownerName)

	def Type(self):
		return self.cfg.invtypes.Get(self.typeID)

	def Group(self):
		return self.cfg.invgroups.Get(self.groupID)


class EveLocations(util.Row):
	__guid__ = "dbrow.Location"

	def __getattr__(self, name):
		if name == "name" or name == "description":
			name = "locationName"
		value = _urga(self, name)
		return value

	def __str__(self):
		return "EveLocation ID: %d, \"%s\"" % (self.locationID, self.locationName)

#	def Station(self):
#		return self.cfg.GetSvc("stationSvc").GetStation(self.id)



class RamCompletedStatus(util.Row):
	def __getattr__(self, name):
		if name == "name":
			name = "completedStatusName"
    
		value = _urga(self, name)
#		if name == "completedStatusName":
#			return self.cfg.Tr(value, "dbo.ramCompletedStatuses.completedStatusText", self.completedStatusID)
#		elif name == "description":
#			return self.cfg.Tr(value, "dbo.ramCompletedStatuses.description", self.completedStatusID)
		return value

	def __str__(self):
		try:
			return "RamCompletedStatus ID: %d, \"%s\"" % (self.completedStatusID, self.completedStatusName)
		except:
			sys.exc_clear()
			return "RamCompletedStatus containing crappy data"


class RamActivity(util.Row):
	def __getattr__(self, name):
    
		if name == "name":
			name = "activityName"
    
		value = _urga(self, name)
#		if name == "activityName":
#			return self.cfg.Tr(value, "dbo.ramActivities.activityName", self.activityID)
#		elif name == "description":
#			return self.cfg.Tr(value, "dbo.ramActivities.description", self.activityID)
		return value

	def __str__(self):
		try:
			return "RamActivity ID: %d, \"%s\"" % (self.activityID, self.activityName)
		except:
			sys.exc_clear()
			return "RamActivity containing crappy data"



class MapCelestialDescription(util.Row):
	def __getattr__(self, name):
		value = _urga(self, name)
#		if name == "description":
#			return self.cfg.Tr(value, "dbo.mapCelestialDescriptions.description", self.celestialID)
		return value

	def __str__(self):
		return "MapCelestialDescriptions ID: %d" % (self.celestialID)



class CrpTickerNames(util.Row):
	def __getattr__(self, name):
		if name == "name" or name == "description":
			return self.tickerName
		else:
			return _urga(self, name)

	def __str__(self):
		return "CorpTicker ID: %d, \"%s\"" % (self.corporationID, self.tickerName)


class AllShortNames(util.Row):
	def __getattr__(self, name):
		if name == "name" or name == "description":
			return self.shortName
		else:
			return _urga(self, name)

	def __str__(self):
		return "AllianceShortName ID: %d, \"%s\"" % (self.allianceID, self.shortName)


class Certificate(util.Row):
	def __getattr__(self, name):
		value = _urga(self, name)
#		if name == "description":
#			return self.cfg.Tr(value, "cert.certificates.description", self.dataID)
		return value

	def __str__(self):
		return "Certificate ID: %d" % (self.certificateID)


class Dud(object):
	pass


class memoize(object):
	"""single-shot memoizing descriptor"""
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


class Config(object):

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
		const.groupMothership: 1000000.0,
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
		}


	# on-demand loaders for each table follow

	@memoize
	def invcategories(self):
		return self._loadfrombulk("categories", self.defaults.invcategories)

	@memoize
	def invgroups(self):
		return self._loadfrombulk("groups", self.defaults.invgroups)

	@memoize
	def metagroups(self):
		return self._loadfrombulk("metagroups", self.defaults.invmetagroups)

	@memoize
	def invtypes(self):
		return self._loadfrombulk("types", self.defaults.invtypes)

	@memoize
	def invbptypes(self):
		return self._loadfrombulk("bptypes", self.defaults.invbptypes)

	@memoize
	def eveowners(self):
		rs = self._loadfrombulk("owners", self.defaults.eveowners)
		self._loadfrombulk("config.StaticOwners", rs, hint=1)
		return rs

	@memoize
	def corptickernames(self):
		return self._loadfrombulk("tickernames", self.defaults.corptickernames)

	@memoize
	def allianceshortnames(self):
		return self._loadfrombulk("allianceshortnames", self.defaults.allianceshortnames)

	@memoize
	def certificates(self):
		return self._loadfrombulk("certificates", self.defaults.certificates)

	@memoize
	def certificaterelationships(self):
		return self._loadfrombulk("certificaterelationships", self.defaults.certificaterelationships)

	@memoize
	def evegraphics(self):
		return self._loadfrombulk("graphics", self.defaults.evegraphics)

	@memoize
	def eveunits(self):
		return self._loadfrombulk("units", self.defaults.eveunits)

	@memoize
	def groupsByCategories(self):
		if self.compatibility:
			self.groupsByCategories = util.FilterRowset(self.invgroups.header, self.invgroups.data.values(), "categoryID")
		else:
			self.groupsByCategories = self.invgroups.GroupedBy("categoryID")
		return self.groupsByCategories

	@memoize
	def typesByGroups(self):
		if self.compatibility:
			self.typesByGroups = util.FilterRowset(self.invtypes.header, self.invtypes.data.values(), "groupID")
		else:
			self.typesByGroups = self.invtypes.GroupedBy("groupID")
		return self.typesByGroups

	@memoize
	def typesByMarketGroups(self):
		if self.compatibility:
			self.typesByMarketGroups = util.FilterRowset(self.invtypes.header, self.invtypes.data.values(), "marketGroupID")
		else:
			self.typesByMarketGroups = self.invtypes.GroupedBy("marketGroupID")
		return self.typesByMarketGroups

	@memoize
	def shiptypes(self):
		obj = self.cache.LoadObject("config.BulkData.shiptypes")
		if type(obj) is tuple:
			# old style.
			self.shiptypes = util.IndexRowset(obj[0], obj[1], "shipTypeID")
		else:
			self.shiptypes = util.IndexRowset(obj.header.Keys(), list(obj), "shipTypeID")
		return self.shiptypes


	def _invmetatypes_load(self):
		obj = self.cache.LoadObject("config.BulkData.invmetatypes")
		if type(obj) is tuple:
			# old style.
			self.invmetatypes = util.FilterRowset(obj[0], obj[1], "parentTypeID")
			self.invmetatypesByTypeID = util.FilterRowset(obj[0], obj[1], "typeID")
		else:
			self.invmetatypes = util.FilterRowset(obj.header.Keys(), list(obj), "parentTypeID")
			self.invmetatypesByTypeID = util.FilterRowset(obj.header.Keys(), list(obj), "typeID")

	@memoize
	def invmetatypes(self):
		self._invmetatypes_load()
		return self.invmetatypes

	@memoize
	def invmetatypesByTypeID(self):
		self._invmetatypes_load()
		return self.invmetatypesByTypeID

	@memoize
	def dgmattribs(self):
		return self._loadfrombulk("dgmattribs", self.defaults.dgmattribs, "IndexRowset", "attributeID", RowClass=DgmAttribute)

	@memoize
	def dgmeffects(self):
		return self._loadfrombulk("dgmeffects", self.defaults.dgmeffects, "IndexRowset", "effectID", RowClass=DgmEffect)

	@memoize
	def dgmtypeattribs(self):
		return self._loadfrombulk("dgmtypeattribs", self.defaults.dgmtypeattribs, "IndexedRowLists", "typeID")

	@memoize
	def dgmtypeeffects(self):
		return self._loadfrombulk("dgmtypeeffects", self.defaults.dgmtypeeffects, "IndexedRowLists", "typeID")

	@memoize
	def ramaltypes(self):
		return self._loadfrombulk("ramaltypes", self.defaults.ramaltypes)

	@memoize
	def ramactivities(self):
		return self._loadfrombulk("ramactivities", self.defaults.ramactivities)

	@memoize
	def ramcompletedstatuses(self):
		return self._loadfrombulk("ramcompletedstatuses", self.defaults.ramcompletedstatuses)

	@memoize
	def invtypereactions(self):
		return self._loadfrombulk("invtypereactions", self.defaults.invreactiontypes, "FilterRowset", "reactionTypeID")

	@memoize
	def ramaltypesdetailpercategory(self):
		return self._loadfrombulk("ramaltypesdetailpercategory", self.defaults.ramaltypesdetailpercategory, "FilterRowset", "assemblyLineTypeID")

	@memoize
	def ramaltypesdetailpergroup(self):
		return self._loadfrombulk("ramaltypesdetailpergroup", self.defaults.ramaltypesdetailpergroup, "FilterRowset", "assemblyLineTypeID")

	@memoize
	def ramtypematerials(self):
		return self._loadfrombulk("ramtypematerials", self.defaults.ramtypematerials, "special1")

	@memoize
	def ramtyperequirements(self):
		return self._loadfrombulk("ramtyperequirements", self.defaults.ramtyperequirements, "special2")

	@memoize
	def evelocations(self):
		rs = self._loadfrombulk("locations", self.defaults.evelocations)
		self._loadfrombulk("config.StaticLocations", rs, hint=1)
		return rs

	@memoize
	def mapcelestialdescriptions(self):
		return self._loadfrombulk("mapcelestialdescriptions", self.defaults.mapcelestialdescriptions)

	@memoize
	def locationwormholeclasses(self):
		return self._loadfrombulk("locationwormholeclasses", self.defaults.locationwormholeclasses)


	def _invcontrabandtypes_load(self):
		self.invcontrabandTypesByFaction = {}
		self.invcontrabandFactionsByType = {}
		obj = self.cache.LoadObject("config.InvContrabandTypes")
		for each in obj:
			if each.factionID not in self.invcontrabandTypesByFaction:
				self.invcontrabandTypesByFaction[each.factionID] = {}
			self.invcontrabandTypesByFaction[each.factionID][each.typeID] = each
			if each.typeID not in self.invcontrabandFactionsByType:
				self.invcontrabandFactionsByType[each.typeID] = {}
			self.invcontrabandFactionsByType[each.typeID][each.factionID] = each

	@memoize
	def invcontrabandTypesByFaction(self):
		self._invcontrabandtypes_load()
		return self.invcontrabandTypesByFaction

	@memoize
	def invcontrabandTypesByFaction(self):
		self._invcontrabandtypes_load()
		return self.invcontrabandFactionsByType



	def __init__(self, cache, compatibility=False):
		self.cache = cache
		self.callback = None
		self.compatibility = compatibility

		self.tables = frozenset((tableName for tableName in dir(self.__class__) if isinstance(getattr(self.__class__, tableName), memoize)))

		# define default table properties

		defaults = self.defaults = Dud()

		defaults.invcategories = Recordset(InvCategory, "categoryID")
		defaults.invgroups = Recordset(InvGroup, "groupID")
		defaults.invmetagroups = Recordset(InvMetaGroup, "metaGroupID")
		defaults.invtypes = Recordset(InvType, "typeID")
		defaults.invbptypes = Recordset(util.Row, "blueprintTypeID")
		defaults.dgmattribs = ItemsRecordset(DgmAttribute, "attributeID")
		defaults.dgmeffects = ItemsRecordset(DgmEffect, "effectID")
		defaults.dgmtypeeffects = util.FilterRowset()
		defaults.dgmtypeattribs = util.FilterRowset()
		defaults.invmetatypes = util.FilterRowset()

		defaults.invreactiontypes = util.FilterRowset()

		defaults.evegraphics = Recordset(EveGraphics, "graphicID")
		defaults.eveunits = Recordset(util.Row, "unitID")
		defaults.eveowners = Recordset(EveOwners, "ownerID")
		defaults.evelocations = Recordset(EveLocations, "locationID")
		defaults.corptickernames = Recordset(CrpTickerNames, "corporationID")
		defaults.allianceshortnames = Recordset(AllShortNames, "allianceID")

		defaults.ramaltypes = Recordset(util.Row, "assemblyLineTypeID")
		defaults.ramaltypesdetailpercategory = util.FilterRowset()
		defaults.ramaltypesdetailpergroup = util.FilterRowset()
		defaults.ramactivities = Recordset(RamActivity, "activityID")
		defaults.ramtyperequirements = {}
		defaults.ramtypematerials = Recordset(util.Row, "typeID")
		defaults.ramcompletedstatuses = Recordset(RamCompletedStatus, "completedStatusID")
		defaults.mapcelestialdescriptions = Recordset(MapCelestialDescription, "celestialID")

		defaults.certificates = Recordset(Certificate, "certificateID")
		defaults.certificaterelationships = Recordset(util.Row, "relationshipID")

		defaults.locationwormholeclasses = Recordset(util.Row, "locationID")

		self._attrCache = {}


	def release(self):
		for tableName in self.tables:
			delattr(self, tableName)
		self._attrCache = {}

	def _loadfrombulk(self, this, dst, typ=None, key=None, RowClass=None, hint=False):

		# get table name.
		if not hint:
			for tableName, table in self.defaults.__dict__.iteritems():
				if table is dst:
					break

		if this.startswith("config."):
			what = this
		else:
			what = "config.BulkData." + this

		obj = self.cache.LoadObject(what)

		if typ is None:
			# Simple load (IndexRowset compatible)

			if self.compatibility:
				if type(obj) == dbutil.CRowset:
					table.header = obj.header.Keys()
					table.data.clear()
					keycol = obj.header.Keys().index(table.keycolumn)
					for i in obj:
						a = list(i)
						table.data[a[keycol]] = a
				else:
					table.data.clear()
					table.header = obj[0]            
					keycol = table.header.index(dst.keycolumn)
					for i in obj[1]:
						table.data[i[keycol]] = i
			else:
				# Custom loading. Slightly faster and more powerful.
				if hint:
					# if this is hint data, just add it to the specified table (dst)
					rs = dst

					# add the lines
					rs.lines.extend(obj.lines)

					# fix index
					ki = rs.key
					i = rs.items
					for line in obj.lines:
						i[line[ki]] = line
				else:
					if type(obj) == dbutil.CRowset:
						rs = util.IndexRowset(obj.header.Keys(), obj, key=table.keycolumn, RowClass=table.rowclass, cfgInstance=self)
					else:
						rs = util.IndexRowset(obj[0], obj[1], key=table.keycolumn, RowClass=table.rowclass, cfgInstance=self)

		else:
			# Specialized load

			if typ == "FilterRowset":
				rs = util.FilterRowset(obj.header.Keys(), list(obj), key)

			elif typ == "special1":
				rs = {}
				for row in obj:
					key = row.typeID
					if key in rs:
						rs[key].append(row)
					else:
						rs[key] = [row]

			elif typ == "special2":
				rs = {}
				for row in obj:
					key = row.typeID, row.activityID
					if key in rs:
						rs[key].append(row)
					else:
						rs[key] = [row]
	
			elif typ == "IndexRowset":
				rs = util.IndexRowset(obj[0], obj[1], key, RowClass=RowClass)

			elif typ == "IndexedRowLists":
				rs = util.IndexedRowLists(obj, (key,))

		return rs


	def prime(self, tables=None, callback=None, debug=False):
		"""Loads the tables named in the tables sequence. If no tables are
specified, it will load all supported ones. A callback function can be provided
which will be called as func(current, total, tableName).

		This function should be used in the following situations:
		- The ConfigMgr instance is going to be used in a multi-threaded app.
		- The Application wants to load all data at once instead of on access.
		"""

		if debug:
			self._debug = True
			start = time.clock()
			print >>sys.stderr, "LOADING STATIC DATABASE"
			print >>sys.stderr, "  machoCachePath:", self.cache.machocachepath
			print >>sys.stderr, "  machoVersion:", self.cache.machoVersion

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
					print "  priming:", tableName
				# now simply trigger the property's getters
				getattr(self, tableName)

		finally:
			if debug:
				self._debug = False

		if debug:
			t = time.clock() - start
			print >>sys.stderr, "Priming took %ss (of which %ss decoding)" % (t, self.cache._time_load)


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
		value = attr.get(attributeID, None)
		if value is None:
			return self.dgmattribs.Get(attributeID).defaultValue
		return value


	def GetLocationWormholeClass(self, solarSystemID, constellationID, regionID):
		rec = self.locationwormholeclasses.Get(solarSystemID, None) \
		or self.locationwormholeclasses.Get(constellationID, None) \
		or self.locationwormholeclasses.Get(regionID, None)
		if rec:
			return rec.wormholeClassID
		return 0

