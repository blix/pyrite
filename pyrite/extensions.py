#Copyright 2008 Govind Salinas <blix@sophiasuchtig.com>

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 2 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pyrite

_extensions = {}

def extensions():
    return _extensions

def on_load(commands):
    for name, path in pyrite.config.items('pyrite.addons'):
        module = pyrite.dyn_import(name, True, None)
        if not module:
            continue
        _extensions[name] = module
        if hasattr(module, 'on_load'):
            if module.on_load(commands):
                _extensions[name] = module
        else:
            _extensions[name] = module

def on_before_command(module, cmd, args, flags):
    for e in _extensions.values():
        if hasattr(e, 'on_before_command'):
            e.on_before_command(module, cmd, args, flags)

def on_after_command(module, cmd, args, flags):
    for e in _extensions.values():
        if hasattr(e, 'on_after_command'):
            e.on_after_command(module, cmd, args, flags)
