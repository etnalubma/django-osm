from django.db import connection, transaction
import os
from djangoosm.models import *
from djangoosm.utils.words import normalize_street_name,  printable_street_name
from django.db import transaction
from osm.parser import OSMXMLFile
from osm.objects import Way, Node, Relation, ObjectPlaceHolder
from djangoosm import OSM_SRID
from settings import DEFAULT_SRID
from django.contrib.gis.geos import Point, LineString, MultiLineString, Polygon, GEOSGeometry
from django.contrib.gis.gdal import OGRGeometry, SpatialReference
from datetime import datetime
from progressbar import Percentage, RotatingMarker, ETA, ProgressBar, Bar

streets_tags = [u'highway']

widgets = ['Elements: ', Percentage(), ' ', Bar(marker='='), ' ', ETA()]



def osm_change_srid(geom, srid):
    """ Converts standard merkartor to desired projection """
    obj = OGRGeometry(geom.wkt)
    obj.srs = OSM_SRID
    obj.transform_to(SpatialReference(srid))
    return obj.geos

@transaction.commit_on_success
def import_osm(osmfile):
    print "Parsing OSM File"
    osmobjects = OSMXMLFile(osmfile)
    osmobjects.statistic()
    
    # Import nodes
    print "Importing Nodes:"
    nodes_total = len(osmobjects.nodes)    
    nodes_count = 0
    pbar = ProgressBar(widgets=widgets, maxval=nodes_total).start()
    for node_id, node in osmobjects.nodes.iteritems():
        if type(node) == ObjectPlaceHolder:
            continue    
        geom = Point(float(node.lon),float(node.lat), srid=OSM_SRID)
        if OSM_SRID != 'EPSG:900913':
            geom = osm_change_srid(geom, 'EPSG:900913')


        user, created = Users.objects.get_or_create(id=node.uid, defaults={'name': node.user})

        django_node = Nodes(
            id = node_id,
            version = node.version or 0,
            user = user,
            tstamp = datetime.strptime(node.timestamp,"%Y-%m-%dT%H:%M:%SZ"),
            changeset_id = node.changeset or 0,
            geom = geom
        )
        django_node.save()

            
        for k, v in node.tags.iteritems():
            django_nodetag = NodeTags(
                node = django_node,
                k = k,
                v = v
            )
            django_nodetag.save()
        nodes_count += 1
        pbar.update(nodes_count)
    pbar.finish()

    
    # Import ways
    print "Importing Ways:"    
    ways_total = len(osmobjects.ways)
    ways_count = 0
    pbar = ProgressBar(widgets=widgets, maxval=ways_total).start()        
    for way_id, way in osmobjects.ways.iteritems():
    
        if type(way) == ObjectPlaceHolder:
            continue
            
        user, created = Users.objects.get_or_create(id=node.uid, defaults={'name': node.user})
        
        django_way = Ways(
            id = way_id,
            version = way.version or 0,
            user = user,
            tstamp = datetime.strptime(way.timestamp,"%Y-%m-%dT%H:%M:%SZ"),
            changeset_id = way.changeset or 0
        )
        django_way.save()
        
        for seq in range(0, len(way.nodes)):
            django_node = Nodes.objects.get(id=way.nodes[seq].id)
            django_waynode = WayNodes(
                way = django_way,
                node = django_node,
                sequence_id = seq+1
            )
            django_waynode.save()

        for k, v in way.tags.iteritems():
            django_waytag = WayTags(
                way = django_way,
                k = k,
                v = v
            )
            django_waytag.save()

        ways_count += 1
        pbar.update(ways_count)        
    pbar.finish()
        
    # Import Relations
    print "Importing Relations:"    
    relations_count = 0  
    relations_total = len(osmobjects.relations)
    pbar = ProgressBar(widgets=widgets, maxval=relations_total).start()      
    for relation_id, relation in osmobjects.relations.iteritems():
        if type(relation) == ObjectPlaceHolder:
            continue    
    
        user, created = Users.objects.get_or_create(id=node.uid, defaults={'name': node.user})
            
        django_relation = Relations(
            id = relation_id,
            version = relation.version or 0,
            user = user,
            tstamp = datetime.strptime(relation.timestamp,"%Y-%m-%dT%H:%M:%SZ"),
            changeset_id = relation.changeset or 0,
        )

        django_relation.save()
        
        sequence = 1
        for member, role in relation.members:
            if type(member) == Node:
                member_type = 'N'
            elif type(member) == Way:
                member_type = 'W'
            elif type(member) == Relation:
                member_type = 'R'
            elif type(member) == ObjectPlaceHolder:
                continue
            
            django_relation_member = RelationMembers(
                relation = django_relation,
                member_id = member.id, 
                member_type = member_type,
                member_role = role,
                sequence_id = sequence
            )
            django_relation_member.save()
            sequence += 1

        for k, v in relation.tags.iteritems():
            django_relationtag = RelationTags(
                relation = django_relation,
                k = k,
                v = v
            )
            django_relationtag.save()
        relations_count += 1
        pbar.update(relations_count)        
    pbar.finish()
        
        
        
@transaction.commit_on_success
def set_streets():
    ways = Ways.objects.all()
    streets = {}
    
    # Delete previous streets
    ways.update(street=None)
    Streets.objects.all().delete()
    
    print "Creating Streets:"
    ways_total = len(ways)
    ways_count = 0
    pbar = ProgressBar(widgets=widgets, maxval=ways_total).start()    
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

        ways_count +=1
        pbar.update(ways_count)
    pbar.finish()
            
@transaction.commit_on_success
def set_doors():
    
    # Clear previous WayNodesDoor
    WayNodesDoor.objects.all().delete()
    
    # Get street number relations  of sequential scheme
    qsrel = Relations.objects.all()
    qsrel = qsrel.filter(relationtags__k = 'type', relationtags__v = 'street_number')
    qsrel = qsrel.filter(relationtags__k = 'scheme', relationtags__v = 'sequential')


    print "Setting Doors:"
    relations_total = len(qsrel)
    relations_count = 0
    pbar = ProgressBar(widgets=widgets, maxval=relations_total).start()    
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

            else:
                print "Skipped '%s' for %s: role is not a number or empty" % \
                       (wnd.member_role, wnd.waynode.way.street.name)
        relations_count += 1
        pbar.update(relations_count)
    pbar.finish()

def set_intersections():
    streets = Streets.objects.all()
    print "Setting Streets:"    
    street_count = 0
    street_total = len(streets)
    pbar = ProgressBar(widgets=widgets, maxval=street_total).start()    
    for street in streets:
        for intersection in street.intersections:
            si = StreetIntersection(first_street=street,second_street=intersection)
            si.save()

            #street.intersects_with.add(intersection)
            #intersection.intersects_with.add(street)
        #street.save()
        street_count += 1
        pbar.update(street_count)
    pbar.finish()
    
def import_and_update(osmfile):
    print "Importing OSM File. This could take a while."
    import_osm(osmfile)
    set_streets()
    set_intersections()
    set_doors()
    
