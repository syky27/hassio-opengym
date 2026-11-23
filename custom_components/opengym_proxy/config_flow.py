import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_UPSTREAM, DOMAIN


def _guess(hass):
    """The openGym app's address on the internal network, if the Supervisor knows the app."""
    try:
        from homeassistant.components.hassio import get_addons_list, hostname_from_addon_slug
        for app in get_addons_list(hass) or []:
            if app["slug"].endswith("_opengym"):
                return f"http://{hostname_from_addon_slug(app['slug'])}:8080"
    except Exception:  # noqa: BLE001 - no Supervisor, or its API moved: the user types it
        pass
    return "http://local-opengym:8080"


class OpenGymFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            upstream = user_input[CONF_UPSTREAM].rstrip("/")
            try:
                async with async_get_clientsession(self.hass).get(f"{upstream}/api/health", timeout=10) as res:
                    ok = res.status == 200 and (await res.json()).get("ok") is True
            except Exception:  # noqa: BLE001
                ok = False
            if ok:
                return self.async_create_entry(title="openGym", data={CONF_UPSTREAM: upstream})
            errors["base"] = "cannot_connect"
        default = (user_input or {}).get(CONF_UPSTREAM) or _guess(self.hass)
        return self.async_show_form(
            step_id="user", errors=errors,
            data_schema=vol.Schema({vol.Required(CONF_UPSTREAM, default=default): str}))
