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

## How it is built

Home Assistant builds the app on your device from `opengym/Dockerfile`, which pulls the two
images upstream publishes (`opengym-api`, `opengym-web`) and puts them in one container behind
ingress. This repository contains no openGym code and no exercise media; those come from
upstream's images, under upstream's terms (see its
[NOTICE](https://github.com/DuarteSantos8/openGym/blob/main/NOTICE.md) — the exercise media is
licensed for use within openGym only).

A scheduled workflow opens a pull request when upstream publishes a release. Once merged,
Home Assistant offers the update.

## License

AGPL-3.0, the same as openGym. See [LICENSE](LICENSE).
