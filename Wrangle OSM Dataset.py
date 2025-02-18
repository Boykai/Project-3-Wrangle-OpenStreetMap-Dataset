# -*- coding: utf-8 -*-
'''
Created on Tue Jan 17 16:19:36 2017

@author: Boykai
'''

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET  # Use cElementTree or lxml if too slow
from collections import defaultdict
import re
import pprint
import string
import codecs
import json
import os
from pymongo import MongoClient


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
            f.write("<?xml version='1.0' encoding='UTF-8'?>\n")
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
                  acceptable format (a list of strings)
                  
        mapping: Keys that are found as street suffix for tag attributes are 
                 to be replaced by key's value (a string dictonary of strings)
                 
        clean_streets_dict: Dictionary mapping dirty street names to clean
                            street names (a dictionary of strings)
                            
        expected_zip: List of valid Brooklyn zip codes (a list of strings)
        '''
        self.sample_file = sample_file
        self.street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
        self.expected = ['Alley', 
                         'Americas', 
                         'Atrium',
                         'Avenue', 
                         'Bayside',
                         'Boulevard', 
                         'Bowery', 
                         'Broadway', 
                         'Bushwick', 
                         'Center', 
                         'Circle', 
                         'Clinton', 
                         'Close', 
                         'Commons', 
                         'Court', 
                         'Crescent', 
                         'Drive', 
                         'East', 
                         'Expressway', 
                         'Extension', 
                         'Finest', 
                         'Fulton', 
                         'Gardens',
                         'Gratta', 
                         'Hamilton', 
                         'Heights', 
                         'Highway', 
                         'Island', 
                         'Lafayette', 
                         'Lane', 
                         'Loop', 
                         'Macdougal', 
                         'Mall', 
                         'MetroTech', 
                         'Mews', 
                         'North', 
                         'Oval', 
                         'Park', 
                         'Parkway', 
                         'Path', 
                         'Piers', 
                         'Place', 
                         'Plaza', 
                         'Promenade', 
                         'Remsen', 
                         'Reservation', 
                         'Rico', 
                         'Road', 
                         'Roadbed', 
                         'Rockaways', 
                         'Row', 
                         'Slip', 
                         'South', 
                         'Southwest', 
                         'Square', 
                         'Street', 
                         'Terrace', 
                         'Trail', 
                         'Turnpike', 
                         'Vanderbilt', 
                         'Village',
                         'Warren', 
                         'Walk',
                         'West',
                         'WestBayside', 
                         'Willoughby']
        [self.expected.append(letter) for letter in string.ascii_uppercase]
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
                                       'Plz' : 'Plaza',
                                       'Rd' : 'Road',
                                       'ST' : 'Street',
                                       'St': 'Street',
                                       'St.': 'Street',
                                       'st' : 'Street',
                                       'St ' : 'Street',
                                       'St. ' : 'Street',
                                       'Steet' : 'Street',
                                       'street' : 'Street',
                                       'Streeet' : 'Street'}
        self.clean_streets_dict = {'Graham Avenue #1' : 'Graham Avenue',
                                   'Nostrand Avenue,  #107' : 'Nostrand Avenue',
                                   '305 Schermerhorn St., Brooklyn, NY 11217' : 'Schermerhorn Street',
                                   '1st' : '1st Avenue',
                                   'Coney Island Avenue, Ste 200' : 'Coney Island Avenue',
                                   'Broadway #205' : 'Broadway',
                                   '218650358': 'NaN',
                                   '16th Street # 3' : '16th Street', 
                                   'Hanover Square #3' : 'Hanover Square',
                                   'Union Avenue 4B' : 'Union Avenue',
                                   'Joralemon Street, #4CF' : 'Joralemon Street',
                                   'Main St., Suite 500' : 'Main Street',
                                   'Broadway #506' : 'Broadway',
                                   'Mott St #507' : 'Mott Street',
                                   '32nd street with 7th' : '32nd Street',
                                   '861' : 'NaN',
                                   'wyckoff ave unit A28' : 'Wyckoff Avenue',
                                   'Dekalb Ave, 2nd Floor' : 'Dekalb Avenue', 
                                   'Wall Street 12th Floor' : 'Wall Street',
                                   'Manhattan Avenue (2nd Floor)' : 'Manhattan Avenue',
                                   'University Plz' : ' University Plaza',
                                   'Linden Boulevard Outer Eb Rb' : 'Linden Boulevard',
                                   'bus_stop' : 'NaN',
                                   'DeKalb Avenue 4 floor' : 'Dekalb Avenue'}
        self.expected_zip = ['11201', 
                             '11203', 
                             '11204', 
                             '11205', 
                             '11206', 
                             '11207', 
                             '11208', 
                             '11209', 
                             '11210', 
                             '11211', 
                             '11212', 
                             '11213', 
                             '11214', 
                             '11215', 
                             '11216', 
                             '11217', 
                             '11218', 
                             '11219', 
                             '11220', 
                             '11221', 
                             '11222', 
                             '11223', 
                             '11224', 
                             '11225', 
                             '11226', 
                             '11228', 
                             '11229', 
                             '11230', 
                             '11231', 
                             '11232', 
                             '11233', 
                             '11234', 
                             '11235', 
                             '11236', 
                             '11237', 
                             '11238', 
                             '11239']

        
        
        
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
        
    def getCleanStreetsDict(self):
        '''
        @return clean street dict. (a dictionary of strings)
        '''
        return self.clean_streets_dict
        
    def getExpectedZip(self):
        '''
        @return list of expected zip codes for Brooklyn. (a list of strings)
        '''
        return self.expected_zip
        
    def auditStreetType(self, street_types, street_name):
        '''
        Audits street type by checking if the street type is in the list 
        of expected street type values.
        
        Searches street_type aganist regex to find street suffix. If the street 
        type is not in defaultdict set, it is added to street_types defaultdict.
        
        The string of street_name is the value set to the street_type key 
        in street_types defaultdict.

        street_types: Street type is a dictionary set, which is mutated within 
                      the function, passed from audit function. 
                      (a string defaultdict set of strings)
                      
        street_name: Street name string value found in tag attribute. (a string)
        '''
        m = self.getStreetTypeRegex().search(street_name)
            
        if m:
            street_type = m.group()
            if street_type not in self.getExpected():
                street_types[street_type].add(street_name)

    def auditZipType(self, zip_types, zip_name):
        '''
        Audits zip code type by checking if the zip type is in the list 
        of expected zip type values.

        The string of zip_name is the value set to the zip_type key 
        in zip_types defaultdict.

        zip_types: Zip type is a dictionary set, which is mutated within 
                      the function, passed from audit function. 
                      (a string defaultdict set of strings)
                      
        zip_name: Zip name string value found in tag attribute. (a string)
        '''
        if zip_name not in self.getExpectedZip():
            zip_types[zip_name].add('NaN')
                
    def isStreetName(self, elem):
        '''
        Evaluates if tag attribute is equal to a address of type street.

        elem: XML tag element object (a object)

        @return: Bool if the tag attribute is equal to a address of type street.
        '''
        return (elem.attrib['k'] == 'addr:street')

    def isZipCode(self, elem):
        '''
        Evaluates if tag attribute is equal to a address of type postcode.

        elem: XML tag element object (a object)

        @return: Bool if the tag attribute is equal to a address of type postcode.
        '''
        return (elem.attrib['k'] == 'addr:postcode')
        
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
            zip_types = defaultdict(set)
            f.seek(0)

            for event, elem in ET.iterparse(f, events=('start',)):
                if elem.tag == 'node' or elem.tag == 'way':
                    for tag in elem.iter('tag'):
                        if self.isStreetName(tag):
                            self.auditStreetType(street_types, tag.attrib['v'])
                        if self.isZipCode(tag):
                            self.auditZipType(zip_types, tag.attrib['v'])
                elem.clear()           
        street_types = self.sortStreets(street_types)

        return [street_types, zip_types]

        
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
        
        Assumes that every key given by self.audit() is of type string.
        
        Assumes that every assigned to a key value given by self.adult() is of
        type string.
        
        Assumes that every key given by self.audit() has valid string value.
        
        
        @return: Clean sorted defaultdict of street names with correct suffixes
                 (a defaultdict of strings)
        '''
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
                    self.clean_streets_dict[bad_street] = good_street

        return self.clean_streets_dict

        
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
            output.write("<?xml version='1.0' encoding='UTF-8'?>\n")
            output.write('<osm>\n  ')
            osm_file = open(self.getSampleFile(), 'r')
            
            for event, elem in ET.iterparse(osm_file, events=('start', 'end')):
                # Begin processing when the end of the element is reached
                # Include all elements, except 'osm', for processing (so that your files are identical)
                if event == 'end' and (elem.tag in ['node', 'way', 'relation', 'bounds','meta','note'] ):
                    for tag in elem.iter('tag'):
                        # Check if tag is a street name tag, set street name to street
                            if self.isStreetName(tag):
                                street = tag.attrib['v']   
                                # If street name is in clean streets dict, replace
                                # dirty street with clean street value
                                if street in cleaned_streets.keys(): 
                                    tag.attrib['v'] = cleaned_streets[street]
                        # Check if tag is a zip code tag, set zip code to 'NaN' if not valid
                            if self.isZipCode(tag):
                                zip_code = tag.attrib['v']
                                if zip_code not in self.getExpectedZip():
                                    tag.attrib['v'] = 'NaN'
                    # Move the write function inside the condition, so that it only writes
                    # tags that you specify (i.e. everything apart from the root <osm> element)
                    output.write(ET.tostring(elem, encoding='utf-8'))
                    elem.clear()
            output.write('</osm>')
            osm_file.close()

            
class JsonFile(object):
    def __init__(self, output_file):
        '''
        Initialize a JSON File instance, saves all parameters as attributes 
        of the instance. Takes in an XML file and returns a JSON file      
        
        lower: Regex created to find lowercase characters for 
               tag elements (a regex)
              
        lower_colon: Regex created to find lowercase characters for 
                     tag elements when a colon is included (a regex)
                     
        problemchars: Regex created to find special characters for 
                      tags and tag elements (a regex)
                        
        created_tags: Tag element names, which are deemed as acceptable for
                      adding information (a list of strings)
                  
        output_file: XML OSM output file, created in given output_file 
                     path (a string)  
        '''
        self.lower = re.compile(r'^([a-z]|_)*$')
        self.lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
        self.problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
        self.created_tags = [ 'version', 'changeset', 'timestamp', 'user', 'uid']
        self.output_file = output_file

    
    def getElement(self, file_in, tags=('node', 'way', 'relation')):
        '''
        XML tag element generator
        
        tags: tag elements to search for in OSM file (a tuple of strings)
        
        @yield element if it is the right type of tag

        Reference:
        http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
        '''
        context = iter(ET.iterparse(file_in, events=('start', 'end')))
        _, root = next(context)
        
        for event, elem in context:
            if event == 'end' and elem.tag in tags:
                yield elem
                root.clear()    
        
    def shapeElement(self, element):
        '''
        Takes in XML element, shapes it into JSON node as dictionary, returns shaped element.
        
        element: XML ElementTree element, which is shaped into JSON node (an ET object)
        
        @return: node for JSON file creation (a dictionary)
        '''
        node = {}
        address = {}
        created = {}
        node_refs = []
        pos = []
        
        if element.tag == 'node' or element.tag == 'way' :
            node['type'] = element.tag
    
            # Get and store GPS (lat, lon) cooridinates
            if 'lat' in element.attrib.keys() and 'lon' in element.attrib.keys():
                try:
                    lat = float(element.attrib['lat'])
                    lon = float(element.attrib['lon'])
                    pos.insert(0,lat)
                    pos.insert(1,lon)
                except:
                    pass
            
            # Get and set {tag : attrib} into dict    
            for k, m in element.attrib.items():
                if k not in pos:
                    if k in self.created_tags:
                        created[k] = m
                    else:
                        node[k] = m
                      
            # Get and set node type into node dict
            if created:
                node['created'] = created
            if pos:
                node['pos'] = pos
            if address:
                node['address'] = address
            if node_refs:
                node['node_refs'] = node_refs
            if 'lon' in node.keys():
                node.pop('lon')
            if 'lat' in node.keys():
                node.pop('lat')
            
            # Iterate over subtags in element, set attribs when valid
            for child in element:
                if child.tag == 'nd':
                    try:
                        node['node_refs'].append(child.attrib['ref'])
                    except:
                        node['node_refs'] = []
                        node['node_refs'].append(child.attrib['ref'])
                elif child.tag == 'tag':
                    # Clean and set 'addr:' attrib
                    if self.problemchars.search(child.attrib['k']):
                        pass
                    elif child.attrib['k'].startswith('addr:'):
                        key = re.sub('addr:', '', child.attrib['k']).strip()
                        if self.lower_colon.match(key):
                            break
                        else:
                            try:
                                node['address'][key] = child.attrib['v']
                            except:
                                node['address'] = {}
                                node['address'][key] = child.attrib['v']
                    # Set already clean attrib
                    else:
                        node[child.attrib['k']] = child.attrib['v']
                      
            return node
        else:
            return None

            
    def processMap(self, pretty = False):
        '''
        Takes an XML file, maps and creates a JSON file of the same information,
        struction, and element nodes as the input XML file
        
        pretty: If pretty, creates a human readable JSON file (a bool)
        
        @return: List of JSON dictionary shaped node elements (a list)
        '''
        file_in = self.output_file
        file_out = '{0}.json'.format(file_in)
        data = []
        
        '''
        # Create JSON output file, shape and map each XML element
        with codecs.open(file_out, 'w') as fo:
            for _, element in ET.iterparse(file_in):
                el = self.shapeElement(element)
                if el:
                    data.append(el)
                    if pretty:
                        fo.write(json.dumps(el, indent=2) + '\n')
                    else:
                        fo.write(json.dumps(el) + '\n')

        return data
        '''
        with codecs.open(file_out, 'w') as fo:
            for i, element in enumerate(self.getElement(file_in)):
                el = self.shapeElement(element)
                if el:
                    data.append(el)
                    if pretty:
                        fo.write(json.dumps(el, indent = 2) + '\n')
                    else:
                        fo.write(json.dumps(el) + '\n')
                        
        return data
def mongoAggregate(cursor):
    '''
    Takes in pymongo aggregate cursor object, iterates through each element
    within the aggregation, then returns the list of elements
    
    cursor: pymongo aggreate cursor object, which is iterated (a cursor object)
    
    @return: List of aggregation elements (a list)
    '''
    results_list = []
    
    [results_list.append(result) for result in cursor]
     
    return results_list
        
if __name__ == '__main__':
        
    # Get OSM File, which is Brooklyn OpenStreetMap
    # https://mapzen.com/data/metro-extracts/metro/brooklyn_new-york/
    xml_original_file = 'brooklyn_new-york.osm'  # Original OSM File input name
    xml_sample_file = 'sample.osm'  # Sample OSM File output name
    xml_cleaned_file = 'output.osm'
    sample_size = 1
    
    # Initialize and create OSM original file and sample file
    if sample_size == 1:
        xml_sample_file = xml_original_file
        
    osm = OSMFile(xml_original_file, xml_sample_file, sample_size)
    
    if sample_size != 1:
        osm.createSampleFile()
    
    # Initialize and clean street type tag attributes
    print('\nInitialzing and getting street type tag attributes...')
    cleanSt = CleanStreets(xml_sample_file)

    # Audit street tag attributes and store vales in unexpected_street dict
    # returns street type keys with street name values dict
    print('\nPerforming audit on street types...')
    audit_results = cleanSt.audit(xml_sample_file)
    unexpected_streets = audit_results[0]
    unexpected_zips = audit_results[1]
    
    print('There are ' + str(len(unexpected_streets.values())) + ' unique unexpected streets.')
    print('Dictionary of unexpected street name types with street names: ')
    pprint.pprint(unexpected_streets)
    
    print('\nThere are ' + str(len(unexpected_zips.values())) + ' unique unexpected zip codes.')
    print('Dictionary of unexpected zip code types with street names: ')
    pprint.pprint(unexpected_zips)

    # Clean street values and store cleaned streets in clean_street_dict
    print('\nCleaning street type values...')
    clean_streets_dict = cleanSt.clean(unexpected_streets)
    print('There are ' + str(len(cleanSt.getCleanStreetsDict().values())) + ' street names to be replaced.')
    print('Dictionary of dirty street keys and clean street values: ')
    pprint.pprint(clean_streets_dict)
    
    
    # Find and write clean street names to XML file, save updated XML file
    print('\nCreating new output.osm file with cleaned street types...')
    cleanSt.writeClean(clean_streets_dict)
    clean_audit_results = cleanSt.audit(xml_sample_file)
    clean_unexpected_streets = clean_audit_results[0]
    
    print('There are ' + str(len(clean_unexpected_streets.values())) + ' unique unexpected streets.')
    print('New audit after street names have been replaced with clean street names: ')
    pprint.pprint(clean_unexpected_streets)
    
    if sample_size != 1:
        print('\nDeleting XML sample file...')
        #os.remove(xml_sample_file)
    
    # Initialize and create JSON file from cleaned XML output.osm file
    print('\nCreating new JSON file from cleaned XML file...')
    js = JsonFile(xml_cleaned_file)
    data = js.processMap()
    print('\nDeleting XML cleaned file...')
    os.remove(xml_cleaned_file)

    # Initialize and create MongoDB database from JSON document list 'data'
    print('\nCreating new MongoDB database \'brooklyn\' from cleaned JSON file...')
    client = MongoClient('mongodb://localhost:27017')
    db = client.osm_results
    db.brooklyn.insert_many(data, bypass_document_validation=True)
    del data[:]
    
    # Run and output MongoDB querires and results
    print('\nRunning MongoDB queries...')
    
    print('\nTotal number of documents: ')
    print('db.brooklyn.find().count()')
    print(str(db.brooklyn.find().count()))
    
    print('\nNumber of \'way\' type documents: ')
    print('db.brooklyn.find({\'type\' :\'way\'}).count()')
    print(str(db.brooklyn.find({'type' :'way'}).count()))
    
    print('\nNumber of \'node\' type documents: ')
    print('db.brooklyn.find({\'type\' :\'node\'}).count()')
    print(str(db.brooklyn.find({'type' :'node'}).count()))
    
    print('\nNumber of unique users: ')
    print('len(db.brooklyn.distinct(\'created.user\'))')
    print(str(len(db.brooklyn.distinct('created.user'))))
                                                
    print('\nTop 1 contributing user: ')
    top_contributor_pipeline = [{'$group':
                                    {'_id':'$created.user', 
                                     'count':{'$sum':1}}}, 
                                {'$sort':
                                    {'count':1}}, 
                                {'$limit':1}]
    print('db.brooklyn.aggregate(' + str(top_contributor_pipeline) + ')')
    top_contributor = mongoAggregate(db.brooklyn.aggregate(top_contributor_pipeline))
    print(str(top_contributor[0]))
                                                
    print('\nNumber of users appearing only once (having 1 post): ')
    unique_user_count_pipeline =[{'$group':
                                     {'_id':'$created.user', 
                                      'count':{'$sum':1}}}, 
                                {'$group':
                                    {'_id':'$count', 
                                     'num_users':{'$sum':1}}}, 
                                {'$sort':
                                    {'_id':1}}, 
                                {'$limit':1}]                                    
    print('db.brooklyn.aggregate(' + str(unique_user_count_pipeline) + ')')
    unique_user_count = mongoAggregate(db.brooklyn.aggregate(unique_user_count_pipeline))
    print(str(unique_user_count[0]))

                       
    print('\nTop 10 appearing amenities: ')
    top_10_amenities_pipeline = [{'$match':
                                     {'amenity':{'$exists':1}}}, 
                                 {'$group':
                                     {'_id':'$amenity', 
                                      'count':{'$sum':1}}}, 
                                {'$sort':
                                     {'count':1}}, 
                                {"$limit":10}]
    print('db.brooklyn.aggregate(' + str(top_10_amenities_pipeline) + ')')
    top_10_amenities = mongoAggregate(db.brooklyn.aggregate(top_10_amenities_pipeline))
    print(str(top_10_amenities))
                                        
    print('\nHighest population religion: ')
    most_pop_religion_pipeline = [{'$match':
                                      {'amenity':{'$exists':1}, 
                                       'amenity':'place_of_worship'}}, 
                                  {'$group':
                                      {'_id':'$religion', 
                                       'count':{'$sum':1}}}, 
                                  {'$sort':
                                      {'count':1}}, 
                                  {'$limit':1}]
    print('db.brooklyn.aggregate(' + str(most_pop_religion_pipeline) + ')')
    most_pop_religion = mongoAggregate(db.brooklyn.aggregate(most_pop_religion_pipeline))
    print(str(most_pop_religion[0]))
                                             
    print('\nMost popular cuisines: ')
    most_pop_cuisine_pipeline = [{'$match':
                                     {'amenity':{'$exists':1}, 
                                      'amenity':'restaurant'}}, 
                                 {'$group':
                                     {'_id':'$cuisine', 
                                     'count':{'$sum':1}}}, 
                                 {'$sort':
                                     {'count':1}}, 
                                {'$limit':2}]          
    print('db.brooklyn.aggregate(' + str(most_pop_cuisine_pipeline) + ')')
    most_pop_cuisine = mongoAggregate(db.brooklyn.aggregate(most_pop_cuisine_pipeline))
    print(str(most_pop_cuisine[0]))
    
    print('\nPostal Codes: ')
    postal_codes_pipeline = [{'$match':
                                 {'address.postcode':{'$exists':1},
                                  'address.postcode':'NaN'}}, 
                             {'$group':
                                 {'_id':'$address.postcode', 
                                  'count':{'$sum':1}}}, 
                             {'$sort':{'count':1}}]
    print('db.brooklyn.aggregate(' + str(postal_codes_pipeline) + ')')                             
    postal_codes = mongoAggregate(db.brooklyn.aggregate(postal_codes_pipeline))
    print(str(postal_codes[0]))