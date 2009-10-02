"""EmbedFS manager (handles .stuff files).

Copyright (c) 2003-2009 Jamie "Entity" van den Berge <jamie@hlekkir.com>

This code is free software; you can redistribute it and/or modify
it under the terms of the BSD license (see the file LICENSE.txt
included with the distribution).
"""


import cStringIO
import struct
import glob
import os

idString = "EmbedFs 1.0"

class EmbedFS(object):
	"""Manages a single EmbedFS file."""

	def __init__(self, fileName):
		self.offsets = []
		self.lengths = []
		self.files = files = {}
		self.filenames = []

		addo = self.offsets.append
		addl = self.lengths.append
		addf = self.filenames.append

		# open file and check
		f = open(fileName, "rb")
		self.name = fileName
		f.seek(-len(idString)-1, 2)
		if idString != f.read(len(idString)):
			raise RuntimeError("Invalid id string in EmbedFS file")
		f.seek(0)
		self.numFiles, = struct.unpack("<L", f.read(4))

		# read directory
		for i in range(self.numFiles):
			length, nameLength = struct.unpack("<2L", f.read(8))
			name = f.read(nameLength+1).replace('\\', '/').strip("\0")
			addf(name)
			addl(length)
			files[name.lower()] = i

		# calculate offsets
		offset = f.tell()
		for length in self.lengths:
			addo(offset)
			offset += length

		self.stream = f

	def open(self, name):
		f = self._open(name)
		if f:
			return f
		raise KeyError("File not found")

	def __getitem__(self, ix):
		return self.filenames[ix]

	def __contains__(self, this):
		return this.lower() in self.files

	def __len__(self):
		return len(self.filenames)

	def _open(self, name):
		# internal open.
		ix = self.files.get(name.lower(), -1)
		if ix == -1:
			return None
		self.stream.seek(self.offsets[ix])
		return cStringIO.StringIO(self.stream.read(self.lengths[ix]))



class EmbedFSDirectory(object):
	"""Manages folder with EFS files"""
	def __init__(self, path="."):
		self.stuff = []
		for stuffFile in glob.glob(os.path.join(path, "*.stuff")):
			self.stuff.append(EmbedFS(stuffFile))

	def __getitem__(self, ix):
		return self.stuff[ix]

	def open(self, name):
		for efs in self.stuff:
			f = efs._open(name)
			if f:
				return f
		raise IndexError("File not found")
