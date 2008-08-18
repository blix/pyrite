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
from twisted.web.static import File as StaticFile
from twisted.python.filepath import FilePath
from twisted.web.woven import page
from mako.template import Template
from mako.lookup import TemplateLookup
import re, os

class ErrorPage(page.Page):
    def render(self, request):
        request.setResponseCode(http.NOT_ALLOWED)
        return 'Access Denied.'

class FileWithoutDir(StaticFile):
   """Acts just like static.File but won't return directory listings"""

   def directoryListing(self):
       return ErrorPage()

class Root(resource.Resource, FilePath):
    def __init__(self, port, path, io):
        resource.Resource.__init__(self)
        self._port = port
        self._io = io
        if not path:
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
        self._file_access = FilePath(self._template_dir)
        try:
            self._parse_setup()
        except IOError, e:
            io.error_out(_('Failed to load config file %s: %s') %
                         (config_file, e))
        self.putChild(self._config['static_path'], 
                      FileWithoutDir(self._config['static_path_full']))

    def _parse_setup(self):
        self._config = {}
        execfile(os.path.join(self._file_access.path, '__config__.py'), {},
                              self._config)
        if 'url_map' not in self._config:
            raise IOError(_('Missing url_map.'))
        self._mappings = []
        for exp, orig in self._config['url_map']:
            f = orig.split('/')
            f = os.path.join(*f)
            f = self._file_access.child(f)
            if not f.exists():
                raise IOError(_('Path %s is not under template dir.') % orig)
            self._mappings.append((re.compile(exp), f))
        if 'static_path' not in self._config:
            self._config['static_path'] = 'static'

        fullpath = self._file_access.child(self._config['static_path'])
        self._config['static_path_full'] = fullpath.path

    def getChild(self, name, request):
        return self

    def render_GET(self, request):
        path = request.path[1:]
        uri = request.uri[1:]
        if hasattr(os, 'winver'):
            lookup = TemplateLookup(directories=[self._file_access.path],
                                default_filters=[], input_encoding='utf-8')
        else:
            lookup = TemplateLookup(directories=['/'],
                                default_filters=[], input_encoding='utf-8')
        for regex, f in self._mappings:
            match = regex.match(uri)
            if match:
                vars = match.groupdict()
                self._io.info('matched: ' + regex.pattern)
                self._io.info('vars: ' + str(vars))
                self._io.info('serving: ' + f.path)
                request.setHeader('Content-Type', 'text/html; charset=utf-8')
                t = Template(filename=f.path, default_filters=[],
                             input_encoding='utf-8', lookup=lookup)
                try:
                    return t.render(**vars)
                except BaseException, e:
                    for num, line in enumerate(t.code.splitlines()):
                        print '%d: %s' % (num, line)
                    raise
        print 'not serving:', uri

    def run(self):
        s = server.Site(self)
        reactor.listenTCP(self._port, s)
        try:
            reactor.run()
        except:
            pass
