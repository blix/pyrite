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

def noop(message):return message #Don't know if I really want to localize the
                              #cmd line. For now continue to add localzable
                              #strings with the _() but make it a noop
import __builtin__, imp
__builtin__.__dict__['_'] = noop

help_str = _("Pyrite Distributed SCM")

modules = {}

def dyn_import(module, io, is_extension=False, path=None):
    if module in modules:
        return
    package = None
    if is_extension:
        if path:
            raise Exception('custom extension paths not yet supported')
        else:
            package = 'pyrite.addons'
    else:
        package = 'pyrite.commands'
    try:
        m = __import__(package, fromlist=module)
        f, p, d = imp.find_module(module, m.__path__)
        modules[module] = m = imp.load_module(package + '.' + module,
                                              f, p, d)
        return m
    except ImportError, inst:
        io.warn(_('Failed to load extension %s: %s') %
                       (module, inst.message))
        return None
