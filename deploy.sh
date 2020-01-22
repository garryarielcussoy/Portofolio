#!/bin/bash

eval "$(ssh-agent -s)" &&
ssh-add -k ~/.ssh/id_rsa &&
cd ~/backend # Go to Portofolio folder (where the git clone take place)
git pull

source ~/.profile
echo "$DOCKERHUB_PASS" | docker login --username $DOCKERHUB_USER --password-stdin
docker stop serbabukube # Stop running docker
docker rm serbabukube # Remove the container 
docker rmi garryarielcussoy/serbabuku:be # Remove the image
docker run -d --name serbabukube -p 5000:5000 garryarielcussoy/serbabuku:be # Run the docker