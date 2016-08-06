upstream %upstream% {
	%servers%
}

server {
    listen 80;
    server_name %domainname%;
	rewrite ^(.*)$  https://$host$1 permanent;
}

server {
    listen 443;
	server_name %domainname%;
    ssl on;
    ssl_certificate  %sslpem%;
    ssl_certificate_key  %sslkey%;
	location / {
	    proxy_set_header Host $host;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_pass http://%upstream%;
		proxy_http_version 1.1;
	    proxy_set_header Upgrade $http_upgrade;
	    proxy_set_header Connection "upgrade";
	}
}
