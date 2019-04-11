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
    wo_lib_echo_fail "Use: curl -sL wops.cc | sudo bash"
    exit 100
fi

# check if git is installed
[ -z "$(command -v git)" ] && {
    apt-get update -qq && apt-get install git -qq
} > /dev/null 2>&1

# set github repository branch
if [ -n "$1" ]; then
    wo_branch="$1"
else
    wo_branch=master
fi

# update or clone wordops repositoru
if [ -d /tmp/WordOps/.git ]; then
    git -C /tmp/WordOps fetch --all
    git -C /tmp/WordOps reset --hard origin/${wo_branch}
    git -C /tmp/WordOps clean -f
else
    rm -rf /tmp/WordOps
    git clone https://github.com/WordOps/WordOps.git /tmp/WordOps -b "$wo_branch" -q
fi

# execute install script
if [ -x /tmp/WordOps/install ]; then
    /tmp/WordOps/install
fi
