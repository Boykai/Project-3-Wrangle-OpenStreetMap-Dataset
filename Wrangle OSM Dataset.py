# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 16:19:36 2017

@author: Boykai
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET  # Use cElementTree or lxml if too slow
from collections import defaultdict
import re
import pprint


class OSMFile(object):
    '''
    OSM File handler
    From Udacity
    '''
    def __init__(self, osm_file, sample_file, sample_size):
        '''
        Initialize a OSM File instance, saves all sampled top level tags 
        into sample_file.osm, saves all parameters as attributes of instance.

        osm_file: Original OSM input file, downloaded from 
                  OSM website, OSM file path. (a string)
        
        sample_file: Sampled OSM output file, created in given sample_file 
                     path (a string)
        
        sample_size: A sample size that takes every sample_size-th 
                     top level element (a non-zero, positive integer)
        '''
        self.osm_file = osm_file
        self.sample_file = sample_file
        self.sample_size = sample_size
        
    def getSampleFile(self):
        '''
        @return sample file name and/or directory. (a string)
        '''
        return self.sample_file
    
    def getOsmFile(self):
        '''
        @return OSM file name and/or directory. (a string)
        '''
        return self.osm_file
    
    def getSampleSize(self):
        '''
        @return sample size. (a non-zero, positive integer)
        '''
        return self.sample_size
    
    def getElement(self, tags=('node', 'way', 'relation')):
        '''
        XML tag element generator
        
        tags: tag elements to search for in OSM file (a tuple of strings)
        
        @yield element if it is the right type of tag

        Reference:
        http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
        '''
        context = iter(ET.iterparse(self.getOsmFile(), events=('start', 'end')))
        _, root = next(context)
        
        for event, elem in context:
            if event == 'end' and elem.tag in tags:
                yield elem
                root.clear()

    def createSampleFile(self):
        '''
        Creates and writes to sample file, a new OSM file to work with 
        while cleaning. By created a sample file, the time it takes to 
        analysis, audit, clean, and write the clean data is greatly reduced.
        '''
        with open(self.getSampleFile(), 'wb') as output:
            output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            output.write('<osm>\n  ')
            
            k = self.getSampleSize() 
            
            # Write every kth top level element
            for i, element in enumerate(self.getElement()):
                if i % k == 0:
                    output.write(ET.tostring(element, encoding='utf-8'))

            output.write('</osm>')

class CleanStreets(object):
    '''
    Clean Streets of OSM File
    From Udacity
    '''
    def __init__(self, sample_file):
        '''
        Initialize a Clean Streets instance, saves all parameters as attributes 
        of the instance. Finds and returns all instances of unexpected 
        street suffixes.

        sample_file: Sampled OSM output file, created in given sample_file 
                     path (a string)        
        
        street_type_re: Regex created to find the street suffix for 
                        tag attributes. (a regex)
                        
        expected: Expected street names, street names which are deemed as 
                  acceptable format. (a list of strings)
                  
        mapping: Keys that are found as street suffix for tag attributes are 
                 to be replaced by key's value. (a string dictonary of strings)
        '''
        self.sample_file = sample_file
        self.street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
        self.expected = ['Avenue',
                         'Boulevard',
                         'Commons',
                         'Court',
                         'Drive',
                         'Lane',
                         'Parkway',
                         'Place',
                         'Road',
                         'Square',
                         'Street',
                         'Trail']

        # UPDATE THIS VARIABLE
        self.mapping = { 'St': 'Street',
                         'St.': 'Street'}

    def getSampleFile(self):
        '''
        @return sample file name and/or directory. (a string)
        '''
        return self.sample_file
        
    def getStreetTypeRegex(self):
        '''
        @return street name type regex. (a string regex)
        '''
        return self.street_type_re
    
    def getExpected(self):
        '''
        @return street suffixes. (a list of strings)
        '''
        return self.expected
        
    def auditStreetType(self, street_types, street_name):
        '''
        Audits street type by checking if the street type is in the list 
        of expected street type values.
        
        Searches street_type aganist regex to find street suffix. If the street 
        type is not in defaultdict set, it is added to street_types defaultdict.
        
        The string of street_name is the value set to the street_type key 
        in street_types defaultdict.

        street_types: Street type is a dictionary set, which is mutated within 
                      the function, passed from aduit function. 
                      (a string defaultdict set of strings)
                      
        street_name: Street name string value found in tag attribute. (a string)
        '''
        m = self.getStreetTypeRegex().search(street_name)
            
        if m:
            street_type = m.group()
            if street_type not in self.getExpected():
                street_types[street_type].add(street_name)

    def isStreetName(self, elem):
        '''
        Evaluates if tag attribute is equal to a address of type street.

        elem: XML tag element object (a object)

        @return: Bool if the tag attribute is equal to a address of type street.
        '''
        return (elem.attrib['k'] == 'addr:street')


    def audit(self):
        '''
        Iterates over XML tag elements in order to find all of the addresses 
        of type street.
        
        Evaluates the tag 'v' attributes to determine if the street suffixes 
        are within the expected street suffix list.

        @return: Defaultdict of unexpected street suffixes as keys, 
                 the full street names as values. (a defaultdict of strings)
        '''
        with open(self.getSampleFile(), 'r') as finput:
            street_types = defaultdict(set)
            
            for event, elem in ET.iterparse(finput, events=('start',)):
    
                if elem.tag == 'node' or elem.tag == 'way':
                    for tag in elem.iter('tag'):
                        if self.isStreetName(tag):
                            self.auditStreetType(street_types, tag.attrib['v'])

        street_types = self.sortStreets(street_types)

        return street_types

    def sortStreets(self, unsorted_streets):
        '''
        Sorts street types defaultdict by key, with proper values.
        
        unsorted_streets: Unsorted defaultdict of street types with values
                          equal to the instances of street type 
                          (a defaultdict of strings)
                          
        @return: Sorted defaultdict of unexpected street suffixes as keys,
                 the full street names as values. (a defaultdict of strings)
        '''
        sorted_streets = {}

        sorted_keys = sorted(unsorted_streets.keys())
        
        for key in sorted_keys:
            sorted_streets[key] = unsorted_streets[key]

        return sorted_streets

    def clean(self):
        '''
        Get unexpected street suffixes and replace with acceptable street
        suffixes when determined that the data is unacceptably dirty.
        
        @return: Clean sorted defaultdict of street names with correct suffixes
                 (a defaultdict of strings)
        '''
        
        return clean_streets

            
if __name__ == '__main__':
        
    # Get OSM File, which is Brooklyn OpenStreetMap
    # https://mapzen.com/data/metro-extracts/metro/brooklyn_new-york/
    osm_file = 'brooklyn_new-york.osm'  # Original OSM File input name
    sample_file = 'sample.osm'  # Sample OSM File output name
    sample_size = 100   

    # Initialize and create OSM original file and sample file
    osm = OSMFile(osm_file, sample_file, sample_size)
    osm.createSampleFile()
    
    # Initialize and clean street type tag attributes
    cleanSt = CleanStreets(sample_file)
    unexpected_streets = cleanSt.audit()
    
    pprint.pprint(unexpected_streets)
    
    

