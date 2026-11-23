# openGym

Unofficial packaging of [openGym](https://github.com/DuarteSantos8/openGym). Turn on **Show in sidebar** on the app page and open it from the
sidebar. It works on your local address and through Home Assistant Cloud (Nabu Casa) alike.

## Signing in

Home Assistant decides who can open the panel; openGym then has its own profiles, one per
person. Create yours with **Create new profile → Password**. The first profile on a fresh
install is the admin (Settings → Admin dashboard: invites, users, password resets).

Use a password, not a passkey. A passkey belongs to one hostname, and Home Assistant is usually
reached at several (local address, Nabu Casa address), so a passkey made on one fails on the
other. If you only ever use one https address, set **Origin** to it and passkeys work there.

## Options

| Option | Default | What it does |
|---|---|---|
| Password sign-in | on | Name + password sign-in. Leave on unless you set Origin. |
| First profile is admin | on | The first profile on an empty install becomes admin. |
| Allow guests | on | "Continue without account" (data stays in that browser). |
| Invite only | off | New profiles need an invite code from the admin dashboard. |
| Session length | 90 | Days a sign-in lasts. |
| Default language | – | e.g. `de`, `fr`, `pt-BR`. |
| MCP server | off | AI clients on your LAN, see below. |
| Origin | – | Advanced, for passkeys: your single https address. |

## The phone app

The openGym iPhone/Android app talks to a server directly and cannot go through Home
Assistant's sign-in, so it cannot connect over Nabu Casa. Two ways to use a phone:

- Open openGym in the Home Assistant companion app or a browser. This works everywhere.
- At home only: enable port 8080 under Configuration → Network, then in the phone app choose
  "Connect to my server" with `http://<home-assistant-ip>:8080` and a pairing code from
  Settings → Account → Pair the mobile app. That port has no Home Assistant sign-in in front
  of it, only openGym's own; do not forward it to the internet.

## MCP for AI clients (LAN only)

openGym's MCP server lets an AI client read and, if the token allows it, change your plan and
log. Turn on **MCP server**, enable port 8080 under Configuration → Network, restart, then make a
token in openGym under Settings → Integrations → API tokens and give the client
`http://<home-assistant-ip>:8080/mcp` with the header `Authorization: Bearer ogt_…`.

It does not work through Nabu Casa, for the same reason as the phone app: Home Assistant only
lets requests with a Home Assistant login through, and these clients sign in to openGym with a
token instead. The Claude/ChatGPT "connector" sign-in also needs openGym on a public https address
of its own, which this app does not provide. Ignore the MCP address openGym's Settings page
shows; use the one above.

## Data and backups

Everything is in the app's data folder and is included in Home Assistant backups (the app is
stopped for a moment while it is backed up). Restoring a backup restores profiles and workouts.

## Not included

The AI Coach's bundled runtimes and OIDC sign-in are not set up by this app.
