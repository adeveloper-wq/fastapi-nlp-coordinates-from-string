# Coordinates from words (Spacy, Geopy)
- uses NLP and geocoding to extract a location from a string of words
- switching randomly between three different services for geocoding (Mapbox, Geonames, Nominatim) to stay below the rate limits

## How to run
- build the docker-image: `docker build -t myimage .`
- run: `docker run -e MAPBOX_TOKEN=token -e GEONAMES_USERNAME=username --name mycontainer -p 80:80 myimage`
- use: call `/coordinates/?video_title=...`
- stop: `docker stop mycontainer`
- remove: `docker rm mycontainer`