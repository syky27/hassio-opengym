# Wraps the two upstream images in one container. Nothing from upstream is copied into this
# repository: the device pulls the published images and this file only rearranges them.
ARG OPENGYM_VERSION=1.4.5

# Renders upstream's own nginx config inside the web image, where its CSP (with the per-release
# script hash) is in the environment, with the two changes ingress needs.
FROM ghcr.io/duartesantos8/opengym-web:${OPENGYM_VERSION} AS web
USER root
ENV NGINX_PORT=8099 BACKEND=127.0.0.1 PORT=3000 BASE_PATH=""
RUN set -eu; t=/etc/nginx/templates/default.conf.template; \
    # Ingress shows the app in a frame on Home Assistant's own origin: upstream forbids all framing.
    grep -q 'X-Frame-Options "DENY"' "$t"; \
    echo "$CONTENT_SECURITY_POLICY" | grep -q "frame-ancestors 'none'"; \
    grep -q '^    server_tokens off;$' "$t"; \
    grep -q '^        proxy_set_header Host $host;$' "$t"; \
    export CONTENT_SECURITY_POLICY="$(echo "$CONTENT_SECURITY_POLICY" | sed "s/frame-ancestors 'none'/frame-ancestors 'self'/")"; \
    { \
      sed -e 's/X-Frame-Options "DENY"/X-Frame-Options "SAMEORIGIN"/' \
          -e 's/^    listen ${NGINX_PORT};$/    listen 8099;\n    listen 8080;/' \
          -e 's/^        proxy_set_header Host $host;$/&\n        proxy_set_header Origin $api_origin;/' \
          -e 's/^    server_tokens off;$/    server_tokens off;\n    if ($ingress_denied) { return 403; }/' "$t" \
      | envsubst "$(printf '${%s} ' $(grep -o '\${[A-Z_]*}' "$t" | tr -d '${}' | sort -u))"; \
    } > /opengym.conf; \
    grep -q 'listen 8080;' /opengym.conf; grep -q 'ingress_denied' /opengym.conf; grep -q 'api_origin' /opengym.conf; \
    ! grep -q '\${' /opengym.conf

FROM ghcr.io/duartesantos8/opengym-api:${OPENGYM_VERSION}
ARG BUILD_VERSION=dev
LABEL io.hass.version="${BUILD_VERSION}" io.hass.type="app" io.hass.arch="aarch64|amd64"
RUN apk add --no-cache nginx jq \
 && ln -sf /dev/stdout /var/log/nginx/access.log && ln -sf /dev/stderr /var/log/nginx/error.log
COPY --from=web /usr/share/nginx/html /usr/share/nginx/html
COPY --from=web /opengym.conf /etc/nginx/http.d/default.conf
COPY ingress-guard.conf /etc/nginx/http.d/00-ingress-guard.conf
COPY run.sh /run.sh
RUN chmod +x /run.sh && nginx -t
ENV DATA_DIR=/data PORT=3000 TRUST_PROXY=1 RP_NAME=openGym
CMD ["/run.sh"]
