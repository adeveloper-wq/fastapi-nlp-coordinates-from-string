import string
import time
import spacy
import geopy
from geopy.extra.rate_limiter import RateLimiter
from typing import Optional
from fastapi import FastAPI

app = FastAPI()

nlp_wk = spacy.load('xx_ent_wiki_sm')

# MAPBOX GEOCODER ODER GEONAMES
locator = geopy.geocoders.Nominatim(user_agent="mygeocoder")
geocode = RateLimiter(locator.geocode, min_delay_seconds=1)

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
        geocode_result = geocode(location_string)
        if geocode_result is not None:
            point = geocode_result.point
            if point is not None:
                locations_coordinates.append({'latitude': point.latitude, 'longitude': point.longitude})
        if(len(locations_coordinates) > 0):
                break
        """ print("GEOCODE")
        print(time.time() - start) """
            
    """ print(location_strings)
    print(locations_coordinates) """
            
    return locations_coordinates


""" @app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q} """