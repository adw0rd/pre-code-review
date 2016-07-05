#!/usr/bin/env python
# coding: utf-8
"""
Pre Code Review
@requirements pep8, pyflakes
"""

from __future__ import with_statement
import os
import re
import six
import shutil
import subprocess
import sys
import tempfile

IGNORE_FILES = [
    r'\/migrations\/',  # South
    # r'\/sphinxapi\.py',  # Sphinx
]

HANDLERS = {
    'pep8': {'args': ['--ignore=E501']},
    'pyflakes': {},
}


def system(*args, **kwargs):
    kwargs.setdefault('stdout', subprocess.PIPE)
    proc = subprocess.Popen(args, **kwargs)
    out, err = proc.communicate()
    return out


def main(DEBUG=False, ignore_files=[]):
    CURRENT_DIR = os.path.dirname(__file__)

    # Check files only staged
    modified = re.compile('[AM]+\s+(?P<name>.*\.py)$', re.MULTILINE)  # see also MM, UU
    modified_files = system('git', 'status', '--porcelain')
    if six.PY3:
        modified_files = modified_files.decode()
    modified_files = modified.findall(modified_files)
    files = set()
    for file_ in modified_files:
        if not any([ignore.search(file_) for ignore in ignore_files]):
            files.add(file_)
    files = list(files)

    error = False
    for handler in HANDLERS:
        # Create temporary dir (sandbox)
        tempdir = tempfile.mkdtemp()
        for name in files:
            filename = os.path.join(tempdir, name)
            filepath = os.path.dirname(filename)
            if not os.path.exists(filepath):
                os.makedirs(filepath)
            with file(filename, 'w') as f:
                if DEBUG:
                    # Because `git-show` gives only `staged` content,
                    #   and we want to receive the current content of the file, then
                    #   we change directory to the `.git/hooks` and get the absolute
                    #   path to the file
                    out = open(os.path.join(CURRENT_DIR, "..", "..", name), 'r').read()
                else:
                    out = system('git', 'show', ':' + name)
                if handler == "pep8":
                    # For the `pep8` we need convert content to ASCII charset,
                    #   to correctly processed E501 (line too long).
                    # And for pyflakes not worth the hassle, as it complains
                    #   about an invalid utf-8.
                    out = str(out.decode('utf-8').encode('ascii', 'replace'))
                f.write(out)
        try:
            if 'args' in HANDLERS[handler]:
                args = HANDLERS[handler].get('args')
            else:
                args = []
            HANDLERS[handler]['result'] = system(handler, cwd=tempdir, *args + ['.'])
            if HANDLERS[handler]['result']:
                error = True
        except:
            # Windows (exception "WindowsError") swears by pyflakes, so I just ignored.
            pass

        # Cleanup
        shutil.rmtree(tempdir)

    if error is True:
        print ("*" * 33, "\n{:*^33}\n".format(" CODE REVIEW IS FAILED "), "*" * 33)
        print ("Check files:", ", ".join(files))
        for handler in HANDLERS:
            try:
                if HANDLERS[handler]['result']:
                    print (handler + ":")
                    print (HANDLERS[handler]['result'])
            except KeyError:
                pass
        # If errors exist, then stop the commit
        sys.exit(1)

if __name__ == '__main__':
    IGNORE_FILES_REGEXP = [re.compile(regexp) for regexp in IGNORE_FILES]
    try:
        DEBUG = sys.argv[1] == "--debug"
    except IndexError:
        DEBUG = False
    main(DEBUG, ignore_files=IGNORE_FILES_REGEXP)
