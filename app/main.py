from random import randrange
import os
import time
import spacy
import geopy
from geopy.extra.rate_limiter import RateLimiter
from typing import Optional
from fastapi import FastAPI

app = FastAPI()

nlp_wk = spacy.load('xx_ent_wiki_sm')

# MAPBOX GEOCODER ODER GEONAMES
locator_nominatim = geopy.geocoders.Nominatim(user_agent="mygeocoder")
geocode_nominatim = RateLimiter(locator_nominatim.geocode, min_delay_seconds=1)

mapbox_token = os.environ['MAPBOX_TOKEN'];
geocode_mapbox = geopy.geocoders.MapBox(api_key=mapbox_token).geocode

geonames_username = os.environ['GEONAMES_USERNAME']
geocode_geonames = geopy.geocoders.GeoNames(username=geonames_username).geocode

@app.get("/coordinates/")
def get_coordinates(video_title: str = ""):
    start = time.time()    
    
    doc = nlp_wk(video_title)
    #doc = nlp_wk("Vintage Culture at Museu do Amanhã, in Rio de Janeiro, Brazil for Cercle")

    location_strings = []
    for ent in doc.ents:
        if(ent.label_ == 'LOC'):
            location_strings.append(ent.text)            
            
    locations_coordinates = []
    
    for location_string in location_strings:
        random_service = randrange(3)
        if random_service == 0:
            geocode_result = geocode_nominatim(location_string)
            if geocode_result is not None:
                point = geocode_result.point
                if point is not None:
                    locations_coordinates.append({'latitude': point.latitude, 'longitude': point.longitude})
        elif random_service == 1:
            geocode_result = geocode_mapbox(location_string)
            if geocode_result is not None:
                point = geocode_result.point
                if point is not None:
                    locations_coordinates.append({'latitude': point.latitude, 'longitude': point.longitude})
        else:
            geocode_result = geocode_geonames(location_string)
            if geocode_result is not None:
                point = geocode_result.point
                if point is not None:
                    locations_coordinates.append({'latitude': point.latitude, 'longitude': point.longitude})
                    
        if(len(locations_coordinates) > 0):
                break
            
    return locations_coordinates