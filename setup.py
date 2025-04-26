# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 bendikro bro.devel+ifacewatch@gmail.com
#
# This file is part of Iface Watch and is licensed under GNU General Public
# License 3.0, or later, with the additional special exception to link portions
# of this program with the OpenSSL library. See LICENSE for more details.
#

from setuptools import find_packages, setup

__plugin_name__ = "IfaceWatch"
__author__ = "Bro"
__author_email__ = "bro.devel+ifacewatch@gmail.com"
__version__ = "2.0"
__url__ = "https://github.com/bendikro/deluge-iface-watch"
__license__ = "GPLv3"
__description__ = """
Iface Watch will monitor a specified network interface and
notify deluge (libtorrent) when the IP changes.
"""
__long_description__ = __description__

__pkg_data__ = {__plugin_name__.lower(): ["data/*"]}
packages = find_packages()

setup(
    name=__plugin_name__,
    version=__version__,
    description=__description__,
    author=__author__,
    author_email=__author_email__,
    url=__url__,
    license=__license__,
    long_description=__long_description__ if __long_description__ else __description__,
    packages=packages,
    extras_require={"dev": ["pytest", "pytest-mock", "deluge", "PyGObject"]},
    package_data=__pkg_data__,
    entry_points={
        "deluge.plugin.core": [
            f"{__plugin_name__} = {__plugin_name__.lower()}:CorePlugin",
        ],
        "deluge.plugin.gtk3ui": [
            f"{__plugin_name__} = {__plugin_name__.lower()}:Gtk3UIPlugin",
        ],
        f"{__plugin_name__.lower()}.libpaths": [
            "pyiface = ifacewatch.include.pyiface",
            "ifcfg   = ifacewatch.include.ifcfg.src",
        ],
    },
)
