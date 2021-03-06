# Coordinates from words (Spacy, Geopy) (work-in-progress)
- uses NLP and geocoding to extract a location from a string of words
- switching randomly between three different services for geocoding ([Mapbox](https://www.mapbox.com/), [GeoNames](https://www.geonames.org/), [Nominatim](https://nominatim.org/)) to stay below the rate limits

## How to run
- build the docker-image: `docker build -t myimage .`
- run: `docker run -e OPEN_CAGE_KEY=... -e MAPQUEST_KEY=... -e MAPTILER_KEY=... -e GEOCODIO_KEY=... -e HERE_KEY=... -e BING_MAPS_KEY=... -e MAPBOX_TOKEN=... -e GEONAMES_USERNAME=... -e PYTHONUNBUFFERED=TRUE --name mycontainer -p 80:80 myimage`
- use: call `/coordinates/?video_title=...`
- stop: `docker stop mycontainer`
- remove: `docker rm mycontainer`

Used as a micro service in [this small app](https://github.com/adeveloper-wq/youtube-map-backend).