# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 16:19:36 2017

@author: Boykai
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET  # Use cElementTree or lxml if too slow


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
            
if __name__ == '__main__':
        
    # Get OSM File, which is Brooklyn OpenStreetMap
    # https://mapzen.com/data/metro-extracts/metro/brooklyn_new-york/
    osm_file = 'brooklyn_new-york.osm'  # Original OSM File input name
    sample_file = 'sample.osm'  # Sample OSM File output name
    sample_size = 100   

    # Initialize and create OSM original file and sample file
    osm = OSMFile(osm_file, sample_file, sample_size)
    osm.createSampleFile()