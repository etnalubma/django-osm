Introduction
============

django-osm is an intent to integrate functionalities to django framework using the 
osm database. We choose to use osmosis as our interface to convert osm models into 
postgis. 

Requirements
============

 * PostGis
 * Osmosis trunk version. 
 * GeoDjango
 
Installation
============

Follow the instructions to install osmosis following
http://wiki.openstreetmap.org/wiki/Osmosis_PostGIS_Setup

After installed, run the sql of osmosis structure into your model database:

$ psql -d database_name -U database_owner < osmosis/script/pgsql_simple_schema_0.6.sql 


Now, we are ready to import osm data to postgis database using osmosis:

$ ./osmosis-trunk/bin/osmosis --read-xml file="inputfile.osm" --write-pgsql user="user" password="pass" database="database_name"


To see more options of osmosis tool check:
http://wiki.openstreetmap.org/wiki/Osmosis/DetailedUsage

Then you need to configure the svn file sources in your settings.py with OSM_CSV_ROOT:
For example:
OSM_CSV_ROOT = os.path.join(os.path.dirname(__file__), 'csv')

This folder must contain 2 files: 
  * specialchars.csv
    This file must contain 2 columns: the first is a special character, the second is the replaced character
  * abbreviations.csv
    This file must contain 2 columns: the first is a prefix, the second is the normalized prefix




Then you have to run django shell and run 3 scripts:

$ django shell
>>> from osm.utils.model import *
>>> update_osmosis_tables()
>>> set_searchable_ways()
>>> set_relations()

This scripts should add indexes to some models, add extra models for searchable ways, and populate streets and door numbers from relations of type street_numer.
To see specification:
http://wiki.openstreetmap.org/wiki/Argentina:Altura_de_las_Calles

utils Functions
===============

model.py
========

Contains the methods to readapt osmosis model and create extra util models.


lists.py
==========

Contains street lists queries that couldn't be created with standard ORM of django.


words.py
========

Contains normalization functions for street search.


search.py
=========

get_location_by_intersection:
This function takes 2 street names and return all the intersections between ways with such names.

get_location_by_door:
This function get a string with name of street and returns a tuple:
    - The first element is a GEOS Point object.
    - The second element is a door distance from this point to the target.
    
The search procedure return this cases:
    - If there is not match or there is no numbers for that match returns None
    - If there is an exact match returns the point and 0 for distance
    - If there is an aproximated match returns the closest door point and the distance
    - If there are 2 point in a way that surround the door number, then return an 
      interpolation for that point in proportion of the distance, and a aproximate radius.



