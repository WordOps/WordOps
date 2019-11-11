"""WordOps main application entry point."""
import sys
from os import geteuid

from cement.core.exc import CaughtSignal, FrameworkError
from cement.core.foundation import CementApp
from cement.ext.ext_argparse import ArgParseArgumentHandler
from cement.utils.misc import init_defaults

from wo.core import exc

# this has to happen after you import sys, but before you import anything
# from Cement "source: https://github.com/datafolklabs/cement/issues/290"
if '--debug' in sys.argv:
    sys.argv.remove('--debug')
    TOGGLE_DEBUG = True
else:
    TOGGLE_DEBUG = False

# Application default.  Should update config/wo.conf to reflect any
# changes, or additions here.
defaults = init_defaults('wo')

# All internal/external plugin configurations are loaded from here
defaults['wo']['plugin_config_dir'] = '/etc/wo/plugins.d'

# External plugins (generally, do not ship with application code)
defaults['wo']['plugin_dir'] = '/var/lib/wo/plugins'

# External templates (generally, do not ship with application code)
defaults['wo']['template_dir'] = '/var/lib/wo/templates'


def encode_output(app, text):
    """ Encode the output to be suitable for the terminal

    :param app: The Cement App (unused)
    :param text: The rendered text
    :return: The encoded text
    """

    return text.encode("utf-8")


class WOArgHandler(ArgParseArgumentHandler):
    class Meta:
        label = 'wo_args_handler'

    def error(self, message):
        super(WOArgHandler, self).error("unknown args")


class WOApp(CementApp):
    class Meta:
        label = 'wo'

        config_defaults = defaults

        # All built-in application bootstrapping (always run)
        bootstrap = 'wo.cli.bootstrap'

        # Internal plugins (ship with application code)
        plugin_bootstrap = 'wo.cli.plugins'

        # Internal templates (ship with application code)
        template_module = 'wo.cli.templates'

        extensions = ['mustache']

        hooks = [
            ("post_render", encode_output)
        ]

        output_handler = 'mustache'

        arg_handler = WOArgHandler

        debug = TOGGLE_DEBUG

        exit_on_close = True


class WOTestApp(WOApp):
    """A test app that is better suited for testing."""
    class Meta:
        # default argv to empty (don't use sys.argv)
        argv = []

        # don't look for config files (could break tests)
        config_files = []

        # don't call sys.exit() when app.close() is called in tests
        exit_on_close = False


# Define the applicaiton object outside of main, as some libraries might wish
# to import it as a global (rather than passing it into another class/func)
app = WOApp()


def main():
    with app:
        try:
            global sys

            # if not root...kick out
            if not geteuid() == 0:
                print("\nNon-privileged users cant use WordOps. "
                      "Switch to root or invoke sudo.\n")
                app.close(1)
            app.run()
        except AssertionError as e:
            print("AssertionError => %s" % e.args[0])
            app.exit_code = 1
        except exc.WOError as e:
            # Catch our application errors and exit 1 (error)
            print('WOError > %s' % e)
            app.exit_code = 1
        except CaughtSignal as e:
            # Default Cement signals are SIGINT and SIGTERM, exit 0 (non-error)
            print('CaughtSignal > %s' % e)
            app.exit_code = 0
        except FrameworkError as e:
            # Catch framework errors and exit 1 (error)
            print('FrameworkError > %s' % e)
            app.exit_code = 1
        finally:
            # Print an exception (if it occurred) and --debug was passed
            if app.debug:
                import sys
                import traceback

                exc_type, exc_value, exc_traceback = sys.exc_info()
                if exc_traceback is not None:
                    traceback.print_exc()


if __name__ == '__main__':
    main()
