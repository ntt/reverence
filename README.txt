Reverence - REVERse ENgineered Cache Explorer
            
Copyright (C)2003-2009 by Jamie "Entity" van den Berge
All rights reserved.

Reverence is an advanced EVE Online cache/bulkdata handling toolkit for Python.



LICENSE
=======
Reverence is distributed under the terms of the BSD license
(see the file LICENSE.txt included with the distribution).



FEATURES
========
- High-performance iterative cache/bulkdata decoder.
- 100% compatibility with all bulkdata, cache and settings files.
- Programmatic access to data tables.
- Transparent loading of bulkdata on accessing tables.
- Simultaneous handling of data from multiple EVE installations/versions.
- Container classes for all data items found in cache and bulkdata.
- Offline RemoteSvc calls, provided the relevant cachefiles exist. Note that
  this software DOES NOT interact with the EVE Online client or server.
- EmbedFS (.stuff) file support.
- Various EVE related utility functions and constants.



REQUIREMENTS
============
- Windows (XP or later) or Linux. (untested on Mac)
- x86/x64 compatible processor.
- Python 2.6.
- An EVE Online installation.

Notes:

- A full EVE installation is not required in every case. It is perfectly
  acceptable to have only the bulkdata and cache folders in the EVE root.

- On Windows, the location of the cache folder is automatically detected
  (in Local AppData, or EVE's root when EVE is normally run with /LUA:OFF).

- On Linux, the EVE installation is assumed to be either a manually copied
  install with the cache folder placed inside the EVE root, OR an installation
  under WINE. In the latter case, the location of the cache folder is searched
  for in the expected location in the ~/.wine dir, based on the root location
  specified. If this directory cannot be found, the cache path needs to be
  specified with the cachepath keyword when instantiating blue.EVE.



SECURITY WARNING
================
!!! DO NOT DECODE DATA FROM UNTRUSTED SOURCES WITH THIS LIBRARY !!!
The decoder component of this library is basically a glorified cPickle, and
in fact supports embedded python pickles. Decoding maliciously constructed
or erroneous data may compromise your system's security and/or stability.



INSTALLATION
============
Windows users can download an installer here:
http://github.com/ntt/reverence/

Linux users:
Download the source distribution from the same location as above, extract the
contents of the archive, cd to the project directory and run the following:

   python setup.py install



USAGE
=====
Most of the stuff that matters has docstrings.

Using the toolkit is fairly easy, here is an example:

    >>> from reverence import blue
    >>> eve = blue.EVE(pathToEVE)
    >>> cfg = eve.getconfigmgr()

You then have access to the associated EVE installation's bulkdata.
Note that you do not need to run EVE for this to work. The toolkit does not
interact with running EVE processes in any way.

For example, to get some basic properties of a raven:

    >>> rec = cfg.invtypes.Get(638)
    >>> print rec.name, rec.basePrice
    Raven 108750000.0

The columns of a table can be obtained through the header attribute:

    >>> print cfg.invmetatypes.header
    ('typeID', 'parentTypeID', 'metaGroupID')


The content of the tables is outside the scope of this document. Please refer
to an EVE Online database dump for more information on the database schema.

Below is a description of the different table types and a list of tables:

IndexRowset - these are simple keyed tables:

  Getting a specific record:

    >>> rec = cfg.invtypes.Get(638)

  Iterating over records (inefficient):

    >>> for row in cfg.eveunits:
    ...   print row
    ...
    Row(unitID:1,unitName:Length,displayName:)
    Row(unitID:2,unitName:Mass,displayName:kg)
    Row(unitID:3,unitName:Time,displayName:sec)
    (etc)

  Iterating over records (more efficient):

    >>> for u, d in cfg.eveunits.Select("unitName", "displayName"):
    ...   print u, d
    ...
    Length
    Mass kg
    Time sec
    (etc)

  The following tables are in IndexRowset form:

    TABLENAME                    PRIMARY KEY
    ---------------------------  ------------------
    invcategories                categoryID         
    invgroups                    groupID            
    invmetagroups                metaGroupID        
    invtypes                     typeID             
    invbptypes                   blueprintTypeID    
    dgmattribs                   attributeID        
    dgmeffects                   effectID           
    evegraphics                  graphicID          
    eveunits                     unitID             
    eveowners                    ownerID            
    evelocations                 locationID         
    corptickernames              corporationID      
    allianceshortnames           allianceID         
    ramaltypes                   assemblyLineTypeID 
    ramactivities                activityID
    ramcompletedstatuses         completedStatusID
    mapcelestialdescriptions     celestialID
    certificates                 certificateID
    certificaterelationships     relationshipID
    locationwormholeclasses      locationID


FilterRowset - these are accessed as dicts, keyed on the table's "primary key",
and each value is a standard list or an IndexRowset containing the data rows
for the key.

  Getting the attributes of a Raven:

    >>> for row in cfg.dgmtypeattribs[638]:
    ...   print row.attributeID, row.value
    ...

  Or prettier:

    >>> for row in cfg.dgmtypeattribs[638]:
    ...   print cfg.dgmattribs.Get(row.attributeID).attributeName,"=",row.value
    ...
    damage = 0.0
    hp = 6641.0
    powerOutput = 9500.0
    lowSlots =  5.0
    (etc)

  The following tables are in FilterRowset form:

    TABLENAME                    PRIMARY KEY        
    ---------------------------  ------------------
    dgmtypeeffects               typeID
    dgmtypeattribs               typeID
    invmetatypes                 typeID
    invreactiontypes             reactionTypeID
    ramaltypesdetailpercategory  assemblyLineTypeID
    ramaltypesdetailpergroup     assemblyLineTypeID
    ramtyperequirements          typeID
    ramtypematerials             typeID


The library supports loading of data in .stuff files. There are a couple of
ways of doing this. The following example shows the EVE method of loading
the galaxy map hierarchy:

    >>> f = blue.ResFile()
    >>> f.Open("res:/UI/Shared/Maps/mapcache.dat")
    >>> mapcache = blue.marshal.Load(f.Read())

Note that this requires that you have previously instantiated an EVE object,
as the blue module will assume the last instantiated EVE is where you want to
read the .stuff data from.

If you have instantiated multiple EVE objects, you can still access the
.stuff files of any instance by calling the ResFile() of that instance instead
of blue module:

    >>> f = eve.ResFile()

A shortcut is also provided for loading data from the .stuff filesystem in a
more friendly manner:

    >>> data = eve.readstuff("path goes here")



ACKNOWLEDGEMENTS
================
This product contains code that emulates or copies aspects of the internal API
of EVE Online, with permission from CCP.

Thanks to CCP for granting permission for releasing this product.

EVE Online is a registered trademark of CCP hf.
