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
# A stop from the Supervisor is a clean exit; any process dying on its own is not, and ends the
# container so the Supervisor can restart them all.
pids=
trap 'kill $pids 2>/dev/null; exit 0' TERM INT
if [ "$(opt mcp)" = true ]; then
  # Tells the app to show the MCP page in Settings. The server holds no data: it calls the API
  # with each request's own token. No ORIGIN for it: the one configured address is not where a
  # LAN client reaches it, and with none set it turns every browser page away (DNS rebinding).
  export MCP=on
  ( cd /opt/mcp/mcp && exec env -u ORIGIN OPENGYM_API_URL=http://127.0.0.1:3000 MCP_PORT=3100 \
      su node -s /bin/sh -c 'exec node src/http.js' ) & pids="$pids $!"
fi
node server.js & pids="$pids $!"
nginx -g 'daemon off;' & pids="$pids $!"
# Polled: busybox's `wait -n` did not return here when node died.
while :; do
  for p in $pids; do kill -0 "$p" 2>/dev/null || break 2; done
  sleep 5 & wait $!
done
kill $pids 2>/dev/null || true
exit 1
