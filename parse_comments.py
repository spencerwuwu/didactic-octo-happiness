#!/usr/bin/env python3

import sys
import os
import logging
import json

from optparse import OptionParser
from optparse import OptionGroup
from string import Template

BLACK_LIST = []

class CommentObj:
    def __init__(self, index=0):
        self.line_no = index
        self.content = None

    def __str__(self):
        return "%d %s" % (self.line_no, self.content)

    def serialize(self):
        return {"line_no": self.line_no, "content": self.content}

class FuncObj:
    def __init__(self):
        self.line_no = 0
        self.file_name = None
        self.func_name = None
        self.pre_comments = []
        self.inner_comments = []

    def sanitize_newline(self, string):
        return string.replace("\n", " ")

    def serialize_comments(self, flag="pre"):
        ret = []
        if flag == "pre":
            s_list = self.pre_comments
        else:
            s_list = self.inner_comments

        for comment in s_list:
            ret.append(comment.serialize())
        return ret

    def __str__(self):
        template = Template("""
============ $func_name ============
$file_name
$line_no
## Pre-comment:
$pre_comment
## Inner-comment:
$inner_comment
====================================
""")
        prop = dict()
        prop["file_name"] = self.file_name
        prop["line_no"] = self.line_no
        prop["func_name"] = self.func_name
        prop["pre_comment"] = ";\n".join(str(cmt) for cmt in self.pre_comments)
        prop["inner_comment"] = ";\n".join(str(cmt) for cmt in self.inner_comments)
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
        elif "static struct" in line or "typedef struct" in line or line.startswith("struct"):
            # Also skip structs
            possible_start = None
            n_index = skip_area(src_f, index)
            continue
        else:
            break

    if possible_start is not None:
        return possible_start
    return index
""" 
" Skip comments
"""
def skip_comments(src_f, index):
    n_index = index
    while n_index < len(src_f):
        index = n_index
        n_index += 1
        if "*/" in src_f[index]:
            break
    return n_index

"""
" Skip parts like struct {xxx}
"""
def skip_area(src_f, index):
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
        elif line.startswith("//"):
            continue
        elif line.startswith("@"):
            continue
        else:
            if func_started == 0:
                func_started = 1
                # Parse function declaration
                if "{" not in line:
                    found = 0
                    while True and n_index < len(src_f):
                        index = n_index
                        n_index += 1
                        n_line = src_f[index].strip()
                        line += (" " + n_line)
                        if "{" in line:
                            found = 1
                            break
                if "/*" in line:
                    n_index = skip_comments(src_f, index)
                elif "//" in line:
                    continue
            bracket_hier += line.count("{")
            bracket_hier -= line.count("}")

    return n_index


"""
" Get the function name from function declaration
"""
def _get_func_name(func_declare):
    tokens = func_declare.split(" ")

    # If in the form "int main (..."
    for index in range(len(tokens)):
        if tokens[index].startswith("("):
            i = index - 1
            while len(tokens[i]) == 0 and i >= 0:
                i -= 1
            return tokens[i]

    for index in range(len(tokens)):
        if "(" in tokens[index]:
            return tokens[index].split("(")[0]


"""
" Get the contents of comments
"""
def _collect_comments(src_f, index):
    comment = CommentObj(index + 1)
    n_index = index + 1
    line = src_f[index].strip()
    content = line.split("/*", 1)[1].strip()
    if "*/" in content:
        content = content.rsplit("*/", 1)[0]
        comment.content = content
        return n_index, comment

    while index < len(src_f):
        index = n_index
        n_index += 1
        line = src_f[index].strip()
        if line.startswith("* "):
            line = line.split("* ", 1)[1].strip()
        if "*/" in line:
            content = "%s\n%s" % (content, line.split("*/", -1)[0])
            break
        else:
            content += ("\n" + line)

    comment.content = content
    return n_index, comment


"""
" Returns a FuncObj object
"""
def _handle_func_body(src_f, index, log):
    func_obj = FuncObj()
    n_index = index
    bracket_hier = 0
    func_started = 0
    skip = 0
    # return at seeing the last }
    while n_index < len(src_f) and not (func_started != 0 and bracket_hier == 0):
        index = n_index
        n_index += 1
        line = src_f[index].strip()

        if len(line) == 0:
            continue
        elif line.startswith("#"):
            n_index = _skip_inlines(src_f, index, n_index)
        elif line.startswith("@"):
            continue
        elif line.startswith("/*"):
            n_index, comment = _collect_comments(src_f, index)
            if func_started == 0:
                func_obj.pre_comments.append(comment)
            else:
                func_obj.inner_comments.append(comment)
        elif line.startswith("//"):
            comment = line[2:]
            comment_obj = CommentObj(index + 1)
            comment_obj.content = comment
            if bracket_hier == 0:
                func_obj.pre_comments.append(comment_obj)
            else:
                func_obj.inner_comments.append(comment_obj)
        else:
            if func_started == 0:
                func_started = 1
                # Parse function declaration
                func_obj.line_no = index + 1
                if "{" not in line:
                    found = 0
                    while True and n_index < len(src_f):
                        index = n_index
                        n_index += 1
                        n_line = src_f[index].strip()
                        line += (" " + n_line)
                        if "{" in line:
                            found = 1
                            break
                    if found == 0:
                        return n_index, func_obj
                src_f[index] = line
                if "(" not in line \
                   or " inline " in line\
                   or "typedef struct" in line\
                   or "static struct" in line:
                    skip = 1
                else:
                    func_obj.func_name = _get_func_name(line)
                if "/*" in line:
                    if skip != 1:
                        n_index, comment = _collect_comments(src_f, index)
                        func_obj.inner_comments.append(comment)
                    else:
                        n_index = skip_comments(src_f, index)
                elif "//" in line:
                    if skip != 1:
                        comment = CommentObj(index + 1)
                        comment.content = line.split("//", 1)[1]
                        func_obj.inner_comments.append(comment)
            bracket_hier += line.count("{")
            bracket_hier -= line.count("}")

    return n_index, func_obj


"""
" Entry of function_name - comments parser
"""
def parse_func_comment(src, log):
    if src in BLACK_LIST:
        return []
    try:
        with open(src) as fd:
            src_f = fd.read()
            src_f = src_f.splitlines()
    except:
        print('oops')
        return []
    next_index = _handle_header(src_f)
    log.info("Starts parsing %s" % src)
    log.debug("From line: %d" % next_index)

    func_objs = []
    while next_index < len(src_f):
        next_index, func_obj = _handle_func_body(src_f, next_index, log)
        if func_obj.func_name is None:
            continue
        func_obj.file_name = src
        func_objs.append(func_obj)
        log.debug(func_obj)

    return func_objs


"""
" Write the results into json
"""

def write2_json(json_file, func_objs):
    rets = []
    for obj in func_objs:
        ret = dict()
        ret["file_name"] = obj.file_name
        ret["line_no"] = obj.line_no
        ret["func_name"] = obj.func_name
        ret["pre_comments"] = obj.serialize_comments("pre")
        ret["inner_comments"] = obj.serialize_comments("inner")
        rets.append(ret)
    with open(json_file, "w") as fd:
        json.dump(rets, fd)


def main():
    usage = "usage: %prog [options] <path to file or directory>"
    parser = OptionParser(usage=usage)

    # Loggine configuration
    logging_group = OptionGroup(parser, "Logging Configuration")
    logging_group.add_option("-d", "--debug", dest='debug', action="store_true", help="Enable debug logging")
    parser.add_option_group(logging_group)

    # JSON configuration
    json_group = OptionGroup(parser, "JSON Configuration")
    json_group.add_option("-s", "--save", dest='json_file', action="store", help="Store to a .json file")
    parser.add_option_group(json_group)

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
        for src in files:
            if src.endswith(".c") or src.endswith(".cpp") or src.endswith(".y") or src.endswith(".h"):
                func_objs += parse_func_comment(src, log)
    else:
        parser.error("%s not exists" % args[0])
        sys.exit(1)

    if options.json_file is not None:
        write2_json(options.json_file, func_objs)

if __name__ == '__main__':
    main()
