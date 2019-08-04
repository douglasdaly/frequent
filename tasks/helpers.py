# -*- coding: utf-8 -*-
"""
Helper functions for tasks.
"""
import os
import subprocess

from frequent import __version__


#
#   Constants
#

VERSION = __version__


#
#   Functions
#

def convert_rst_to_markdown(content):
    """Convert an rst file to markdown"""
    ret = list()
    curr = content.splitlines(keepends=False)
    for i in range(len(curr)):
        line = curr[i].strip('>').strip()
        if line.startswith('#'):
            line = '#%s' % line
        ret.append(line)
    return '\n' + '\n'.join(ret) + '\n'


def create_change_item(reference, context, message):
    """Creates a new Towncrier change file"""
    file = os.path.join('changes', '%s.%s' % (reference, context))
    with open(file, 'w') as fout:
        fout.write(message)
    return file


def log(msg, name=None, level=None):
    """Prints output to the screen"""
    ret = ''
    if name:
        ret += "[%s] " % name.lower()
    if level:
        ret += "(%s) " % level.upper()
    print(ret + msg)
    return


def ctx_run(ctx, cmd, draft=False, log_fn=log):
    """Helper to either run cmd or just display it"""
    if draft:
        log_fn('Would run: %s' % cmd)
        return
    return ctx.run(cmd)


def get_alias_cmd(alias):
    """Gets the command for the given alias (if any)"""
    res = subprocess.run(['/bin/bash', '-i', '-c', 'alias %s' % alias],
                         capture_output=True)
    if res.returncode == 0:
        s_out = res.stdout.decode('utf-8').strip()
        return s_out.split('=')[-1].strip('"').strip("'")
    return alias


def get_todos(file, context=None, project=None):
    """Gets the todo items from file"""
    if not file.endswith('txt'):
        file = '%s.txt' % file
    if not file.startswith('todos'):
        file = os.path.join('todos/', file)

    with open(file, 'r') as fin:
        contents = fin.readlines()

    return contents


def insert_text(original, new, after):
    """Inserts the new text into the original"""
    ret = list()
    for line in original.split('\n'):
        ret.append(line)
        if line == after:
            for new_line in new.split('\n'):
                ret.append(new_line)
    return '\n'.join(ret)


def print_block(text):
    """Prints a block of text"""
    print('\n  ----- START -----')
    for line in text.split('\n'):
        print('  %s' % line)
    print('  -----  END  -----\n')
    return


#
#   Variables
#

TODO_CMD = get_alias_cmd(os.getenv('TODO_CMD', 'todo.sh'))

