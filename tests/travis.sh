#!/usr/bin/env bash
#
# WordOps travis testing script
#
#
CSI='\033['
CEND="${CSI}0m"
CGREEN="${CSI}1;32m"

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
if ! {
    echo -e "${CGREEN}#############################################${CEND}"
    echo -e '       Simple site create              '
    echo -e "${CGREEN}#############################################${CEND}"
    wo site create html.net --html && wo site create php.com --php && wo site create mysql.com --mysql && wo site create proxy.com --proxy=127.0.0.1:3000
    wo site create wp1.com --wp && wo site create wpsc1.net --wpsc && wo site create wpfc1.com --wpfc
    wo site create wpsc-php73.net --wpsc --php73 && wo site create wpfc-php73.net --wpfc --php73
    wo site create wprocket.net --wprocket && wo site create wprocket-php73.net --wprocket --php73
    wo site create wpce.net --wpce && wo site create wpce-php73.net --wpce --php73
    wo site create wpredis.net --wpredis && wo site create wpredis-php73.net --wpredis --php73

}; then
    exit_script
fi
if ! {
    echo -e "${CGREEN}#############################################${CEND}"
    echo -e '       Multi-site create              '
    echo -e "${CGREEN}#############################################${CEND}"
    wo site create wpsubdir1.com --wpsubdir && wo site create wpsubdir-php73.com --wpsubdir --php73
    wo site create wpsubdirwpsc1.com --wpsubdir --wpsc && wo site create wpsubdirwpsc2.com --wpsubdir --wpfc && wo site create wpsubdirwpsc1-php73.com --wpsubdir --wpsc --php73 && wo site create wpsubdirwpsc2-php73.com --wpsubdir --wpfc --php73
    wo site create wpsubdomain1.com --wpsubdomain && wo site create wpsubdomain1-php73.com --wpsubdomain --php73 && wo site create wpsubdomainwpsc.org --wpsubdomain --wpsc && wo site create wpsubdomainwpfc.org --wpsubdomain --wpfc && wo site create wpsubdomainwpfc2.in --wpfc --wpsubdomain
    echo -e "${CGREEN}#############################################${CEND}"
    echo -e '       wo site update              '
    echo -e "${CGREEN}#############################################${CEND}"
    wo site create 1.com --html && wo site create 2.com --php && wo site create 3.com --mysql
    wo site update 1.com --wp && wo site update 2.com --php73 && wo site update 3.com --php73 && wo site update 1.com --wpfc && wo site update 1.com --wpsc && wo site update 1.com --wpredis
}; then
    exit_script
fi
if ! {
    echo -e "${CGREEN}#############################################${CEND}"
    echo -e '       wo stack upgrade              '
    echo -e "${CGREEN}#############################################${CEND}"
    wo stack upgrade --force
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
