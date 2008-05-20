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
from pyrite.sequencer import *
from pyrite.repository import Repo
import os, cPickle
from pyrite.standard.help import HelpError

options = [
('i', 'interactive', _('ask before commiting a change, allowing an edit'), 0),
('p', 'preserve', _('preserve merge commits in interactive mode'), 0),
('m', 'merge', _('use merging stratagies (allows rename detection)'), 0),
('o', 'onto', _('the new base for the branch'), 1),
('f', 'from', _('changes will will be taken from this branch'), 1),
('b', 'base', _('changes will be relative to this branch'), 1)
]

help_str =_("""
pyt alter [OPTIONS] --base <upstream> [--from <branch>] [--onto <newbase>]
pyt alter [OPTIONS] --interactive --base <starting commit>
pyt alter [OPTIONS] -i -b <upstream> [-f <branch>] [-o <newbase>]
pyt alter cont[inue]
pyt alter skip
pyt alter abort

The alter command serves two related purposes, it basically re-applies commits
in an easy and automated way.  You should not rebase published changes because
the result is a different history.

The first form is useful if you have a branch that is forks from a mainline
and you want to update it so that forked branch's new contents are "on top of"
the updated mainline's.  You can think of it as follows:  It finds commits in
<branch> (defaulted to the current branch) that aren't in <upstream>.  It
then removes them from the <branch> and pulls from <upstream>.  Then it
re-applies the commits it removed.  If you specify --onto, <branch> will
become a decendant of <newbase>.

The interactive mode is basically a swiss army knife for managing your history.
Using interactive mode, you can split, combine (squash), edit and delete
commits from the branch.  It presnets you a list of commits with the default
action of "pick" which will apply the commit.  You can change this to "edit"
to change the contents of the commit, or "squash" which will merge it with
the previous commit.  You can also use this to change the order of the
commits or remove them entirely.  Pyt will occasionally stop to let you know
of a problem or to let you edit a commit.  You can use the cont[inue],
abort and skip subcommands to tell pyt what action to take next

You can combine both modes if you want to change history based on the history
of another branch.
""")

def _handle_subcommands(command, sequencer):
    if command in ('cont', 'continue', 'skip'):
        if command == 'skip':
            sequencer.skip()
        else:
            sequencer.finish_last()
        return sequencer.run()

    elif command == 'abort':
        sequencer.abort()
        commit = pyrite.repo.get_commit_info('HEAD',
                                             [Repo.ID, Repo.SUBJECT])
        subj = commit[Repo.SUBJECT]
        if len(subj) > 30:
            subj = subj[:30] + '...'
        pyrite.ui.info(_('Rebase aborted, HEAD is at %s: %s') %
                       (commit[Repo.ID][:8], subj))
        return True, None

    else:
        raise HelpError(cmd, _('%s is not a command') % args[0])

def _finish(done, last_id):
    if done:
        pyrite.ui.info(_('Rebase completed.\n\n'))
        #pyrite.ui.info(_('If you wish to go back to your original state'
        #                 'run\n"pyt revert -'))
        # need to provide a git reset --hard sequencer._head cmd
    else:
        c = pyrite.repo.get_commit_info('HEAD', [Repo.ID, Repo.SUBJECT])
        pyrite.ui.info(_('HEAD is at %s "%s"') % (c[Repo.ID][:8],
                                                c[Repo.SUBJECT][:30]))
        c = pyrite.repo.get_commit_info(last_id, [Repo.ID, Repo.SUBJECT])
        pyrite.ui.info(_('Changes from %s "%s" have been applied.') %
                      (c[Repo.ID][:8], c[Repo.SUBJECT]))
        pyrite.ui.info(_('Once you are done editing, you can run'))
        pyrite.ui.info(_('"pyt alter continue."\n\n'))

def run(cmd, args, flags):

    curbranch = pyrite.repo.branch()
    interactive = 'interactive' in flags
    preserve = 'preserve' in flags
    merge = flags.get('merge', None)
    base = flags.get('base', None)
    branch = flags.get('from', None)
    onto = flags.get('onto', None)

    done = False
    sequencer_file = os.path.join(pyrite.repo.get_repo_dir(), 'pyrite-seq')
    in_progress = os.path.isfile(sequencer_file)
    sequencer = None
    try:
        if in_progress:
            if base or branch or onto or interactive:
                raise HelpError(cmd, _('Already modifying this branch.\n'
                                       'You can "pyt %s abort" to cancel.') % cmd)

            if not args:
                raise HelpError(cmd, _('Tell me an action to take.'))

            f = open(sequencer_file, 'rb')
            try:
                sequencer = cPickle.load(f)
                done, last_id = _handle_subcommands(args[0], sequencer)
                _finish(done, last_id)
                return
            finally:
                f.close()

        sequencer = pyrite.sequencer.Sequencer(pyrite.repo)
        head_id = pyrite.repo.get_commit_info('HEAD', [Repo.ID])[Repo.ID]
        sequencer.set_head(head_id)
        done = not in_progress
        if not base:
            pyrite.ui.error_out(_('%s not in progress, nothing to do') % cmd)

        for c in (base, branch, onto):
            if not pyrite.repo.get_commit_info(c):
                raise HelpError(cmd, _('%s does not appear to be a commit') %
                            c)

        end = branch or 'HEAD'
        commits = pyrite.repo.get_history(base, end, limit=-1,
                                data=[Repo.ID, Repo.SUBJECT, Repo.PARENTS])
        message = []
        for commit in reversed([c for c in commits]):
            message.append('pick %s %s\n' % (commit[Repo.ID][:8],
                                           commit[Repo.SUBJECT]))
        message.append('\n\n')
        if interactive:
            msg_onto = onto or head_id[:8]
            extra = [
                _('You are rebasing onto %s\n\n') % msg_onto,
                _('If you empty out this file the operation will be '
                  'cancelled.\n\n'),
                _('You can use any of the following operations...'),
                _('pick'),
                _('edit'),
                _('squash'),
                _('merge'),
                _('mark'),
            ]
            message = pyrite.ui.edit(message, extra, 'pyt-seq-file')
            if not message:
                pyrite.ui.info(_('Nothing to do, rebase cancelled.'))
                return
            message = message.splitlines()

        if pyrite.repo.changed_files():
            raise SequencerDirtyWorkdirError()
        done = False
        if branch:
            pyrite.repo.checkout(branch)
        sequencer.set_branch(pyrite.repo.branch())
        if onto:
            pyrite.repo.move_head_to(onto, True)
        else:
            pyrite.repo.move_head_to(base, True)
        for line in message:
            if not line.strip():
                continue
            sequencer.add(line)
        done, last_id = sequencer.run()
        _finish(done, last_id)

    except UnintializedSequencerError, inst:
        pyrite.ui.error_out('internal error:' + inst.message)

    except SequencerDirtyWorkdirError:
        pyrite.ui.info(_('The working directory has changes.  '
            'The working directory must be clean to \nstart a rebase.\n\n'
            'You can either abandon your current changes by doing '
            '"pyt revert" or you \ncan commit your changes and then go '
            'back and change it later if you desire.'))

    except SequencerMergeNeeded:
        pyrite.ui.info(_('\nOne or more files have conflicting changes.'))
        pyrite.ui.info(_('\nThe following files need resolving'))
        for f in pyrite.repo.list(unresolved=True).keys():
            pyrite.ui.info('..' + f)
        pyrite.ui.info(_('\nRun "pyt resolve" to run a merge program.\n\n'))

    except SequencerError, inst:
        pyrite.ui.error_out(inst.message)

    finally:
        if not done:
            f = open(sequencer_file, 'wb')
            try:
                cPickle.dump(sequencer, f)
            finally:
                f.close()
        else:
            try:
                os.remove(sequencer_file)
            except OSError:
                pass
