#!/usr/bin/env python3

import sys
import os
import logging
import json

from subprocess import Popen, PIPE

def _run_cmd(cmd, log):
    log.info(cmd)
    try:
        process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        out, err = process.communicate()
        if process.returncode != 0:
            log.info("Returned with code: %d" % process.returncode)
            log.info(err.decode())
            print("Command '%s' failed with %d" % (cmd, process.returncode))
            return False
    except Exception:
        print("Exception")
        logger.error("Exception:", exc_info=True)
        return False
    return True


def make_configure(proj_name, log):
    build_path = "to_compile/%s/" % proj_name
    cmd = "cd %s && ./configure && CFLAGS=\"-g\" CXXFLAGS=\"-g\" make" % build_path
    if not _run_cmd(cmd, log):
        return "failed", build_path
    return "built", build_path


def make_autogen(proj_name, log):
    return "not-support", ""


def make_make(proj_name, log):
    build_path = "to_compile/%s" % proj_name
    make_cmd = "cd %s && CXXFLAGS=\"-g\" CFLAGS=\"-g\" make" % build_path
    if not _run_cmd(make_cmd, log):
        return "failed", build_path
    return "built", build_path


def make_cmake(proj_name, log):
    build_path = "to_compile/%s/%s-build" % (proj_name, proj_name)
    mkdir_cmd = "mkdir %s" % build_path
    if not _run_cmd(mkdir_cmd, log):
        return "failed", build_path
    cmake_cmd = "cd %s && cmake -E env CXXFLAGS=\"-g\" CFLAGS=\"-g\" cmake .. && make" % build_path
    if not _run_cmd(cmake_cmd, log):
        return "failed", build_path
    return "built", build_path


def make_custom(proj_name, log):
    build_path = "to_compile/%s/src/" % proj_name
    cmd = "cd %s && ./configure CFLAGS=\'-g\' CXXFLAGS=\'-g\' && make" % build_path
    if not _run_cmd(cmd, log):
        return "failed", build_path
    return "built", build_path


def make_all(log, prev_data=None):
    entries = os.listdir("to_compile")
    if prev_data is None:
        compile_results = {}
    else:
        compile_results = prev_data

    for entry in entries:
        log.info("=================")
        log.info("%s" % entry)
        log.info("-----------------")
        if compile_results and \
           entry in compile_results:
            if compile_results[entry]["status"] == "built":
                print("%s finished" % entry)
                log.info("%s finished" % entry)
                continue
            elif compile_results[entry]["status"] == "failed":
                print("%s failed before, passed" % entry)
                log.info("%s failed before, passed" % entry)
                continue
        result = {}
        result["proj_name"] = entry
        files = os.listdir("to_compile/%s" % entry)
        if entry == "gprolog-1.4.5":
            result["type"] = "conf"
            print("*conf: %s" % entry)
            status, compiled_dir = make_custom(entry, log)
            result["status"] = status
            result["dir"] = compiled_dir
            continue
        if "configure" in files:
            result["type"] = "conf"
            print("conf : %s" % entry)
            status, compiled_dir = make_configure(entry, log)
            result["status"] = status
            result["dir"] = compiled_dir
        elif "Makefile" in files:
            result["type"] = "make"
            print("make : %s" % entry)
            status, compiled_dir = make_make(entry, log)
            result["status"] = status
            result["dir"] = compiled_dir
        elif "CMakeLists.txt" in files:
            result["type"] = "cmake"
            print("cmake: %s" % entry)
            status, compiled_dir = make_cmake(entry, log)
            result["status"] = status
            result["dir"] = compiled_dir
        elif "autogen.sh" in files:
            result["type"] = "auto"
            print("auto: %s" % entry)
            status, compiled_dir = make_autogen(entry, log)
            result["status"] = status
            result["dir"] = compiled_dir
        else:
            result["type"] = "unknown"
            log.info("cannot compile %s" % entry)
            print("%s gg" % entry)
            status, compiled_dir = (None, None)
            result["status"] = status
            result["dir"] = compiled_dir

        compile_results[entry] = result
        with open("compile_log.json", "w") as fd:
            json.dump(compile_results, fd)
    return compile_results


def main():
    logging.basicConfig(filename="compile.log", level=logging.INFO, 
                        format='  %(name)s\t%(levelname)s\t%(message)s')

    log = logging.getLogger("compile_func")

    with open("compile_log.json", "r") as fd:
        data = fd.read()
        if len(data) > 0:
            prev_data = json.loads(data)
        else:
            prev_data = None

    rets = make_all(log, prev_data)
    with open("compile_log.json", "w") as fd:
        json.dump(rets, fd)
        

if __name__ == '__main__':
    main()
