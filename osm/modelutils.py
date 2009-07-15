from models import *
from django.db import connection, transaction
import os

searchable_tags = ['highway']

def set_searchable_ways():
    # Create extra tables
    cursor = connection.cursor()
    cursor.execute(SQL_SEARCH_TABLES)
    transaction.commit_unless_managed()        
    try:
        cursor.execute(SQL_TAGS_KEYS)
        transaction.commit_unless_managed()        
    except:
        pass    
    # Create SearchableWays
    ways = Ways.objects.all()
    for w in ways:
        wtags = WayTags.objects.filter(way = w).values()
        tags = {}
        for wt in wtags:
            tags[wt['k']] = wt['v']
            
        # Control correct keys for way
        if 'name' in tags.keys() and \
           set(searchable_tags).intersection(set(tags.keys())) <> set():            
            
            # Create searchable way 
            sw = SearchableWay(name=tags['name'],way=w)
            sw.save()
            
            # Create searchable nodes
            nodes = w.nodes_set.all()
            for nod in nodes:
                try:
                    sn = SearchableNode.objects.get(node=nod)
                except SearchableNode.DoesNotExist:
                    sn = SearchableNode(node=nod)
                sn.save()                
                wd = WayDoor(way=sw,node=sn)
                wd.save()
                
def set_relations():    
    # Get relations type street_number
    stags = RelationTags.objects.filter(k='type',v='street_number')
    strel = set(map(lambda x: x.relation, stags))
    print strel
    
    # Filter sequential types
    strel = filter(lambda x: x.relationtags_set.filter(k='scheme',v='sequential').count() > 0, strel)
    
    for rel in strel:
        # add Ways and nodes
        
        # Get SearchableWays from relation
        Rmw = RelationMembers.objects.filter(relation=rel, member_type='W')
        Sw = SearchableWay.objects.filter(way__id__in = [r.member_id for r in Rmw])
        
        # Get RelationMembers of type Node
        Rmn = RelationMembers.objects.filter(relation=rel, member_type='N')
        
        for rn in Rmn:
            dnumber = rn.member_role
            # Get searchable node
            snode = SearchableNode.objects.get(node__id=rn.member_id)
            
            # Get ways in relation asociated width snode
            sways = Sw & snode.ways_set.all()
            
            # Add door number to way door relation
            for sway in sways:
                wd = WayDoor.objects.filter(way=sway, node=snode)
                wd.update(number=dnumber)

SQL_SEARCH_TABLES = """   
DROP TABLE IF EXISTS osm_waydoor;
DROP TABLE IF EXISTS osm_searchableway;
DROP TABLE IF EXISTS osm_searchablenode;

CREATE TABLE "osm_searchableway" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" text,
    "way_id" integer NOT NULL UNIQUE REFERENCES "ways" ("id") DEFERRABLE INITIALLY DEFERRED,
    "sequence" text
)
;
CREATE TABLE "osm_searchablenode" (
    "id" serial NOT NULL PRIMARY KEY,
    "node_id" integer NOT NULL UNIQUE REFERENCES "nodes" ("id") DEFERRABLE INITIALLY DEFERRED
)
;
CREATE TABLE "osm_waydoor" (
    "id" serial NOT NULL PRIMARY KEY,
    "number" integer,
    "way_id" integer NOT NULL REFERENCES "osm_searchableway" ("id") DEFERRABLE INITIALLY DEFERRED,
    "node_id" integer NOT NULL REFERENCES "osm_searchablenode" ("id") DEFERRABLE INITIALLY DEFERRED
)
;
CREATE INDEX "osm_waydoor_way_id" ON "osm_waydoor" ("way_id");
CREATE INDEX "osm_waydoor_node_id" ON "osm_waydoor" ("node_id");
"""

SQL_TAGS_KEYS = """
ALTER TABLE way_tags ADD COLUMN "id" serial PRIMARY KEY;
ALTER TABLE relation_tags ADD COLUMN "id" serial PRIMARY KEY;
ALTER TABLE node_tags ADD COLUMN "id" serial PRIMARY KEY;
ALTER TABLE relation_members ADD COLUMN "id" serial PRIMARY KEY;
"""
