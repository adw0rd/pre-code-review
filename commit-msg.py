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

HANDLERS = {
    'check_task_tracking_identificator': {},
    # 'check_title_and_comment_content': {}
}

ISSUE_PREFIX = "PROJ"
ISSUE_ID_FORMAT = '[{project_id}-{issue_number}]'
ISSUE_ID_FORMAT_HELP_KWARGS = {'project_id': ISSUE_PREFIX, 'issue_number': 1027}


def check_task_tracking_identificator(message):
    id_re = re.compile('\[\#?[A-Z]{2,5}-\d+\]', re.MULTILINE)
    if not id_re.search(message):
        return "Wrong Issue ID! Use format: {frmt}, example: {example}".format(
            frmt=ISSUE_ID_FORMAT, example=ISSUE_ID_FORMAT.format(**ISSUE_ID_FORMAT_HELP_KWARGS)), False
    else:
        return "All right!", True


def main(message):
    error = False
    for handler_name in HANDLERS:
        handler = globals()[handler_name]
        if isinstance(handler, FunctionType):
            HANDLERS[handler_name]['result'], status = handler(message)
            if status is False:
                error = True
    if error is True:
        print ("*" * 34, "\n{:*^34}\n".format(" CHECK COMMIT IS FAILED "), "*" * 34)
        for handler_name in HANDLERS:
            print ("> {}:".format(handler_name))
            print (">>", HANDLERS[handler_name]['result'])
        sys.exit(1)

if __name__ == "__main__":
    message_filename = sys.argv[1]
    message_file = open(message_filename, 'r')
    message_text = message_file.read()
    main(message_text)
