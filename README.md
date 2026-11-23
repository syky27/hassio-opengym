# openGym for Home Assistant (unofficial)

Runs [openGym](https://github.com/DuarteSantos8/openGym), the self-hosted gym and body-weight
tracker, as a Home Assistant app (add-on). It opens in the Home Assistant sidebar, so it is
reachable wherever Home Assistant is, including through Home Assistant Cloud (Nabu Casa) remote
access. No ports to open and no domain to set up.

This is community packaging and is not affiliated with the openGym project.

## What you get

| | At home | Away, through Nabu Casa | Set up in |
|---|---|---|---|
| openGym in the Home Assistant sidebar and companion app | yes | yes | [Part 1](#part-1--install-opengym) |
| The openGym phone app (iPhone, Android) syncing with this server | yes | yes | [Part 3](#part-3--connect-the-opengym-phone-app-optional) |
| MCP server for AI clients | yes | no | [Part 4](#part-4--mcp-for-ai-clients-on-your-lan-optional) |

## Part 1 — Install openGym

1. In Home Assistant open **Settings → Apps → App store**.
2. Press **⋮** (top right) → **Repositories**, paste this address and press **Add**:

   ```
   https://github.com/syky27/hassio-opengym
   ```

   Or use this button:
   [![Add repository](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fsyky27%2Fhassio-opengym)
3. Close the dialog, find **openGym** in the store (reload the page if it is not listed) and
   press **Install**. Home Assistant builds the app on your device; this takes a few minutes.
4. Press **Start**.
5. On the same page turn on **Show in sidebar**. Home Assistant leaves this off, and without it
   there is no openGym entry in the sidebar.
6. Click **openGym** in the sidebar.
7. Press **Create new profile → Password**, pick a name and a password of at least 10
   characters. The first profile becomes the admin.
   [Why a password and not a passkey?](#signing-in-passwords-not-passkeys)

Options and details: [opengym/DOCS.md](opengym/DOCS.md).

## Part 2 — Use it away from home

There is nothing to set up. openGym is part of your Home Assistant, so it is wherever Home
Assistant is:

- **Browser:** open your Nabu Casa address, sign in to Home Assistant, click **openGym** in the
  sidebar.
- **Phone:** open the Home Assistant companion app and pick **openGym** from the sidebar.

Your Nabu Casa address is shown under **Settings → Home Assistant Cloud → Remote access**. It
looks like `https://abcdefgh1234abcdefgh1234abcdefgh.ui.nabu.casa`.

## Part 3 — Connect the openGym phone app (optional)

The openGym app from the App Store or the Android APK cannot use the sidebar route: it talks to
a server directly and has no Home Assistant login
([details](#background-why-the-phone-app-needs-its-own-way-in)). This repository contains a
small Home Assistant integration, **openGym phone app access**, that gives it a way in: it
serves openGym's API at `/opengym` on your Home Assistant address, without the Home Assistant
login. Nabu Casa carries that path like any other.

### Step 1 — Install the integration

Pick one.

**Without HACS.** Install and start the **Terminal & SSH** app from the App store, open its
terminal and paste:

```sh
cd /config && mkdir -p custom_components && wget -qO- https://github.com/syky27/hassio-opengym/archive/refs/heads/master.tar.gz | tar xz --strip-components=2 -C custom_components hassio-opengym-master/custom_components/opengym_proxy
```

**With HACS.** Press this button and confirm; it opens HACS with this repository filled in.
Then press **Download**.

[![Open this repository in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=syky27&repository=hassio-opengym&category=integration)

Or by hand: HACS → ⋮ → **Custom repositories** → add
`https://github.com/syky27/hassio-opengym` as type **Integration**, then download
"openGym phone app access".

### Step 2 — Restart Home Assistant

**Settings → System → Restart Home Assistant**. The integration is not
visible before the restart.

### Step 3 — Add the integration

**Settings → Devices & services → Add integration**, search for **openGym phone app access**,
leave the address as it is filled in and press **Submit**. It should say "Created configuration
for openGym". If it says "No openGym answered at that address", the openGym app is not running:
start it (Part 1, step 4) and try again.

### Step 4 — Check it in a browser

Open this address in any browser, with your own Nabu Casa address in front:

```
https://abcdefgh1234abcdefgh1234abcdefgh.ui.nabu.casa/opengym/api/health
```

You should see exactly this kind of answer, with no login page:

```json
{"ok":true,"users":1,"writable":true}
```

Do not go on until this works. `404: Not Found` means step 2 or step 3 is missing.

### Step 5 — Get a pairing code

In openGym in the Home Assistant sidebar: **Settings → Account → Pair the mobile app**. Confirm
with your password. The code is valid for **5 minutes**; get a new one if it runs out.

### Step 6 — Connect the phone app

In the phone app choose **Connect to my server** (first launch, or Settings → Account). Type the
address and the code, then press **Connect**.

The address is your Home Assistant address **followed by `/opengym`**, nothing more:

```
https://abcdefgh1234abcdefgh1234abcdefgh.ui.nabu.casa/opengym
```

| Address | Works? |
|---|---|
| `https://abcdefgh….ui.nabu.casa/opengym` | **Yes.** Use this one. It works at home and away. |
| `https://abcdefgh….ui.nabu.casa` | No. Without `/opengym` the app reaches Home Assistant, not openGym. |
| `https://abcdefgh….ui.nabu.casa/opengym/api` | No. The app adds `/api` itself. |
| `https://abcdefgh….ui.nabu.casa/api/hassio_ingress/…` or `…/app/…_opengym` | No. Those are the sidebar addresses from the browser bar; they need a Home Assistant login. |
| `http://192.168.1.10:8123/opengym` or `http://homeassistant.local:8123/opengym` | Only on your home network, and only where the phone allows plain `http` (Android does; iPhone may refuse). Prefer the Nabu Casa address. |

### If it does not connect

| The app says | Cause | Fix |
|---|---|---|
| "That address answers, but a login page or proxy rule replied instead of openGym" | The address has no `/opengym`, or the integration is not added | Check the address against the table above, then redo step 4 |
| The code is wrong or expired | Pairing codes last 5 minutes and work once | Get a new code (step 5) |
| "Your server was reached, but it refused the app's request (CORS)" | The address points at Home Assistant itself | Add `/opengym` |
| Nothing answers | Remote access is off, or the address is mistyped | Check Settings → Home Assistant Cloud → Remote access |

### What you are opening up

With the integration added, openGym's API is reachable from the internet by anyone who knows
your Nabu Casa address, guarded by openGym's own pairing codes, tokens and password sign-in
instead of Home Assistant's login. Only the API is served, not the openGym pages, and creating
profiles through this path is blocked (make them in the sidebar). Use real passwords. Removing
the integration under Devices & services closes the path at once.

## Part 4 — MCP for AI clients on your LAN (optional)

openGym's MCP server lets an AI client read and, if the token allows it, change your plan and
log. It works on your home network only.

1. On the openGym app page: **Configuration** → turn on **MCP server**; under **Network** enter
   `8080` for the port; **Save** and restart the app.
2. In openGym: **Settings → Integrations → API tokens → New token**. Copy it (shown once).
3. Point a client on your home network at `http://<home-assistant-ip>:8080/mcp`, with the
   header `Authorization: Bearer ogt_…`. For example, with Home Assistant at `192.168.1.10`:

   ```bash
   claude mcp add --transport http opengym http://192.168.1.10:8080/mcp --header "Authorization: Bearer ogt_…"
   ```

openGym's own Settings page shows an MCP address built from its configured origin; ignore it and
use the one above. "Use your subscription" (the Claude/ChatGPT connector sign-in) does not work
in this setup: those services call from their own servers and need openGym at a public `https`
address of its own. Port 8080 has no Home Assistant login in front of it, only openGym's own;
do not forward it to the internet.

## Updating

The app and the phone app integration are two separate pieces and update separately.

**The openGym app**

1. Settings → Apps → App store → ⋮ → **Check for updates**.
2. Open **openGym** and press **Update**.

Home Assistant rebuilds the app on your device, which takes a few minutes. Profiles and
workouts are kept. Home Assistant also checks for updates on its own, so the update may already
be listed under Settings.

**The phone app integration** (only if you installed it)

- Installed with the Terminal command: delete the old folder, run the command from Part 3
  step 1 again, and restart Home Assistant:

  ```sh
  rm -rf /config/custom_components/opengym_proxy
  ```

- Installed through HACS: HACS lists the update; download it and restart Home Assistant.

Updating the app never installs or updates the integration.

## Signing in: passwords, not passkeys

Home Assistant decides who can open the panel; openGym then has its own profiles. This app turns
on openGym's **password sign-in** and expects you to use it. Passkeys, openGym's usual default,
do not fit behind Home Assistant:

- **A passkey belongs to one hostname.** The browser ties it to the site's hostname when it is
  created and only offers it there.
- **openGym accepts exactly one address.** The server is configured with a single origin and
  rejects a passkey sign-in from any other.
- **Home Assistant has several.** `homeassistant.local`, a LAN IP, your Nabu Casa address: a
  passkey made on one fails on the others.
- **Local addresses usually cannot use passkeys at all.** Browsers allow them only over `https`
  and never on a bare IP address, so on `http://192.168.1.10:8123` openGym reports that the
  browser does not support passkeys.

So the app leaves openGym's origin on a neutral `http` value and uses passwords, which work on
every address.

If you only ever open openGym at one `https` address (your Nabu Casa one), you can have
passkeys: set the app's **Origin** option to that address, for example
`https://abcdefgh1234abcdefgh1234abcdefgh.ui.nabu.casa` (no path, no trailing slash), and
restart. The trade-off: sign-in then stops working on plain-`http` local addresses, because the
session cookie becomes https-only. This option is untested, and passkeys may not work inside the
Home Assistant companion app's embedded browser; use Safari or another real browser for them.

## Background: why the phone app needs its own way in

Home Assistant shows an app's web page through *ingress*: a private path
(`/api/hassio_ingress/<token>/`) that Home Assistant only serves to a browser carrying a
**Home Assistant login session cookie**. Nabu Casa remote access forwards your Home Assistant
address and nothing else, so everything that reaches openGym through the sidebar has passed that
check first.

The phone app and an MCP client are not a browser logged in to Home Assistant. They talk
straight to an openGym address and authenticate with an openGym token in an `Authorization`
header. They have no Home Assistant session cookie and no way to get one, so through ingress
Home Assistant answers them with 401 before openGym ever sees the request. That is why the phone
app needs the `/opengym` path from Part 3, and why MCP is offered only on the direct LAN port.

## How it is built

Home Assistant builds the app on your device from `opengym/Dockerfile`, which pulls the three
images upstream publishes (`opengym-api`, `opengym-web`, `opengym-mcp`) and puts them in one
container behind ingress. This repository contains no openGym code and no exercise media; those
come from upstream's images, under upstream's terms (see its
[NOTICE](https://github.com/DuarteSantos8/openGym/blob/main/NOTICE.md) — the exercise media is
licensed for use within openGym only).

A nightly workflow follows openGym: when upstream publishes a release, it moves this repository
to that version, builds and starts the result, and only if that works commits it and publishes a
GitHub release with the same number. Home Assistant then offers the app update, and HACS the
integration update. Versions are openGym's (`1.4.5`), with a fourth number for changes to the
packaging alone (`1.4.5.1`).

## License

AGPL-3.0, the same as openGym. See [LICENSE](LICENSE).
