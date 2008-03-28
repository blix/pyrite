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
from pyrite.repository import Repo, RepoError
from pyrite.standard.help import HelpError

help_str =_("""
pyt cherry  [--record-origin] [--no-commit ] [--edit] <commit>
pyt cherry [--limit <limit commit>] --identify <search from commit>

The cherry command allows you to find and apply changes from another
branch.

Using -i and passing it a commit id will find changes not in
the current branch but in the passed commit.  A leading "-" means the
commit has already been cherry picked while a "+" means it has not.
Passing a limit will tell the command to stop reporting once it reaches
that limit

Once you have identified your commit to cherry-pick, you can simply call
pyt cherry <commit> and it will be applied.  You can use -r to record
the fact that it was cherry picked and from whence it came.  You can use
-e to manually edit the original commit message.
""")

def _run_cherry_pick(commit, edit, record, dryrun):
    c = pyrite.repo.get_commit_info(commit, [Repo.ID, Repo.SUBJECT, Repo.BODY])
    head = pyrite.repo.get_commit_info('HEAD')
    try:
        pyrite.repo.cherry_pick(c[Repo.ID], dryrun=dryrun)
    except RepoError, inst:
        return False, inst.args[0].splitlines()[0], c[Repo.ID]

    orig_id = c[Repo.ID]
    if (edit or record) and not dryrun:
        message = [c[Repo.SUBJECT], '\n', c[Repo.BODY]]
        if record:
            message.append(_('\n(Cherry Picked From: %s)\n') % orig_id)
        if edit:
            extra = []
            message = pyrite.ui.edit(message, extra, 'cherry-' + orig_id)

            if not message:
                pyrite.repo.move_head_to(head[Repo.ID])
                return False, _('No commit message, aborting'), orig_id

        try:
            pyrite.repo.move_head_to('HEAD^')
            pyrite.repo.update_index()
            del c[Repo.ID]
            del c[Repo.BODY]
            c[Repo.SUBJECT] = ''.join(message)
            pyrite.repo.commit(c)
        except RepoError, inst:
            pyrite.repo.move_head_to(head[Repo.ID])
            return False, inst.args[0].splitlines()[0]
    if dryrun:
        pyrite.repo.move_head_to('HEAD^')
    return True, None, orig_id

def run(cmd, *args, **flags):
    edit = 'edit' in flags
    dryrun = 'no-commit' in flags
    record = 'record-origin' in flags
    limit = flags.get('limit-commit', None)
    downstream = flags.get('identify', None)

    if (edit or record or dryrun) and (limit or downstream):
        raise HelpError({'command': cmd, 'message':
            _('Incompatable arguments passed')})

    if not args and not downstream:
        raise HelpError({'command': cmd, 'message':
            _('Need commmit(s) to cherry pick or -i')})

    output = None
    if downstream:
        output = pyrite.repo.cherry(downstream, limit=limit)
        pyrite.ui.info(output)
    else:
        for commit in args:
            succ, err, id = _run_cherry_pick(commit, edit, record, dryrun)
            if not succ:
                pyrite.ui.info([
                    _('Failed to cherry pick %s') % id, 'Reason: ' + err,
                    _('Please resolve any problem and commit using '
                               'pyt commit -c %s\n\n  ') % id[:10]
                ])
            else:
                pyrite.ui.info(_('Cherry picked: %s') % id)

