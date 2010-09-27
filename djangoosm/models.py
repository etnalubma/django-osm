from django.contrib.gis.db import models
from settings import DEFAULT_SRID
# ---------------------------------------------------------------------
# This model was extracted from inspectdb of a osmosis schema version 4
# and modified to fit foreign keys and many to many relations.
# To check osmosis go to:
# http://wiki.openstreetmap.org/wiki/Osmosis_PostGIS_Setup
# ---------------------------------------------------------------------

#class SchemaInfo(models.Model):
#    version = models.IntegerField(primary_key=True)
#    class Meta:
#        db_table = u'schema_info'

class Users(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()

    def __unicode__(self):
        return self.name

class Nodes(models.Model):
    id = models.IntegerField(primary_key=True) 
    version = models.IntegerField()
    user = models.ForeignKey('Users')
    tstamp = models.DateTimeField()
    changeset_id = models.IntegerField() 
    geom = models.PointField(srid=DEFAULT_SRID)
    streets = models.ManyToManyField('Ways', through='WayNodes')
    objects = models.GeoManager()

    @property
    def tags(self):
        ntags = NodeTags.objects.filter(node = self).values()
        out = {}
        for nt in ntags:
            out[nt['k']] = nt['v']        

        return out

    def __unicode__(self):
        return u"%i" % self.id

class Streets(models.Model):
    name = models.TextField(null=True)
    norm = models.TextField(null=True)
    old = models.TextField(null=True)
    intersects_with = models.ManyToManyField('self', 
                                             through='StreetIntersection', 
                                             symmetrical=False)

    @property
    def intersections(self):
        out = Streets.objects.filter(ways__waynodes__node__waynodes__way__street = self)
        out = out.exclude(id = self.id)
        out = out.distinct()
        
        return out
        
    def __unicode__(self):
        return self.name

class StreetIntersection(models.Model):
    first_street = models.ForeignKey('Streets', related_name='first_intersection')
    second_street = models.ForeignKey('Streets', related_name='second_intersection')
    
    def __unicode__(self):
        return u'%s y %s' %(self.first_street, self.second_street)

class Ways(models.Model):
    id = models.IntegerField(primary_key=True)
    version = models.IntegerField()
    user = models.ForeignKey('Users')
    tstamp = models.DateTimeField()
    changeset_id = models.IntegerField()
    street = models.ForeignKey('Streets', null=True)
    
    @property
    def tags(self):
        wtags = WayTags.objects.filter(way = self).values()
        out = {}
        for wt in wtags:
            out[wt['k']] = wt['v']        

        return out 

    def __unicode__(self):
        return u"%i" % self.id

class WayNodes(models.Model):
    way = models.ForeignKey('Ways')
    node = models.ForeignKey('Nodes') 
    sequence_id = models.IntegerField()

    class Meta:
        unique_together = ('way','sequence_id')
        ordering = ['way','sequence_id']

    def __unicode__(self):
        return u"(%i, %i)" % (self.way_id, self.node_id)


class Relations(models.Model):
    id = models.IntegerField(primary_key=True)
    version = models.IntegerField()
    user = models.ForeignKey('Users')
    tstamp = models.DateTimeField()
    changeset_id = models.IntegerField()

    @property
    def tags(self):
        rtags = RelationTags.objects.filter(relation = self).values()
        out = {}
        for rt in rtags:
            out[rt['k']] = rt['v']        

        return out

    def __unicode__(self):
        return u"%i" % self.id

class RelationMembers(models.Model):
    relation = models.ForeignKey('Relations') 
    member_id = models.IntegerField() 
    member_type = models.TextField() 
    member_role = models.TextField()
    sequence_id = models.IntegerField()

    class Meta:
        ordering = ['relation','sequence_id','member_type','member_role']

    def __unicode__(self):
        return u"%s (%i, %i, %s)" % (self.member_type, self.relation_id, 
                     self.member_id, self.member_role or u'')

class NodeTags(models.Model):
    node = models.ForeignKey('Nodes') 
    k = models.TextField()
    v = models.TextField()

    def __unicode__(self):
        return u"%s (%s: %s)" % (self.node_id, self.k, self.v)


class WayTags(models.Model):
    way = models.ForeignKey('Ways')
    k = models.TextField()
    v = models.TextField()

    def __unicode__(self):
        return u"%s (%s: %s)" % (self.way_id, self.k, self.v)

class RelationTags(models.Model):
    relation = models.ForeignKey('Relations')
    k = models.TextField()
    v = models.TextField()

    def __unicode__(self):
        return u"%s (%s: %s)" % (self.relation_id, self.k, self.v)
  
class WayNodesDoor(models.Model):
    waynode = models.OneToOneField('WayNodes')
    number = models.IntegerField(null=True)

    def __unicode__(self):
        return u"%i -> %i" (self.way_id, self.number)

