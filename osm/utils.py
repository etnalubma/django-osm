from django.contrib.gis.gdal import OGRGeometry, SpatialReference
from osm.models import SearchableWay, WayNodes, WayNodesDoor
from django.utils import simplejson
from django.contrib.gis.geos import Point

def get_locations_by_intersection(street1,street2):
    """
    This function return a list of nodes that match the intersection of streets.     
    """
    qs = Nodes.objects.filter(waynodes__way__searchableway__name__startswith=street1)
    qs.filter(waynodes__way__searchableway__name__startswith=street2)

    return [n.geom for n in qs1]

def get_location_by_door(street, door):
    """ 
    This function get a string with name of street and returns a tuple:
        - The first element is a GEOS Point object.
        - The second element is a door distance from this point to the target.
        
    The search procedure return this cases:
        - If there is not match or there is no numbers for that match returns None
        - If there is an exact match returns the point and 0 for distance
        - If there is an aproximated match returns the closest door point and the distance
        - If there are 2 point in a way that surround the door number, then return an 
          interpolation for that point in proportion of the distance, and a aproximate radius.
    """
    d = int(door)
    # maxium door distance
    dmax = d+20000

    # Get ways data
    qset = WayNodes.objects.select_related('way_searchableway', 'node').filter(way__searchableway__name__startswith = street)
    
    # Set points grouped by way
    waysdict = {}
    for wn in qset:
        try:
            # This is making queries, need to be checked
            door = wn.waynodesdoor.number
        except WayNodesDoor.DoesNotExist:
            door = None
        
        point = {
            'way_id': wn.way_id,
            'geom': wn.node.geom,
            'door': door,
            'id': wn.node_id,
        }
        if wn.way_id in waysdict.keys():
            waysdict[wn.way_id].append(point)
        else:
            waysdict[wn.way_id] = [point]
    
    if waysdict == {}:
        return None
        
    # get all nodes
    nodes = reduce(lambda x,y: x+y, waysdict.values(), [])
  
    # Get the closest door number node    
    # c = min t (|door[t] - d| >= 0)
    c = min(nodes, key=lambda x: abs((x['door'] or dmax)-d))
    
    if c['door'] is None:
        # there's not door numbers to compare
        return None
    
    elif c['door'] == d:
        # c is the exact solution
        return (c['geom'], 0)

    
    cway_id = c['way_id']

    # get the nodes in the way of c width door number, sorted by door number
    cnodes = [n for n in waysdict[cway_id] if n['door'] is not None]
    cnodes.sort(lambda x, y: cmp(x['door'], y['door']))
    
    lcnodes = len(cnodes)
    cindex = cnodes.index(c)
    
    # Get start & ending nodes for current door
    # s = max t (door[t] <= d)
    # e = min t (door[t] >= d)
    
    if c['door'] < d:
        if lcnodes == cindex+1:
            # there's no bigger door in this way
            return (c['geom'], abs(c['door']-d))
        else:
            s = c
            e = cnodes[cindex+1]
    
    elif c['door'] > d:
        if cindex == 0:
            # there's no smaller door in this way
            return (c['geom'], abs(c['door']-d))
        else:
            s = cnodes[cindex-1]
            e = c

    # Get sequence of nodes between s and e
    sindex = waysdict[cway_id].index(s)
    eindex = waysdict[cway_id].index(e)
    if sindex < eindex:
        sequence = waysdict[cway_id][sindex:eindex+1]
    else:
        sequence = list(reversed(waysdict[cway_id][eindex:sindex+1]))

    # Calculate door distance proportion
    prop = float(d-s['door'])/float(e['door'] - s['door']) 
    
    # Calculate total sequence distance
    d_seq = sum(sequence[s]['geom'].distance(sequence[s+1]['geom']) 
                for s in range(0,len(sequence)-1))
    
    # Calculate distance between s point and the x point
    d_stox = d_seq * prop
    
    # Search closest point to x
    d_ptox = d_stox
    p_index = 0

    while p_index < len(sequence):
        dist = sequence[p_index]['geom'].distance(sequence[p_index+1]['geom'])
        #import pdb; pdb.set_trace()
        if dist >= d_ptox:
            break
        else:
            d_ptox -= dist
            p_index +=1

    # Calculate proportion of interpolated point
    pprop = d_ptox / sequence[p_index]['geom'].distance(sequence[p_index+1]['geom'])
    
    point = interpolate_point(
        sequence[p_index]['geom'],
        sequence[p_index+1]['geom'], 
        pprop
    )

    return (point, float(e['door']-s['door'])/2)

def interpolate_point(p1, p2, prop):
    """ Calculates the point in the segment p1, p2
        d is the proportion of distance betwen p1 and p2
    """
    out = Point(
        (p2.x - p1.x)*prop + p1.x,
        (p2.y - p1.y)*prop + p1.y,
    )
    return out

