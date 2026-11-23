# openGym for Home Assistant (unofficial)

Runs [openGym](https://github.com/DuarteSantos8/openGym), the self-hosted gym and body-weight
tracker, as a Home Assistant app (add-on). It opens in the Home Assistant sidebar, so it is
reachable wherever Home Assistant is, including through Home Assistant Cloud (Nabu Casa) remote
access. No ports to open and no domain to set up.

This is community packaging and is not affiliated with the openGym project.

## Install

1. Settings → Apps → App store → ⋮ → Repositories, add `https://github.com/syky27/hassio-opengym`.
2. Install **openGym**, start it, turn on **Show in sidebar**, and open it.
3. Create your profile with a **password** (the first profile becomes the admin).

[![Add repository](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fsyky27%2Fhassio-opengym)

Details, options and limits: [opengym/DOCS.md](opengym/DOCS.md).

## What works where

| | At home (local address) | Away, through Nabu Casa |
|---|---|---|
| openGym in the Home Assistant sidebar / companion app | yes | yes |
| openGym phone app (iPhone, Android) connected to this server | yes | only with the extra integration below |
| MCP server for AI clients | yes, with port 8080 and the MCP option enabled | no |

### Why the phone app and MCP cannot go through Nabu Casa

Home Assistant shows an app's web page through *ingress*: a private path
(`/api/hassio_ingress/<token>/`) that Home Assistant only serves to a browser carrying a
**Home Assistant login session cookie**. Nabu Casa remote access forwards your Home Assistant
address and nothing else, so everything that reaches openGym from outside has passed that check
first.

- The **phone app** and an **MCP client** are not a browser logged in to Home Assistant. They
  talk straight to an openGym address and authenticate with an openGym token in an
  `Authorization` header. They have no Home Assistant session cookie, and no way to get one, so
  Home Assistant answers them with 401 before openGym ever sees the request.
- **Claude, ChatGPT and Gemini connectors** have a second problem: they call the MCP address from
  their own servers and sign in with OAuth, which needs openGym to be at one public https address
  of its own, with `/.well-known/…` documents at that host's root. Behind ingress the root of the
  host is Home Assistant, not openGym.

So both need a way in that skips Home Assistant's login. On your home network that is the app's
optional **port 8080** (Configuration → Network), which reaches openGym directly and is guarded
only by openGym's own sign-in and tokens. Do not forward that port to the internet as it is. To
use the phone app or MCP away from home you need your own route to port 8080 with https in front
(a VPN such as Tailscale or WireGuard, or a Cloudflare Tunnel); this repository does not set that
up.

### Phone app through Nabu Casa

This repository also contains a small Home Assistant integration, **openGym phone app access**,
that gives the phone app a way in. It serves openGym's API, and only the API, at
`/opengym/api/…` on your Home Assistant address without the Home Assistant login, and passes it
to the openGym app. Because it is an ordinary Home Assistant path, Nabu Casa carries it.

1. Install it: HACS → ⋮ → Custom repositories → add this repository as type **Integration**,
   then download "openGym phone app access". Or copy `custom_components/opengym_proxy` into
   your Home Assistant `config/custom_components/`. Restart Home Assistant.
2. Settings → Devices & services → Add integration → **openGym phone app access** → Submit.
3. In openGym (in the sidebar): Settings → Account → Pair the mobile app, to get a code.
4. In the phone app: Connect to my server, address
   `https://<your-nabu-casa-address>/opengym` (mind the `/opengym`), and the code.

What you are agreeing to: openGym's API is then reachable from the internet by anyone who knows
your Nabu Casa address, guarded by openGym's own pairing codes, tokens and password sign-in
instead of Home Assistant's login. Creating profiles through this path is blocked; make them in
the sidebar panel. Use real passwords. Removing the integration closes the path at once.

### MCP on your LAN

1. Turn on the **MCP server** option, enable port **8080** under Network, restart the app.
2. In openGym: Settings → Integrations → API tokens → New token. Copy it (shown once).
3. Point a local client at `http://<home-assistant-ip>:8080/mcp` with the header
   `Authorization: Bearer ogt_…`, for example:

   ```bash
   claude mcp add --transport http opengym http://<home-assistant-ip>:8080/mcp --header "Authorization: Bearer ogt_…"
   ```

openGym's Settings page shows an MCP address built from its configured origin; ignore it and use
the one above. "Use your subscription" (the Claude/ChatGPT connector sign-in) does not work in
this setup, for the reason given above.

## How it is built

Home Assistant builds the app on your device from `opengym/Dockerfile`, which pulls the two
images upstream publishes (`opengym-api`, `opengym-web`, `opengym-mcp`) and puts them in one container behind
ingress. This repository contains no openGym code and no exercise media; those come from
upstream's images, under upstream's terms (see its
[NOTICE](https://github.com/DuarteSantos8/openGym/blob/main/NOTICE.md) — the exercise media is
licensed for use within openGym only).

A scheduled workflow opens a pull request when upstream publishes a release. Once merged,
Home Assistant offers the update.

## License

AGPL-3.0, the same as openGym. See [LICENSE](LICENSE).
