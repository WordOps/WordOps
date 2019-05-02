"""WordOps exception classes."""


class WOError(Exception):
    """Generic errors."""

    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg

    def __str__(self):
        return self.msg


class WOConfigError(WOError):
    """Config related errors."""
    pass


class WORuntimeError(WOError):
    """Generic runtime errors."""
    pass


class WOArgumentError(WOError):
    """Argument related errors."""
    pass
