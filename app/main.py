from random import randrange
import os
import spacy
import geopy
from geopy.extra.rate_limiter import RateLimiter
from fastapi import FastAPI
import sqlite3

app = FastAPI()

nlp_wk_multi = spacy.load('xx_ent_wiki_sm')
nlp_wk_en = spacy.load('en_core_web_md')
nlp_wk_de = spacy.load('de_core_news_md')

def get_geocoders():
    locator_nominatim = geopy.geocoders.Nominatim(user_agent="geocoder-awefawefawefawefawef")
    geocode_nominatim = RateLimiter(locator_nominatim.geocode, min_delay_seconds=1)

    mapbox_token = os.environ['MAPBOX_TOKEN'];
    locator_mapbox = geopy.geocoders.MapBox(api_key=mapbox_token)
    geocode_mapbox = RateLimiter(locator_mapbox.geocode, min_delay_seconds=1)

    geonames_username = os.environ['GEONAMES_USERNAME']
    locator_geonames = geopy.geocoders.GeoNames(username=geonames_username)
    geocode_geonames = RateLimiter(locator_geonames.geocode, min_delay_seconds=1)
    
    bing_key = os.environ['BING_MAPS_KEY']
    locator_bing = geopy.geocoders.Bing(api_key=bing_key)
    geocode_bing = RateLimiter(locator_bing.geocode, min_delay_seconds=1)
    
    open_cage_key = os.environ['OPEN_CAGE_KEY']
    locator_open_cage = geopy.geocoders.OpenCage(api_key=open_cage_key)
    geocode_open_cage = RateLimiter(locator_open_cage.geocode, min_delay_seconds=1)
    
    mapquest_key = os.environ['MAPQUEST_KEY']
    locator_mapquest = geopy.geocoders.OpenMapQuest(api_key=mapquest_key)
    geocode_mapquest = RateLimiter(locator_mapquest.geocode, min_delay_seconds=1)
    
    maptiler_key = os.environ['MAPTILER_KEY']
    locator_maptiler = geopy.geocoders.MapTiler(api_key=maptiler_key)
    geocode_maptiler = RateLimiter(locator_maptiler.geocode, min_delay_seconds=1)
    
    geocodio_key = os.environ['GEOCODIO_KEY']
    locator_geocodio = geopy.geocoders.Geocodio(api_key=geocodio_key)
    geocode_geocodio = RateLimiter(locator_geocodio.geocode, min_delay_seconds=1)
    
    here_key = os.environ['HERE_KEY']
    locator_here = geopy.geocoders.HereV7(apikey=here_key)
    geocode_here = RateLimiter(locator_here.geocode, min_delay_seconds=1)
    
    return geocode_nominatim, geocode_mapbox, geocode_geonames, geocode_bing, geocode_open_cage, geocode_mapquest, geocode_maptiler, geocode_geocodio, geocode_here

def get_geocode(service: int, location_string: str, geocoders):
    try:
        return geocoders[service](location_string)
    except:
        new_service = (service + 1) % 9
        return get_geocode(new_service, location_string, geocoders)

@app.get("/coordinates/")
def get_coordinates(video_title: str = "", advanced_location_search: str = "", language: str = "en"):
    video_title = video_title.replace('"', '').replace("|", "").replace("/", "")
    
    geocoders = get_geocoders()
    
    doc = None
    
    location_strings = []
    
    if "en" in language:
        doc = nlp_wk_en(video_title)
        for ent in doc.ents:
            if(ent.label_ == 'GPE'):
                location_strings.append(ent.text)
    elif "de" in language:
        doc = nlp_wk_de(video_title)
        for ent in doc.ents:
            if(ent.label_ == 'LOC'):
                location_strings.append(ent.text)
    else:
        doc = nlp_wk_multi(video_title)
        for ent in doc.ents:
            if(ent.label_ == 'LOC'):
                location_strings.append(ent.text)
                     
            
    locations_coordinates = []
        
    random_service = 0
    
    for location_string in location_strings:
        random_service = randrange(9)
        geocode_result = get_geocode(random_service, location_string, geocoders)
        count = 0
        while geocode_result is None:
            random_service = (random_service + 1) % 9
            geocode_result = get_geocode(random_service, location_string, geocoders)
            count = count + 1
            if count >= 9:
                break
        
        if geocode_result is not None:
            locations_coordinates.append({'latitude': geocode_result.latitude, 'longitude': geocode_result.longitude})  
            print("1-" + location_string + " " + video_title)         
        if(len(locations_coordinates) > 0):
                break
            
    cnx = None
            
    if len(locations_coordinates) == 0:
        video_title = video_title.replace(" - ", " ").replace(":", "").replace("  ", " ")
        
        cnx = sqlite3.connect('file:/code/app/cities.db?mode=ro', uri=True)
        cursor = cnx.cursor()
        
        for word in video_title.split():
            stripped_word = word.strip()
            cursor.execute("SELECT Coordinates FROM cities WHERE Name = ? ORDER BY Population DESC", (stripped_word,))
            record = cursor.fetchone()
            if record is not None:
                # print(record)
                print("2-" + word + " " + video_title)
                coordinates = record[0].split(r"\,")
                latitude = float(coordinates[0])
                longitude = float(coordinates[1])
                locations_coordinates.append({'latitude': latitude, 'longitude': longitude})             
                break
            
    if len(locations_coordinates) == 0 :
        video_title = video_title.replace(" - ", " ").replace(":", "").replace("  ", " ")

        cursor = cnx.cursor()
        
        for word in video_title.split():
            stripped_word = word.strip()
            if len(stripped_word) >= 4:
                stripped_word = r"%\," + stripped_word + r"\,%"
                cursor.execute("PRAGMA case_sensitive_like = on")
                cursor.execute("SELECT Coordinates FROM cities WHERE ('\,' || \"Alternate Names\" || '\,') LIKE ? AND Population > 0 ORDER BY Population DESC", (stripped_word,))
                record = cursor.fetchone()
                if record is not None:
                    # print(record)
                    # print(video_title)
                    # print(stripped_word)
                    coordinates = record[0].split(r"\,")
                    latitude = float(coordinates[0])
                    longitude = float(coordinates[1])
                    locations_coordinates.append({'latitude': latitude, 'longitude': longitude})  
                    print("3-" + word + " " + video_title)           
                    break
        
    return locations_coordinates