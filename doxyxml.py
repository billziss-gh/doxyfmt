# doxyxml.py
#
# Copyright (c) 2014-2020, Bill Zissimopoulos. All rights reserved.
#
# This file is part of Doxyover.
#
# It is licensed under the MIT license. The full license text can be found
# in the License.txt file at the root of this project.

import os, xml.etree.ElementTree as ET
from itertools import chain

def itermaptext(elem, escape, textmap, tailmap, filter = None):
    g = elem.tag
    f = textmap.get(g)
    t = elem.text or ""
    t = t and t.strip()
    if f:
        if callable(f):
            f = f(elem)
        yield f % escape(t)
    elif t:
        yield escape(t)
    for e in elem:
        g = e.tag
        if filter:
            c = filter.get(g, True)
            if callable(c):
                c = c(e)
            if not c:
                continue
        yield from itermaptext(e, escape, textmap, tailmap, filter)
        f = tailmap.get(g)
        t = e.tail or ""
        t = t and t.strip()
        if f:
            if callable(f):
                f = f(e)
            yield f % escape(t)
        elif t:
            yield escape(t)

class element(object):
    def __init__(self, XMLElement):
        if XMLElement is None:
            XMLElement = ET.Element("")
        self.XMLElement = XMLElement
    def __str__(self):
        return str(self.XMLElement)
    def __bool__(self):
        return "" != self.XMLElement.tag
    def __getitem__(self, name):
        return self.__getattr__(name)
    def __getattr__(self, name):
        conv = name[-1:]
        name = name[:-1]
        if conv == "A":
            if name:
                return self.XMLElement.get(name)
            else:
                return ""
        elif conv == "E":
            if name:
                return element(self.XMLElement.find(name))
            else:
                return self
        elif conv == "L":
            if name:
                return [element(e) for e in self.XMLElement.findall(name)]
            else:
                return [self]
        elif conv == "N":
            if name:
                XMLElement = self.XMLElement.find(name)
                return XMLElement.tag if XMLElement is not None else ""
            else:
                return self.XMLElement.tag
        elif conv == "S" or conv == "T":
            if name:
                attr = self.XMLElement.get(name)
                if attr is not None:
                    return attr
                result = "".join(
                    chain.from_iterable(e.itertext() for e in self.XMLElement.findall(name)))
            else:
                result = "".join(self.XMLElement.itertext())
            return result if conv == "S" else result.strip()
        else:
            raise AttributeError
    def Maptext(self, escape, textmap, tailmap, filter = None):
        if "" == self.XMLElement.tag:
            return ""
        escape = escape or (lambda t: t)
        textmap = textmap or {}
        tailmap = tailmap or {}
        return "".join(itermaptext(self.XMLElement, escape, textmap, tailmap, filter))

class compound(object):
    def __init__(self, parser, ref):
        self.parser = parser
        self.cref = ref
        self.cdef = None
    def __str__(self):
        return str(self.cref)
    def element(self):
        if self.cdef is None:
            self.cdef = self.parser.parse_compound(self.cref.refidA)
        return self.cdef

class parser(object):
    def __init__(self, path):
        self.indexDir = os.path.dirname(path)
        self.index = {}
        with open(path) as file:
            for e in ET.parse(file).findall("compound"):
                self.index[e.get("refid")] = compound(self, element(e))
    def parse_compound(self, id):
        with open(os.path.join(self.indexDir, id + ".xml")) as file:
            return element(ET.parse(file).find("compounddef[@id='" + id + "']"))
