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

from pyrite.server import Root

options = [
('p', 'port', _('Specify a port.'), 1),
('t', 'template', _('Specify a directory of templates to use.'), 1)
]

help_str =_("""
pyt serve [ --port <portnumber>] [--template <templatedir>]

The serve command starts a webserver that you can use to browse and
share your repository.

""")

def run(cmd, args, flags, io, settings, repo):
    port = flags.get('port', None)
    if not port:
        port = settings.get_option('instaweb.port')
    if not port:
        port = settings.get_option('web.port')
    if not port:
        port = 8000
    template = flags.get('template', None)
    if not template:
        template = settings.get_option('instaweb.template')
    if not template:
        template = settings.get_option('web.template')

    Root(port, template, io).run()
