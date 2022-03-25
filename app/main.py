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
locator_nominatim = geopy.geocoders.Nominatim(user_agent="geocoder-awefawefawefawefawef")
geocode_nominatim = RateLimiter(locator_nominatim.geocode, min_delay_seconds=1)

mapbox_token = os.environ['MAPBOX_TOKEN'];
locator_mapbox = geopy.geocoders.MapBox(api_key=mapbox_token)
geocode_mapbox = RateLimiter(locator_mapbox.geocode, min_delay_seconds=1)

geonames_username = os.environ['GEONAMES_USERNAME']
locator_geonames = geopy.geocoders.GeoNames(username=geonames_username)
geocode_geonames = RateLimiter(locator_geonames.geocode, min_delay_seconds=1)

def get_geocode(service: int, location_string: str):
    if service == 0:
        try:
            return geocode_geonames(location_string)
        except:
            try:
                return geocode_mapbox(location_string)
            except:
                try: 
                    return geocode_geonames(location_string)
                except:
                    print("None", flush=True)
                    return None
    elif service == 1:
        try:
            return geocode_mapbox(location_string)
        except:
            try:
                return geocode_geonames(location_string)
            except:
                try: 
                    return geocode_mapbox(location_string)
                except:
                    print("None", flush=True)
                    return None
    elif service == 2:
        try:
            return geocode_geonames(location_string)
        except:
            try:
                return geocode_geonames(location_string)
            except:
                try: 
                    return geocode_mapbox(location_string)
                except:
                    print("None", flush=True)
                    return None

@app.get("/coordinates/")
def get_coordinates(video_title: str = ""):
    start = time.time()    
    
    doc = nlp_wk(video_title)

    location_strings = []
    for ent in doc.ents:
        if(ent.label_ == 'LOC'):
            location_strings.append(ent.text)            
            
    locations_coordinates = []
    
    for location_string in location_strings:
        
        random_service = randrange(3)
        
        geocode_result = get_geocode(random_service, location_string)
        point = None
        if geocode_result is not None:
            point = geocode_result.point
        
        count = 0
        while geocode_result is None or point is None:
            random_service = (random_service + 1) % 3
            geocode_result = get_geocode(random_service, location_string)
            if geocode_result is not None:
                point = geocode_result.point
            else:
                point = None
            
            count = count + 1
            if count >= 3:
                break
        
        if geocode_result is not None and point is not None:
            locations_coordinates.append({'latitude': point.latitude, 'longitude': point.longitude})
                    
        if(len(locations_coordinates) > 0):
                break
            
    return locations_coordinates