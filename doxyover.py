#!/usr/bin/env python
#
# Copyright (c) 2014-2020, Bill Zissimopoulos. All rights reserved.
#
# Redistribution  and use  in source  and  binary forms,  with or  without
# modification, are  permitted provided that the  following conditions are
# met:
#
# 1.  Redistributions  of source  code  must  retain the  above  copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions  in binary  form must  reproduce the  above copyright
# notice,  this list  of conditions  and the  following disclaimer  in the
# documentation and/or other materials provided with the distribution.
#
# 3.  Neither the  name  of the  copyright  holder nor  the  names of  its
# contributors may  be used  to endorse or  promote products  derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY  THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND  ANY EXPRESS OR  IMPLIED WARRANTIES, INCLUDING, BUT  NOT LIMITED
# TO,  THE  IMPLIED  WARRANTIES  OF  MERCHANTABILITY  AND  FITNESS  FOR  A
# PARTICULAR  PURPOSE ARE  DISCLAIMED.  IN NO  EVENT  SHALL THE  COPYRIGHT
# HOLDER OR CONTRIBUTORS  BE LIABLE FOR ANY  DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL,  EXEMPLARY,  OR  CONSEQUENTIAL   DAMAGES  (INCLUDING,  BUT  NOT
# LIMITED TO,  PROCUREMENT OF SUBSTITUTE  GOODS OR SERVICES; LOSS  OF USE,
# DATA, OR  PROFITS; OR BUSINESS  INTERRUPTION) HOWEVER CAUSED AND  ON ANY
# THEORY  OF LIABILITY,  WHETHER IN  CONTRACT, STRICT  LIABILITY, OR  TORT
# (INCLUDING NEGLIGENCE  OR OTHERWISE) ARISING IN  ANY WAY OUT OF  THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# doxyover(1)
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
        self.XMLElement = XMLElement
    def __str__(self):
        return str(self.XMLElement)
    def __getitem__(self, name):
        if name.endswith("$"):
            name = name[:-1]
            sret = True
        else:
            sret = False
        if name:
            attr = self.XMLElement.get(name)
            if attr is not None:
                return attr
            list = self.XMLElement.findall(name)
        else:
            list = [self.XMLElement]
        if sret:
            return "".join(chain.from_iterable(e.itertext() for e in list))
        else:
            return [element(e) for e in list]

class compound(object):
    def __init__(self, parser, ref):
        self.parser = parser
        self.cref = ref
        self.cdef = None
    def __str__(self):
        return str(self.cref)
    def element(self):
        if self.cdef is None:
            self.cdef = self.parser.parseCompound(self.cref["refid$"])
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
