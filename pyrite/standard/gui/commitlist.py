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

import pyrite, pyrite.repository
from pyrite.standard.help import HelpError
import pygtk, gtk
pygtk.require('2.0')
import os

class CommitList(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)
        self.file_path = os.path.abspath(os.path.dirname(__file__))
        self._repo = None

        self._toolbar = gtk.Toolbar()
        self.pack_start(self._toolbar, expand=False)

        icon = gtk.image_new_from_file(
                    os.path.join(self.file_path, 'resultset_previous.png'))
        self._backBtn = gtk.ToolButton(icon_widget=None, label=None)
        self._backBtn.set_icon_widget(icon)
        self._toolbar.add(self._backBtn)
        self._backBtn.connect('clicked', self.back_clicked)

        icon = gtk.image_new_from_file(
                    os.path.join(self.file_path, 'resultset_next.png'))
        self._nextBtn = gtk.ToolButton(icon_widget=None, label=None)
        self._nextBtn.set_icon_widget(icon)
        self._toolbar.add(self._nextBtn)
        self._nextBtn.connect('clicked', self.next_clicked)

        icon = gtk.image_new_from_file(
                    os.path.join(self.file_path, 'application_view_list.png'))
        button = gtk.ToolButton(icon_widget=None, label=None)
        button.set_icon_widget(icon)
        self._toolbar.add(button)
        button.connect('clicked', self.filter_clicked)
        
        self._listView = gtk.TreeView()
        self._listViewModel = gtk.ListStore(str, str, str, str, str, object)
        self._listView.set_model(self._listViewModel)
        scroll = gtk.ScrolledWindow()
        scroll.add(self._listView)
        self.pack_start(scroll)

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_('Commit ID'), renderer, text=0)
        column.set_resizable(True)
        self._listView.append_column(column)
        column = gtk.TreeViewColumn(_('Author'), renderer, text=1)
        self._listView.append_column(column)
        column.set_resizable(True)
        column = gtk.TreeViewColumn(_('Email'), renderer, text=2)
        self._listView.append_column(column)
        column.set_resizable(True)
        column = gtk.TreeViewColumn(_('Date'), renderer, text=3)
        self._listView.append_column(column)
        column.set_resizable(True)
        column = gtk.TreeViewColumn(_('Subject'), renderer, text=4)
        self._listView.append_column(column)
        column.set_resizable(True)

        self._commitstart = 0
        self._filter = None

    def setRepo(self, repo):
        self._repo = repo
        self._populateCommits()

    def _populateCommits(self):
        self._listViewModel.clear()
        if self._commitstart < 1:
            self._backBtn.set_sensitive(False)
        else:
            self._backBtn.set_sensitive(True)
        orig_commitstart = self._commitstart
        for c in self._repo.get_history(None, None, 100,
                                        skip=self._commitstart):
            id, name, email, date, subj, body = c
            self._listViewModel.append((id, name, email, date, subj, c))
            self._commitstart += 1
        if (self._commitstart - orig_commitstart) < 100:
            self._nextBtn.set_sensitive(False)
        else:
            self._nextBtn.set_sensitive(True)

    def back_clicked(self, widget):
        if self._commitstart < 200:
            self._commitstart = 0
        self._commitstart -= 200
        self._populateCommits()

    def next_clicked(self, widget):
        self._populateCommits()

    def filter_clicked(self, widget):
        pass
