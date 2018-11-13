
from setuptools import setup, find_packages
import sys
import os
import glob
import configparser
import re
import shutil

conf = []
templates = []

long_description = '''WordOps is the commandline tool to manage your
                      Websites based on WordPress and Nginx with easy to use
                      commands'''

for name in glob.glob('config/plugins.d/*.conf'):
    conf.insert(1, name)

for name in glob.glob('wo/cli/templates/*.mustache'):
    templates.insert(1, name)

if not os.path.exists('/var/log/wo/'):
    os.makedirs('/var/log/wo/')

if not os.path.exists('/var/lib/wo/'):
    os.makedirs('/var/lib/wo/')

# WordOps git configuration management
config = configparser.ConfigParser()
config.read(os.path.expanduser("~")+'/.gitconfig')
try:
    wo_user = config['user']['name']
    wo_email = config['user']['email']
except Exception as e:
    print("WordOps (wo) required your name & email address to track"
          " changes you made under the Git version control")
    print("WordOps (wo) will be able to send you daily reports & alerts in "
          "upcoming version")
    print("WordOps (wo) will NEVER share your information with other parties")

    wo_user = input("Enter your name: ")
    while wo_user is "":
        print("Unfortunately, this can't be left blank")
        wo_user = input("Enter your name: ")

    wo_email = input("Enter your email: ")

    while not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$",
                       wo_email):
        print("Whoops, seems like you made a typo - the e-mailaddress is invalid...")
        wo_email = input("Enter your email: ")

    os.system("git config --global user.name {0}".format(wo_user))
    os.system("git config --global user.email {0}".format(wo_email))

if not os.path.isfile('/root/.gitconfig'):
      shutil.copy2(os.path.expanduser("~")+'/.gitconfig', '/root/.gitconfig')

setup(name='wo',
      version='3.9.0',
      description=long_description,
      long_description=long_description,
      classifiers=[],
      keywords='',
      author='WordOps',
      author_email='core@wordops.org',
      url='https://wordops.io',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests',
                                      'templates']),
      include_package_data=True,
      zip_safe=False,
      test_suite='nose.collector',
      install_requires=[
          # Required to build documentation
          # "Sphinx >= 1.0",
          # Required for testing
          # "nose",
          # "coverage",
          # Required to function
          'cement == 2.4',
          'pystache',
          'python-apt',
          'pynginxconfig',
          'PyMySQL == 0.8.0',
          'psutil == 3.1.1',
          'sh',
          'SQLAlchemy',
          ],
      data_files=[('/etc/wo', ['config/wo.conf']),
                  ('/etc/wo/plugins.d', conf),
                  ('/usr/lib/wo/templates', templates),
                  ('/etc/bash_completion.d/',
                   ['config/bash_completion.d/wo_auto.rc']),
                  ('/usr/share/man/man8/', ['docs/wo.8'])],
      setup_requires=[],
      entry_points="""
          [console_scripts]
          wo = wo.cli.main:main
      """,
      namespace_packages=[],
      )
