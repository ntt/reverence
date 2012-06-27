# setup.py
import distutils
from distutils.core import setup
from distutils.core import Extension

import platform
import sys
import os

try:
    os.chdir(os.path.dirname(sys.argv[0]))
except OSError:
    pass

if sys.version_info < (2, 6) or sys.version_info > (2, 8):
	raise RuntimeError("Python 2.6 or 2.7 required")

desc = """\
Reverence is a decoder for, and interface to the bulkdata, cache and
settings of an EVE Online installation. It allows programmatic access
to the game's database tables, and provides various data formatting
functions and helpers for EVE-related applications.
"""


setup(
	name = "reverence",

	url = "http://github.com/ntt/reverence",

	version = "1.5.0",

	description = "Interface to EVE Online resources",

	long_description = desc,

	classifiers = [
		"License :: OSI Approved :: BSD License",
		"Programming Language :: Python :: 2 :: Only",
		"Programming Language :: Python :: 2.6",
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

	ext_modules = [Extension("reverence._blue", [
		"src/blue/__init__.c",
		"src/blue/marshal.c",
		"src/blue/dbrow.c",
		"src/blue/adler32.c",
		"src/blue/virtualfile.c",
	])],

	packages = ["reverence"],
	package_dir = {"reverence": "src"},
	package_data = {"reverence": ['*.txt']},
)


