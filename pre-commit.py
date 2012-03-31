#!/usr/bin/env python
# coding: utf-8
"""
Pre Code Review
@requirements pep8, pyflakes
"""

from __future__ import with_statement
import os
import re
import shutil
import subprocess
import sys
import tempfile

IGNORE_FILES = [
    r'\/migrations\/',  # South
]

def system(*args, **kwargs):
    kwargs.setdefault('stdout', subprocess.PIPE)
    proc = subprocess.Popen(args, **kwargs)
    out, err = proc.communicate()
    return out

def main(DEBUG=False, ignore_files=[]):
    CURRENT_DIR = os.path.dirname(__file__)
    # Проверяем только staged файлы
    modified = re.compile('[AM]+\s+(?P<name>.*\.py)$', re.MULTILINE)  # see also MM, UU
    modified_files = system('git', 'status', '--porcelain')
    modified_files = modified.findall(modified_files)

    files = set()
    for ignore in ignore_files:
        for file_ in modified_files:
            if not ignore.search(file_):
                files.add(file_)
    files = list(files)

    handlers = {
        'pep8': {'args': ['--ignore=E501']},
        'pyflakes': {},
    }
    error = False

    for handler in handlers:
        # Для файлов делаем временную директорию,
        # в этой песочнице они и будут проверяться
        tempdir = tempfile.mkdtemp()
        for name in files:
            filename = os.path.join(tempdir, name)
            filepath = os.path.dirname(filename)
            if not os.path.exists(filepath):
                os.makedirs(filepath)
            with file(filename, 'w') as f:
                if DEBUG:
                    # Так как git show отдает только staged содержимое,
                    #   а нам надо текущее состояние файла, то выходим
                    #   из .git/hooks и получаем полный путь до файла
                    out = open(os.path.join(CURRENT_DIR, "..", "..", name), 'r').read()
                else:
                    out = system('git', 'show', ':' + name)
                if handler == "pep8":
                    # Для pep8 конвертируем в ASCII, чтобы он корректно
                    # обрабатывал E501 (line too long). А для pyflakes не стоит
                    # этого делать, так как он ругается о неправильном utf-8
                    out = str(out.decode('utf-8').encode('ascii', 'replace'))
                f.write(out)
        try:
            if 'args' in handlers[handler]:
                args = handlers[handler].get('args')
            else:
                args = []
            handlers[handler]['result'] = system(handler, cwd=tempdir, *args + ['.'])
            if handlers[handler]['result']:
                error = True
        except:
            # Windows (exception WindowsError) ругается на pyflakes, поэтому
            # просто игнорим. Однако на WindowsError ругается сам pyflakes:
            # undefined name 'WindowsError', если вы не из под Windows
            pass
        # Удаляем песочницу
        shutil.rmtree(tempdir)

    if error is True:
        print "*" * 33, "\n{:*^33}\n".format(" CODE REVIEW IS FAILED "), "*" * 33
        print "Check files:", files
        for handler in handlers:
            try:
                if handlers[handler]['result']:
                    print handler + ":"
                    print handlers[handler]['result']
            except KeyError:
                pass
        # Если всетаки имеем ошибки, то прерываем коммит
        sys.exit(1)

if __name__ == '__main__':
    IGNORE_FILES_REGEXP = [re.compile(regexp) for regexp in IGNORE_FILES]
    try:
        DEBUG = sys.argv[1] == "--debug"
    except IndexError:
        DEBUG = False
    main(DEBUG, ignore_files=IGNORE_FILES_REGEXP)
