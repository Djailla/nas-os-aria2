#!/bin/bash

mkdir -m 755 -p /www/webui
mkdir -m 755 -p /opt/aria2/config
install -m 755 /home/source/rc.local /etc
install -m 755 /home/source/webui-server.py /www/

# Install aria2
apt-get update
apt-get install -y -q python-webpy git aria2

# Install aria2 web ui
cd /tmp
git clone --depth=1 https://github.com/ziahamza/webui-aria2.git
mv webui-aria2/* /www/webui

# Cleanup
apt-get -y -q autoremove git
apt-get -y -q clean
rm -rf /tmp/*

exit 0
