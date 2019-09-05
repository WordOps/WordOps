"""WordOps log module"""


class Log:
    """
        Logs messages with colors for different messages
        according to functions
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    def error(self, msg, exit=True):
        """
        Logs error into log file
        """
        print(Log.FAIL + msg + Log.ENDC)
        self.app.log.error(Log.FAIL + msg + Log.ENDC)
        if exit:
            self.app.close(1)

    def info(self, msg, end='\n', log=True):
        """
        Logs info messages into log file
        """

        print(Log.OKBLUE + msg + Log.ENDC, end=end)
        if log:
            self.app.log.info(Log.OKBLUE + msg + Log.ENDC)

    def warn(self, msg):
        """
        Logs warning into log file
        """
        print(Log.WARNING + msg + Log.ENDC)
        self.app.log.warn(Log.BOLD + msg + Log.ENDC)

    def debug(self, msg):
        """
        Logs debug messages into log file
        """
        self.app.log.debug(Log.HEADER + msg + Log.ENDC)

    def wait(self, msg, end='\r', log=True):
        """
        Logs info messages with validation step
        """
        print(
            Log.OKBLUE + "{0:22}".format(msg) +
            "  [" + Log.ENDC + ".." + Log.OKBLUE + "]" + Log.ENDC, end=end)
        if log:
            self.app.log.info(Log.OKBLUE + msg + Log.ENDC)

    def valide(self, msg, end='\n', log=True):
        """
        Logs info messages after validation step
        """
        print(
            Log.OKBLUE + "{0:22}".format(msg) +
            "  [" + Log.ENDC + Log.OKGREEN + "OK" +
            Log.ENDC + Log.OKBLUE + "]" + Log.ENDC, end=end)
        if log:
            self.app.log.info(Log.OKGREEN + msg + Log.ENDC)

    def failed(self, msg, end='\n', log=True):
        """
        Logs info messages after validation step
        """
        print(
            Log.OKBLUE + "{0:22}".format(msg) +
            "  [" + Log.ENDC + Log.FAIL + "OK" +
            Log.ENDC + Log.OKBLUE + "]" + Log.ENDC, end=end)
        if log:
            self.app.log.info(Log.FAIL + msg + Log.ENDC)
