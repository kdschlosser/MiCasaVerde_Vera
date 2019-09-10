# -*- coding: utf-8 -*-
#
# This file is part of EventGhost.
# Copyright © 2005-2018 EventGhost Project <http://eventghost.net/>
#
# EventGhost is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# EventGhost is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with EventGhost. If not, see <http://www.gnu.org/licenses/>.


from setuptools import setup, find_packages

setup(
    name='micasaverde_vera',
    author='Kevin Schlosser',
    author_email='kevin.g.schlosser@gmail.com',
    version='0.5.9',
    zip_safe=False,
    url='https://github.com/kdschlosser/MiCasaVerde_Vera',
    install_requires=['requests'],
    packages=find_packages('micasaverde_vera'),
    package_dir=dict(
        micasaverde_vera= 'micasaverde_vera'
    ),
    description=(
        'This is a python binding to the MicasaVerde Vera UI7+. This binding '
        'dynamically creates Python object representations of every single '
        'component on the Vera. This includes all plugins. This program '
        'writes code as it goes. so if you add a new node or plugin the '
        'program will create the needed python files to properly represent '
        'that item.'
    ),
    download_url='https://github.com/kdschlosser/MiCasaVerde_Vera',
    keywords=[
        'micasaverde',
        'zwave',
        'ZWave',
        'z wave',
        'Z Wave',
        'MiCasaVerde',
        'vera',
        'Vera'
    ],
    classifiers=[
        "Topic :: Home Automation",
        "Topic :: System :: Hardware",
        "Topic :: System :: Hardware :: Hardware Drivers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: POSIX :: BSD",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
)


