from cement.core.controller import CementBaseController, expose
from cement.core import handler, hook
from wo.core.aptget import WOAptGet
from wo.core.shellexec import WOShellExec
from wo.core.variables import WOVariables
from wo.core.logging import Log
from wo.core.git import WOGit
from wo.core.services import WOService
import string
import random
import sys
import hashlib
import getpass


def wo_secure_hook(app):
    pass


class WOSecureController(CementBaseController):
    class Meta:
        label = 'secure'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = ('Secure command secure auth, ip and port')
        arguments = [
            (['--auth'],
                dict(help='secure auth', action='store_true')),
            (['--port'],
                dict(help='secure port', action='store_true')),
            (['--ip'],
                dict(help='secure ip', action='store_true')),
            (['user_input'],
                dict(help='user input', nargs='?', default=None)),
            (['user_pass'],
                dict(help='user pass', nargs='?', default=None))]
        usage = "wo secure [options]"

    @expose(hide=True)
    def default(self):
            if self.app.pargs.auth:
                self.secure_auth()
            if self.app.pargs.port:
                self.secure_port()
            if self.app.pargs.ip:
                self.secure_ip()

    @expose(hide=True)
    def secure_auth(self):
        """This function secures authentication"""
        passwd = ''.join([random.choice
                         (string.ascii_letters + string.digits)
                         for n in range(6)])
        if not self.app.pargs.user_input:
            username = input("Provide HTTP authentication user "
                             "name [{0}] :".format(WOVariables.wo_user))
            self.app.pargs.user_input = username
            if username == "":
                self.app.pargs.user_input = WOVariables.wo_user
        if not self.app.pargs.user_pass:
            password = getpass.getpass("Provide HTTP authentication "
                                       "password [{0}] :".format(passwd))
            self.app.pargs.user_pass = password
            if password == "":
                self.app.pargs.user_pass = passwd
        Log.debug(self, "printf username:"
                  "$(openssl passwd -crypt "
                  "password 2> /dev/null)\n\""
                  "> /etc/nginx/htpasswd-wo 2>/dev/null")
        WOShellExec.cmd_exec(self, "printf \"{username}:"
                             "$(openssl passwd -crypt "
                             "{password} 2> /dev/null)\n\""
                             "> /etc/nginx/htpasswd-wo 2>/dev/null"
                             .format(username=self.app.pargs.user_input,
                                     password=self.app.pargs.user_pass),
                             log=False)
        WOGit.add(self, ["/etc/nginx"],
                  msg="Adding changed secure auth into Git")

    @expose(hide=True)
    def secure_port(self):
        """This function Secures port"""
        if self.app.pargs.user_input:
            while not self.app.pargs.user_input.isdigit():
                Log.info(self, "Please enter a valid port number ")
                self.app.pargs.user_input = input("WordOps "
                                                  "admin port [22222]:")
        if not self.app.pargs.user_input:
            port = input("WordOps admin port [22222]:")
            if port == "":
                self.app.pargs.user_input = 22222
            while not port.isdigit() and port != "":
                Log.info(self, "Please Enter valid port number :")
                port = input("WordOps admin port [22222]:")
            self.app.pargs.user_input = port
        if WOVariables.wo_platform_distro == 'ubuntu':
            WOShellExec.cmd_exec(self, "sed -i \"s/listen.*/listen "
                                 "{port} default_server ssl http2;/\" "
                                 "/etc/nginx/sites-available/22222"
                                 .format(port=self.app.pargs.user_input))
        if WOVariables.wo_platform_distro == 'debian':
            WOShellExec.cmd_exec(self, "sed -i \"s/listen.*/listen "
                                 "{port} default_server ssl http2;/\" "
                                 "/etc/nginx/sites-available/22222"
                                 .format(port=self.app.pargs.user_input))
        WOGit.add(self, ["/etc/nginx"],
                  msg="Adding changed secure port into Git")
        if not WOService.reload_service(self, 'nginx'):
            Log.error(self, "service nginx reload failed. "
                      "check issues with `nginx -t` command")
        Log.info(self, "Successfully port changed {port}"
                 .format(port=self.app.pargs.user_input))

    @expose(hide=True)
    def secure_ip(self):
        """IP whitelisting"""
        newlist = []
        if not self.app.pargs.user_input:
            ip = input("Enter the comma separated IP addresses "
                       "to white list [127.0.0.1]:")
            self.app.pargs.user_input = ip
        try:
            user_ip = self.app.pargs.user_input.split(',')
        except Exception as e:
            user_ip = ['127.0.0.1']
        for ip_addr in user_ip:
            if not ("exist_ip_address "+ip_addr in open('/etc/nginx/common/'
                    'acl.conf').read()):
                WOShellExec.cmd_exec(self, "sed -i "
                                     "\"/deny/i allow {whitelist_address}\;\""
                                     " /etc/nginx/common/acl.conf"
                                     .format(whitelist_address=ip_addr))
        WOGit.add(self, ["/etc/nginx"],
                  msg="Adding changed secure ip into Git")

        Log.info(self, "Successfully added IP address in acl.conf file")


def load(app):
    handler.register(WOSecureController)
    hook.register('post_argument_parsing', wo_secure_hook)
