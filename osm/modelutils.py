from models import *
from django.db import connection, transaction
import os

searchable_tags = ['highway']
import pdb;

def set_searchable_ways():
    # Create extra tables
    cursor = connection.cursor()
    cursor.execute(SQL_SEARCH_TABLES)
    transaction.commit_unless_managed()        
#    try:
#        cursor.execute(SQL_TAGS_KEYS)
#        transaction.commit_unless_managed()        
#    except:
#        pass    
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
                
def set_relations():    
    # Get relations type street_number
    stags = RelationTags.objects.filter(k='type',v='street_number')
    strel = set(map(lambda x: x.relation, stags))
    
    # Filter sequential types
    strel = filter(lambda x: x.relationtags_set.filter(k='scheme',v='sequential').count() > 0, strel)
    
    for rel in strel:
        # add Ways and nodes
        
        # Get Ways id from relation
        rmemberways = RelationMembers.objects.filter(relation=rel, member_type='W')
        ways_id = [r.member_id for r in rmemberways]
        
        # Get RelationMembers of type Node
        rmembernodes = RelationMembers.objects.filter(relation=rel, member_type='N')
        
        for rmn in rmembernodes:
            number = rmn.member_role
            waynodes = WayNodes.objects.filter(way__id__in = ways_id, node__id = rmn.member_id)
            
            for wn in waynodes:
                wnd = WayNodesDoor(waynode=wn, number=number)
                wnd.save()
            # Get searchable node
            #snode = SearchableNode.objects.get(node__id=rn.member_id)
            
            # Get ways in relation asociated width snode
            #sways = Sw & node.way.all()
            
            # Add door number to way door relation
            #print dnumber, " - ".join([s.name for s in sways])
            #
            #for sway in sways:
            #    wd = WayDoor.objects.filter(way=sway, node=snode)
            #    wd.update(number=dnumber)

SQL_SEARCH_TABLES = """   
DROP TABLE IF EXISTS osm_waynodesdoor;
DROP TABLE IF EXISTS osm_searchableway;

CREATE TABLE "osm_searchableway" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" text,
    "way_id" integer NOT NULL UNIQUE REFERENCES "ways" ("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE "osm_waynodesdoor" (
    "id" serial NOT NULL PRIMARY KEY,
    "waynode_id" integer NOT NULL UNIQUE REFERENCES "way_nodes" ("id") DEFERRABLE INITIALLY DEFERRED,
    "number" integer
)
;
"""

SQL_TAGS_KEYS = """
ALTER TABLE ONLY way_nodes DROP CONSTRAINT pk_way_nodes;
ALTER TABLE way_nodes ADD COLUMN "id" serial PRIMARY KEY;
ALTER TABLE way_tags ADD COLUMN "id" serial PRIMARY KEY;
ALTER TABLE relation_tags ADD COLUMN "id" serial PRIMARY KEY;
ALTER TABLE node_tags ADD COLUMN "id" serial PRIMARY KEY;
ALTER TABLE relation_members ADD COLUMN "id" serial PRIMARY KEY;
"""
