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
import codecs
import json


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
        print('Creating sample XML file...')
        
        with open(self.getSampleFile(), 'wb') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<osm>\n  ')
            
            k = self.getSampleSize() 
            
            # Write every kth top level element
            for i, element in enumerate(self.getElement()):
                if i % k == 0:
                    f.write(ET.tostring(element, encoding='utf-8'))

            f.write('</osm>')

            
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
        self.expected = ['Alley',
                         'Americas',
                         'Avenue',
                         'Boulevard',
                         'Broadway',
                         'Center',
                         'Commons',
                         'Court',
                         'Crescent',
                         'Drive',
                         'East',
                         'Heights',
                         'Highway',
                         'Lane',
                         'Loop',
                         'North',
                         'Park',
                         'Parkway',
                         'Place',
                         'Plaza',
                         'Road',
                         'Roadbed',
                         'Slip',
                         'South',
                         'Square',
                         'Street',
                         'Terrace',
                         'Trail',
                         'Walk',
                         'West']

        self.dirty_to_clean_streets = {'Ave' : 'Avenue',
                                       'Ave.' : 'Avenue',
                                       'Avene' : 'Avenue',
                                       'Avenue,' : 'Avenue',
                                       'avenue' : 'Avenue',
                                       'ave' : 'Avenue',
                                       'Blvd' : 'Boulevard',
                                       'Crt' : 'Court',
                                       'Ctr' : 'Court',
                                       'Dr' : 'Drive',
                                       'Rd' : 'Road',
                                       'ST' : 'Street',
                                       'St': 'Street',
                                       'St.': 'Street',
                                       'st' : 'Street',
                                       'St ' : 'Street',
                                       'St. ' : 'Street',
                                       'street' : 'Street',
                                       'Streeet' : 'Street'}
        
        
        
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
        
        
    def getDirtyToCleanStreets(self):
        '''
        @return dirty to clean streets mapping dict. (a dictionary of strings)
        '''
        return self.dirty_to_clean_streets
        
        
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


    def audit(self, audit_file):
        '''
        Iterates over XML tag elements in order to find all of the addresses 
        of type street.
        
        Evaluates the tag 'v' attributes to determine if the street suffixes 
        are within the expected street suffix list.

        @return: Defaultdict of unexpected street suffixes as keys, 
                 the full street names as values. (a defaultdict of strings)
        '''
        with open(audit_file, 'r') as f:
            street_types = defaultdict(set)
            f.seek(0)

            for event, elem in ET.iterparse(f, events=('start',)):
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

        
    def clean(self, unexpected_dirty_streets):
        '''
        Get unexpected street suffixes and replace with acceptable street
        suffixes when determined that the data is unacceptably dirty.
        
        Assumes that every key given by self.aduit() is of type string.
        
        Assumes that every assigned to a key value given by self.adult() is of
        type string.
        
        Assumes that every key given by self.aduit() has valid string value.
        
        
        @return: Clean sorted defaultdict of street names with correct suffixes
                 (a defaultdict of strings)
        '''
        clean_streets_dict = {}
        unexpected_streets = unexpected_dirty_streets.copy()
        
        
        #Iterate over unexpected street types found
        for key in unexpected_streets.keys():
            
            # Determine if unexpected street type is not acceptable
            if key in self.dirty_to_clean_streets.keys():
                list_of_streets = list(unexpected_streets[key])
                
                # Iterate over streets of unacceptable street type    
                for i, street in enumerate(list_of_streets):
                    street_name = street[ : -len(key)]
                    good_street = (street_name +  self.dirty_to_clean_streets[key])
                    bad_street = str(list(unexpected_streets[key])[i])
                    
                    # Save each unacceptabled street as [key] to 
                    # acceptable street as [value] in clean_streets_dict
                    clean_streets_dict[bad_street] = good_street

        return clean_streets_dict

        
    def writeClean(self, cleaned_streets):
        '''
        Get cleaned streets mapping dictionary and use that dictionary to find
        and replace all bad street name tag attributes within XML file.
    
        Iterate through XML file to find all bad instances of tag attribute 
        street names, and replace with correct mapping value from cleaned_streets
        mapping dictionary. 
        
        Stores new cleaned XML file in 'output.osm'
        
        celaned_streets: Clean sorted defaultdict of street names with correct suffixes
                         (a defaultdict of strings)
    
        '''
        with open('output.osm', 'w') as output:
            output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            output.write('<osm>\n  ')
            osm_file = open(self.getSampleFile(), "r")
            
            for event, elem in ET.iterparse(osm_file, events=('start', 'end')):
                # 1. begin processing when the end of the element is reached
                # 2. Include all elements, except 'osm', for processing (so that your files are identical)
                if event == 'end' and (elem.tag in ["node", "way", "relation", "bounds","meta","note"] ):
                    for tag in elem.iter("tag"):
                        # Check if tag is a street name tag,. set street name to street
                            if self.isStreetName(tag):
                                street = tag.attrib['v']   
                                # If street name is in clean streets dict, replace
                                # dirty street with clean street value
                                if street in cleaned_streets.keys(): 
                                    tag.attrib['v'] = cleaned_streets[street]
                    # 3. move the write function inside the condition, so that it only writes
                    # tags that you specify (i.e. everything apart from the root <osm> element)
                    output.write(ET.tostring(elem, encoding='utf-8'))
            output.write('</osm>')
            osm_file.close()

            
class JsonFile(object):
    def __init__(self, output_file):
        self.lower = re.compile(r'^([a-z]|_)*$')
        self.lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
        self.problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
        self.created_tags = [ 'version', 'changeset', 'timestamp', 'user', 'uid']
        self.output_file = output_file

            
if __name__ == '__main__':
        
    # Get OSM File, which is Brooklyn OpenStreetMap
    # https://mapzen.com/data/metro-extracts/metro/brooklyn_new-york/
    osm_file = 'brooklyn_new-york.osm'  # Original OSM File input name
    sample_file = 'sample.osm'  # Sample OSM File output name
    output_file = 'output.osm'
    sample_size = 1


    # Initialize and create OSM original file and sample file
    osm = OSMFile(osm_file, sample_file, sample_size)
    osm.createSampleFile()
    
    # Initialize and clean street type tag attributes
    print('\nInitialzing and getting street type tag attributes...')
    cleanSt = CleanStreets(sample_file)

    # Audit street tag attributes and store vales in unexpected_street dict
    # returns street type keys with street name values dict
    print('\nPerforming audit on street types...')
    unexpected_streets = cleanSt.audit(sample_file)
    print('Dictionary of unexpected street name types with street names: ')
    pprint.pprint(unexpected_streets)

    # Clean street values and store cleaned streets in clean_street_dict
    print('\nCleaning street type values...')
    clean_streets_dict = cleanSt.clean(unexpected_streets)
    print('Dictionary of dirty street keys and clean street values: ')
    pprint.pprint(clean_streets_dict)
    
    # Find and write clean street names to XML file, save updated XML file
    print('\nCreating new output.osm file with cleaned street types...')
    cleanSt.writeClean(clean_streets_dict)
    print('New audit after street names have been replaced with clean street'
          + 'names: ')
    pprint.pprint(cleanSt.audit(output_file))
    

