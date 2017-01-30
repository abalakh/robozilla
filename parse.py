#!/usr/bin/env python
from __future__ import print_function

import os
import sys
import fnmatch

from handlers.base import BZIsOpen, BZDecorator
from bz import BZReader
from writer import BugReportWriter

_current_path = os.path.dirname(os.path.realpath(__file__))

_output_name = 'output'

_default_output_path = os.path.join(_current_path, _output_name)

_file_pattern = '*.py'


_handlers = [BZIsOpen, BZDecorator]
_writer = BugReportWriter
_bz_reader = BZReader


def _parse_file(file_path):
    with open(file_path) as fr:
        line_number = 0
        for line in fr:
            for handler in _handlers:
                if handler.is_string_present(line):
                    bug_ids = handler.re_retrieve(line)
                    for bug_id in bug_ids:
                        yield bug_id, file_path, line_number, handler.__name__

            line_number += 1


def _get_files(directory):
    for name in os.listdir(directory):
        full_path = os.path.join(directory, name)
        if os.path.isdir(full_path):
            for file_path in _get_files(full_path):
                yield file_path
        elif os.path.isfile(full_path):
            if fnmatch.fnmatch(full_path, _file_pattern):
                yield full_path


def main(source_path):
    bz_reader = _bz_reader()
    bug_report_writer = BugReportWriter()
    bug_report_writer.start()
    for file_path in _get_files(source_path):
        for data in _parse_file(file_path):
            bug_id, bug_file_path, line_number, handler_name = data
            bug_data = bz_reader.get_bug_data(bug_id)
            bug_report_writer.write(
                bug_id, bug_data, handler_name, bug_file_path, line_number)
    bug_report_writer.finish()

if __name__ == '__main__':
    print(__file__)
    print(_current_path)
    print(_default_output_path)
    args = sys.argv
    if len(sys.argv) > 1:
        scan_dir = sys.argv[1]
    else:
        print('please supply dir to scan')
        print('usage: parse.py dir_to_parse_path')
        sys.exit(2)

    main(scan_dir)