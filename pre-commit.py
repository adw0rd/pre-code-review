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


def system(*args, **kwargs):
    kwargs.setdefault('stdout', subprocess.PIPE)
    proc = subprocess.Popen(args, **kwargs)
    out, err = proc.communicate()
    return out

def main(DEBUG=False):
    CURRENT_DIR = os.path.dirname(__file__)
    # Проверяем тольrо staged файлы
    modified = re.compile('[AM]+\s+(?P<name>.*\.py)$', re.MULTILINE)  # see also MM, UU
    files = system('git', 'status', '--porcelain')
    files = modified.findall(files)
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
                    #   а нам надо текущее состояние файла:
                    # XXX: Refactor me!
                    out = open(os.path.join(CURRENT_DIR, "..", "..", "..", name), 'r').read()
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
        print "*" * 33
        print "*****", "CODE REVIEW IS FAILED", "*****"
        print "*" * 33
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
    try:
        DEBUG = sys.argv[1] == "--debug"
    except IndexError:
        DEBUG = False
    main(DEBUG)
