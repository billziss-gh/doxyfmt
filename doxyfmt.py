#!/usr/bin/env python
#
# doxyfmt.py
#
# Copyright (c) 2014-2020, Bill Zissimopoulos. All rights reserved.
#
# This file is part of Doxyfmt.
#
# It is licensed under the MIT license. The full license text can be found
# in the License.txt file at the root of this project.

# # doxyfmt(1)
# ============
#
# NAME
# ----
# doxyfmt - extract documentation from source files
#
# SYNOPSIS
# --------
# doxyfmt OPTIONS [file]
#
# DESCRIPTION
# -----------
# The *doxyfmt* utility is a wrapper around *doxygen* that can produce output
# in a variety of formats using a simple template engine.
#
# For information on the source code documentation format accepted by
# *dogygen* and thence *doxyfmt* please refer to the *doxygen*
# documentation online.
#
# PYTHON TEMPLATE LANGUAGE
# ------------------------
# *Doxyfmt* templates are written in the Python Template Language.
# They are essentially Python source code with the addition of a single new
# feature, the *:* construct.
#
# The *:* construct is a shortcut for embedding text to be output in Python
# source. Everything placed after a *:* will be copied to the output, Python
# expressions can also be inserted by using the *${ python expression }*
# construct (similar to shell expansion).
#
# Example:
#
#     : <summary>
#     : <div class="summary">
#     : <h1 class="${elem.tag}-name">${name}</h1>
#     if abst:
#         : <div class="${elem.tag}-abstract">${abst}</div>
#     : </div>
#     : </summary>
#
# DOXYFMT TEMPLATES
# -------------------
# Refer to the bundled templates for examples.
#
# OPTIONS
# -------
#
# COPYRIGHT
# ---------
# (C) 2014-2020 Bill Zissimopoulos

import argparse, os, shutil, subprocess, sys
from glob import glob

sys.dont_write_bytecode = True
import pytempl
import doxylib

def info(s):
    print("%s: %s" % (os.path.basename(sys.argv[0]), s))
def warn(s):
    print("%s: %s" % (os.path.basename(sys.argv[0]), s), file=sys.stderr)
def fail(s, exitcode = 1):
    warn(s)
    sys.exit(exitcode)

def readconf(path):
    conf = {}
    with open(path) as file:
        cont = ""
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.endswith("\\"):
                cont += line[:-1]
                continue
            if cont:
                line = cont + line
                cont = ""
            part = line.split("=", maxsplit=1)
            if 2 != len(part):
                continue
            plus = False
            if part[0].endswith("+"):
                part[0] = part[0][:-1]
                plus = True
            part[0] = part[0].strip()
            part[1] = part[1].strip()
            if plus:
                prev = conf.get(part[0], "")
                if prev:
                    part[1] = prev + " " + part[1]
            conf[part[0]] = part[1]
    return conf

def run():
    path = args.file
    xdir = os.path.join(args.conf["outdir"], "xml")
    conf = readconf(path)
    for k in conf:
        if k.startswith("GENERATE_"):
            conf[k] = "NO"
    for k in args.conf:
        if k == k.upper():
            conf[k] = args.conf[k]
    conf["GENERATE_HTML"] = "NO"
    conf["GENERATE_LATEX"] = "NO"
    conf["GENERATE_RTF"] = "NO"
    conf["GENERATE_MAN"] = "NO"
    conf["GENERATE_DOCBOOK"] = "NO"
    conf["GENERATE_XML"] = "YES"
    conf["XML_PROGRAMLISTING"] = "NO"
    conf["XML_OUTPUT"] = xdir
    doxy = shutil.which("doxygen")
    if not doxy:
        if sys.platform.startswith("win32"):
            doxy = r"C:\Program Files\Doxygen\bin\doxygen.exe"
    os.makedirs(xdir, exist_ok=True)
    subprocess.run(
        [doxy, "-"],
        input="\n".join("%s=%s" % (k, v) for k, v in conf.items()).encode("utf-8"),
        cwd=os.path.dirname(path) or None,
        check=True)
    p = doxylib.parser(os.path.join(xdir, "index.xml"))
    conf.update(args.conf)
    args.template.main(conf, p.index)
    if not args.keep_xml:
        shutil.rmtree(xdir, ignore_errors=True)

def main():
    global args
    progdir = os.path.dirname(sys.argv[0])
    formats = [os.path.basename(f)[:-len(".pyt")]
        for f in glob(os.path.join(os.path.join(progdir, "formats", "*.pyt")))]
    p = argparse.ArgumentParser()
    p.add_argument("-f", dest="format", choices=formats, default="markdown",
        help="output format")
    p.add_argument("-F", dest="template",
        help="format template file (overrides -f)")
    p.add_argument("-c", dest="conflist", action="append", metavar="NAME=VALUE",
        help="set configuration value")
    p.add_argument("-k", dest="keep_xml", action="store_true",
        help="keep doxygen xml files")
    p.add_argument("-o", dest="outdir",
        help="output directory")
    p.add_argument("file", nargs="?", default="Doxyfile")
    args = p.parse_args(sys.argv[1:])
    args.conf = {}
    for i in args.conflist or []:
        p = i.split("=", maxsplit=1)
        if 2 == len(p):
            args.conf[p[0]] = p[1]
        else:
            args.conf[p[0]] = True
    args.conf.setdefault("outdir", args.outdir or ".")
    args.conf["outdir"] = os.path.abspath(args.conf["outdir"])
    if args.template is None:
        args.template = os.path.join(progdir, "formats", args.format + ".pyt")
    args.template = pytempl.template_load(args.template)
    run()

def __entry():
    try:
        main()
    except EnvironmentError as ex:
        fail(ex)
    except subprocess.CalledProcessError as ex:
        fail(ex)
    except KeyboardInterrupt:
        fail("interrupted", 130)

if "__main__" == __name__:
    __entry()
