"""WordOps Nginx Manager"""
import subprocess

from wo.core.logging import Log


def check_config(self):
    """Check Nginx configuration and return boolean"""
    Log.debug(self, "Testing Nginx configuration ")
    # Check Nginx configuration before executing command
    sub = subprocess.Popen('nginx -t', stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, shell=True)
    output, error_output = sub.communicate()
    if 'emerg' in str(error_output):
        Log.debug(self, "Nginx configuration check failed")
        return False
    else:
        Log.debug(self, "Nginx configuration check was successful")
        return True
