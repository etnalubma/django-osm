from django.contrib.gis.db import models

# ---------------------------------------------------------------------
# This model was extracted from inspectdb of a osmosis schema version 4
# and modified to fit foreign keys and many to many relations.
# To check osmosis go to:
# http://wiki.openstreetmap.org/wiki/Osmosis_PostGIS_Setup
# ---------------------------------------------------------------------

class SchemaInfo(models.Model):
    version = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'schema_info'

class Users(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    class Meta:
        db_table = u'users'

class Nodes(models.Model):
    id = models.BigIntegerField(primary_key=True) 
    version = models.IntegerField()
    user = models.ForeignKey('Users')
    tstamp = models.DateTimeField()
    changeset_id = models.BigIntegerField() 
    geom = models.PointField()
    streets = models.ManyToManyField('Ways', trough='WayNodes')
    objects = models.GeoManager()
    class Meta:
        db_table = u'nodes'

class Ways(models.Model):
    id = models.BigIntegerField(primary_key=True)
    version = models.IntegerField()
    user_id = models.ForeignKey('Users')
    tstamp = models.DateTimeField()
    changeset_id = models.BigIntegerField()
    class Meta:
        db_table = u'ways'

class WayNodes(models.Model):
    way = models.ForeignKey('Ways') 
    node = models.ForeignKey('Nodes') 
    sequence_id = models.IntegerField()
    class Meta:
        db_table = u'way_nodes'
        order_by = ('sequence_id',)

class Relations(models.Model):
    id = models.BigIntegerField(primary_key=True)
    version = models.IntegerField()
    user = models.ForeignKey('Users')
    tstamp = models.DateTimeField()
    changeset_id = models.BigIntegerField()
    class Meta:
        db_table = u'relations'

class RelationMembers(models.Model):
    relation_id = models.BigIntegerField() 
    member_id = models.BigIntegerField() 
    member_type = models.TextField() 
    member_role = models.TextField()
    sequence_id = models.IntegerField()
    class Meta:
        db_table = u'relation_members'

class NodeTags(models.Model):
    node = models.ForeignKey('Nodes') 
    k = models.TextField()
    v = models.TextField()
    class Meta:
        db_table = u'node_tags'

class WayTags(models.Model):
    way = models.ForeignKey('Ways')
    k = models.TextField()
    v = models.TextField()
    class Meta:
        db_table = u'way_tags'

class RelationTags(models.Model):
    relation = models.ForeignKey('Relations') 
    k = models.TextField()
    v = models.TextField()
    class Meta:
        db_table = u'relation_tags'

