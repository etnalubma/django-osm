# -*- coding: utf-8 -*-

from django.db import connection

def get_streets_list(street):
    """ Esta funcion auxiliar sirve para desambiguar una busqueda de calles """

    cursor = connection.cursor()

    cursor.execute("""SELECT DISTINCT osm_searchableway.name FROM osm_searchableway 
    WHERE osm_searchableway.norm ILIKE %s""",['%%%s%%' % street])
    return cursor.fetchall()    

def get_intersection_list(street, intersection):
    """ Esta funcion auxiliar sirve para desambiguar una busqueda de interseccion de calles. """

    cursor = connection.cursor()

    cursor.execute("""SELECT DISTINCT w1.name, w2.name FROM 
(osm_searchableway w1 join way_nodes wn1 on (w1.way_id = wn1.way_id)) join 
(osm_searchableway w2 join way_nodes wn2 on (w2.way_id = wn2.way_id))
on (wn1.node_id = wn2.node_id and w1.norm != w2.norm)
 and w1.norm ilike %s and w2.norm ilike %s """,['%%%s%%' % street,'%%%s%%' % intersection])
    return cursor.fetchall()
