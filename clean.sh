docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)
docker images | grep none | awk "{print $3}" | xargs docker rmi
