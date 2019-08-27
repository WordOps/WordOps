#!/usr/bin/env bash
# -------------------------------------------------------------------------
# WordOps support script
# -------------------------------------------------------------------------
# Website:       https://wordops.net
# GitHub:        https://github.com/WordOps/WordOps
# Copyright (c) 2019 - WordOps
# This script is licensed under M.I.T
# -------------------------------------------------------------------------
# wget -qO wo wops.cc && sudo bash wo
# -------------------------------------------------------------------------
# Version 3.9.8.4 - 2019-08-28
# -------------------------------------------------------------------------

if [ -f /var/log/wo/wordops.log ]; then
    cd /var/log/wo/ || exit 1
    if {
        tar -I pigz -cf wordops.tar.gz wordops.log
    }; then
        wo_link=$(curl -sL --upload-file wordops.tar.gz https://transfer.sh/wordops.tar.gz)
        echo
        echo "Here the link to provide in your github issue : $wo_link"
        echo
    fi
    cd || exit 1
fi
