from django.db import connection, transaction
import os
from osm.models import *
from osm.utils.words import normalize_street_name,  printable_street_name
from django.db import transaction

streets_tags = [u'highway']

@transaction.commit_on_success
def set_streets():
    ways = Ways.objects.all()
    streets = {}
    
    # Delete previous streets
    ways.update(street=None)
    Streets.objects.all().delete()
    
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
        print(w)
            
@transaction.commit_on_success
def set_doors():
    
    # Clear previous WayNodesDoor
    WayNodesDoor.objects.all().delete()
    
    
    
    # Get street number relations  of sequential scheme
    qsrel = Relations.objects.all()
    qsrel = qsrel.filter(relationtags__k = 'type', relationtags__v = 'street_number')
    qsrel = qsrel.filter(relationtags__k = 'scheme', relationtags__v = 'sequential')


    for rel in qsrel:
        
        # Get Ways id from relation
        rmemberways = RelationMembers.objects.filter(relation=rel, member_type='W')
        ways_id = [r.member_id for r in rmemberways]

        # Get RelationMembers of type Node
        rmembernodes = RelationMembers.objects.filter(relation=rel, member_type='N')
        
        for rmn in rmembernodes:
            number = rmn.member_role.strip()
            if number.isdigit():
                waynodes = WayNodes.objects.filter(way__id__in = ways_id, node__id = rmn.member_id)
                
                for wn in waynodes:
                    wnd = WayNodesDoor(waynode=wn, number=number)
                    wnd.save()
                    print wnd.number, wnd.waynode.way.street.name
            else:
                print "Skipped '%s' for %s: role is not a number or empty" % \
                       (wnd.member_role, wnd.waynode.way.street.name)


def set_intersections():
    streets = Streets.objects.all()
    for street in streets:
        for intersection in street.intersections:
            si = StreetIntersection(first_street=street,second_street=intersection)
            si.save()
            print(si)
            #street.intersects_with.add(intersection)
            #intersection.intersects_with.add(street)
        #street.save()
