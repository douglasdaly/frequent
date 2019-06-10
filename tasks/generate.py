# -*- coding: utf-8 -*-
"""
Tasks to generate various items.

Changelog generation code adapted from the pipenv project:
    https://github.com/pypa/pipenv/blob/master/tasks/release.py

Contributor email code borrowed from the pip project:
    https://github.com/pypa/pip/blob/master/tasks/generate.py

"""
#
#   Imports
#
import datetime
import glob
import os
import re
import sys
import tempfile

import invoke

from .helpers import TODO_CMD
from .helpers import VERSION
from .helpers import convert_rst_to_markdown
from .helpers import create_change_item
from .helpers import ctx_run
from .helpers import get_todos
from .helpers import insert_text
from .helpers import log as hlog
from .helpers import print_block


#
#   Helpers
#

def log(msg, level=None):
    hlog(msg, name='generate', level=level)


def run(ctx, cmd, draft):
    return ctx_run(ctx, cmd, draft=draft, log_fn=log)


def create_docs_changelog(new_entry, write=True):
    """Creates a new changelog rst file for the docs"""
    base_dir = 'docs/changelogs/'
    curr_files = glob.glob(os.path.join(base_dir, 'changelog_*.rst'))
    curr_files = [os.path.basename(x) for x in curr_files]

    p = re.compile(r"^changelog_(\d+)\.rst$")
    indices = sorted([p.match(f).groups()[0] for f in curr_files])
    if indices:
        next_idx = int(indices[-1])+1
    else:
        next_idx = 1
    new_file = os.path.join(base_dir, 'changelog_%s.rst' % next_idx)

    contents = new_entry.split('\n')
    version, date = (x.strip() for x in contents[0].split('-', maxsplit=1))
    version = version[1:-1]
    date = datetime.datetime.strptime(date, "%Y-%m-%d").strftime('%B %d, %Y')

    new_contents = list()
    new_contents.append(version)
    new_contents.append("=" * len(version) + '\n')
    new_contents.append(':Release: %s' % date)
    new_contents.extend(contents[2:])
    new_contents = '\n'.join(new_contents)

    if write:
        with open(new_file, 'w') as fout:
            fout.write(new_contents)
        return new_file
    return new_contents


def changelog_rst_to_md(ctx, path):
    """Convert a CHANGELOG.rst to a CHANGELOG.md file"""
    content = ctx.run(
        'pandoc %s -f rst -t commonmark' % path, hide=True
    ).stdout.strip()

    content = re.sub(
        r"([^\n]+)\n?\s+\[[\\]+(#\d+)\]\(https://github\.com/douglasdaly/[\w\-]+/issues/\d+\)",  # noqa
        r"\1 \2", content, flags=re.MULTILINE
    )

    return convert_rst_to_markdown(content)


#
#   Tasks
#

@invoke.task
def authors(ctx, draft=False, branch='master'):
    """Generates the AUTHORS file"""
    _, tmp = tempfile.mkstemp(suffix='.csv')
    log('Getting contributions')
    ctx.run(f'git fame --log ERROR --branch {branch} --format csv > {tmp}',
            encoding="utf-8", hide=True)
    fame = open(tmp, 'r').readlines()
    os.remove(tmp)

    if not fame[0].startswith('Author'):
        log('Errors occurred while getting authors:', level='ERROR')
        errs = []
        for ln in fame:
            if ln.startswith('Author'):
                break
            errs.append(ln)
        print_block('\n'.join(errs))
        sys.exit(1)

    log('Getting contributor information')
    r = ctx.run('git log --use-mailmap --format"=%aN <%aE>"',
                encoding="utf-8", hide=True)
    author_emails = {}
    seen_authors = set()
    for author in r.stdout.splitlines():
        author = author.strip().split()
        email = None if '@' not in author[-1] else author[-1]
        author = ' '.join([x for x in author if '@' not in x])
        if email and author.lower() not in seen_authors:
            seen_authors.add(author.lower())
            author_emails[author] = email

    print(fame)

    log('Getting contributor names')
    auths = []
    for ln in fame[1:]:
        ln = ln.strip()
        if not ln:
            break
        t_auth = ln.split(',')[0]
        if t_auth.lower() not in ('douglas daly',):
            if t_auth in author_emails:
                t_auth += " %s" % author_emails[t_auth]
            auths.append(t_auth.strip())

    with open('AUTHORS', 'r') as fin:
        in_contents = fin.readlines()

    out_contents = []
    for ln in in_contents:
        ln = ln.strip('\n')
        if ln == 'Contributors:':
            break
        out_contents.append(ln)

    if auths:
        out_contents.append('Contributors:\n')
        for t_auth in auths:
            out_contents.append('    - %s' % t_auth)

    out_contents = '\n'.join(out_contents)
    if draft:
        log('Would generate AUTHORS:')
        print_block(out_contents)
    else:
        with open('AUTHORS', 'w') as fout:
            fout.write(out_contents)
        log('Generated AUTHORS file')

    run(ctx, 'git add AUTHORS', draft)
    return


@invoke.task
def todos(ctx, draft=False):
    """Compiles todos/done.txt file contents into Towncrier items"""
    log('Loading completed todo items')
    t_done = get_todos('todos/done.txt')
    if not t_done:
        log('No completed todos')
        return
    else:
        log('Loaded %s completed todos' % len(t_done))

    run(ctx, '%s report' % TODO_CMD, draft)
    run(ctx, 'git add todos/report.txt', draft)

    cnt = 0
    for i, t in enumerate(t_done):
        t_words = t.strip().split()
        t_date = t_words[1].replace('-', '')
        t_context = None
        t_ref = None
        n_str = list()
        for w in t_words[2:]:
            if w.startswith('+'):
                t_context = w[1:].lower()
            elif w.startswith('@'):
                try:
                    t_ref = int(w[1:])
                except ValueError:
                    log("Invalid @context issue number given: %s" % w,
                        level='error')
                    sys.exit(1)
            else:
                n_str.append(w)
        n_str = ' '.join(n_str)

        if t_context is None:
            log('No context given, assuming: misc', level='info')
            t_context = 'misc'
        if t_context in ('add', 'change', 'remove', 'fix', 'deprecate'):
            if not t_context.endswith('e'):
                t_context += 'e'
            if not t_context.endswith('d'):
                t_context += 'd'
        elif t_context not in ('security', 'misc'):
            log('Unknown context given, skipping: %s' % t_context,
                level='warn')
            continue

        if t_ref is None:
            t_ref = 't%s%s%s' % (t_context[0].upper(), t_date, i+1)

        if draft:
            t_file = 'changes/%s.%s' % (t_ref, t_context)
            log('Would create %s: %s' % (t_file, n_str))
        else:
            t_file = create_change_item(t_ref, t_context, n_str)
            log('Created %s: %s' % (os.path.basename(t_file), n_str))
        run(ctx, 'git add %s' % t_file, draft)
        cnt += 1

    if cnt > 0:
        tmp_str = '%s new items' % cnt
        if draft:
            tmp_str = 'Would have added %s' % tmp_str
        else:
            tmp_str = 'Added %s' % tmp_str
        log(tmp_str)

    if draft:
        log('Would clear: todos/done.txt')
    else:
        log('Clearing file: todos/done.txt')
        open('todos/done.txt', 'w').close()
    run(ctx, 'git add todos/done.txt', draft)
    run(ctx, 'git add todos/todo.txt', draft)

    return


@invoke.task
def changelog(ctx, draft=False):
    """Generates the CHANGELOG file"""
    todos(ctx, draft=draft)
    rel_ver = ctx.run('git rev-parse --abbrev-ref HEAD', hide=True).stdout
    if rel_ver.startswith('release') or rel_ver.startswith('hotfix'):
        rel_ver = rel_ver.split('/')[-1].strip('v')
    else:
        rel_ver = VERSION

    curr_md = open('CHANGELOG.md', 'r').read()
    if draft:
        ctx.run(f"towncrier --draft --version {rel_ver} > CHANGELOG.draft.rst",
                hide=True)
        log('Would clear changes/*')
        md_content = changelog_rst_to_md(ctx, 'CHANGELOG.draft.rst')
        new_md = insert_text(curr_md, md_content, "[//]: # (BEGIN)")
        rst_content = open('CHANGELOG.draft.rst', 'r').read()
        os.remove('CHANGELOG.draft.rst')
        log('Would create new docs/changelog file:')
        print_block(create_docs_changelog(rst_content, write=False))

    else:
        if os.path.exists('CHANGELOG.draft.md'):
            os.remove('CHANGELOG.draft.md')
            ctx.run('git add CHANGELOG.draft.md')
        ctx.run(f'towncrier --yes --version {rel_ver}', hide=True)
        ctx.run('git add changes/')
        md_content = changelog_rst_to_md(ctx, 'CHANGELOG.rst')
        new_md = insert_text(curr_md, md_content, "[//]: # (BEGIN)")
        with open('CHANGELOG.md', 'w') as fout:
            fout.writelines(new_md)
        ctx.run('git add CHANGELOG.md')
        rst_content = open('CHANGELOG.rst', 'r').read()
        os.remove('CHANGELOG.rst')
        ctx.run('git add CHANGELOG.rst')
        doc_file = create_docs_changelog(rst_content)
        ctx.run('git add %s' % doc_file)

    return

