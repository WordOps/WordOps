#!/usr/bin/env bash
#
# WordOps travis testing script
#
#
# Colors
CSI='\033['
CRED="${CSI}1;31m"
CGREEN="${CSI}1;32m"
CEND="${CSI}0m"

exit_script() {
    tar -I pigz -cf wordops.tar.gz /var/log/wo
    curl --progress-bar --upload-file wordops.tar.gz https://transfer.vtbox.net/$(basename "wordops.tar.gz") && echo "" | sudo tee -a $HOME/.transfer.log && echo ""
    exit 1
}

if ! {
    echo -e "${CGREEN}#############################################${CEND}"
    echo -e '       stack install             '
    echo -e "${CGREEN}#############################################${CEND}"
    wo --help && wo stack install && wo stack install --proftpd
}; then
    exit_script
fi

    echo -e "${CGREEN}#############################################${CEND}"
    echo -e '       Simple site create              '
    echo -e "${CGREEN}#############################################${CEND}"
    site_types='html php mysql wp wpfc wpsc wpredis wpce wprocket wpsubdomain wpsubdir'
    for site in $site_types; do
        echo -ne "       Installing $site               [..]\r"
        if {
            wo site create ${site}.net --${site}
        } >> /var/log/wo/test.log; then
            echo -ne "       Installing $site                [${CGREEN}OK${CEND}]\\r"
            echo -ne '\n'
        else
            echo -e "        Installing $site              [${CRED}FAIL${CEND}]"
            echo -ne '\n'
            exit_script

        fi
    done
    for site in $site_types; do
        echo -ne "       Installing $site php73              [..]\r"
        if {
            wo site create ${site}.com --${site} --php73
        } >> /var/log/wo/test.log; then
            echo -ne "       Installing $site php73               [${CGREEN}OK${CEND}]\\r"
            echo -ne '\n'
        else
            echo -e "        Installing $site php73              [${CRED}FAIL${CEND}]"
            echo -ne '\n'
            exit_script

        fi
    done

if ! {
    echo -e "${CGREEN}#############################################${CEND}"
    echo -e '       Multi-site create              '
    echo -e "${CGREEN}#############################################${CEND}"
    wo site create wpsubdirwpsc1.com --wpsubdir --wpsc && wo site create wpsubdirwpsc2.com --wpsubdir --wpfc && wo site create wpsubdirwpsc1-php73.com --wpsubdir --wpsc --php73 && wo site create wpsubdirwpsc2-php73.com --wpsubdir --wpfc --php73
    wo site create wpsubdomain1.com --wpsubdomain && wo site create wpsubdomain1-php73.com --wpsubdomain --php73 && wo site create wpsubdomainwpsc.org --wpsubdomain --wpsc && wo site create wpsubdomainwpfc.org --wpsubdomain --wpfc && wo site create wpsubdomainwpfc2.in --wpfc --wpsubdomain
    echo -e "${CGREEN}#############################################${CEND}"
    echo -e '       wo site update              '
    echo -e "${CGREEN}#############################################${CEND}"
    wo site create 1.com --html && wo site create 2.com --php && wo site create 3.com --mysql
    wo site update 1.com --wp && wo site update 2.com --php73 && wo site update 3.com --php73
    wo site update 1.com --wp && wo site update 1.com --wpfc && wo site update 1.com --wpsc && wo site update 1.com --wpredis && wo site update 1.com --wpce && wo site update 1.com --wprocket && wo site update 1.com --php73=off
}; then
    exit_script
fi
if ! {
    echo -e "${CGREEN}#############################################${CEND}"
    echo -e '       wo stack upgrade              '
    echo -e "${CGREEN}#############################################${CEND}"
    wo stack upgrade --force
    wo stack upgrade --nginx --force
    wo stack upgrade --php --force
    wo stack upgrade --netdata --force
    wo stack upgrade --phpmyadmin --force
    wo stack upgrade --composer --force
    wo stack upgrade --dashboard --force
}; then
    exit_script
fi
echo -e "${CGREEN}#############################################${CEND}"
echo -e '       various informations             '
echo -e "${CGREEN}#############################################${CEND}"
wp --allow-root --info
cat /etc/nginx/nginx.conf
wo site info wp1.com
cat /etc/mysql/my.cnf
