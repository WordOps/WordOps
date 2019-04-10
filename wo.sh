#!/usr/bin/env bash
# -------------------------------------------------------------------------
# WordOps install script downloader
# -------------------------------------------------------------------------
# Website:       https://wordops.net
# GitHub:        https://github.com/WordOps/WordOps
# Copyright (c) 2019 - WordOps
# This script is licensed under M.I.T
# -------------------------------------------------------------------------
# Version 3.9.5 - 2019-04-10
# -------------------------------------------------------------------------

###
# 1 - Check whether the installation is called with elevated rights
###
if [[ $EUID -ne 0 ]]; then
    wo_lib_echo_fail "Sudo privilege required..."
    wo_lib_echo_fail "Use: wget -qO wo wops.cc && sudo bash wo"
    exit 100
fi

[ -z "$(command -v git)" ] && {
    apt-get update -qq && apt-get install git -qq
} > /dev/null 2>&1

# update or clone wordops repositoru
if [ -d /tmp/WordOps/.git ]; then
    git -C /tmp/WordOps pull origin master -q
else
    rm -rf /tmp/WordOps
    git clone https://github.com/WordOps/WordOps.git /tmp/WordOps -b "$@" -q
fi

if [ -x /tmp/WordOps/install ]; then
/tmp/WordOps/install "$@"
fi
