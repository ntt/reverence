"""
Minimal Cerberus (localization subsystem) implementation.

This code is free software; you can redistribute it and/or modify
it under the terms of the BSD license (see the file LICENSE.txt
included with the distribution).

Part of this code is inspired by or based on EVE Online.
Used with permission from CCP.
"""

# Note: If I had to write about all the stuff that is wrong with the Cerberus
# code in the EVE client, this script file would probably be twice as big.

import os
import cPickle

import gc

from . import embedfs


class BasePropertyHandler(object):
	__id__ = 10

	def __init__(self, localizationInstance, cfgInstance):
		self.cfg = cfgInstance
		self.localization = localizationInstance

	def default(self, value, languageID, **kwargs):
		return value


class MessageIDPropertyHandler(BasePropertyHandler):
	__id__ = 5

	def default(self, value, languageID, **kwargs):
		return self.localization.GetByMessageID(value, languageID)


class LocationPropertyHandler(BasePropertyHandler):
	__id__ = 3

	def name(self, locationID, languageID, *args, **kwargs):
		return self.cfg.evelocations.Get(locationID).locationName or 'None'

	def rawName(self, locationID, languageID, *args, **kwargs):
		return self.cfg.evelocations.Get(locationID).GetRawName(languageID)


class ItemPropertyHandler(BasePropertyHandler):
	__id__ = 2

	def name(self, itemID, languageID, *args, **kwargs):
		return self.cfg.invtypes.Get(itemID).typeName or 'None'

	def rawName(self, itemID, languageID, *args, **kwargs):
		return self.cfg.invtypes.Get(itemID).GetRawName(languageID)


class NpcOrganizationPropertyHandler(BasePropertyHandler):
	__id__ = 1

	def name(self, npcOrganizationID, languageID, *args, **kwargs):
		#if const.minFaction <= npcOrganizationID <= const.maxFaction or const.minNPCCorporation <= npcOrganizationID <= const.maxNPCCorporation:
		return self.cfg.eveowners.Get(npcOrganizationID).name


	def rawName(self, npcOrganizationID, languageID, *args, **kwargs):
		#if const.minFaction <= npcOrganizationID <= const.maxFaction or const.minNPCCorporation <= npcOrganizationID <= const.maxNPCCorporation:
		return self.cfg.eveowners.Get(npcOrganizationID).GetRawName(languageID)


class NumericPropertyHandler(BasePropertyHandler):
	__id__ = 9


class Localization(object):

	def __init__(self, root, languageID="en-us", cfgInstance=None):
		self.cfg = cfgInstance or cfg

		self._propertyHandlers = {}
		for cls in globals().itervalues():
			if isinstance(cls, type) and issubclass(cls, BasePropertyHandler):
				self._propertyHandlers[cls.__id__] = cls(self, cfgInstance)

		stuff = embedfs.EmbedFS(os.path.join(root, "resLocalization.stuff"))
		stuffFSD = embedfs.EmbedFS(os.path.join(root, "resLocalizationFSD.stuff"))

		def _loadlanguage(languageID, s1, s2):
			x, data = cPickle.loads(s1.open("res/localization/localization_%s.pickle" % languageID).read())
			data.update(cPickle.loads(s2.open("res/localizationFSD/localization_fsd_%s.pickle" % languageID).read())[1])
			return data

		self.languageID = languageID

		# load primary language
		self.primary = _loadlanguage(languageID, stuff, stuffFSD)

		# if the primary language isn't english, load the english pack as fallback
		if languageID != "en-us":
			self.fallback = _loadlanguage("en-us", stuff, stuffFSD)
		else:
			self.fallback = None

		self.languageLabels = {}

		# load labels
		for efs, resname in (
			(stuff, "res/localization/localization_main.pickle"),
			(stuffFSD, "res/localizationFSD/localization_fsd_main.pickle"),
		):
			unPickledObject = cPickle.loads(efs.open(resname).read())
			for messageID, dataRow in unPickledObject['labels'].iteritems():
				fp = dataRow['FullPath']
				label = fp + '/' + dataRow['label'] if fp else dataRow['label']
				self.languageLabels[label.encode('ascii')] = messageID

		# clean up some stuff immediately (frees ~4MB)
		del unPickledObject, stuff, stuffFSD
		gc.collect()


	def _format(self, fmt, param, languageID):
		raw, noclue, tokens = fmt
		try:
			for token, data in tokens.iteritems():
				handler = self._propertyHandlers[data['variableType']]
				getter = getattr(handler, data['propertyName'] or "default")
				replacement = getter(param[data['variableName']], languageID, **data['kwargs'])
				raw = raw.replace(token, unicode(replacement))
		except KeyError:
			print "NO HANDLER FOR:"
			print "- token:", token
			print "- data:", data
			print "- param:", param
			print "- format:", raw
			raise

		return raw


	def GetByMessageID(self, messageID, languageID=None, **kwarg):
		if messageID is None:
			return ""

		tr = self.primary.get(messageID, False)
		if tr == False and self.fallback:
			tr = self.fallback.get(messageID)
		if tr:
			if kwarg or tr[2]:
				return self._format(tr, kwarg, languageID)
			return tr[0]

		return "<NO TEXT, messageID=%d, param=%s>" % (messageID, kwarg)


	def GetByLabel(self, label, languageID=None, **kwarg):
		try:
			messageID = self.languageLabels[label]
		except KeyError:
			return '[no label: %s]' % label

		return self.GetByMessageID(messageID, languageID, **kwarg)


	# The special handling of important names in EVE isn't necessary for Reverence.
	GetImportantByMessageID = GetByMessageID
	GetImportantByLabel = GetByLabel

