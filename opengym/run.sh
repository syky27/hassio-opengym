#!/bin/sh
set -eu
opt() { jq -r "(.$1 // \"\") | tostring" /data/options.json; }
flag() { [ "$(opt "$1")" = true ] && echo 1 || echo 0; }

export PASSWORD_LOGIN="$(flag password_login)" FIRST_USER_ADMIN="$(flag first_user_admin)"
export ALLOW_GUEST="$(flag allow_guest)" INVITE_ONLY="$(flag invite_only)"
export SESSION_DAYS="$(opt session_days)"
[ -z "$(opt default_lang)" ] || export DEFAULT_LANG="$(opt default_lang)"

# http on purpose by default: the session cookie then has no Secure flag and works on the local
# http address and the Nabu Casa https one alike. Passkeys need the single https origin instead.
ORIGIN="$(opt origin)"; export ORIGIN="${ORIGIN:-http://homeassistant.local:8123}"
RP_ID="${ORIGIN#*://}"; RP_ID="${RP_ID%%[:/]*}"; export RP_ID

cd /app
# A stop from the Supervisor is a clean exit; either process dying on its own is not, and ends
# the container so the Supervisor can restart both.
trap 'kill "$api" "$web" 2>/dev/null; exit 0' TERM INT
node server.js & api=$!
nginx -g 'daemon off;' & web=$!
# Polled: busybox's `wait -n` did not return here when node died.
while kill -0 "$api" 2>/dev/null && kill -0 "$web" 2>/dev/null; do sleep 5 & wait $!; done
kill "$api" "$web" 2>/dev/null || true
exit 1
