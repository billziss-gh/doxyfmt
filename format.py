# format.py
#
# Copyright (c) 2014-2020, Bill Zissimopoulos. All rights reserved.
#
# This file is part of Doxyover.
#
# It is licensed under the MIT license. The full license text can be found
# in the License.txt file at the root of this project.

import os

section_titles = {
}

class format(object):
    section_titles = {
        "user-defined": "",
        "public-type": "",
        "public-func": "",
        "public-attrib": "",
        "public-slot": "",
        "signal": "",
        "dcop-func": "",
        "property": "",
        "event": "",
        "public-static-func": "",
        "public-static-attrib": "",
        "protected-type": "",
        "protected-func": "",
        "protected-attrib": "",
        "protected-slot": "",
        "protected-static-func": "",
        "protected-static-attrib": "",
        "package-type": "",
        "package-func": "",
        "package-attrib": "",
        "package-static-func": "",
        "package-static-attrib": "",
        "private-type": "",
        "private-func": "",
        "private-attrib": "",
        "private-slot": "",
        "private-static-func": "",
        "private-static-attrib": "",
        "friend": "",
        "related": "",
        "define": "Macros",
        "prototype": "",
        "typedef": "Typedefs",
        "enum": "",
        "func": "Functions",
        "var": "",
    }

    def __init__(self, index, outdir, fileext):
        self.index = index
        self.outdir = outdir
        self.fileext = fileext
        self.language = ""

    def setoutfile(self, file):
        pass
    def title(self, text, heading):
        pass
    def name(self, kind, text, desc):
        pass
    def syntax(self, text):
        pass
    def parameters(self, parl):
        pass
    def returns(self, retv):
        pass
    def members(self, list):
        pass
    def description(self, desc):
        pass
    def event(self, elem, ev):
        pass

    def __title(self, text, heading):
        if text:
            self.title(text, heading)
    def __name(self, kind, text, desc):
        if text:
            self.name(kind, text, desc)
    def __syntax(self, text):
        if text:
            self.syntax(text)
    def __parameters(self, parl):
        if parl.T:
            self.parameters(parl)
    def __returns(self, retv):
        if retv.T:
            self.returns(retv)
    def __members(self, list):
        if list:
            self.members(list)
    def __description(self, desc):
        if not desc.T:
            return
        self.__parameters(desc[".//parameterlistE"])
        self.__returns(desc[".//simplesect[@kind='return']E"])
        self.description(desc)

    def memberdef(self, elem):
        self.event(elem, "begin")
        self.__name(elem.kindA, elem.nameS, elem.briefdescriptionE)
        self.__syntax(elem.definitionS + elem.argsstringS)
        self.__description(elem.detaileddescriptionE)
        self.event(elem, "end")

    def sectiondef(self, elem):
        self.event(elem, "begin")
        text = elem.headerS
        if not text:
            text = self.section_titles.get(elem.kindA, "")
        self.__title(text, 2)
        self.__description(elem.descriptionE)
        for memb in elem.memberdefL:
            self.memberdef(memb)
        self.event(elem, "end")

    def innerclass_section(self, elem):
        list = elem.innerclassL
        if list:
            self.__title("Structures", 2)
            for incl in list:
                lang = self.language
                comp = self.index[incl.refidA].element()
                self.compounddef(comp)
                self.language = lang

    def compounddef(self, elem):
        self.language = elem.languageA
        self.event(elem, "begin")
        if "file" == elem.kindA:
            text = elem.titleS
            if not text:
                text = elem.locationE.fileA
                if not text or os.path.isabs(text):
                    text = elem.compoundnameS
            self.__title(text, 1)
        else:
            self.__name(elem.kindA, elem.compoundnameS, elem.briefdescriptionE)
        self.__description(elem.detaileddescriptionE)
        self.innerclass_section(elem)
        for sect in elem.sectiondefL:
            self.sectiondef(sect)
        self.event(elem, "end")

    def main(self):
        for i in self.index:
            comp = self.index[i].element()
            if "file" != comp.kindA:
                continue
            file = comp.locationE.fileA
            if not file:
                file = elem.compoundnameS
            file = file.replace("_", "__").replace(":", "").replace("/", "_").replace("\\", "_")
            with open(os.path.join(self.outdir, file + self.fileext), "w") as ofile:
                self.setoutfile(ofile)
                self.compounddef(comp)
