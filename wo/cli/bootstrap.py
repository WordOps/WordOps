"""WordOps bootstrapping."""

# All built-in application controllers should be imported, and registered
# in this file in the same way as WOBaseController.

from cement.core import handler
from wo.cli.controllers.base import WOBaseController


def load(app):
    handler.register(WOBaseController)
