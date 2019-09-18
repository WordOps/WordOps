
import glob
import os

from setuptools import find_packages, setup

conf = []
templates = []

long_description = '''WordOps  An essential toolset that eases WordPress
                      site and server administration. It provide the ability
                      to Install a high performance WordPress stack
                      with a few keystrokes'''

for name in glob.glob('config/plugins.d/*.conf'):
    conf.insert(1, name)

for name in glob.glob('wo/cli/templates/*.mustache'):
    templates.insert(1, name)

if not os.path.exists('/var/log/wo/'):
    os.makedirs('/var/log/wo/')

if not os.path.exists('/var/lib/wo/'):
    os.makedirs('/var/lib/wo/')

setup(name='wo',
      version='3.9.8.12',
      description=long_description,
      long_description=long_description,
      classifiers=[],
      keywords='',
      author='WordOps',
      author_email='contact@wordops.io',
      url='https://wordops.net',
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
          'cement == 2.8.2',
          'pystache',
          'python-apt',
          'pynginxconfig',
          'PyMySQL',
          'psutil',
          'sh',
          'SQLAlchemy',
          'requests',
          'distro',
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
