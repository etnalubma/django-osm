BEGIN;

DELETE FROM osm_users;
DELETE FROM osm_nodes;
DELETE FROM osm_ways;
DELETE FROM osm_relations;
DELETE FROM osm_nodetags; 
DELETE FROM osm_waynodes;
DELETE FROM osm_waytags;
DELETE FROM osm_relationmembers;
DELETE FROM osm_relationtags;

COPY osm_users FROM '/tmp/osm_users.csv';
COPY osm_nodes FROM '/tmp/osm_nodes.csv';
COPY osm_ways FROM '/tmp/osm_ways.csv';
COPY osm_relations FROM '/tmp/osm_relations.csv';
COPY osm_waynodes FROM '/tmp/osm_waynodes.csv';
COPY osm_waytags FROM '/tmp/osm_waytags.csv';
COPY osm_relationtags FROM '/tmp/osm_relationtags.csv';
COPY osm_nodetags FROM '/tmp/osm_nodetags.csv'; 
COPY osm_relationmembers FROM '/tmp/osm_relationmembers.csv';

COMMIT;
