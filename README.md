#SIMCU AUTO WEB PROXY for Docker
## run:
> docker run -d --name Simcu-AWP --privileged -v /var/run/docker.sock:/var/run/docker.sock -v /home/https:/https -p 80:80 -p 443:443 simcu/awp

### you can only run one container for http/https proxy

###run the start.sh to start up!

####  Please see the blog:  http://blog.simcu.com/archives/489

