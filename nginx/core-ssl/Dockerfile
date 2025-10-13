FROM nginx:1.28.0-alpine

RUN apk add --no-cache \
        bash \
        certbot \
        curl \
        gettext \
        libcap \
        logrotate \
        openssl \
        su-exec \
        tzdata

RUN setcap 'cap_net_bind_service=+ep' /usr/sbin/nginx

COPY options-ssl-nginx.conf /defaults/options-ssl-nginx.conf
COPY entrypoint.sh /entrypoint.sh
COPY templates /templates

RUN chmod +x /entrypoint.sh

VOLUME ["/etc/letsencrypt", "/var/www/certbot"]

ENTRYPOINT ["/entrypoint.sh"]
