
import glob
import os

from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

conf = []
templates = []

short_description = """An essential toolset that eases WordPress
                    site and server administration"""

for name in glob.glob('config/plugins.d/*.conf'):
    conf.insert(1, name)

for name in glob.glob('wo/cli/templates/*.mustache'):
    templates.insert(1, name)

if not os.path.exists('/var/log/wo/'):
    os.makedirs('/var/log/wo/')

if not os.path.exists('/var/lib/wo/tmp/'):
    os.makedirs('/var/lib/wo/tmp/')

setup(name='wordops',
      version='3.9.9.2',
      description='WordPress & server administration toolset',
      long_description=long_description,
      long_description_content_type="text/markdown",
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Development Status :: 5 - Production/Stable",
          "Environment :: Console",
          "Natural Language :: English",
          "Topic :: System :: Systems Administration",
      ],
      keywords='',
      author='WordOps',
      author_email='contact@wordops.io',
      url='https://github.com/WordOps/WordOps',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests',
                                      'templates']),
      include_package_data=True,
      zip_safe=False,
      test_suite='nose.collector',
      python_requires='>=3.5',
      install_requires=[
          # Required to build documentation
          # "Sphinx >= 1.0",
          # Required to function
          'cement == 2.8.2',
          'pystache >= 0.5.4',
          'pynginxconfig >= 0.3.4',
          'PyMySQL >= 0.9.3',
          'psutil >= 5.6.3',
          'sh >= 1.12.14',
          'SQLAlchemy >= 1.3.8',
          'requests >= 2.22.0',
          'distro >= 1.4.0',
          'apt-mirror-updater >= 6.1',
      ],
      extras_require={  # Optional
          'testing': ['nose', 'coverage'],
      },
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
