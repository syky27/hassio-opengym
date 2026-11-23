"""Lets the openGym phone app reach the openGym app's API through Home Assistant.

Serves /opengym/api/... without a Home Assistant login and forwards it to the openGym app,
which checks its own pairing codes and tokens. Only the API: no pages, and no way to sign up.
"""
from aiohttp import web

from homeassistant.components.http import HomeAssistantView
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_UPSTREAM, DOMAIN

# Not ours to pass on: hop-by-hop headers, Home Assistant's own cookies (the ingress session
# among them), and forwarding headers a caller could have made up.
DROP = {"host", "cookie", "connection", "keep-alive", "transfer-encoding", "content-length", "upgrade",
        "x-forwarded-for", "x-forwarded-host", "x-forwarded-proto", "x-real-ip", "cf-connecting-ip"}
DROP_BACK = {"connection", "keep-alive", "transfer-encoding", "content-length", "content-encoding", "set-cookie"}


async def async_setup_entry(hass, entry):
    # aiohttp cannot take a route away again, so the view is registered once and reads its
    # target from here: reconfiguring or removing the entry takes effect without a restart.
    if DOMAIN not in hass.data:
        hass.http.register_view(ProxyView(hass))
    hass.data[DOMAIN] = entry.data[CONF_UPSTREAM].rstrip("/")
    return True


async def async_unload_entry(hass, entry):
    hass.data[DOMAIN] = None
    return True


class ProxyView(HomeAssistantView):
    url = "/opengym/api/{path:.*}"
    name = "opengym_proxy"
    requires_auth = False  # openGym checks its own codes and tokens
    # Home Assistant answers the CORS preflight on its own routes, so it has to allow the phone
    # app's WebView origin; openGym's own CORS headers are dropped below, two sets are refused.
    cors_allowed = True

    def __init__(self, hass):
        self.hass = hass

    async def _proxy(self, request, path):
        upstream = self.hass.data.get(DOMAIN)
        if not upstream:
            raise web.HTTPNotFound
        # This address is on the internet. A paired phone never creates a profile, so nobody
        # arriving this way may: profiles are made in the openGym panel inside Home Assistant.
        if path.startswith("register/"):
            return web.json_response({"error": "create profiles in Home Assistant"}, status=403)
        headers = {k: v for k, v in request.headers.items() if k.lower() not in DROP}
        headers["X-Forwarded-For"] = request.remote or ""
        async with async_get_clientsession(self.hass).request(
            request.method, f"{upstream}/api/{path}", params=request.query, headers=headers,
            data=request.content if request.can_read_body else None, allow_redirects=False,
        ) as res:
            back = web.StreamResponse(status=res.status, headers={
                k: v for k, v in res.headers.items()
                if k.lower() not in DROP_BACK and not k.lower().startswith("access-control-")})
            await back.prepare(request)
            async for chunk in res.content.iter_chunked(65536):
                await back.write(chunk)
            await back.write_eof()
            return back

    get = post = put = delete = _proxy
