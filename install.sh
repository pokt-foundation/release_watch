#!/bin/bash

root_dir="$(cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
pdir="$(pwd)"

cd "$root_dir"
/usr/bin/env python3 -m venv ./venv
./venv/bin/pip install .

mkdir -p ~/.config/systemd/user
cp ./config/release-watch.service ~/.config/systemd/user
systemctl --user enable release-watch.service
