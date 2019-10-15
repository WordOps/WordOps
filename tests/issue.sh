#!/usr/bin/env bash
# -------------------------------------------------------------------------
# WordOps support script
# -------------------------------------------------------------------------
# Website:       https://wordops.net
# GitHub:        https://github.com/WordOps/WordOps
# Copyright (c) 2019 - WordOps
# This script is licensed under M.I.T
# -------------------------------------------------------------------------
# curl -sL git.io/fjAp3 | sudo -E bash -
# -------------------------------------------------------------------------
# Version 3.9.8.4 - 2019-08-28
# -------------------------------------------------------------------------

if [ -f /var/log/wo/wordops.log ]; then
    cd /var/log/wo/ || exit 1
    wo_link=$(curl -sL --upload-file wordops.log https://transfer.vtbox.net/wordops.txt)
    echo
    echo "Here the link to provide in your github issue : $wo_link"
    echo
    cd || exit 1
fi
