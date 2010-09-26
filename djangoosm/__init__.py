import csv, codecs
from django.conf import settings 

OSM_CSV_ROOT = settings.OSM_CSV_ROOT

OSM_ABBREVIATIONS_FILE = 'abbreviations.csv'
OSM_SPECIAL_CHARS_FILE = 'specialchars.csv'

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')

def load_special_chars(path):
    try:
        fd = codecs.open(path,'r','utf-8')
    except IOError:
        raise "osm: cannot open %s" % path
        
    schars = csv.reader(utf_8_encoder(fd), delimiter=',', quotechar='"')
    out = {}
    
    for k, v in schars:
        out[unicode(k.lower(),'utf-8')] = unicode(v,'utf-8')
        out[unicode(v.lower(),'utf-8')] = unicode(v,'utf-8')
    
    return out

def load_prefix_list(path):
    try:
        fd = codecs.open(path,'r','utf-8')
    except IOError:
        raise "osm: cannot open %s" % path
                
    schars = csv.reader(fd, delimiter=',', quotechar='"')
    out = {}
    for k, v in schars:
        out[unicode(k.lower(),'utf-8')] = unicode(v,'utf-8')
    
    return out

special_chars = load_special_chars(OSM_CSV_ROOT+'/'+OSM_SPECIAL_CHARS_FILE)
prefix_list = load_special_chars(OSM_CSV_ROOT+'/'+OSM_ABBREVIATIONS_FILE)

