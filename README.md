# Uses NLP and geocoding to extract a location from a string of words
- build the docker-image: `docker build -t myimage .`
- run: `docker run -e MAPBOX_TOKEN=token -e GEONAMES_USERNAME=username --name mycontainer -p 80:80 myimage`
- stop: `docker stop mycontainer`
- remove: `docker rm mycontainer`
