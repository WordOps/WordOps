#!/usr/bin/env bash
# -------------------------------------------------------------------------
# WordOps support script
# -------------------------------------------------------------------------
# Website:       https://wordops.net
# GitHub:        https://github.com/WordOps/WordOps
# Copyright (c) 2024 - WordOps
# This script is licensed under M.I.T
# -------------------------------------------------------------------------
# curl -sL git.io/fjAp3 | sudo -E bash -
# -------------------------------------------------------------------------
# Version 3.21.0 - 2024-05-29
# -------------------------------------------------------------------------

if [ -f /var/log/wo/wordops.log ]; then
    cd /var/log/wo/ || exit 1
    sed -E 's/([a-zA-Z0-9.-]+\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/domain.anonymized/g' /var/log/wo/wordops.log >/var/log/wo/wordops-issue.log
    wo_link=$(curl -sL --upload-file wordops-issue.log https://transfer.vtbox.net/wordops.txt)
    echo
    echo "Here the link to provide in your github issue : $wo_link"
    echo
    cd || exit 1
fi
