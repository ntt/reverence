# setup.py
import sys

if sys.version_info < (2, 7) or sys.version_info >= (2, 8):
	raise RuntimeError("Python 2.7 required")

try:
	from setuptools import setup
	from setuptools import Extension
except ImportError:
	from distutils.core import setup
	from distutils.extension import Extension

import platform
import os

try:
    os.chdir(os.path.dirname(sys.argv[0]))
except OSError:
    pass


desc = """\
Reverence is a decoder for, and interface to the bulkdata, cache and
settings of an EVE Online installation. It allows programmatic access
to the game's database tables, and provides various data formatting
functions and helpers for EVE-related applications.
"""



# Collect all the subpackages for inclusion.
p_names = []  # package names.
p_dirs = {}   # folders for said packages.

for path, dirs, files in os.walk("src"):
	if "__init__.py" in files:
		# derive the name from the folder
		p = ("reverence." + path[4:].replace("\\", ".")).strip(".")
		p_names.append(p)  # add it to the package list
		p_dirs[p] = path   # add its path


setup(
	name = "reverence",

	url = "http://github.com/ntt/reverence",

	version = "1.8.0",

	install_requires = ['PyYAML'],

	description = "Interface to EVE Online resources",

	long_description = desc,

	classifiers = [
		"License :: OSI Approved :: BSD License",
		"Programming Language :: Python :: 2 :: Only",
		"Programming Language :: Python :: 2.7",
		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: Developers",
		"Topic :: Database",
		"Topic :: Software Development :: Libraries :: Python Modules",
		"Operating System :: Microsoft :: Windows",
		"Operating System :: POSIX :: Linux",
	],

	license = "BSD",
	author = "Jamie van den Berge",
	author_email = "jamie@hlekkir.com",

	ext_modules = [
		Extension("reverence._blue", [
			"src/blue/__init__.c",
			"src/blue/marshal.c",
			"src/blue/dbrow.c",
			"src/blue/adler32.c",
		]),

		Extension("reverence._pyFSD", [
			"src/blue/fsd.c",
		])
	],

	packages = p_names,
	package_dir = p_dirs,
	package_data = {"reverence": ['*.txt']},
)


