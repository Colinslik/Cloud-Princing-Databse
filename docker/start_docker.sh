#!/bin/sh

# Create data container
ls | grep alameter-docker | xargs docker load -i
docker inspect alameter-data > /dev/null 2>&1
if [ $? -eq 1 ]
then
    docker volume create alameter-data
fi

# Start containers
docker run -d --privileged --name='alameter' --env "PDA_CONSOLE_PORT=8999" --net=host --volume alameter-data:/opt/prophetstor/alameter/var prophetservice/alameter

echo
echo "=========================================================================="
docker ps | grep prophetservice/alameter

