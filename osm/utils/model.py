from django.db import connection, transaction
import os
from osm.models import *
from osm.utils.words import normalize_street_name,  printable_street_name


streets_tags = [u'highway']

def set_streets():
    
    # Create SearchableWays
    ways = Ways.objects.all()
    
    streets = {}
    for w in ways:

        tags = w.tags
        reqset = set(streets_tags).intersection(set(tags.keys()))        

        # Control correct keys for way
        if (u'name' not in tags.keys()) or (reqset == set()):
            continue
            
        name = printable_street_name(tags[u'name'])
        norm = normalize_street_name(tags[u'name'])

        if not (norm in streets.keys()):
            s = Streets(name=name, norm=norm)
            s.save()
            streets[norm] = s

        w.street = streets[norm]
        w.save()
            

def set_relations():
    # Get relations type street_number
    stags = RelationTags.objects.filter(k='type',v='street_number')
    strel = set(map(lambda x: x.relation, stags))
    print strel
    # Filter sequential types
    strel = filter(lambda x: x.relationtags_set.filter(k='scheme',v='sequential').count() > 0, strel)
    print strel
    for rel in strel:
        # add Ways and nodes
        
        # Get Ways id from relation
        rmemberways = RelationMembers.objects.filter(relation=rel, member_type='W')
        ways_id = [r.member_id for r in rmemberways]
        print ways_id
        # Get RelationMembers of type Node
        rmembernodes = RelationMembers.objects.filter(relation=rel, member_type='N')
        
        for rmn in rmembernodes:
            number = rmn.member_role.strip()
            if number.isdigit():
                waynodes = WayNodes.objects.filter(way__id__in = ways_id, node__id = rmn.member_id)
                
                for wn in waynodes:
                    wnd = WayNodesDoor(waynode=wn, number=number)
                    wnd.save()
                    print wnd.number, wnd.waynode.way.searchableway.name
            else:
                print "Skipped '%s' for %s: role is not a number or empty" % \
                       (wnd.member_role, wnd.waynode.way.searchableway.name)



