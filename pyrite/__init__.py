
def run():
    pass

def expandopts()
    pass
    
    
commands = {
"apply|import": (import,
            [(_('s'), _('stat'), _('Output a diffstat for the input.  Does not actually apply.')),
            _('c'), _('check'), _('Check to see if it would apply.  Does not actually apply.')),
            _('v'), _('verbose'), _('Report progress to stdout'))],
            _('Import a patch that has been exported by pyt'),
            _('pyt import [OPTIONS]... [PATCHES]...')),
"archive": (archive,
            [(_('f'), _('format'), _('specify zip or tar, default is tar')),
            _('c'), _('commit'), _('commit (commitid, symbolic reference) to create an archive for'))]
            _('Create an archive of files from a commit'),
            _('pyt archive [OPTIONS]... [PATHS]...')),
"bisect": (bisect,
            [],
            _('Find the change that introduced a bug by binary search. (see "pyt help bisect" for more info")'),
            _('pyt bisect <subcommand> <options>')),
"blame|annotate": (blame,
            [(_('l'), _('long'), _('show long rev')),
            (_('n'), _('number'), _('show line numbers'))],
            _('Show what revision and author edited a file line-by-line'),
            _('pyt blame [OPTIONS]... [COMMIT[:COMMIT]] [FILE]')),
"branch": (branch,
            [(_('d'), _('delete'), _('delete the named branch')),
            (_('f'), _('force'), _('force creation or deletion')),
            (_('m'), _('move'), _('rename the branch')),
            (_('r'), _('remote'), _('list or delete remote-tracking branches')),
            (_('v'), _('verbose'), _('show detailed information')),
            (_('t'), _('track'), _('set up a tracking branch')),
            (_('n'), _('no-track'), _('do not automatically track'))],
            _('list, switch to, create or delete branches'),
            _('pyt branch [OPTIONS]... <starting-commit> <oldbranch> <newbranch>')),
"checkout|reset|co": (checkout,
            [(_('b'), _('branch'), _('Create a new branch starting at this commit')),
            (_('f'), _('force'), _('Force operation'))],
            _('Checkout a specific revision of the history'),
            _('pyt checkout [OPTIONS] <commit> [PATHS]...')),
"checkin|commit|ci": (checkin,
            [(_('c'), _('commit'), _('Reuse commit message, author and timestamp')),
            (_('a'), _('author'), _('Use as author of the commit')),
            (_('m'), _('message'), _('Use as the commit message'),
            (_('s'), _('signoff'), _('Add a Signed-off-by line to the message')),
            (_('n'), _('no-verify'), _('bypass precommit hooks')),
            (_(''), _('ammend'), _('Replace the current tip with the new commit')),
            (_('v'), _('verbose'), _('show diff at the bottom of the commit message'))],
            _('Record changes to the repository'),
            _('pyt commit [OPTIONS]...')),
"cherry": (cherry,
            [(_('e'), _('edit'), _('edit the commit message before commiting')),
            (_('n'), _('no-commit'), _('apply changes to working directory but do not commit'))],
            _('Apply the change introduced by an existing commit'),
            _('pyt cherry [OPTIONS]... <commit>')),
"clone": (clone,
            [(_('n'), _('no-checkout'), _('no checkout of HEAD is done after clone is complete')),
            (_('b'), _('bare'), _('clone target dir is the git dir')),
            (_('d'), _('depth'), _('create a shallow clone up to depth'))],
            _('Clone a repository into a new directory'),
            _('pyt clone [OPTIONS]... <repository> [<directory>]')),
"config": (config,
            [(_('r'), _('repo-only'), _('option only applies to current repo')),
            (_('d'), _('delete'), _('delete option')),
            (_('a'), _('all'), _('show all variables'))]
            _('Set or get configuration variables'),
            _('pyt config [OPTIONS]... [variable [newvalue]]')),
"diff": (diff,
            [(_('p'), _('patch'), _('generate a patch')),
            (_('s'), _('stat'), _('show a diffstat')),
            (_('c'), _('color'), _('show colored diff')),
            (_('t'), _('template'), _('use a formatted template')),
            (_(''), _('style'), _('use a predefined style')),
            (_('d'), _('detect'), _('detect renames and copies')),
            (_(''), _('ignore-eol'), _('ignore end of line whitespace differences')),
            (_('w'), _('ignore-whitespace'), _('ignore all whitespace'))],
            _('Show changes between to commits or a commit and the working directory'),
            _('pyt diff [OPTIONS] [commit1[commit2]] [PATHS]...')),
"email": (email,
            [(_(''), _('bcc'), _('Specify bcc recipients')),
            (_(''), _('cc'), _('Specify cc recipients')),
            (_('c'), _('compose'), _('launch an editor to write an introductory message')),
            (_('f'), _('from'), _('Specify the sender address')),
            (_(''), _('smtp-server'), _('Specify the SMTP server')),
            (_('s'), _('subject'), _('Specify the subject of the introductory mail')),
            (_('d'), _('dry-run'), _('Do everything but send the mails')),
            (_('t'), _('to'), _('Specify the recipients'))],
            _('Send a collection of patches as emails'),
            _('pyt email [OPTIONS]... ')),
"export": (export,
            (_('c'), _('compose'), _('launch an editor to write an introductory message')),
            (_('o'), _('output'), _('path of file to output to')),
            (_('s'), _('signoff'), _('Add a Signed-off-by line to the message')),
            (_('o'), _('output'), _('file or directory to save to ("-" for stdout)'))
            (_('n'), _('numbered'), _('create patches with names prefixed [PATCH n/m]')),
            (_('f'), _('force'), _('overwrite existing files'))],
            _('Export patches suitable to be emailed or imported'),
            _('pyt export [OPTIONS] [REVISION1[:REVISION2]]')),
"fetch": (fetch,
            [(_('f'), _('force'), _('force fetch even if the local branch does not decend from the remote one')),
            (_('n'), _('no-tags'), _('do not download any tags')),
            (_('e'), _('extra-tags'), _('download tags thier related objects even if they would not be reachable otherwise')),
            (_('d'), _('depth'), _('maximum number of commits to fetch'))],
            _('Get objects and refs from another repository'),
            _('pyt fetch [OPTIONS]... <repository> [[+]srccommit[:destcommit]]')),
"grep": (grep,
            [(_('i'), _('ignore-case'), _('ignore case differences')),
            (_('w'), _('whole-word'), _('match whole word')),
            (_('n'), _('no-binary'), _('do not match against binary files')),
            (_('v'), _('invert'), _('invert match')),
            (_('f'), _('full-path'), _('print the full path to the file')),
            (_(''), _('no-name'), _('do not print the path/name of the file')),
            (_('e'), _('extended-regex'), _('use POSIX extended regex')),
            (_('b'), _('basic-string'), _('match string is not a regex')),
            (_('c'), _('count'), _('print the number of matches per file')),
            (_('r'), _('revision'), _('match against the supplied revision'))],
            _('Print lines matching a pattern'),
            _('pyt grep [OPTIONS] <pattern> [PATH]')),
"gui|view": (gui,
            [(_('b'), _('browse'), _('launch the history browser'))],
            _('launch the graphical interface or history browser'),
            _('pyt gui [OPTION]')),
"help": (help,
            [],
            _('view the general help or help for a command'),
            _('pyt help [command]')),
"init": (init,
            [],
            _('Create an empty repository'),
            _('pyt init')),
"log": (log,
            [(_('s'), _('style'), _('specify a predefined style'),
            (_('t'), _('template'), _('specify a template for the output')),
            (_('l'), _('limit'), _('specify the maximum number or commits to show (defualt 10)')),
            (_('p'), _('patch'), _('show the patch for the commit')),
            (_('n'), _('names'), _('show symbolic names for the commits')),
            (_('f'), _('follow-renames'), _('show history of files beyond renames')),],
            _('Show commit logs'),
            _('pyt log [OPTIONS]... [firstcommit[:secondcommit] [PATHS]...')),
"merge": (merge,
            [(_('s'), _('summary'), _('show a diffstat at the end of the merge')),
            (_('m'), _('message'), _('specify the message to use for the commit'))],
            _('join two or more development histories together'),
            _('pyt merge [OPTIONS]... <branch> [BRANCHES]...')),
"pull": (pull,
            [(_('f'), _('force'), _('force fetch even if the local branch does not decend from the remote one')),
            (_('n'), _('no-tags'), _('do not download any tags')),
            (_('e'), _('extra-tags'), _('download tags thier related objects even if they would not be reachable otherwise')),
            (_('d'), _('depth'), _('maximum number of commits to fetch')),
            _(''), _('no-commit'), _('merge the files in the working directory but do not commit the change')),
            (_('s'), _('summary'), _('show a diffstat at the end of the merge'))],
            _('Fetch and merge in one operation'),
            _('pyt pull [OPTIONS]... <repository> [[+]srccommit[:destcommit]]')),
"push": (push,
            [(_('a'), _('all'), _('push all heads'),
            (_('t'), _('all-tags'), _('push all tags'),
            (_('f'), _('force'), _('update the remote branch even if it does not decend from the local branch'),
            (_('v'), _('verbose'), _('show extra output'),],
            _('Update remote refs and their associated objects'),
            _('pyt push [OPTIONS] <target-repository> [[+]sourcecommit[:targetcommit]]')),
"rebase": (rebase,
            [(_('i'), _('interactive'), _('ask before commiting a change, allowing an edit'),
            (_('p'), _('preserve-merges'), _('preserve merge commits in interactive mode')),
            (_(''), _('diffstat'), _('display a diffstat of what changed upstream since the last rebase')),
            (_('c'), _('continue'), _('continue rebase operation after resolving a merge')),
            (_('s'), _('skip'), _('continue the rebase operation skipping the current patch')),
            (_('a'), _('abort'), _('restore the current branch to its original state')),
            (_('m'), _('merge'), _('use merging stratagies (allows rename detection)')),
            (_('n'), _('newbase'), _('rebase changes from <upstream> to <branch> onto this new base (do not include commits in <upstream>)'))],
            _('Forward port local commits to the updated upstream head'),
            _('pyt rebase [OPTIONS] <upstream> [branch]')),
"remove|rm": (remove,
            [(_('f'), _('force'), _('override the up-to-date check')),
            (_('n'), _('no-remove'), _('do not actually remove the file(s)')),
            (_('r'), _('recursive'), _('remove recursively when leading directory is given'))],
            _('Remove files from the working directory and tell pyt about it'),
            _('pyt remove [OPTIONS] file')),
"rename|mv": (rename,
            [(_('f'), _('force'), _('force rename even if target exists'),
            (_('i'), _('ignore-errors'), _('skip operations that result in errors')),
            (_('n'), _('no-move'), _('do not actually move the file(s)'))],
            _('Move or rename a file and tell pyt about it'),
            _('pyt rename [OPTIONS]... <source>... <destination>')),
"revert": (revert,
            [(_('e'), _('edit'), _('edit the commit message before commiting'),
            (_('n'), _('no-commit'), _('prepare the working directory but do not commit')),],
            _('Revert a change in the history by applying a new commit'),
            _('pyt revert [OPTIONS] <commit>')),
"show": (show,
            [(_('s'), _('style'), _('use a predefined style')),
            (_('t'), _('template'), _('specify your own template to use'))],
            _('show files trees tags and commits'),
            _('pyt show [OPTIONS] <object>')),
"status": (status,
            [(_('c'), _('commit'), _('Reuse commit message, author and timestamp')),
            (_('a'), _('author'), _('Use as author of the commit')),
            (_('m'), _('message'), _('Use as the commit message'),
            (_('s'), _('signoff'), _('Add a Signed-off-by line to the message')),
            (_('n'), _('no-verify'), _('bypass precommit hooks')),
            (_(''), _('ammend'), _('Replace the current tip with the new commit')),
            (_('v'), _('verbose'), _('show diff at the bottom of the commit message'))],
            _('Show status of the working directory'),
            _('pyt status [OPTIONS]')),
"squash": (squash,
            [],
            _('merge all changes into the working directory and create a new commit'),
            _('pyt squash <commit>')),
"tag": (tag,
            [(_('d'), _('delete'), _('delete the given tag')),
            (_('s'), _('sign'), _('make a signed tag')),
            (_('a'), _('annotated'), _('make an annotaged tag')),
            (_('k'), _('key'), _('use as the signing key')),
            (_('v'), _('verify'), _('verify the signature of the tag')),
            (_('l'), _('list'), _('list tags with an optional matching pattern')),],
            _('create, list or delete tags'),
            _('pyt tag [OPTIONS] <name> [head]')),
"update|addremove": (addremove,
                [(_('r'), _('remove'), _('only remove deleted files')),
                 (_('a'), _('add'), _('only add new files')),
                 (_('u'), _('update'), _('only update tracked files'))],
                 _('pyt update [OPTION]... [FILE]...')),
                
"verify|fsck": (verify,
            [(_('t'), _('tags'), _(''),
            (_('v'), _('verbose'), _('output extra information'))],
            _('verify integrity of the repository'),
            _('pyt verify [OPTIONS]...')),
"web": (web,
            [(_('l'), _('log'), _('')),
            (_('d'), _('daemon'), _('')),
            (_('e'), _('error-log'), _('')),
            (_('p'), _('port'), _('')),
            (_('n'), _('name'), _('')),
            (_('c'), _('config'), _('')),
            (_('s'), _('style'), _('')),
            (_('t'), _('template'), _('')),
            (_('6'), _('ipv6'), _('')),],
            _('export a repository over http'),
            _('pyt web [OPTIONS]...')),
}
