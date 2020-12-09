# doxyfmt.py
#
# Copyright (c) 2014-2020, Bill Zissimopoulos. All rights reserved.
#
# This file is part of Doxyover.
#
# It is licensed under the MIT license. The full license text can be found
# in the License.txt file at the root of this project.

import os, re, xml.etree.ElementTree as ET

# Use doxystream to squash multiple blank lines. Note that doxystream
# will *NOT* write the last line if it does not end in newline (\n).
class doxystream(object):
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

class doxyfmt(object):
    section_titles = {
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
    anon_re = re.compile(r"@[0-9]")
    description_filter = {
        "para": lambda e: (e.find("parameterlist") is None) and
            e.find("simplesect[@kind='copyright']") is None,
    }

    def __init__(self, index, outdir, fileext):
        self.index = index
        self.outdir = outdir
        self.fileext = fileext
        self.language = ""
        self.copytext = ""
        self.stack = []
        self.__level = 1

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
    def __copyright(self, text):
        if text:
            self.copyright(text)
    def __name(self, kind, text, desc):
        if text:
            if self.anon_re.match(text):
                text = "anonymous " + kind
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
            if self.maptext(elem, self.description_filter):
                self.description(elem)
    def __event(self, elem, ev):
        if "begin" == ev:
            self.stack.append(elem)
            self.event(elem, ev)
        elif "end" == ev:
            self.event(elem, ev)
            self.stack.pop()

    def memberdef(self, elem):
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
        elif elem.kindA in ["define"]:
            self.__name(elem.kindA, elem.nameS, elem.briefdescriptionE)
            param = ""
            if elem.paramE:
                param = "(" + ", ".join(e.T for e in elem[".//defnameL"]) + ")"
            self.__syntax("#define " + elem.nameT + param)
            self.__description(elem.detaileddescriptionE)
        elif elem.kindA in ["typedef"]:
            pass # ignore
        else:
            raise NotImplementedError(elem.kindA)
        self.__event(elem, "end")

    def sectiondef(self, elem):
        self.__event(elem, "begin")
        text = elem.headerT
        if not text:
            text = self.section_titles.get(elem.kindA, "")
        self.__heading(text)
        self.__description(elem.descriptionE)
        for e in elem.innerclassL:
            self.compounddef(self.index[e.refidA].element())
        for e in elem.memberdefL:
            self.memberdef(e)
        self.__event(elem, "end")

    def compounddef(self, elem):
        # massage compounddef so that innerclass appears inside sectiondef
        e = elem.XMLElement
        incl = e.findall("innerclass")
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
            self.__description(elem.briefdescriptionE)
            self.__description(elem.detaileddescriptionE)
            for sect in elem.sectiondefL:
                self.sectiondef(sect)
            self.__copyright(self.copytext)
        elif elem.kindA in ["struct", "union"]:
            self.__name(elem.kindA, elem.compoundnameS, elem.briefdescriptionE)
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
            with open(os.path.join(self.outdir, file + self.fileext), "w") as ofile:
                self.reset(ofile)
                self.compounddef(comp)
