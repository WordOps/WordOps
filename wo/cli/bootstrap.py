"""WordOps bootstrapping."""

# All built-in application controllers should be imported, and registered
# in this file in the same way as WOBaseController.


from wo.cli.controllers.base import WOBaseController


def load(app):
    app.handler.register(WOBaseController)
