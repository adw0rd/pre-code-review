#!/usr/bin/env python
# coding: utf-8
"""
Commit Message Review

Format:
<issue Title> [<PREFIX>-<ID>] <Comment>

Example:
git commit -m "Неполадки в системе приема наличности [XXX-4242] Была исправлена проблема с \
заглушкой для обменного сервиса (невозможно было установить соединение с удаленным сервером).\
Добавили временный кеш и несколько дополнительных бекендов + балансировка"
"""

import sys
import re
from types import FunctionType

def check_task_tracking_identificator(message):
    issue_prefix = "XXX"
    frmt = '[{project_id}-{issue_number}]'
    frmt_data = {'project_id': issue_prefix, 'issue_number': 4242}
    id_re = re.compile('\[\#?' + issue_prefix + '-\d+\]', re.MULTILINE)
    if not id_re.search(message):
        return "Wrong Issue ID! Use format: {frmt}, example: {example}".format(
            frmt=frmt, example=frmt.format(**frmt_data)), False
    else:
        return "All right!", True

def main(message):
    error = False
    handlers = {check_task_tracking_identificator: ''}
    for handler in handlers:
        if isinstance(handler, FunctionType):
            handlers[handler], status = handler(message)
            if status is False:
                error = True
    if error is True:
        print "*" * 34, "\n{:*^34}\n".format(" CHECK COMMIT IS FAILED "), "*" * 34
        for handler in handlers:
            print ">", handler.__name__ + ":"
            print ">>", handlers[handler]
        sys.exit(1)

if __name__ == "__main__":
    message_filename = sys.argv[1]
    message_file = open(message_filename, 'r')
    message_text = message_file.read()
    main(message_text)
