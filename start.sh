#!/bin/sh
docker run -d --name Simcu-AWP --privileged -v /var/run/docker.sock:/var/run/docker.sock -v /home/https:/https -p 80:80 -p 443:443 simcu/awp
