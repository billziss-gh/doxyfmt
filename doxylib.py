# doxylib.py
#
# Copyright (c) 2014-2020, Bill Zissimopoulos. All rights reserved.
#
# This file is part of Doxyfmt.
#
# It is licensed under the MIT license. The full license text can be found
# in the License.txt file at the root of this project.

import os, re, xml.etree.ElementTree as ET
from itertools import chain

def itermaptext(elem, escape, textmap, tailmap, filter = None):
    g = elem.tag
    f = textmap.get(g)
    t = elem.text or ""
    if f:
        if callable(f):
            f = f(elem)
        if "%T" == f[:2]:
            f = f[2:]
            t = t and t.lstrip()
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
        if f:
            if callable(f):
                f = f(e)
            if "%T" == f[:2]:
                f = f[2:]
                t = t and t.lstrip()
            yield f % escape(t)
        elif t:
            yield escape(t)

class element:
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

class compound:
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

class parser:
    def __init__(self, path):
        self.indexDir = os.path.dirname(path)
        self.index = {}
        with open(path) as file:
            for e in ET.parse(file).findall("compound"):
                self.index[e.get("refid")] = compound(self, element(e))
    def parse_compound(self, id):
        with open(os.path.join(self.indexDir, id + ".xml")) as file:
            return element(ET.parse(file).find("compounddef[@id='" + id + "']"))

# Use ostream to squash multiple blank lines. Note that ostream
# will *NOT* write the last line if it does not end in newline (\n).
class ostream:
    def __init__(self, strm):
        self.__strm = strm
        self.__tail = ""
        self.__nlct = 0
    def write(self, s):
        for l in s.splitlines(True):
            if self.__tail:
                l = self.__tail + l
                self.__tail = ""
            if "\n" != l[-1:]:
                self.__tail = l
                break
            t = l.lstrip(" ")
            if "\n" != t:
                self.__nlct = 1
            else:
                self.__nlct += 1
                if 2 < self.__nlct:
                    continue
                l = t
            self.__strm.write(l)

class format:
    section_titles = {
        # DoxSectionKind
        "user-defined": "",
        "public-type": "",
        "public-func": "Methods",
        "public-attrib": "Fields",
        "public-slot": "",
        "signal": "",
        "dcop-func": "",
        "property": "",
        "event": "",
        "public-static-func": "Static Methods",
        "public-static-attrib": "Static Fields",
        "protected-type": "",
        "protected-func": "Protected Methods",
        "protected-attrib": "Protected Fields",
        "protected-slot": "",
        "protected-static-func": "Protected Static Methods",
        "protected-static-attrib": "Protected Static Fields",
        "package-type": "",
        "package-func": "Package Methods",
        "package-attrib": "Package Fields",
        "package-static-func": "Package Static Methods",
        "package-static-attrib": "Package Static Fields",
        "private-type": "",
        "private-func": "Private Methods",
        "private-attrib": "Private Fields",
        "private-slot": "",
        "private-static-func": "Private Static Methods",
        "private-static-attrib": "Private Static Fields",
        "friend": "",
        "related": "",
        "define": "Macros",
        "prototype": "",
        "typedef": "Typedefs",
        "enum": "Enums",
        "func": "Functions",
        "var": "",
        # internal
        "innerclass": "Data Structures",
    }
    kind_titles = {
        # DoxCompoundKind
        "class": "class",
        "struct": "struct",
        "union": "union",
        "interface": "interface",
        "protocol": "protocol",
        "category": "category",
        "exception": "",
        "service": "",
        "singleton": "",
        "module": "",
        "type": "",
        "file": "",
        "namespace": "",
        "group": "",
        "page": "",
        "example": "",
        "dir": "",

        # DoxMemberKind
        "define": "",
        "property": "",
        "event": "",
        "variable": "",
        "typedef": "typedef",
        "enum": "enum",
        "function": "%s()",
        "signal": "",
        "prototype": "",
        "friend": "",
        "dcop": "",
        "slot": "",
        "interface": "",
        "service": "",
        # internal
        "FUNCTION-MACRO": "%s()",
        "OBJECT-MACRO": "",
    }
    anon_re = re.compile(r"@[0-9]")
    summary_filter = description_filter = {
        "para": lambda e: (e.find("parameterlist") is None) and
            e.find("simplesect[@kind='copyright']") is None,
    }

    def __init__(self, conf, index):
        self.conf = conf
        self.index = index
        self.outdir = conf["outdir"]
        self.fileext = conf["fileext"]
        self.language = ""
        self.copytext = ""
        self.stack = []
        self.__level = 1
        self.__typedef_set = set()

    def depth(self, tag):
        depth = 0
        for e in self.stack:
            if tag == e.N:
                depth += 1
        return depth

    def reset(self, file):
        pass

    def escape(self, text):
        return text
    def maptext(self, elem, filter = None):
        return elem.Maptext(self.escape, None, None, filter)

    def heading(self, text, level):
        pass
    def summary(self, elem):
        pass
    def copyright(self, text):
        pass
    def name(self, kind, text, desc):
        pass
    def syntax(self, text):
        pass
    def parameters(self, elst):
        pass
    def returns(self, elem):
        pass
    def enumvalues(self, elst):
        pass
    def description(self, elem):
        pass
    def event(self, elem, ev):
        pass

    def __heading(self, text):
        if text:
            self.heading(text, self.__level + self.depth("sectiondef"))
    def __summary(self, elem, elem2 = None):
        if None != elem2:
            desc = ET.Element("description")
            desc.extend(elem.XMLElement.findall("para"))
            desc.extend(elem2.XMLElement.findall("para"))
            elem = element(desc)
        if elem.T:
            self.summary(elem)
    def __copyright(self, text):
        if text:
            self.copyright(text)
    def __name(self, kind, text, desc):
        if text:
            kind = self.kind_titles.get(kind, "")
            if self.anon_re.match(text):
                text = ""
            if "%s" in kind:
                text = kind % text
            else:
                text = " ".join([kind, text])
            self.name(kind, text, desc)
    def __syntax(self, text):
        if text:
            self.syntax(text)
    def __parameters(self, elst):
        if elst.T:
            self.parameters(elst)
    def __returns(self, elem):
        if elem.T:
            self.returns(elem)
    def __enumvalues(self, elst):
        if elst:
            self.enumvalues(elst)
    def __description(self, elem):
        if elem.T:
            self.__parameters(elem[".//parameterlistE"])
            self.__returns(elem[".//simplesect[@kind='return']E"])
            if self.maptext(elem, self.description_filter).strip():
                self.description(elem)
    def __event(self, elem, ev):
        if "begin" == ev:
            self.stack.append(elem)
            self.event(elem, ev)
        elif "end" == ev:
            self.event(elem, ev)
            self.stack.pop()

    def memberdef(self, elem):
        if elem.kindA in ["typedef"]:
            e = elem[".//ref[@kindref='compound']E"]
            if e:
                self.__typedef_set.add(e.refidA)
                self.compounddef(self.index[e.refidA].element(), elem.nameS, elem.definitionT)
                return

        self.__event(elem, "begin")
        if elem.kindA in ["function"]:
            self.__name(elem.kindA, elem.nameS, elem.briefdescriptionE)
            self.__syntax(elem.definitionT + elem.argsstringT)
            self.__description(elem.detaileddescriptionE)
        elif elem.kindA in ["variable"]:
            self.__name(elem.kindA, elem.nameS, elem.briefdescriptionE)
            self.__syntax(elem.definitionT)
            self.__description(elem.detaileddescriptionE)
        elif elem.kindA in ["enum"]:
            self.__name(elem.kindA, elem.nameS, elem.briefdescriptionE)
            self.__enumvalues(elem.enumvalueL)
            self.__description(elem.detaileddescriptionE)
        elif elem.kindA in ["typedef"]:
            self.__name(elem.kindA, elem.nameS, elem.briefdescriptionE)
            self.__syntax(elem.definitionT)
            self.__description(elem.detaileddescriptionE)
        elif elem.kindA in ["define"]:
            if elem.paramE:
                kind = "FUNCTION-MACRO"
            else:
                kind = "OBJECT-MACRO"
            self.__name(kind, elem.nameS, elem.briefdescriptionE)
            param = ""
            if elem.paramE:
                param = "(" + ", ".join(e.T for e in elem[".//defnameL"]) + ")"
            self.__syntax("#define " + elem.nameT + param)
            self.__description(elem.detaileddescriptionE)
        else:
            raise NotImplementedError(elem.kindA)
        self.__event(elem, "end")

    def sectiondef(self, elem):
        count = 0
        for e in elem.innerclassL:
            if e.refidA not in self.__typedef_set:
                count += 1
        for e in elem.memberdefL:
            count += 1
        if 0 == count:
            return

        self.__event(elem, "begin")
        text = elem.headerT
        if not text:
            text = self.section_titles.get(elem.kindA, "")
        self.__heading(text)
        self.__summary(elem.descriptionE)
        contents = []
        for e in elem.innerclassL:
            if e.refidA not in self.__typedef_set:
                contents.append(self.index[e.refidA].element())
        for e in elem.memberdefL:
            contents.append(e)
        order = self.conf.get("order", "source")
        if "doxygen" == order:
            pass
        elif "alpha" == order:
            contents.sort(key = lambda e: e.compoundnameS or e.nameS)
        else: # "source"
            contents.sort(key = lambda e: "%s:%10s:%10s" %
                (e.locationE.fileA, e.locationE.lineA, e.locationE.columnA))
        for e in contents:
            if "compounddef" == e.N:
                self.compounddef(e)
            elif "memberdef" == e.N:
                self.memberdef(e)
        self.__event(elem, "end")

    def compounddef(self, elem, override_name=None, override_definition=None):
        # massage compounddef so that innerclass appears inside sectiondef
        e = elem.XMLElement
        incl = e.findall("innerclass")
        if incl:
            for i in incl:
                e.remove(i)
            sect = ET.Element("sectiondef", { "kind": "innerclass" })
            sect.extend(incl)
            e.append(sect)

        self.__event(elem, "begin")
        if elem.kindA in ["file"]:
            text = elem.titleT
            if not text:
                text = elem.locationE.fileA
                if not text or os.path.isabs(text):
                    text = elem.compoundnameS
            self.__heading(text)
            self.__summary(elem.briefdescriptionE, elem.detaileddescriptionE)
            for sect in elem.sectiondefL:
                self.sectiondef(sect)
            self.__copyright(self.copytext)
        elif elem.kindA in ["struct", "union"]:
            self.__name(elem.kindA, override_name or elem.compoundnameS, elem.briefdescriptionE)
            if override_definition:
                self.__syntax(override_definition)
            self.__description(elem.detaileddescriptionE)
            for sect in elem.sectiondefL:
                self.sectiondef(sect)
        else:
            raise NotImplementedError(elem.kindA)
        self.__event(elem, "end")

    def main(self):
        for i in self.index:
            comp = self.index[i].element()
            if "file" != comp.kindA:
                continue
            self.language = comp.languageA
            self.copytext = comp[".//simplesect[@kind='copyright']E"]["T"]
            file = comp.locationE.fileA
            if not file:
                file = elem.compoundnameS
            file = file.replace("_", "__").replace(":", "").replace("/", "_").replace("\\", "_")
            with open(os.path.join(self.outdir, file + self.fileext), "w", newline="\n") as ofile:
                self.reset(ofile)
                self.compounddef(comp)
