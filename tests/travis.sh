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

export DEBIAN_FRONTEND=noninteractive
unset LANG
export LANG='en_US.UTF-8'
export LC_ALL='C.UTF-8'

if [ -z "$1" ]; then
{
    apt-get -qq purge mysql* graphviz* redis*
    apt-get install -qq git python3-setuptools python3-dev python3-apt ccze tree
    sudo apt-get -qq autoremove --purge
} > /dev/null 2>&1
fi

exit_script() {
    curl --progress-bar --upload-file /var/log/wo/wordops.log https://transfer.vtbox.net/"$(basename wordops.txt)" && echo ""
    exit 1
}

echo -e "${CGREEN}#############################################${CEND}"
echo -e '       stack install             '
echo -e "${CGREEN}#############################################${CEND}"
stack_list='nginx php php73 mysql redis fail2ban clamav proftpd netdata phpmyadmin composer dashboard extplorer adminer redis phpredisadmin mysqltuner utils ufw ngxblocker cheat nanorc'
for stack in $stack_list; do
    echo -ne "       Installing $stack               [..]\r"
    if {
        wo stack install --${stack}
    } >>/var/log/wo/test.log; then
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
site_types='html php php73 mysql wp wpfc wpsc wpredis wpce wprocket wpsubdomain wpsubdir ngxblocker'
for site in $site_types; do
    echo -ne "       Creating $site               [..]\r"
    if {
        wo site create ${site}.net --${site}
    } >>/var/log/wo/test.log; then
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
other_site_types='html mysql wp wpfc wpsc wpredis wpce wprocket wpsubdomain wpsubdir ngxblocker'
for site in $other_site_types; do
    echo -ne "       Updating site to $site php73              [..]\r"
    if {
        wo site update ${site}.net --php73
    } >>/var/log/wo/test.log; then
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
wo site create wp.io --wp >>/dev/null 2>&1
for site in $wp_site_types; do
    echo -ne "        Updating WP to $site              [..]\r"
    if {
        wo site update wp.io --${site}
    } >>/var/log/wo/test.log; then
        echo -ne "       Updating WP to $site               [${CGREEN}OK${CEND}]\\r"
        echo -ne '\n'
    else
        echo -e "        Updating WP to $site              [${CRED}FAIL${CEND}]"
        echo -ne '\n'
        exit_script

    fi
done

echo -e "${CGREEN}#############################################${CEND}"
echo -e '       wo site create wpsubdir              '
echo -e "${CGREEN}#############################################${CEND}"

wp_site_types='wpfc wpsc wpce wprocket wpredis'
for site in $wp_site_types; do
    echo -ne "        Creating wpsubdir $site              [..]\r"
    if {
        wo site create wpsubdir"$site".io --wpsubdir --${site}
    } >>/var/log/wo/test.log; then
        echo -ne "       Creating wpsubdir $site               [${CGREEN}OK${CEND}]\\r"
        echo -ne '\n'
    else
        echo -e "        Creating wpsubdir $site              [${CRED}FAIL${CEND}]"
        echo -ne '\n'
        exit_script

    fi
done

echo -e "${CGREEN}#############################################${CEND}"
echo -e '       wo site create wpsubdomain              '
echo -e "${CGREEN}#############################################${CEND}"

wp_site_types='wpfc wpsc wpce wprocket wpredis'
for site in $wp_site_types; do
    echo -ne "        Creating wpsubdomain $site              [..]\r"
    if {
        wo site create wpsubdomain"$site".io --wpsubdomain --${site}
    } >>/var/log/wo/test.log; then
        echo -ne "       Creating wpsubdomain $site               [${CGREEN}OK${CEND}]\\r"
        echo -ne '\n'
    else
        echo -e "        Creating wpsubdomain $site              [${CRED}FAIL${CEND}]"
        echo -ne '\n'
        exit_script

    fi
done
if [ -z "$1" ]; then
    echo -e "${CGREEN}#############################################${CEND}"
    echo -e '       wo stack upgrade              '
    echo -e "${CGREEN}#############################################${CEND}"
    stack_upgrade='nginx php php73 mysql redis netdata dashboard phpmyadmin composer ngxblocker'
    for stack in $stack_upgrade; do
        echo -ne "      Upgrading $stack               [..]\r"
        if {
            wo stack upgrade --${stack} --force
        } >>/var/log/wo/test.log; then
            echo -ne "       Upgrading $stack               [${CGREEN}OK${CEND}]\\r"
            echo -ne '\n'
        else
            echo -e "        Upgrading $stack              [${CRED}FAIL${CEND}]"
            echo -ne '\n'
            exit_script

        fi
    done
fi
echo -e "${CGREEN}#############################################${CEND}"
echo -e '       wo clean              '
echo -e "${CGREEN}#############################################${CEND}"
stack_clean='fastcgi redis opcache all'
for stack in $stack_clean; do
    echo -ne "       cleaning $stack cache              [..]\r"
    if {
        wo clean --${stack}
    } >>/var/log/wo/test.log; then
        echo -ne "       cleaning $stack cache               [${CGREEN}OK${CEND}]\\r"
        echo -ne '\n'
    else
        echo -e "        cleaning $stack cache              [${CRED}FAIL${CEND}]"
        echo -ne '\n'
        exit_script

    fi
done

echo -e "${CGREEN}#############################################${CEND}"
echo -e '       wo secure              '
echo -e "${CGREEN}#############################################${CEND}"
echo -ne "       wo secure --auth                   [..]\r"
if {
    wo secure --auth wordops mypassword
} >>/var/log/wo/test.log; then
    echo -ne "       wo secure --auth                   [${CGREEN}OK${CEND}]\\r"
    echo -ne '\n'
else
    echo -e "       wo secure --auth                   [${CRED}FAIL${CEND}]"
    echo -ne '\n'
    exit_script

fi
echo -ne "       wo secure --sshport                [..]\r"
if {
    wo secure --sshport 2022
} >>/var/log/wo/test.log; then
    echo -ne "       wo secure --sshport                [${CGREEN}OK${CEND}]\\r"
    echo -ne '\n'
else
    echo -e "       wo secure --sshport                [${CRED}FAIL${CEND}]"
    echo -ne '\n'
    exit_script

fi
echo -ne "       wo secure --ssh                    [..]\r"
if {
    wo secure --ssh --force
} >>/var/log/wo/test.log; then
    echo -ne "       wo secure --ssh                    [${CGREEN}OK${CEND}]\\r"
    echo -ne '\n'
else
    echo -e "       wo secure --ssh                    [${CRED}FAIL${CEND}]"
    echo -ne '\n'
    exit_script

fi

echo -e "${CGREEN}#############################################${CEND}"
echo -e '       WP-CLI info             '
echo -e "${CGREEN}#############################################${CEND}"
wp --allow-root --info

echo
echo -e "${CGREEN}#############################################${CEND}"
echo -e '       wo site info             '
echo -e "${CGREEN}#############################################${CEND}"

wo site info wp.net

echo
echo -e "${CGREEN}#############################################${CEND}"
echo -e '       wo info             '
echo -e "${CGREEN}#############################################${CEND}"
wo info

echo -e "${CGREEN}#############################################${CEND}"
echo -e '       wo stack purge              '
echo -e "${CGREEN}#############################################${CEND}"
stack_purge='nginx php php73 mysql redis fail2ban clamav proftpd netdata phpmyadmin composer dashboard extplorer adminer redis ufw ngxblocker cheat nanorc'
for stack in $stack_purge; do
    echo -ne "       purging $stack              [..]\r"
    if {
        wo stack purge --${stack} --force
    } >>/var/log/wo/test.log; then
        echo -ne "       purging $stack               [${CGREEN}OK${CEND}]\\r"
        echo -ne '\n'
    else
        echo -e "        purging $stack              [${CRED}FAIL${CEND}]"
        echo -ne '\n'
        exit_script

    fi
done
