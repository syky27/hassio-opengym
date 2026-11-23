#!/bin/sh
# Moves every place that names the packaged openGym version to $1. Used by the release workflow.
set -eu
new=$1
sed -i "s/^ARG OPENGYM_VERSION=.*/ARG OPENGYM_VERSION=$new/" opengym/Dockerfile
sed -i "s/^version: .*/version: \"$new\"/" opengym/config.yaml
sed -i "s/^  \"version\": .*/  \"version\": \"$new\"/" custom_components/opengym_proxy/manifest.json
sed -i "0,/^## /s//## $new\n\n- openGym $new: https:\/\/github.com\/DuarteSantos8\/openGym\/releases\/tag\/v$new\n\n## /" opengym/CHANGELOG.md
