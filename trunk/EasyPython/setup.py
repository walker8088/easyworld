
# version (should be imported from drpython.py or __init__.py)
MY_VER='0.10'

# package name, do not change
MY_NAME = 'EasyPython'

AUTHOR = 'walker li'
AUTHOR_EMAIL = 'walker8088@gmail.com'
URL = 'http://easypython.org'

# Trove classification (get list with python setup.py register --list-classifiers)
classifiers = """
Development Status :: 5 - Production/Stable
Environment :: MacOS X
Environment :: Win32 (MS Windows)
Environment :: X11 Applications :: GTK
Intended Audience :: Developers
Intended Audience :: Education
Intended Audience :: Information Technology
Intended Audience :: Other Audience
Intended Audience :: Science/Research
Intended Audience :: System Administrators
OSI Approved :: GNU General Public License (GPL)
Natural Language :: Chinese_Simple
Operating System :: MacOS :: MacOS X
Operating System :: Microsoft :: Windows
Operating System :: POSIX :: Linux
Programming Language :: Python
Topic :: Documentation
Topic :: Software Development
Topic :: Text Editors
Topic :: Text Editors :: Integrated Development Environments (IDE)
"""

# take name and description from setup.py docstring
#description = __doc__.split('\n\n', 1)
name= 'EasyPython' #description[0].split(' ', 1)[0]

# please add every package data file to be installed to the list
DATA = [
    'documentation/*',
    'bitmaps/*.ico', 'bitmaps/*.png',
    'bitmaps/16/*.png', 'bitmaps/24/*.png',
    'EasyPython.pyw'
]

import sys
if len(sys.argv) == 1:
    sys.argv.append("py2exe")

from distutils.core import setup

# and now standard distutils installation routine
setup(name=name,
    version=MY_VER,
    description='', #description[0],
    long_description='', #description[1],
    classifiers = filter(None, classifiers.split('\n')),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    platforms = "any",
    license = 'GPL',
    packages=[ MY_NAME ],
    package_dir={ MY_NAME : '.' },
    package_data={ MY_NAME : DATA },
    scripts=['postinst.py'],
)
