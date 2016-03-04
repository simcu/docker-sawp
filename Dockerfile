FROM alpine
ADD files /home
RUN apk add --update python=2.7.11-r3 \
	&& apk add nginx \
	&& mv /home/nginx.conf /etc/nginx/nginx.conf \
	&& python /home/get-pip.py \
    && pip install docker-py \
    && pip install pytz \
    && rm -rf /var/cache/apk/* \
    && mv /home/simcu_awp.py /home/simcu-awp \
    && chmod +x /home/simcu-awp && rm /home/git-pip.py
ENTRYPOINT ["/home/simcu-awp"]
