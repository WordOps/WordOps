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
    curl --progress-bar --upload-file /var/log/wo/wordops.log https://transfer.vtbox.net/"$(basename wordops.log)" && echo "" | sudo tee -a $HOME/.transfer.log && echo ""
    exit 1
}

echo -e "${CGREEN}#############################################${CEND}"
echo -e '       stack install             '
echo -e "${CGREEN}#############################################${CEND}"
stack_list='nginx php php73 mysql redis fail2ban clamav proftpd admin'
for stack in $stack_list; do
    echo -ne "       Installing $stack               [..]\r"
    if {
        wo stack install --${stack}
    } >> /var/log/wo/test.log; then
        echo -ne "       Installing $stack                [${CGREEN}OK${CEND}]\\r"
        echo -ne '\n'
    else
        echo -e "        Installing $stack              [${CRED}FAIL${CEND}]"
        echo -ne '\n'
        exit_script

    fi
done

echo -e "${CGREEN}#############################################${CEND}"
echo -e '       Simple site create              '
echo -e "${CGREEN}#############################################${CEND}"
site_types='html php php73 mysql wp wpfc wpsc wpredis wpce wprocket wpsubdomain wpsubdir'
for site in $site_types; do
    echo -ne "       Creating $site               [..]\r"
    if {
        wo site create ${site}.net --${site}
    } >> /var/log/wo/test.log; then
        echo -ne "       Creating $site                [${CGREEN}OK${CEND}]\\r"
        echo -ne '\n'
    else
        echo -e "        Creating $site              [${CRED}FAIL${CEND}]"
        echo -ne '\n'
        exit_script

    fi
done
echo -e "${CGREEN}#############################################${CEND}"
echo -e '       wo site update --php73              '
echo -e "${CGREEN}#############################################${CEND}"
other_site_types='html mysql wp wpfc wpsc wpredis wpce wprocket wpsubdomain wpsubdir'
for site in $other_site_types; do
    echo -ne "       Updating site to $site php73              [..]\r"
    if {
        wo site update ${site}.net --php73
    } >> /var/log/wo/test.log; then
        echo -ne "       Updating site to $site php73               [${CGREEN}OK${CEND}]\\r"
        echo -ne '\n'
    else
        echo -e "        Updating site to $site php73              [${CRED}FAIL${CEND}]"
        echo -ne '\n'
        exit_script

    fi
done

echo -e "${CGREEN}#############################################${CEND}"
echo -e '       wo site update WP              '
echo -e "${CGREEN}#############################################${CEND}"

wp_site_types='wpfc wpsc wpce wprocket wpredis'
wo site create wp.io --wp >> /dev/null 2>&1
for site in $wp_site_types; do
    echo -ne "        Updating WP to $site              [..]\r"
    if {
        wo site update wp.io --${site}
    } >> /var/log/wo/test.log; then
        echo -ne "       Updating WP to $site               [${CGREEN}OK${CEND}]\\r"
        echo -ne '\n'
    else
        echo -e "        Updating WP to $site              [${CRED}FAIL${CEND}]"
        echo -ne '\n'
        exit_script

    fi
done

echo -e "${CGREEN}#############################################${CEND}"
echo -e '       wo stack upgrade              '
echo -e "${CGREEN}#############################################${CEND}"
stack_upgrade='nginx php mysql redis netdata dashboard phpmyadmin'
for stack in $stack_upgrade; do
    echo -ne "      Upgrading $stack               [..]\r"
    if {
        wo stack upgrade --${stack} --force
    } >> /var/log/wo/test.log; then
        echo -ne "       Upgrading $stack               [${CGREEN}OK${CEND}]\\r"
        echo -ne '\n'
    else
        echo -e "        Upgrading $stack              [${CRED}FAIL${CEND}]"
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

echo -e "${CGREEN}#############################################${CEND}"
echo -e '       various informations             '
echo -e "${CGREEN}#############################################${CEND}"
wp --allow-root --info
wo site info wp1.com
wo stack purge --all --force