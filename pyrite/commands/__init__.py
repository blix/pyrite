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

# commands with the second element as 0 are shown only in extended help
# commands with the second element as 1 are shown in normal help

_commands = {
('alter','rebase'): ('alter', 0,
            _('Alter the history to change order, contents partens etc')),
('bisect',): ('bisect', 0,
            _('Find the change that introduced a bug by binary search.')),
('blame', 'annotate'): ('blame', 0,
            _('Show what revision and author edited a file line-by-line')),
('branch',): ('branch', 1,
            _('list, switch to, create or delete branches')),
('checkout', 'co'): ('checkout', 1,
            _('Checkout a specific revision of the history')),
('checkin', 'commit', 'ci'): ('checkin', 1,
            _('Record changes to the repository')),
('cherry',): ('cherry', 0,
            _('Apply the change introduced by an existing commit')),
('clone',): ('clone', 1,
            _('Clone a repository into a new directory')),
('config',): ('config', 1,
            _('Set or get configuration variables')),
('diff',): ('diff', 1,
            _('diff between to commits or a commit and the working set')),
('email',): ('email', 0,
            _('Send a collection of patches as emails')),
('export',): ('export', 0,
            _('Export patches suitable to be emailed or imported')),
('fetch',): ('fetch', 0,
            _('Get objects and refs from another repository')),
('grep',): ('grep', 0,
            _('Print lines matching a pattern')),
('gui', 'view'): ('gui', 1,
            _('launch the graphical interface or history browser')),
('help',): ('help', 1,
            _('view the general help or help for a command')),
('import', 'apply'): ('import', 0,
            _('Import a patch that has been exported by pyt')),
('init',): ('init', 1,
            _('Create an empty repository')),
('log', 'hist', 'history'): ('log', 1,
            _('Show commit logs')),
('move', 'mv', 'rename'): ('move', 0,
            _('Move or rename a file and tell pyt about it')),
('pull',): ('pull', 1,
            _('Fetch and merge in one operation')),
('push',): ('push', 1,
            _('Update remote refs and their associated objects')),
('recover',): ('recover', 0,
            _('Recover the previous state of a branch.')),
('remove', 'rm'): ('remove', 0,
            _('Remove files from the working set and tell pyt about it')),
('resolve', 'res'): ('resolve', 1,
            _('Resolve a merge conflict')),
('revert',): ('revert', 0,
            _('Revert a change in the history by applying a new commit')),
('show',): ('show', 0,
            _('show files, tags and commits')),
('status',): ('status', 1,
            _('Show status of the working set')),
('tag',): ('tag', 0,
            _('create, list or delete tags')),
('track', 'add', 'update'): ('track', 1,
                 _('look for added or removed files from the repository')),
('verify', 'fsck'): ('verify', 0,
            _('verify integrity of the repository'))
}

def get_command_info(cmd):
    for c, info in _commands.iteritems():
        if cmd in c:
            return info



