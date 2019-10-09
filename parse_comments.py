#!/usr/bin/env python3.7

import sys
import os
import logging
import csv

from optparse import OptionParser
from optparse import OptionGroup
from string import Template

class FuncObj:
    def __init__(self):
        self.func_name = None
        self.pre_comment = None 
        self.inner_comments = []

    def sanitize_newline(self, string):
        return string.replace("\n", " ")

    def get_pre_comment(self):
        if self.pre_comment is not None:
            return self.sanitize_newline(self.pre_comment)
        else:
            return "" 

    def get_inner_comment(self):
        return " ".join(self.sanitize_newline(cmt) for cmt in self.inner_comments)

    def __str__(self):
        template = Template("""
============ $func_name ============
## Pre-comment:
$pre_comment
## Inner-comment:
$inner_comment
====================================
""")
        prop = dict()
        prop["func_name"] = self.func_name
        if self.pre_comment is not None:
            prop["pre_comment"] = self.pre_comment
        else:
            prop["pre_comment"] = "" 
        prop["inner_comment"] = "\n".join(cmt for cmt in self.inner_comments)
        return template.substitute(prop)

"""
" This function skips the inline macros
" e.g. 
" # define xxx \    // skipped
"         xxxx      // skipped
"""
def _skip_inlines(src_f, index, n_index):
    line = src_f[index].strip()
    if line.endswith("\\"):
        index = n_index
        n_index += 1
        while src_f[index].strip().endswith("\\") and index < len(src_f):
            index = n_index
            n_index += 1
    return n_index

"""
" Skips the #include <xxx.h>.... part
"""
def _handle_header(src_f):
    index = 0
    n_index = index
    possible_start = None
    while n_index < len(src_f):
        index = n_index
        n_index += 1
        line = src_f[index].strip()

        if len(line) == 0:
            continue
        elif line.startswith("#"):
            line = line[1:].strip()
            if line.startswith("include"):
                possible_start = None
            elif line.startswith("define"):
                possible_start = None
                n_index = _skip_inlines(src_f, index, n_index)
            else:
                continue
        elif line.startswith("/*"):
            possible_start = index
            while index < len(src_f) and not src_f[index].strip().endswith("*/"):
                index = n_index
                n_index += 1
            continue
        elif line.startswith("//"):
            if possible_start is not None:
                possible_start = index
            continue
        else:
            break

    if possible_start is not None:
        return possible_start
    return index


"""
" Get the function name from function declaration
"""
def _get_func_name(func_declare):
    tokens = func_declare.split(" ")

    # If in the form "int main (..."
    for index in range(len(tokens)):
        if tokens[index].startswith("("):
            return tokens[index - 1]

    for index in range(len(tokens)):
        if "(" in tokens[index]:
            return tokens[index].split("(")[0]


"""
" Get the contents of comments
"""
def _collect_comments(src_f, index):
    n_index = index + 1
    line = src_f[index].strip()
    content = line.split("/*", 1)[1]
    if "*/" in content:
        content = content.rsplit("*/", 1)[0]
        return n_index, content

    while index < len(src_f):
        index = n_index
        n_index += 1
        line = src_f[index].strip()
        if line.endswith("*/"):
            content = "%s\n%s" % (content, line.split("*/", -1)[0])
            break
        else:
            content += ("\n" + line)

    return n_index, content


"""
" Returns a FuncObj object
"""
def _handle_func_body(src_f, index, log):
    func_obj = FuncObj()
    n_index = index
    bracket_hier = 0
    func_started = 0
    # return at seeing the last }
    while n_index < len(src_f) and not (func_started != 0 and bracket_hier == 0):
        index = n_index
        n_index += 1
        line = src_f[index].strip()

        if len(line) == 0:
            continue
        elif line.startswith("#"):
            n_index = _skip_inlines(src_f, index, n_index)
        elif line.startswith("/*"):
            n_index, comment = _collect_comments(src_f, index)
            if func_started == 0:
                if func_obj.pre_comment is None:
                    func_obj.pre_comment = comment
                else:
                    func_obj.pre_comment += ("\n" + comment)
            else:
                func_obj.inner_comments.append(comment)
        elif line.startswith("//"):
            comment = line[2:]
            if bracket_hier == 0:
                if func_obj.pre_comment is None:
                    func_obj.pre_comment = comment
                else:
                    func_obj.pre_comment += ("\n" + comment)
            else:
                func_obj.inner_comments.append(comment)
        else:
            if func_started == 0:
                func_started = 1
                # Parse function declaration
                if "{" not in line:
                    while True:
                        index = n_index
                        n_index += 1
                        n_line = src_f[index].strip()
                        line += (" " + n_line)
                        if "{" in line:
                            break
                func_obj.func_name = _get_func_name(line)
                if "/*" in line:
                    n_index, comment = _collect_comments(src_f, index)
                    func_obj.inner_comments.append(comment)
                elif "//" in line:
                    func_obj.inner_comments.append(header.split("//", 1)[1])
            bracket_hier += line.count("{")
            bracket_hier -= line.count("}")

    return n_index, func_obj


"""
" Sub-entry of function_name - comments parser
"""
def _parse_func_comment(src, log):
    with open(src) as fd:
        src_f = fd.read()
        src_f = src_f.splitlines()
    next_index = _handle_header(src_f)
    log.debug("Starts parsing %s" % src)
    log.debug("From line: %d" % next_index)

    func_objs = []
    while next_index < len(src_f):
        next_index, func_obj = _handle_func_body(src_f, next_index, log)
        if func_obj.func_name is None:
            continue
        func_objs.append(func_obj)
        log.debug(func_obj)

    return func_objs

"""
" Entry of function_name - comments parser
"""
def parse_func_comment(src, log):
    if src.endswith(".c") or src.endswith(".cpp") or src.endswith(".y") or src.endswith(".h"):
        return _parse_func_comment(src, log)


"""
" Write the results into csv
"""
def write2_csv(csv_file, func_objs):
    fields = ["func_name", "pre_comment", "inner_comment"]
    rows = []
    for obj in func_objs:
        rows.append(
            {"func_name": obj.func_name, 
             "pre_comment": obj.get_pre_comment(), 
             "inner_comment": obj.get_inner_comment()
            })
    with open(csv_file, "w") as csvfile:
        csvwriter = csv.DictWriter(csvfile, fieldnames=fields)
        csvwriter.writeheader()
        csvwriter.writerows(rows)


def main():
    usage = "usage: %prog [options] <path to file or directory>"
    parser = OptionParser(usage=usage)

    # Loggine configuration
    logging_group = OptionGroup(parser, "Logging Configuration")
    logging_group.add_option("-d", "--debug", dest='debug', action="store_true", help="Enable debug logging")
    parser.add_option_group(logging_group)

    # CSV configuration
    csv_group = OptionGroup(parser, "CSV Configuration")
    csv_group.add_option("-s", "--save", dest='csv_file', action="store", help="Store to a .csv file")
    parser.add_option_group(csv_group)

    (options, args) = parser.parse_args()
    if len(args) == 0:
        parser.error("Missing file or directory")
        sys.exit(1)

    if options.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.basicConfig(level=log_level, 
                        format='  %(name)s\t%(levelname)s\t%(message)s')

    log = logging.getLogger("func_comment")

    if os.path.isfile(args[0]):
        func_objs = parse_func_comment(args[0], log)
    elif os.path.isdir(args[0]):
        files = sorted([os.path.join(root, file) 
                        for root, dirs, files in os.walk(args[0]) for file in files])
        func_objs = []
        for src_file in files:
            func_objs += parse_func_comment(src_file, log)
    else:
        parser.error("%s not exists" % args[0])
        sys.exit(1)

    if options.csv_file is not None:
        write2_csv(options.csv_file, func_objs)

if __name__ == '__main__':
    main()
