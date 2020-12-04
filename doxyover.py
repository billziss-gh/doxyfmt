#!/usr/bin/env python
#
# doxyover.py
#
# Copyright (c) 2014-2020, Bill Zissimopoulos. All rights reserved.
#
# This file is part of Doxyover.
#
# It is licensed under the MIT license. The full license text can be found
# in the License.txt file at the root of this project.

# # doxyover(1)
# ============
#
# NAME
# ----
# doxyover - extract documentation from source files
#
# SYNOPSIS
# --------
# doxyover OPTIONS [file]
#
# DESCRIPTION
# -----------
# The *doxyover* utility is a wrapper around *doxygen* that can produce output
# in a variety of formats using a simple template engine.
#
# For information on the source code documentation format accepted by
# *dogygen* and thence *doxyover* please refer to the *doxygen*
# documentation online.
#
# PYTHON TEMPLATE LANGUAGE
# ------------------------
# *Doxyover* templates are written in the Python Template Language.
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
# DOXYOVER TEMPLATES
# -------------------
# Refer to the bundled templates for examples.
#
# OPTIONS
# -------
#
# COPYRIGHT
# ---------
# (C) 2014-2020 Bill Zissimopoulos

import argparse, os, shutil, subprocess, sys, xml.etree.ElementTree as ET
from itertools import chain
from glob import glob

sys.dont_write_bytecode = True
import pytempl

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
            part = line.split("=", 2)
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

class element(object):
    def __init__(self, XMLElement):
        if XMLElement is None:
            XMLElement = ET.Element("")
        self.XMLElement = XMLElement
    def __str__(self):
        return str(self.XMLElement)
    def __getitem__(self, name):
        selc = name[-1:]
        if selc == "@":
            name = name[:-1]
            if name:
                return self.XMLElement.get(name)
            else:
                return ""
        elif selc == "%":
            name = name[:-1]
            if name:
                return [element(e) for e in self.XMLElement.findall(name)]
            else:
                return [self]
        elif selc == "!":
            name = name[:-1]
            if name:
                return element(self.XMLElement.find(name))
            else:
                return self
        elif selc == "$":
            name = name[:-1]
            if name:
                attr = self.XMLElement.get(name)
                if attr is not None:
                    return attr
                return "".join(
                    chain.from_iterable(e.itertext() for e in self.XMLElement.findall(name)))
            else:
                return "".join(self.XMLElement.itertext())
        else:
            if name:
                attr = self.XMLElement.get(name)
                if attr is not None:
                    return attr
                return [element(e) for e in self.XMLElement.findall(name)]
            else:
                return [self]

class compound(object):
    def __init__(self, parser, ref):
        self.parser = parser
        self.cref = ref
        self.cdef = None
    def __str__(self):
        return str(self.cref)
    def element(self):
        if self.cdef is None:
            self.cdef = self.parser.parseCompound(self.cref["refid@"])
        return self.cdef

class parser(object):
    def __init__(self, path):
        self.indexDir = os.path.dirname(path)
        self.index = {}
        with open(path) as file:
            for e in ET.parse(file).findall("compound"):
                self.index[e.get("refid")] = compound(self, element(e))
    def parseCompound(self, id):
        with open(os.path.join(self.indexDir, id + ".xml")) as file:
            return element(ET.parse(file).find("compounddef[@id='" + id + "']"))

def run():
    path = args.file
    conf = readconf(path)
    for k in conf:
        if k.startswith("GENERATE_"):
            conf[k] = "NO"
    conf["GENERATE_HTML"] = "NO"
    conf["GENERATE_LATEX"] = "NO"
    conf["GENERATE_XML"] = "YES"
    doxy = shutil.which("doxygen")
    if not doxy:
        if sys.platform.startswith("win32"):
            doxy = r"C:\Program Files\Doxygen\bin\doxygen.exe"
    cdir = os.path.dirname(path)
    subprocess.run(
        [doxy, "-"],
        input="\n".join("%s=%s" % (k, v) for k, v in conf.items()).encode("utf-8"),
        cwd=cdir or None,
        check=True)
    xdir = os.path.join(cdir or ".", conf.get("OUTPUT_DIRECTORY", ""), conf.get("XML_OUTPUT", ""))
    p = parser(os.path.join(xdir, "index.xml"))
    args.template.main(p.index)

def main():
    global args
    progdir = os.path.dirname(sys.argv[0])
    formats = [os.path.basename(f)[:-len(".pyt")]
        for f in glob(os.path.join(os.path.join(progdir, "formats", "*.pyt")))]
    p = argparse.ArgumentParser()
    p.add_argument("-f", dest="format", choices=formats, default="html",
        help="output format")
    p.add_argument("-F", dest="template",
        help="format template file (overrides -f)")
    p.add_argument("file", nargs="?", default="Doxyfile")
    args = p.parse_args(sys.argv[1:])
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
