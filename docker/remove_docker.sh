#!/bin/sh

docker stop alameter
docker rm alameter
echo
echo "=========================================================================="
docker ps -a | grep prophetservice/alameter

docker images | grep prophetservice/alameter | awk '{ print $3; }' | uniq | xargs docker rmi --force
echo
echo "=========================================================================="
docker images | grep prophetservice/alameter

if [ "$1" = "all" ]
then
    docker volume rm alameter-data
    echo
    echo "=========================================================================="
    docker volume ls
fi

