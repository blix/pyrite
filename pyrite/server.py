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

from twisted.internet import reactor
from twisted.web import server, resource, http
from mako.template import Template
from mako.lookup import TemplateLookup
import re, os

_mime_types = {
    'css': 'text/css',
}

class WebServer(resource.Resource):
    isLeaf = True
    def __init__(self, port, template, io):
        self._port = port
        self._template_dir = template
        self._io = io
        if not self._template_dir:
            filedir = os.path.dirname(__file__)
            self._template_dir = os.path.abspath(os.path.join(
                                 filedir, 'templates', 'default-web'))
        if not os.path.isdir(self._template_dir):
            raise ValueError(_('template parameter %s is not a dir') %
                             self._template_dir)
        config_file = os.path.join(self._template_dir, '__config__.py')
        if not os.path.isfile(config_file):
            raise ValueError(_('template parameter %s does not have'
                               ' a valid configuration file '
                               '"__config__.py"') % self._template_dir)
        if not self._parse_setup(config_file):
            io.error_out(_('Failed to load config file %s') % config_file)

    def _parse_setup(self, path):
        self._config = {}
        execfile(path, {}, self._config)
        if 'url_map' not in self._config:
            return False
        self._mappings = []
        for exp, f in self._config['url_map']:
            f = f.split('/')
            f.insert(0, self._template_dir)
            f = os.path.join(*f)
            self._mappings.append((re.compile(exp), f))
        return True

    def render_GET(self, request):
        path = request.path[1:]
        uri = request.uri[1:]
        for x in dir(request):
            y = getattr(request, x)
            if isinstance(y, str):
                print x, y
        for mapping, f in self._mappings:
            match = mapping.match(uri)
            if match:
                vars = match.groupdict()
                print 'serving:', f
                lookup = TemplateLookup(directories=['/'])
                return Template(filename=f, lookup=lookup).render(**vars)
        path = os.path.join(self._template_dir, path)
        if os.path.isfile(path):
            f = None
            try:
                idx = path.rfind('.')
                print 'serving static:', path, path[idx + 1:]
                type = _mime_types.get(path[idx + 1:], 'text/plain')
                request.setHeader('content-type', type)
                print request.headers, type
                f = file(path, 'r')
                return f.read()
            except:
                print 'failed to serve:', path
                raise
            finally:
                if f:
                    f.close()
        else:
            print '%s does not exist' % path
        request.setResponseCode(404)

    def run(self):
        s = server.Site(self)
        reactor.listenTCP(self._port, s)
        reactor.run()



