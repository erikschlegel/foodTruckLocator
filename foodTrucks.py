
"""
This program takes inputs of latitude, longitude and radius
and outputs the 5 closest food trucks to orginating location
within the specified radius
Author:  Nse Ekpoudom
Created:  June 22, 2020
"""
import pymongo
import math
from pprint import pprint
import argparse


def get_db():

    uri = "mongodb+srv://foodie:Foodie@cluster0-j0ggs.mongodb.net/test?authSource=admin&replicaSet=Cluster0-shard-0&readPreference=primary&appname=MongoDB%20Compass&ssl=true"
    client = pymongo.MongoClient(uri)
    db = client.eateries
    return db

def convertMilestoKm(miles):
    conversionFactor = 1.60934  # 1 mile to km

    return miles * conversionFactor


def convertkmtoMiles(km):
    conversionFactor = 1.60934  # 1 mile to km

    return km / conversionFactor


# lat is in degrees, radius in miles
# returns min and max in radians
def getLatMinMax(lat, radius):
    earthRadius = 6371  # in km

    radiusKm = convertMilestoKm(radius)

    latMin = math.radians(lat) - radiusKm / earthRadius
    latMax = math.radians(lat) + radiusKm / earthRadius

    return latMin, latMax


# long, lat are in degrees, raduis in miles
# returns min and max in radians
def getLongMinMax(long, lat, radius):
    earthRadius = 6371  # in km
    angRadius = convertMilestoKm(radius) / earthRadius

    deltaLong = math.asin(math.sin(angRadius) / math.cos(math.radians(lat)))

    longMin = math.radians(long) - deltaLong
    longMax = math.radians(long) + deltaLong
    return longMin, longMax


# lat and longit are the originating locaton in radians
def getTrucks(db, lat, longit, latMin, latMax, longMin, LongMax, radius):
    # data pipleline
    pipeline = [
        {
            '$match': {
                'LatitudeRadians': {
                    '$gt': latMin,
                    '$lt': latMax
                },
                'LongitudeRadians': {
                    '$gt': longMin,
                    '$lt': LongMax
                }
            }
        },
        # stage to get the radius from the originating point
        # {
        # '$addFields': {
        # 'dist1': { '$multiply':[{'$sin': lat},{'$cos': 'LatitudeRadians'}] },
        # 'dist2': { '$multiply':[{'$cos': lat},{'$cos': 'LatitudeRadians'}] },
        # 'dist3':{'$cos':{'$subtract':[lat,'LatitudeRadians']}}

        # }
        # },
        # {
        # '$addFields': {
        #    'totdist': { '$acos':{'add':['dist1', {'$multiply':{'dist2','dist3'}}]}}}
        # },
        {
            '$project': {
                '_id': 0,
                'Applicant': 1,
                'Location': 1,
                'Address': 1,
                'FoodItems': 1
            }},
        {
            '$limit': 5
        }

    ]

    location_cursor = db.foodTrucks.aggregate(pipeline)
    return location_cursor
def main():
    parser = argparse.ArgumentParser(description='Food Truck locator')

    parser.add_argument("lat")
    parser.add_argument("long")
    parser.add_argument("radius")
    args = parser.parse_args()

    db = get_db()   #connect to database
    lat = float(args.lat)  # degrees
    longit = float(args.long)  # degrees
    radius = float(args.radius)  # miles

    latMin, latMax = getLatMinMax(lat, radius)
    lngMin, lngMax = getLongMinMax(longit, lat, radius)
    lst = getTrucks(db,lat, longit, latMin, latMax, lngMin, lngMax, radius)

    # output the 5 "closest food trucks"
    print("The closest food trucks to your location are:")
    for doc in lst:
        pprint(doc)

if __name__ == '__main__':
   main()