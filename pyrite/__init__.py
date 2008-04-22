#Copyright 2008 Govind Salinas <blix@sophiasuchtig.com>
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 2 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.


#import gettext
#gettext.install('pyt')
def noop(message):return message #Don't know if I really want to localize the
                              #cmd line. For now continue to add localzable
                              #strings with the _() but make it a noop
import __builtin__
__builtin__.__dict__['_'] = noop

import extensions, options, UI, repository
import pyrite.standard.config as pytconfig
import pyrite.standard.help as pythelp
import sys, imp

config = None

repo = None

ui = UI.UI()

# commands with the second element as 0 are shown only in extended help
# commands with the second element as 1 are shown in normal help
# options with the last arg as 1 want an argument
# options with the last arg as 2 are required
# options with the last arg as 3 are required and want an argument
commands = {
"bisect": ['bisect', 0,
            [],
            _('Find the change that introduced a bug by binary search.')],
"blame|annotate": ['blame', 0,
            [('l', 'long', _('show long rev'), 0),
            ('c', 'commit', _('show the file from its state in this commit'), 1),
            ('s', 'start-line', _('start showing at this line number'), 1),
            ('e', 'end-line', _('don\'t show after this line number'), 1)],
            _('Show what revision and author edited a file line-by-line')],
"branch": ['branch', 1,
            [('d', 'delete', _('delete the named branch'), 0),
            ('f', 'force', _('force creation or deletion'), 0),
            ('m', 'move', _('rename the branch'), 0),
            ('r', 'remote', _('list or delete remote-tracking branches'), 0),
            ('v', 'verbose', _('show detailed information'), 0),
            ('a', 'all', _('show all branches'), 0),
            ('s', 'switch', _('Create a branch and switch to it'), 1)],
            _('list, switch to, create or delete branches')],
"checkout|co": ['checkout', 1,
            [('f', 'force', _('Force operation'), 0),
            ('m', 'merge', _('Merge files if working set is not clean'), 0)],
            _('Checkout a specific revision of the history')],
"checkin|commit|ci": ['checkin', 1,
            [('c', 'commit', _('Reuse commit message, author and timestamp'), 1),
            ('a', 'author', _('Use as author of the commit'), 1),
            ('m', 'message', _('Use as the commit message'), 1),
            ('s', 'signoff', _('Add a Signed-off-by line to the message'), 0),
            ('n', 'no-verify', _('bypass precommit hooks'), 0),
            ('', 'amend', _('Replace the current tip with the new commit'), 0),
            ('e', 'edit', _('Force invoking the editor for the commit message'), 0),
            ('v', 'verbose', _('show diff at the bottom of the commit message'), 0)],
            _('Record changes to the repository')],
"cherry": ['cherry', 0,
            [('e', 'edit', _('edit the commit message before commiting'), 0),
            ('l', 'limit-commit', _('stop looking for candidates after this commit'), 1),
            ('n', 'no-commit', _('limit number of candidates to find'), 0),
            ('r', 'record-origin', _('note on the commit where the change came from'), 0),
            ('i', 'identify', _('find candidates to cherry pick from a branch'), 1)],
            _('Apply the change introduced by an existing commit')],
"clone": ['clone', 1,
            [('n', 'no-checkout', _('no checkout of HEAD is done after clone is complete'), 0),
            ('b', 'bare', _('clone target dir is the git dir'), 0),
            ('d', 'depth', _('create a shallow clone up to depth'), 0)],
            _('Clone a repository into a new directory')],
"config": ['config', 1,
            [('r', 'repo-only', _('option only applies to current repo'), 0),
            ('d', 'delete', _('delete option'), 0),
            ('a', 'all', _('show all configured options'), 0),
            ('s', 'set', _('set a option'), 0),
            ('i', 'ignore', _('ignore a pattern of files'), 0),
            ('u', 'unignore', _('stop ignoring a pattern of files'), 0),
            ('', 'add', _('add variable with the name even if it exists'), 0)],
            _('Set or get configuration variables')],
"diff": ['diff', 1,
            [('s', 'stat', _('show a diffstat'), 0),
            ('c', 'color', _('show colored diff'), 0),
            ('t', 'template', _('use a formatted template'), 1),
            ('', 'style', _('use a predefined style'), 1),
            ('d', 'detect', _('detect renames and copies'), 0),
            ('e', 'ignore-eol', _('ignore end of line whitespace differences'), 0),
            ('w', 'ignore-whitespace', _('ignore all whitespace'), 0)],
            _('diff between to commits or a commit and the working set')],
"email": ['email', 0,
            [('s', 'ssh', _('Send over ssh'), 0)],
            _('Send a collection of patches as emails')],
"export": ['export', 0,
            [('c', 'compose', _('launch an editor to write an introductory message'), 0),
            ('o', 'output-dir', _('file or directory to save to ("-" for stdout)'), 1),
            ('n', 'numbered', _('create patches with names prefixed [PATCH n/m]'), 0),
            ('f', 'force', _('overwrite existing files'), 0),
            ('b', 'bundle', _('create a min-repo that can be used to pull/fetch from'), 1),
            ('v', 'verify', _('verify a bundle'), 1),
            ('a', 'archive', _('create a archive of the workdir for commit'), 1),
            ('', 'format', _('format for an archive, either .tgz (default) or .zip'), 1)],
            _('Export patches suitable to be emailed or imported')],
"fetch": ['fetch', 0,
            [('f', 'force', _('force fetch even if the local branch does not decend from the remote one'), 0),
            ('n', 'no-tags', _('do not download any tags'), 0),
            ('d', 'depth', _('maximum number of commits to fetch'), 0)],
            _('Get objects and refs from another repository')],
"grep": ['grep', 0,
            [('i', 'ignore-case', _('ignore case differences'), 0),
            ('w', 'whole-word', _('match whole word'), 0),
            ('n', 'no-binary', _('do not match against binary files'), 0),
            ('v', 'invert', _('invert match'), 0),
            ('f', 'full-path', _('print the full path to the file'), 0),
            ('', 'no-name', _('do not print the path/name of the file'), 0),
            ('b', 'basic-string', _('match string is not a regex'), 0),
            ('c', 'count', _('print the number of matches per file'), 0),
            ('r', 'revision', _('match against the supplied revision'), 1)],
            _('Print lines matching a pattern'),
            _('pyt grep [OPTIONS] <pattern> [PATH]')],
"gui|view": ['gui', 1,
            [],
            _('launch the graphical interface or history browser'),
            _('pyt gui [OPTION]')],
"help": ['help', 1,
            [('v', 'verbose', _('print full help and aliases'), 0)],
            _('view the general help or help for a command')],
"import|apply": ['import', 0,
            [('b', 'bundle', _('Import a bundle.'), 1),
            ('i', 'interactive', _('Run interactively.'), 0),
            ('s', 'signoff', _('Add Signed-off-by line to message.'), 0),
            ('', 'skip', _('Skip the current patch.'), 0),
            ('', 'resolved', _('Current patch conflict is resolved'), 0)],
            _('Import a patch that has been exported by pyt')],
"init": ['init', 1,
            [],
            _('Create an empty repository')],
"log|hist|history": ['log', 1,
            [('s', 'style', _('specify a predefined style'), 1),
            ('t', 'template', _('specify a template for the output'), 1),
            ('l', 'limit', _('specify the maximum number or commits to show (defualt 10)'), 1),
            ('p', 'patch', _('show the patch for the commit'), 0),
            ('f', 'follow-renames', _('show history of files beyond renames'), 0),
            ('a', 'all', _('do not limit the number of commits to show'), 0)],
            _('Show commit logs')],
"merge": ['merge', 1,
            [('s', 'summary', _('show a diffstat at the end of the merge'), 0),
            ('m', 'message', _('specify the message to use for the commit'), 0)],
            _('join two or more development histories together')],
"move|mv|rename": ['move', 0,
            [('f', 'force', _('force rename even if target exists'), 0),
            ('i', 'ignore-errors', _('skip operations that result in errors'), 0),
            ('n', 'no-move', _('do not actually move the file(s)'), 0)],
            _('Move or rename a file and tell pyt about it')],
"pull": ['pull', 1,
            [('f', 'force', _('allow local branch to not decend from the remote one'), 0),
            ('n', 'no-tags', _('do not download any tags'), 0),
            ('e', 'extra-tags', _('download all tags even those not tracked'), 0),
            ('d', 'depth', _('maximum number of commits to fetch'), 1),
            ('', 'no-commit', _('merge the working set but do not commit the change'), 0),
            ('s', 'summary', _('show a diffstat at the end of the merge'), 0),
            ('r', 'rebase', _('Rebase your changes on top of the changes you pull down'), 0)],
            _('Fetch and merge in one operation')],
"push": ['push', 1,
            [('a', 'all', _('push all heads'), 0),
            ('t', 'all-tags', _('push all tags'), 0),
            ('f', 'force', _('allow remote branch to not decend from the local one'), 0),
            ('v', 'verbose', _('show extra output'), 0)],
            _('Update remote refs and their associated objects')],
"rebase": ['rebase', 0,
            [('i', 'interactive', _('ask before commiting a change, allowing an edit'), 0),
            ('p', 'preserve-merges', _('preserve merge commits in interactive mode'), 0),
            ('', 'diffstat', _('display a diffstat of what changed upstream since the last rebase'), 0),
            ('c', 'continue', _('continue rebase operation after resolving a merge'), 0),
            ('s', 'skip', _('continue the rebase operation skipping the current patch'), 0),
            ('a', 'abort', _('restore the current branch to its original state'), 0),
            ('m', 'merge', _('use merging stratagies (allows rename detection)'), 0),
            ('n', 'newbase', _('rebase changes from <upstream> to <branch> onto this new base (do not include commits in <upstream>)'), 0)],
            _('Forward port local commits to the updated upstream head')],
"remove|rm": ['remove', 0,
            [('f', 'force', _('override the up-to-date check'), 0),
            ('n', 'no-remove', _('do not actually remove the file(s)'), 0),
            ('u', 'untrack', _('do not remove the file(s), just stop tracking them'), 0),
            ('r', 'recursive', _('remove recursively when leading directory is given'), 0)],
            _('Remove files from the working set and tell pyt about it')],
"revert": ['revert', 0,
            [('f', 'files', _('Revert files in the working directory'), 0),
            ('u', 'undo', _('Undo a commit by applying a reverse patch'), 1),
            ('m', 'mainline', _('Undo a commit by applying a reverse patch'), 1),
            ('e', 'edit', _('Edit the commit message before commiting'), 0),
            ('n', 'no-commit', _('Prepare the working set but do not commit'), 0)],
            _('Revert a change in the history by applying a new commit')],
"show": ['show', 0,
            [('s', 'style', _('use a predefined style'), 0),
            ('t', 'template', _('specify your own template to use'), 0)],
            _('show files, tags and commits')],
"status": ['status', 1,
            [('c', 'color', _('Show in color'), 0),
            ('', 'amend', _('Replace the current tip with the new commit'), 0)],
            _('Show status of the working set')],
"squash": ['squash', 0,
            [],
            _('merge all changes into the working set and create a new commit')],
"tag": ['tag', 0,
            [('d', 'delete', _('delete the given tag'), 0),
            ('s', 'sign', _('make a signed tag'), 0),
            ('a', 'annotated', _('make an annotaged tag'), 0),
            ('k', 'key', _('use as the signing key'), 1),
            ('v', 'verify', _('verify the signature of the tag'), 0),
            ('m', 'message', _('specify the message to use for the tag'), 0),
            ('l', 'list', _('list tags with an optional matching pattern'), 0),],
            _('create, list or delete tags')],
"track|add|update": ['track', 1,
                [('f', 'force', _('Add file even if it is ignored'), 0),
                ('v', 'verbose', _('show added files'), 0)],
                 _('look for added or removed files from the repository')],
"verify|fsck": ['verify', 0,
            [('v', 'verbose', _('output extra information'), 0)],
            _('verify integrity of the repository')],
"web": ['web', 0,
            [('l', 'log', _(''), 0),
            ('d', 'daemon', _(''), 0),
            ('e', 'error-log', _(''), 0),
            ('p', 'port', _(''), 0),
            ('n', 'name', _(''), 0),
            ('c', 'config', _(''), 0),
            ('s', 'style', _(''), 0),
            ('t', 'template', _(''), 0),
            ('6', 'ipv6', _(''), 0)],
            _('export a repository over http')]
}

global_options = [(_(''), _('debug-show-trace'), _('print stacktraces on errors'), 0)]

help_str = _("Pyrite Distribute SCM")

modules = {}

aliases_map = {}

def dyn_import(module, is_extension=False, path=None):
    if module in modules: return
    package = None
    if extensions.is_extension(module):
        package = exensions.get_package(module)
    else:
        package = 'pyrite.standard'
    m = __import__(package, fromlist=module)
    f, p, d = imp.find_module(module, m.__path__)
    modules[module] = m = imp.load_module(package + '.' + module, f, p, d)
    return m

def run():
    show_trace = False
    try:
        global repo
        repo = repository.Repo()
        global config
        config = pytconfig.Config()
        extensions.load(commands, modules) #TODO:implement extension loading
        options.expand_aliases(commands, aliases_map)
        
        if len(sys.argv) < 2:
            raise pythelp.HelpError, {'basic': 1}
        cmd = sys.argv[1]
        if not commands.has_key(cmd):
            raise pythelp.HelpError({'unknown': 1, 'command': cmd})
            
        module_name = commands[cmd][0]
        opts = []
        opts.extend(commands[cmd][2])
        opts.extend(global_options)
        flags,args = options.parse(opts, sys.argv[2:], cmd)
        show_trace = flags.get('debug-show-trace', False)
        m = dyn_import(module_name)
        modules[module_name].run(cmd, *args, **flags)

    except pythelp.HelpError, inst:
        if show_trace: raise
        pythelp.run(None, None, **inst.args[0])
    except options.ParseError, inst:
        if show_trace: raise
        ui.error_out(inst)
    except repository.RepoError, inst:
        if show_trace: raise
        ui.error_out(inst)
