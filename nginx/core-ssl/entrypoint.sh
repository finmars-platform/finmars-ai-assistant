#!/bin/bash
set -euo pipefail
umask 027

DOMAIN_RAW="${DOMAIN:-}"
EMAIL="${EMAIL:-}"
TZ="${TZ:-UTC}"
NGINX_USER="${NGINX_USER:-nginx}"
POST_RENEW_SCRIPT="/usr/local/bin/renewal-post-hook.sh"
LOGROTATE_CONFIG="${LOGROTATE_CONFIG:-/etc/logrotate.d/nginx}"
LOGROTATE_STATE="${LOGROTATE_STATE:-/var/lib/logrotate/nginx.status}"

if [[ -z "${DOMAIN_RAW}" ]]; then
  echo "Error: DOMAIN environment variable is required (e.g. example.com)." >&2
  exit 1
fi

DOMAIN_HOST="${DOMAIN_RAW}"
case "${DOMAIN_HOST}" in
  http://*)
    DOMAIN_HOST="${DOMAIN_HOST#http://}"
    ;;
  https://*)
    DOMAIN_HOST="${DOMAIN_HOST#https://}"
    ;;
esac

DOMAIN_HOST="${DOMAIN_HOST%%/}"

if [[ "${DOMAIN_HOST}" == *"/"* ]]; then
  echo "Error: DOMAIN must not contain a path; provide only the domain (e.g. example.com)." >&2
  exit 1
fi

if [[ "${DOMAIN_HOST}" == *:* ]]; then
  echo "Error: DOMAIN must not include a port; provide only the domain (e.g. example.com)." >&2
  exit 1
fi

if [[ -z "${EMAIL}" ]]; then
  echo "Error: EMAIL environment variable is required for Let's Encrypt registration." >&2
  exit 1
fi

export DOMAIN_HOST

CERTBOT_WEBROOT="/var/www/certbot"
NGINX_CONF_DIR="/etc/nginx/conf.d"
HTTP_CONF="${NGINX_CONF_DIR}/http.conf"
HTTPS_CONF="${NGINX_CONF_DIR}/https.conf"
LE_DIR="/etc/letsencrypt"
LIVE_DIR="${LE_DIR}/live/${DOMAIN_HOST}"

mkdir -p "${CERTBOT_WEBROOT}"
mkdir -p "${LE_DIR}"
mkdir -p "${NGINX_CONF_DIR}"

ensure_timezone() {
  if [[ -f "/usr/share/zoneinfo/${TZ}" ]]; then
    ln -sf "/usr/share/zoneinfo/${TZ}" /etc/localtime
    echo "${TZ}" > /etc/timezone
  fi
}

generate_http_config() {
  envsubst '${DOMAIN_HOST}' < /templates/http.conf.template > "${HTTP_CONF}"
  chown root:"${NGINX_USER}" "${HTTP_CONF}"
  chmod 640 "${HTTP_CONF}"
}

generate_https_config() {
  envsubst '${DOMAIN_HOST}' < /templates/https.conf.template > "${HTTPS_CONF}"
  chown root:"${NGINX_USER}" "${HTTPS_CONF}"
  chmod 640 "${HTTPS_CONF}"
  rm -f "${HTTP_CONF}"
}

ensure_tls_assets() {
  if [[ ! -f "${LE_DIR}/options-ssl-nginx.conf" ]]; then
    cp /defaults/options-ssl-nginx.conf "${LE_DIR}/options-ssl-nginx.conf"
  fi

  if [[ ! -f "${LE_DIR}/ssl-dhparams.pem" ]]; then
    echo "Generating Diffie-Hellman parameters (this can take a moment)..."
    openssl dhparam -out "${LE_DIR}/ssl-dhparams.pem" 2048
  fi
}

obtain_initial_certificate_if_needed() {
  if [[ -f "${LIVE_DIR}/fullchain.pem" ]]; then
    return
  fi

  rm -f "${HTTPS_CONF}"

  echo "No existing certificate found. Starting Nginx with temporary HTTP configuration..."
  nginx

  sleep 2

  echo "Requesting initial Let's Encrypt certificate for ${DOMAIN_HOST}..."
  if certbot certonly \
    --webroot -w "${CERTBOT_WEBROOT}" \
    --email "${EMAIL}" \
    --agree-tos \
    --no-eff-email \
    -d "${DOMAIN_HOST}"; then
    echo "Certificate obtained successfully."
  else
    echo "Failed to obtain certificate." >&2
    nginx -s stop || true
    exit 1
  fi

  nginx -s stop
}

ensure_permissions() {
  if [[ -d "${LE_DIR}" ]]; then
    chown -R root:"${NGINX_USER}" "${LE_DIR}"
    find "${LE_DIR}" -type d -exec chmod 750 {} \;
    find "${LE_DIR}" -type f -exec chmod 640 {} \;
  fi

  if [[ -d "${CERTBOT_WEBROOT}" ]]; then
    chown -R "${NGINX_USER}:${NGINX_USER}" "${CERTBOT_WEBROOT}"
    find "${CERTBOT_WEBROOT}" -type d -exec chmod 750 {} \;
    find "${CERTBOT_WEBROOT}" -type f -exec chmod 640 {} \;
  fi

  if [[ -d "/var/cache/nginx" ]]; then
    chown -R "${NGINX_USER}:${NGINX_USER}" /var/cache/nginx
  fi

  mkdir -p /var/run/nginx
  touch /var/run/nginx/nginx.pid
  chown -R "${NGINX_USER}:${NGINX_USER}" /var/run/nginx
  chmod 750 /var/run/nginx
  chmod 640 /var/run/nginx/nginx.pid

  mkdir -p /var/log/nginx
  chown "${NGINX_USER}:${NGINX_USER}" /var/log/nginx
  chmod 750 /var/log/nginx
  touch /var/log/nginx/access.log /var/log/nginx/error.log
  chown "${NGINX_USER}:${NGINX_USER}" /var/log/nginx/access.log /var/log/nginx/error.log
  chmod 640 /var/log/nginx/access.log /var/log/nginx/error.log

  mkdir -p "$(dirname "${LOGROTATE_STATE}")"
  touch "${LOGROTATE_STATE}"
  chown root:root "${LOGROTATE_STATE}"
  chmod 640 "${LOGROTATE_STATE}"
}

write_post_renew_script() {
  cat <<EOF > "${POST_RENEW_SCRIPT}"
#!/bin/sh
set -eu

LE_DIR="${LE_DIR}"
CERTBOT_WEBROOT="${CERTBOT_WEBROOT}"
NGINX_USER="${NGINX_USER}"

if [ -d "\${LE_DIR}" ]; then
  chown -R root:"\${NGINX_USER}" "\${LE_DIR}"
  find "\${LE_DIR}" -type d -exec chmod 750 {} \;
  find "\${LE_DIR}" -type f -exec chmod 640 {} \;
fi

if [ -d "\${CERTBOT_WEBROOT}" ]; then
  chown -R "\${NGINX_USER}:\${NGINX_USER}" "\${CERTBOT_WEBROOT}"
  find "\${CERTBOT_WEBROOT}" -type d -exec chmod 750 {} \;
  find "\${CERTBOT_WEBROOT}" -type f -exec chmod 640 {} \;
fi

if [ -d "/var/cache/nginx" ]; then
  chown -R "\${NGINX_USER}:\${NGINX_USER}" /var/cache/nginx
fi

mkdir -p /var/run/nginx
touch /var/run/nginx/nginx.pid
chown -R "\${NGINX_USER}:\${NGINX_USER}" /var/run/nginx
chmod 750 /var/run/nginx
chmod 640 /var/run/nginx/nginx.pid

mkdir -p /var/log/nginx
chown "\${NGINX_USER}:\${NGINX_USER}" /var/log/nginx
chmod 750 /var/log/nginx
touch /var/log/nginx/access.log /var/log/nginx/error.log
chown "\${NGINX_USER}:\${NGINX_USER}" /var/log/nginx/access.log /var/log/nginx/error.log
chmod 640 /var/log/nginx/access.log /var/log/nginx/error.log

nginx -s reload
EOF

  chmod 750 "${POST_RENEW_SCRIPT}"
}

configure_logrotate() {
  mkdir -p "$(dirname "${LOGROTATE_CONFIG}")"
  cat <<EOF > "${LOGROTATE_CONFIG}"
/var/log/nginx/*.log {
    daily
    rotate 14
    missingok
    notifempty
    compress
    delaycompress
    sharedscripts
    create 640 ${NGINX_USER} ${NGINX_USER}
    postrotate
        nginx -s reopen
    endscript
}
EOF
  chown root:root "${LOGROTATE_CONFIG}"
  chmod 640 "${LOGROTATE_CONFIG}"
}

install_cron_job() {
  cat <<EOF > /etc/crontabs/root
SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
0 0 * * * /usr/sbin/logrotate -s ${LOGROTATE_STATE} ${LOGROTATE_CONFIG}
30 3 * * * certbot renew --webroot -w ${CERTBOT_WEBROOT} --quiet --deploy-hook "${POST_RENEW_SCRIPT}"
EOF
}

ensure_timezone
generate_http_config
ensure_tls_assets
obtain_initial_certificate_if_needed
ensure_permissions
write_post_renew_script
configure_logrotate
generate_https_config
install_cron_job

echo "Starting cron daemon for certificate renewals..."
crond -l 2

echo "Starting Nginx with HTTPS configuration..."
exec /sbin/su-exec "${NGINX_USER}" nginx -g "daemon off;"
