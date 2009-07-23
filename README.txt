Introduction
============

osm-django is an intent to integrate functionalities to django framework using the 
osm database. We choose to use osmosis as our interface to convert osm models into 
postgis. 

Requirements
============

 * PostGis
 * Osmosis trunk version. 

Installation
===========

Follow the instructions to install osmosis following
http://wiki.openstreetmap.org/wiki/Osmosis_PostGIS_Setup

After installed, run the sql of osmosis structure into your model database:
{{{
$ psql -d database_name < osmosis/trunk/scripts/sql_simple_schema_0.6.sql
}}}

Now, we are ready to import osm data to postgis database using osmosis:
{{{
$ ./osmosis-trunk/bin/osmosis --read-xml file="inputfile.osm" --write-pgsql user="user" password="pass" database="database_name"
}}}

To see more options of osmosis tool check:
http://wiki.openstreetmap.org/wiki/Osmosis/DetailedUsage

Then you have to run django shell and run 3 scripts:

{{{
$ django shell
>>> from osm.modelutils import *
>>> update_osmosis_tables()
>>> set_searchable_ways()
>>> set_relations()
}}}

This scripts should add indexes to some models, add extra models for searchable ways, and populate streets and door numbers from relations of type street_numer.
To see specification:
http://wiki.openstreetmap.org/wiki/Argentina:Altura_de_las_Calles


