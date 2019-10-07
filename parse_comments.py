#!/usr/bin/env python3.7

import sys
import os

from optparse import OptionParser
from optparse import OptionGroup

class FuncObj():
    def __init__(self):
        func_name = None
        pre_comments = []
        inner_comments = []
        bracket_hier = 0

def _skip_header(src_f):
    index = 0
    n_index = index
    while n_index < len(src_f):
        index = n_index
        n_index += 1
        line = src_f[index]

        if len(line) == 0:
            continue

    return index

def _parse_func_comment(src):
    obj = FuncObj()
    with open(src) as fd:
        src_f = fd.read()
        src_f = src_f.splitlines()
    start_index = _still_header(src_f)

def parse_func_comment(src):
    if src.endswith(".c") or src.endswith(".cpp"):
        print(src)
        _parse_func_comment(src)


def main():
    usage = "usage: %prog [options] <path to file or directory>"
    parser = OptionParser(usage=usage)

    (options, args) = parser.parse_args()
    if len(args) == 0:
        parser.error("Missing file or directory")
        sys.exit(1)

    if os.path.isfile(args[0]):
        parse_func_comment(args[0])
    elif os.path.isdir(args[0]):
        files = sorted([os.path.join(root, file) 
                        for root, dirs, files in os.walk(args[0]) for file in files])
        for src_file in files:
            parse_func_comment(src_file)
    else:
        parser.error("%s not exists" % args[0])
        sys.exit(1)

if __name__ == '__main__':
    main()
