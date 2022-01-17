#!/bin/bash

root_dir="$(cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
pdir="$(pwd)"

cd "$root_dir"
/usr/bin/env python3 -m venv ./venv
./venv/bin/pip install .

mkdir -p ~/.config/systemd/user
mkdir -p ./build
cp ./config/release-watch.service ./build/release-watch.service
sed -i "s|ExecStart=|ExecStart=${root_dir}/venv/bin/release_watch|g" ./build/release-watch.service
cp ./build/release-watch.service ~/.config/systemd/user
systemctl --user enable release-watch.service
