# -*- coding: utf-8 -*-

from djangoosm import prefix_list, special_chars

def word_strip(strin):
    """ takes extra spaces from a string and return the list of words """
    wlist = filter(lambda x: x<>'',strin.split(' '))
    return wlist

def clean_search_street(street):
    """ This function clean search string """
    not_a_prefix = lambda x: prefix_list.get(x, None) is None
    strout = street.lower()

    for k,v in special_chars.iteritems():
        strout = strout.replace(k,v)
        
    wlist = word_strip(strout)
    wlist = filter(not_a_prefix, wlist)
    
    return u" ".join(wlist)

def normalize_street_name(street):
    not_a_prefix = lambda x: prefix_list.get(x, None) is None
    strout = street
       
    for k,v in special_chars.iteritems():
        strout = strout.replace(k,v)
    
    wlist = word_strip(strout)
    wlist = map(lambda x: prefix_list.get(x.lower(), x), wlist)
    
    return u" ".join(wlist).lower()

def printable_street_name(street):
    not_a_prefix = lambda x: prefix_list.get(x, None) is None
    strout = street
    
    for k,v in special_chars.iteritems():
        if v == u' ':
            strout = strout.replace(k,v)
    
    wlist = word_strip(strout)
    wlist = map(lambda x: prefix_list.get(x.lower(), x), wlist)
    
    return u" ".join(wlist)
