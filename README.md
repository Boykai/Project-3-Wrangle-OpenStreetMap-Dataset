# Project-3-Wrangle-OpenStreetMap-Dataset
Wrangle OpenStreetMap data using MongoDB within a Python environment using PyMongo.

## Introduction
You will choose any area of the world in [Open Street Map](https://www.openstreetmap.org) and use data munging techniques, such as assessing the quality of the data for validity, accuracy, completeness, consistency and uniformity, to clean the OpenStreetMap data for a part of the world that you care about. Finally, you will choose either MongoDB or SQL as the data schema to complete your project. [Project Rubric](https://review.udacity.com/#!/rubrics/25/view)

## Dataset
The [Brooklyn, New York Open Street Map dataset](https://mapzen.com/data/metro-extracts/metro/brooklyn_new-york/) was used for wrangling, cleaning, and querying the MongoDB database. The [OSM XML](https://s3.amazonaws.com/metro-extracts.mapzen.com/brooklyn_new-york.osm.bz2) file type was used while exploring this dataset.

## Installtion
The [MongoDB installation guide](https://docs.mongodb.com/v3.2/tutorial/install-mongodb-on-windows/) should be completed by the user if follow up queries are to be run on the wrangled dataset.

## Wrangling
### Problems Encountered in The Map
After initially inspecting the Brooklyn Open Street Map XML dataset the following problem was discovered and will be discussed as to how it was addressed:
- Inconsistant and over abbreviated street types

### Data Overview
This section contains basic statistics about the dataset and the MongoDB queries used to gather them.
                                                
#### File sizes
                                                
> brooklyn_new-york.osm ......... 653 MB

> output.osm.json .... 719 MB
                                                
#### Number of documents
                                                
> db.brooklyn.find().count()                                                

> 18594867
                                                
#### Number of nodes
                                                
> db.brooklyn.find({'type' :'node'}).count()

> 18947436
                                                
#### Number of ways
                                                
> db.brooklyn.find({'type' :'way'}).count()

> 2705385

#### Number of unique users
                                                
> len(db.brooklyn.distinct("created.user"))

> 1574
                                                
#### Top 1 contributing user
                                                
> db.brooklyn.aggregate([{"$group":{"_id":"$created.user", "count":{"$sum":1}}}, {"$sort":{"count":1}}, {"$limit":1}])

> {u'_id': u'haoyu', u'count': 5}
                                                
#### Number of users appearing only once (having 1 post)
                                                
> db.brooklyn.aggregate([{"$group":{"_id":"$created.user", "count":{"$sum":1}}}, {"$group":{"_id":"$count", "num_users":{"$sum":1}{"$sort":{"_id":1}}, {"$limit":1}])

> {u'_id': 5, u'num_users': 65}
##### “_id” represents postcount

                                                
