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

Take in count that osmosis database must be different than django database.

After installed, run the sql of osmosis structure into your model database:

$ psql -d <osmosis_database_name> -U <osmosis_database_owner> -h localhost < <osmosis_folder>/script/pgsql_simple_schema_0.6.sql 

where <osmosis_database_name> is the name of the database, <osmosis_database_owner> is the
username of osmosis database, and <osmosis_folder> is the folder when osmosis whas installed.

Now, we are ready to import osm data to postgis database using osmosis:

$ <osmosis_folder>/bin/osmosis --read-xml file="<osm_file>" --write-pgsql user="<osmosis_database_owner>" password="<osmosis_password>" database="<osmosis_database_name>"

Where <osm_file> is the .osm file to import. 

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

Don't forget to append osm to the INSTALLED_APPS.

Now you are ready to make a syncdb, or reset of osm to create the osm tables.

When tables where created for osm models, now you can import the data from osmosis database.
First, export database to csv files, with some extra columns for model.

$ psql -U <osmosis_database_owner> -d <osmosis_database_name> < <osm_folder>/osmosis/osmosis2osmdjango_csv.sql

That will copy the tables .csv files to /tmp folder.
Next, import csv files to django database:

$ psql -U <django_database_owner> -d <django_database_name> < <osm_folder>/osmosis/osmdjango_csv_import.sql

Now we have prepopulated models for osm. 
The last thing to do is to populate the extra models, that is streets and door numbers with django shell:

$ django-admin.py shell
>>> from osm.utils.model import *
>>> set_streets()
>>> set_doors()

To see specification of door numbers schema:
http://wiki.openstreetmap.org/wiki/Argentina:Altura_de_las_Calles

utils Functions
===============

model.py
========

Contains the methods to create extra util models.


lists.py
==========

Contains street lists queries that couldn't be created with standard ORM of django.
This will be deprecated soon.

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



