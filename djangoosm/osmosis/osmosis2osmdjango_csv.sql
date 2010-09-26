BEGIN;

DROP SEQUENCE IF EXISTS tmp_way_nodes_id;
DROP SEQUENCE IF EXISTS tmp_way_tags_id;
DROP SEQUENCE IF EXISTS tmp_relation_tags_id;
DROP SEQUENCE IF EXISTS tmp_node_tags_id;
DROP SEQUENCE IF EXISTS tmp_relation_members_id;

CREATE TEMPORARY SEQUENCE tmp_way_nodes_id;
CREATE TEMPORARY SEQUENCE tmp_way_tags_id;
CREATE TEMPORARY SEQUENCE tmp_relation_tags_id;
CREATE TEMPORARY SEQUENCE tmp_node_tags_id;
CREATE TEMPORARY SEQUENCE tmp_relation_members_id;

INSERT INTO users VALUES (-1,'None');

CREATE TEMP TABLE osm_ways AS
    SELECT *, Null as street_id FROM ways;

CREATE TEMP TABLE osm_waynodes AS
    SELECT nextval('tmp_way_nodes_id') as id, way_id, node_id,sequence_id FROM way_nodes;

CREATE TEMP TABLE osm_waytags AS
    SELECT nextval('tmp_way_tags_id') as id, way_id, k, v FROM way_tags;

CREATE TEMP TABLE osm_relationtags AS
    SELECT nextval('tmp_relation_tags_id') as id, relation_id, k, v FROM relation_tags;

CREATE TEMP TABLE osm_nodetags AS
    SELECT nextval('tmp_node_tags_id') as id, node_id, k, v FROM node_tags;

CREATE TEMP TABLE osm_relationmembers AS
    SELECT nextval('tmp_relation_members_id') as id, relation_id, member_id, member_type, member_role, sequence_id FROM relation_members;

COPY users TO '/tmp/osm_users.csv';
COPY nodes TO '/tmp/osm_nodes.csv';
COPY osm_ways TO '/tmp/osm_ways.csv';
COPY relations TO '/tmp/osm_relations.csv';
COPY osm_waynodes TO '/tmp/osm_waynodes.csv';
COPY osm_waytags TO '/tmp/osm_waytags.csv';
COPY osm_relationtags TO '/tmp/osm_relationtags.csv';
COPY osm_nodetags TO '/tmp/osm_nodetags.csv'; 
COPY osm_relationmembers TO '/tmp/osm_relationmembers.csv';

ROLLBACK;
