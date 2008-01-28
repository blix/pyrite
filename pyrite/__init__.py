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


#import gettext
#gettext.install('pyt')
def noop(message):return message #Don't know if I really want to localize the
                              #cmd line. For now continue to add localzable
                              #strings with the _() but make it a noop
import __builtin__
__builtin__.__dict__['_'] = noop                              

import extensions, options, UI, repository
from standard.help import HelpError
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
"apply|import": ['import', 0,
            [('s', 'stat', _('Output a diffstat for the input.  Does not actually apply.'), 0),
            ('c', 'check', _('Check to see if it would apply.  Does not actually apply.'), 0),
            ('v', 'verbose', _('Report progress to stdout'), 0)],
            _('Import a patch that has been exported by pyt')],
"archive": ['archive', 0,
            [('f', 'format', _('specify zip or tar, default is tar'), 0),
            ('c', 'commit', _('commit (commitid, symbolic reference) to create an archive for'), 0)],
            _('Create an archive of files from a commit')],
"bisect": ['bisect', 0,
            [],
            _('Find the change that introduced a bug by binary search.')],
"blame|annotate": ['blame', 0,
            [('l', 'long', _('show long rev'), 0),
            ('n', 'number', _('show line numbers'), 0)],
            _('Show what revision and author edited a file line-by-line')],
"branch": ['branch', 1,
            [('d', 'delete', _('delete the named branch'), 0),
            ('f', 'force', _('force creation or deletion'), 0),
            ('m', 'move', _('rename the branch'), 0),
            ('r', 'remote', _('list or delete remote-tracking branches'), 0),
            ('v', 'verbose', _('show detailed information'), 0),
            ('t', 'track', _('set up a tracking branch'), 0),
            ('a', 'all', _('show all branches'), 0),
            ('n', 'no-track', _('do not automatically track remote branches'), 0)],
            _('list, switch to, or delete branches')],
"checkout|reset|co": ['checkout', 1,
            [('b', 'branch', _('Create a new branch starting at this commit and switch to it'), 1),
            ('f', 'force', _('Force operation'), 0),
            ('m', 'merge', _('Merge files if working set is not clean'), 0)],
            _('Checkout a specific revision of the history')],
"checkin|commit|ci": ['checkin', 1,
            [('c', 'commit', _('Reuse commit message, author and timestamp'), 0),
            ('a', 'author', _('Use as author of the commit'), 0),
            ('m', 'message', _('Use as the commit message'), 0),
            ('s', 'signoff', _('Add a Signed-off-by line to the message'), 0),
            ('n', 'no-verify', _('bypass precommit hooks'), 0),
            ('', '_ammend', _('Replace the current tip with the new commit'), 0),
            ('v', 'verbose', _('show diff at the bottom of the commit message'), 0)],
            _('Record changes to the repository')],
"cherry": ['cherry', 0,
            [('e', 'edit', _('edit the commit message before commiting'), 0),
            ('n', 'no-commit', _('apply changes to working set but do not commit'), 0)],
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
            [(_('p'), _('--patch'), _('generate a patch'), 0),
            (_('s'), _('--stat'), _('show a diffstat'), 0),
            (_('c'), _('--color'), _('show colored diff'), 0),
            (_('t'), _('--template'), _('use a formatted template'), 0),
            (_(''), _('--style'), _('use a predefined style'), 0),
            (_('d'), _('--detect'), _('detect renames and copies'), 0),
            (_(''), _('--ignore-eol'), _('ignore end of line whitespace differences'), 0),
            (_('w'), _('--ignore-whitespace'), _('ignore all whitespace'), 0)],
            _('diff between to commits or a commit and the working set'),
            _('pyt diff [OPTIONS] [commit1[commit2]] [PATHS]...')],
"email": ['email', 0,
            [(_(''), _('--bcc'), _('Specify bcc recipients'), 0),
            (_(''), _('--cc'), _('Specify cc recipients'), 0),
            (_('c'), _('--compose'), _('launch an editor to write an introductory message'), 0),
            (_('f'), _('--from'), _('Specify the sender address'), 0),
            (_(''), _('--smtp-server'), _('Specify the SMTP server'), 0),
            (_('s'), _('--subject'), _('Specify the subject of the introductory mail'), 0),
            (_('d'), _('--dry-run'), _('Do everything but send the mails'), 0),
            (_('t'), _('--to'), _('Specify the recipients'), 0)],
            _('Send a collection of patches as emails'),
            _('pyt email [OPTIONS]... ')],
"export": ['export', 0,
            [(_('c'), _('--compose'), _('launch an editor to write an introductory message'), 0),
            (_('o'), _('--output'), _('path of file to output to'), 0),
            (_('s'), _('--signoff'), _('Add a Signed-off-by line to the message'), 0),
            (_('o'), _('--output'), _('file or directory to save to ("-" for stdout)'), 0),
            (_('n'), _('--numbered'), _('create patches with names prefixed [PATCH n/m]'), 0),
            (_('f'), _('--force'), _('overwrite existing files'), 0)],
            _('Export patches suitable to be emailed or imported'),
            _('pyt export [OPTIONS] [REVISION1[:REVISION2]]')],
"fetch": ['fetch', 0,
            [(_('f'), _('--force'), _('force fetch even if the local branch does not decend from the remote one'), 0),
            (_('n'), _('--no-tags'), _('do not download any tags'), 0),
            (_('e'), _('--extra-tags'), _('download tags thier related objects even if they would not be reachable otherwise'), 0),
            (_('d'), _('--depth'), _('maximum number of commits to fetch'), 0)],
            _('Get objects and refs from another repository'),
            _('pyt fetch [OPTIONS]... <repository> [[+]srccommit[:destcommit]]')],
"grep": ['grep', 0,
            [(_('i'), _('--ignore-case'), _('ignore case differences'), 0),
            (_('w'), _('--whole-word'), _('match whole word'), 0),
            (_('n'), _('--no-binary'), _('do not match against binary files'), 0),
            (_('v'), _('--invert'), _('invert match'), 0),
            (_('f'), _('--full-path'), _('print the full path to the file'), 0),
            (_(''), _('--no-name'), _('do not print the path/name of the file'), 0),
            (_('e'), _('--extended-regex'), _('use POSIX extended regex'), 0),
            (_('b'), _('--basic-string'), _('match string is not a regex'), 0),
            (_('c'), _('--count'), _('print the number of matches per file'), 0),
            (_('r'), _('--revision'), _('match against the supplied revision'), 0)],
            _('Print lines matching a pattern'),
            _('pyt grep [OPTIONS] <pattern> [PATH]')],
"gui|view": ['gui', 1,
            [],
            _('launch the graphical interface or history browser'),
            _('pyt gui [OPTION]')],
"help": ['help', 1,
            [('v', 'verbose', _('print full help and aliases'), 0)],
            _('view the general help or help for a command')],
"init": ['init', 1,
            [],
            _('Create an empty repository')],
"log": ['log', 1,
            [(_('s'), _('--style'), _('specify a predefined style'), 0),
            (_('t'), _('--template'), _('specify a template for the output'), 0),
            (_('l'), _('--limit'), _('specify the maximum number or commits to show (defualt 10)'), 0),
            (_('p'), _('--patch'), _('show the patch for the commit'), 0),
            (_('n'), _('--names'), _('show symbolic names for the commits'), 0),
            (_('f'), _('--follow-renames'), _('show history of files beyond renames'), 0)],
            _('Show commit logs'),
            _('pyt log [OPTIONS]... [firstcommit[:secondcommit] [PATHS]...')],
"merge": ['merge', 1,
            [(_('s'), _('--summary'), _('show a diffstat at the end of the merge'), 0),
            (_('m'), _('--message'), _('specify the message to use for the commit'), 0)],
            _('join two or more development histories together'),
            _('pyt merge [OPTIONS]... <branch> [BRANCHES]...')],
"pull": ['pull', 1,
            [(_('f'), _('--force'), _('force fetch even if the local branch does not decend from the remote one'), 0),
            (_('n'), _('--no-tags'), _('do not download any tags'), 0),
            (_('e'), _('--extra-tags'), _('download tags thier related objects even if they would not be reachable otherwise'), 0),
            (_('d'), _('--depth'), _('maximum number of commits to fetch'), 0),
            (_(''), _('--no-commit'), _('merge the files in the working set but do not commit the change'), 0),
            (_('s'), _('--summary'), _('show a diffstat at the end of the merge'), 0)],
            _('Fetch and merge in one operation'),
            _('pyt pull [OPTIONS]... <repository> [[+]srccommit[:destcommit]]')],
"push": ['push', 1,
            [(_('a'), _('--all'), _('push all heads'), 0),
            (_('t'), _('--all-tags'), _('push all tags'), 0),
            (_('f'), _('--force'), _('update the remote branch even if it does not decend from the local branch'), 0),
            (_('v'), _('--verbose'), _('show extra output'), 0)],
            _('Update remote refs and their associated objects'),
            _('pyt push [OPTIONS] <target-repository> [[+]sourcecommit[:targetcommit]]')],
"rebase": ['rebase', 0,
            [(_('i'), _('--interactive'), _('ask before commiting a change, allowing an edit'), 0),
            (_('p'), _('--preserve-merges'), _('preserve merge commits in interactive mode'), 0),
            (_(''), _('--diffstat'), _('display a diffstat of what changed upstream since the last rebase'), 0),
            (_('c'), _('--continue'), _('continue rebase operation after resolving a merge'), 0),
            (_('s'), _('--skip'), _('continue the rebase operation skipping the current patch'), 0),
            (_('a'), _('--abort'), _('restore the current branch to its original state'), 0),
            (_('m'), _('--merge'), _('use merging stratagies (allows rename detection)'), 0),
            (_('n'), _('--newbase'), _('rebase changes from <upstream> to <branch> onto this new base (do not include commits in <upstream>)'), 0)],
            _('Forward port local commits to the updated upstream head'),
            _('pyt rebase [OPTIONS] <upstream> [branch]')],
"remove|rm": ['remove', 0,
            [(_('f'), _('--force'), _('override the up-to-date check'), 0),
            (_('n'), _('--no-remove'), _('do not actually remove the file(s)'), 0),
            (_('r'), _('--recursive'), _('remove recursively when leading directory is given'), 0)],
            _('Remove files from the working set and tell pyt about it'),
            _('pyt remove [OPTIONS] file')],
"rename|mv": ['rename', 0,
            [(_('f'), _('--force'), _('force rename even if target exists'), 0),
            (_('i'), _('--ignore-errors'), _('skip operations that result in errors'), 0),
            (_('n'), _('--no-move'), _('do not actually move the file(s)'), 0)],
            _('Move or rename a file and tell pyt about it'),
            _('pyt rename [OPTIONS]... <source>... <destination>')],
"revert": ['revert', 0,
            [(_('e'), _('--edit'), _('edit the commit message before commiting'), 0),
            (_('n'), _('--no-commit'), _('prepare the working set but do not commit'), 0)],
            _('Revert a change in the history by applying a new commit'),
            _('pyt revert [OPTIONS] <commit>')],
"show": ['show', 0,
            [(_('s'), _('--style'), _('use a predefined style'), 0),
            (_('t'), _('--template'), _('specify your own template to use'), 0)],
            _('show files trees tags and commits'),
            _('pyt show [OPTIONS] <object>')],
"status": ['status', 1,
            [(_('c'), _('--commit'), _('Reuse commit message, author and timestamp'), 0),
            (_('a'), _('--author'), _('Use as author of the commit'), 0),
            (_('m'), _('--message'), _('Use as the commit message'), 0),
            (_('s'), _('--signoff'), _('Add a Signed-off-by line to the message'), 0),
            (_('n'), _('--no-verify'), _('bypass precommit hooks'), 0),
            (_(''), _('--ammend'), _('Replace the current tip with the new commit'), 0),
            (_('v'), _('--verbose'), _('show diff at the bottom of the commit message'), 0)],
            _('Show status of the working set'),
            _('pyt status [OPTIONS]')],
"squash": ['squash', 0,
            [],
            _('merge all changes into the working set and create a new commit'),
            _('pyt squash <commit>')],
"tag": ['tag', 0,
            [(_('d'), _('--delete'), _('delete the given tag'), 0),
            (_('s'), _('--sign'), _('make a signed tag'), 0),
            (_('a'), _('--annotated'), _('make an annotaged tag'), 0),
            (_('k'), _('--key'), _('use as the signing key'), 0),
            (_('v'), _('--verify'), _('verify the signature of the tag'), 0),
            (_('l'), _('--list'), _('list tags with an optional matching pattern'), 0),],
            _('create, list or delete tags'),
            _('pyt tag [OPTIONS] [<name>] [head]')],
"update|addremove": ['addremove', 1,
                [(_('r'), _('--remove'), _('only remove deleted files'), 0),
                 (_('a'), _('--add'), _('only add new files'), 0)],
                 _('look for added or removed files from the repository'),
                 _('pyt update [OPTION]... [FILE]...')],
"verify|fsck": ['verify', 0,
            [(_('t'), _('--tags'), _(''), 0),
            (_('v'), _('--verbose'), _('output extra information'), 0)],
            _('verify integrity of the repository'),
            _('pyt verify [OPTIONS]...')],
"web": ['web', 0,
            [(_('l'), _('--log'), _(''), 0),
            (_('d'), _('--daemon'), _(''), 0),
            (_('e'), _('--error-log'), _(''), 0),
            (_('p'), _('--port'), _(''), 0),
            (_('n'), _('--name'), _(''), 0),
            (_('c'), _('--config'), _(''), 0),
            (_('s'), _('--style'), _(''), 0),
            (_('t'), _('--template'), _(''), 0),
            (_('6'), _('--ipv6'), _(''), 0)],
            _('export a repository over http'),
            _('pyt web [OPTIONS]...')],
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
    help = dyn_import('help')
    configuration = dyn_import('config')
    show_trace = False
    try:
        global repo
        repo = repository.Repo()
        global config
        config = configuration.Config()
        extensions.load(commands, modules) #TODO:implement extension loading
        options.expand_aliases(commands, aliases_map)
        
        if len(sys.argv) < 2:
            raise help.HelpError, {'basic': 1}
        cmd = sys.argv[1]
        if not commands.has_key(cmd):
            raise HelpError, {'unknown': 1, 'command': cmd}
            
        module_name = commands[cmd][0]
        opts = []
        opts.extend(commands[cmd][2])
        opts.extend(global_options)
        flags,args = options.parse(opts, sys.argv[2:], cmd)
        show_trace = flags.get('debug-show-trace', False)
        m = dyn_import(module_name)
        modules[module_name].run(cmd, *args, **flags)
        
    except help.HelpError, inst:
        if show_trace: raise
        help.run(None, None, **inst.args[0])
    except options.ParseError, arg:
        if show_trace: raise
        ui.error_out(arg)
