# Iface Watch : A Deluge plugin to monitor a network interface for IP changes

Author: bendikro <bro.devel+ifacewatch@gmail.com>

Maintainer: SootyOwl <tyto+ifacewatch@tyto.cc>

License: GPLv3

## Building the plugin

```
#!bash
# Clone the repository
git clone

# Change to the plugin directory
cd deluge-ifacewatch

# Build the plugin
# This will create a .egg file in the dist directory
python setup.py bdist_egg
```

## Installing the plugin

Drop the provided or built egg file into the `plugins` directory of your Deluge configuration directory, and restart Deluge. The plugin should be available in the Preferences dialog under the "Plugins" section.