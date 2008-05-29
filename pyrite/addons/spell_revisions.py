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
from pyrite.utils.help import HelpError
from pyrite.repository import Repo

description = "Allows different ways to specify revisions."

help_str = _("""
The following are standard git notations and are handled by git and supported,
this addon will translate other notations into what git understands.

sha1-id: a minimally short (usually more than 6 characters) hex string.

commit-id: a sha1 that is a hash of all the commit data.

ref: HEAD (tip/head of the current branch), <branch-name> (file names found
under .git/refs/heads/), <remote>/<branch-name> (file found under
.git/refs/remotes/<remote>/), <tag> (file found under .git/refs/tags).  These
may also be specified in .git/info/refs which contains a mapping of sha1-ids.

treeish: any ref or commit-id (also a "tree-id" sha1-id, which is a hash of
just the contents of the working directory a commit maps directly to one
"tree-id")

gittish: treeish with a leading "^" for negation, a series of ~[n] or ^[n]
following the treeish where ~[n] is sort for first parent n times back
and ^[n] is short for nth parent default to first.  There can be arbitrary
combinations of trailing ~ and ^ specifiers.  Commits
that are found in the reflog can also be accessed by gittish@{num},
gittish@{yesterday}, gittish{num month|week|day|hour|second ago} or
gittish@{YYYY-MM-DD HH:MM:SS}.  Git has some other ways to spell revisions
which I will not get into here.

The following will be translated y this addon to gittish notation.  Not that
a ":" is always required.  When "gittish" is optional and not specified
it defaults to HEAD unless otherwise noted.

"n:[gittish]" refers to the commit n after (or before if negative) gittish.
The default will be the NULL commit for that branch (begining).  So if you
want to get the 100th commit in this branch you could just say "100:".
Commits in git do not have a native rev number, so they are defined to be in
the order you get from calling "git rev-list --topo-order --reverse HEAD"
starting from 0 for the first commit.

remote:<remote-name>:<branch-name> refers to the tip of the branch
<branch-name> from the remote <remote-name>

tag:<tag-name> <branch-name> refers to the commit tagged by <tag-name>

branch:<branch-name> refers to the tip of the local branch <branch-name>

"tip:" synonym for HEAD, for Mercurial users (can also be used without the ":"
if it is at the beginning)

To get the following spellings are not yet implemented.

"subject:The subject of a commit:[gittish]" refers to the most recent commit
whose subject line starts with the speficied string after "gittish".
Colon characters need to be escaped with a "\".

The following are nicer ways to access the git reflog.  In order to get at
these, the commit must be in the reflog, which means it is an operation that
has happened recently in this copy of the repository.  If ref is not
specified, HEAD is assumed.

"reflog:yesterday:[ref]" refers to commits the day before the given revision.

"reflog:at:[n:]month|week|day|hour|minute:[ref]" refers to where ref was
pointing to n many timeframes ago

"reflog:n:[ref]" refers to where ref was n many operations ago.

"reflog:date:YYYY-MM-DD-HH-mm-SS:[ref]" refers to what gittish was pointing to
at the date-time specified.

""")

_id_cache = {}
_num_cache = {}
_orig_show_commit = None
_orig_get_template = None

def _update_cache(id):
    if id in _id_cache:
        return
    commits = pyrite.repo.get_history(None, id, -1, [Repo.ID], ordered=True,
                                      reverse=True)
    done = False
    for num, c in enumerate(commits):
        if done:
            continue
        id = c[Repo.ID]
        if id in _id_cache:
            done = True
            continue
        _id_cache[id] = num
        _num_cache[num] = id

def _get_num(id):
    _update_cache(id)
    return _id_cache.get(id, -1)

def _get_id(num, id='HEAD'):
    _update_cache(id)
    return _num_cache.get(num, None)

def _parse_revision(rev):
    # we are ":" delimited
    parts = rev.split(':')
    if len(parts) == 1:
        return rev
    result = ''

    g = globals()
    while parts:
        fmt = parts.pop(0)
        fn_name = '__' + fmt
        if fn_name not in g:
            try:
                num = int(fmt)
                result = __revnum(num, parts, result)
            except TypeError:
                raise HelpError('spell_revisions',
                                _('%s is not a valid way to spell a revision')
                                % fmt)
        else:
            result = g[fn_name](parts, result)
    return result

def __subject(parts, result):
    if not parts:
        raise HelpError('spell_revisions',
                        _('Invalid subject query, no subject name given'))
    subj = ':/'
    if parts[0][0] == '!':
        subj += '!'
    while True:
        if not parts:
            break
        subj += parts.pop(0)
        if subj[-1] == '\\' and subj[-2] != '\\':
            break

    return result + subj

def __tip(parts, result):
    result = result + 'HEAD'
    if parts:
        result += parts.pop(0)
    return result

def __revnum(num, parts, result):
    relto = 'HEAD'
    if parts:
        relto = parts.pop(0)
    relto = pyrite.repo.get_commit_info(relto, [Repo.ID])[Repo.ID]
    max = _get_num(relto)
    if num > max:
        raise HelpError('spell_revisions', _('Revision number %d goes '
                                         'past %s: %d') % (num, relto, max))
    if num < 0:
        id = _get_id(max + num, relto)
    if num > 0:
        id = _get_id(num, relto)
        if not id:
            raise HelpError('spell_revisions', _('%d is not a valid revision '
                                             'number') % num)
    return result + id

def __reflog(parts, result):
    if not parts:
        raise HelpError('spell_revisions', _('Invalid reflog query'))
    relto = 'HEAD'
    type = parts.pop(0)
    if type == 'yesterday':
        if parts:
            relto = parts.pop(0)
        return result + relto + '@{yesterday}'

    if type == 'at':
        if not parts:
            raise HelpError('spell_revisions',
                            _('Invalid reflog "at" query: no timeframe'))
        part = parts.pop(0)
        count = 1
        timeframe = None
        try:
            count = int(part)
            if count < 0:
                raise HelpError('spell_revisions',
                                _('Invalid reflog "at" query: %d must be '
                                  'positive.') % count )
        except ValueError:
            timeframe = part
        if parts:
            timeframe = parts.pop(0)
        if not timeframe in ('month', 'weeks', 'days', 'hour', 'second'):
            raise HelpError('spell_revisions',
                            _('Invalid reflog "at" query: bad or missing '
                              'timeframe "%s".  Need: month, weeks, days, '
                              'hour, second') % timeframe)
        if parts:
            relto = parts.pop(0)
        return result + relto + '@{' + str(count) + ' ' + timeframe + ' ago}'

    if type == 'date':
        if not parts:
            raise HelpError('spell_revisions',
                            _('Invalid reflog "date" query: no date'))
        date_parts = parts.pop(0).split('-')
        if len(date_parts) != 6:
            raise HelpError('spell_revisions',
                            _('Invalid reflog date query: malformed date'
                              '"%s".  Should be in "YYYY-MM-DD-HH-mm-SS" '
                              'format.'))
        if parts:
            relto = parts.pop(0)
        print date_parts
        return result + relto + ('@{%s/%s/%s %s-%s-%s}' % tuple(date_parts))

    try:
        num = int(type)
        if num < 0:
            raise HelpError('spell_revisions',
                        _('Invalid reflog query: "%s" must be positive') %
                        type)
        if parts:
            relto = parts.pop(0)
        return result + relto + '@{%s}' % type
    except ValueError:
        raise HelpError('spell_revisions',
                        _('Invalid reflog query: unknown type "%s"') % type)

def __remote(parts, result):
    if not parts:
        raise HelpError('spell_revisions',
                        _('Invalid remote query, no remote name given'))
    remote = parts.pop(0)
    if not parts:
        raise HelpError('spell_revisions',
                        _('Invalid remote query, no branch name given for '
                          '%s') % remote)

    return result + 'refs/remotes/' + remote + '/' + parts.pop(0)

def __tag(parts, result):
    if not parts:
        raise HelpError('spell_revisions',
                        _('Invalid tag query, no tag name given'))
    return result + 'refs/tags/' + parts.pop(0)

def __branch(parts, result):
    if not parts:
        raise HelpError('spell_revisions',
                        _('Invalid branch query, no branch name given'))
    return result + 'refs/heads/' + parts.pop(0)

def _show_commit(commit, formatter, stream):
    commit['REVNUM'] = str(_get_num(commit[Repo.ID]))
    _orig_show_commit(commit, formatter, stream)

def _get_template(style, template, color):
    data, tmpl = _orig_get_template(style, template, color)
    buffer = tmpl.compiled_buffer()
    for idx, item in enumerate(buffer):
        if len(item) == 1:
            continue
        if item[0] == 'ID':
            buffer.insert(idx, (':',))
            buffer.insert(idx, ('REVNUM', []))
            break
    return data, tmpl

def on_before_command(module, cmd, args, flags):
    if cmd in ('log', 'hist', 'history'):
        if pyrite.utils.io.affirmative(
                                pyrite.settings.get_option(
                                'pyrite.spell_rev.modify_logs')):
            global _orig_show_commit
            _orig_show_commit = module.show_commit
            global _orig_get_template
            _orig_get_template = module.get_template
            module.show_commit = _show_commit
            module.get_template = _get_template

    rev = flags.get('revision-start', None)
    if rev:
        flags['revision-start'] = _parse_revision(rev)

    rev = flags.get('revision-end', None)
    if rev:
        flags['revision-end'] = _parse_revision(rev)
