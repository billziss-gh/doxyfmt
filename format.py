# format.py
#
# Copyright (c) 2014-2020, Bill Zissimopoulos. All rights reserved.
#
# This file is part of Doxyover.
#
# It is licensed under the MIT license. The full license text can be found
# in the License.txt file at the root of this project.

import os, re

section_titles = {
}

class format(object):
    section_titles = {
        "user-defined": "",
        "public-type": "",
        "public-func": "Methods",
        "public-attrib": "Data Members",
        "public-slot": "",
        "signal": "",
        "dcop-func": "",
        "property": "",
        "event": "",
        "public-static-func": "Static Methods",
        "public-static-attrib": "Static Data Members",
        "protected-type": "",
        "protected-func": "Protected Methods",
        "protected-attrib": "Protected Data Members",
        "protected-slot": "",
        "protected-static-func": "Protected Static Methods",
        "protected-static-attrib": "Protected Static Data Members",
        "package-type": "",
        "package-func": "Package Methods",
        "package-attrib": "Package Data Members",
        "package-static-func": "Package Static Methods",
        "package-static-attrib": "Package Static Data Members",
        "private-type": "",
        "private-func": "Private Methods",
        "private-attrib": "Private Data Members",
        "private-slot": "",
        "private-static-func": "Private Static Methods",
        "private-static-attrib": "Private Static Data Members",
        "friend": "",
        "related": "",
        "define": "Macros",
        "prototype": "",
        "typedef": "Typedefs",
        "enum": "Enums",
        "func": "Functions",
        "var": "",
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
        self.detailed = []

    def setoutfile(self, file):
        pass
    def title(self, text, heading):
        pass
    def copyright(self, text):
        pass
    def name(self, text, desc):
        pass
    def syntax(self, text):
        pass
    def parameters(self, parl):
        pass
    def returns(self, retv):
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
            if self.anon_re.match(text):
                text = "anonymous " + kind
            self.name(text, desc)
    def __copyright(self, text):
        if text:
            self.copyright(text)
    def __syntax(self, text):
        if text:
            self.syntax(text)
    def __enumvalues(self, enml):
        if enml:
            self.detailed.append(False)
            for elem in enml:
                self.__name("enum", elem.nameS, elem.briefdescriptionE)
            self.detailed.pop()
    def __parameters(self, parl):
        if parl.T:
            self.parameters(parl)
    def __returns(self, retv):
        if retv.T:
            self.returns(retv)
    def __description(self, desc):
        if not desc.T:
            return
        self.__parameters(desc[".//parameterlistE"])
        self.__returns(desc[".//simplesect[@kind='return']E"])
        if desc.Maptext(None, None, None, self.description_filter):
            self.description(desc)
    def __event(self, elem, ev):
        if "begin" == ev:
            self.detailed.append(
                (elem.N == "compounddef" and elem.kindA in ["class", "struct", "union"]) or
                (elem.N == "memberdef" and elem.kindA in ["define", "enum", "typedef", "function"]))
            self.event(elem, ev)
        elif "end" == ev:
            self.event(elem, ev)
            self.detailed.pop()
    def isdetailed(self):
        return self.detailed and self.detailed[-1]

    def memberdef(self, elem):
        self.__event(elem, "begin")
        if self.isdetailed():
            self.__name(elem.kindA, elem.nameS, elem.briefdescriptionE)
            self.__syntax(elem.definitionS + elem.argsstringS)
            self.__enumvalues(elem.enumvalueL)
            self.__description(elem.detaileddescriptionE)
        else:
            self.__name(elem.kindA, " ".join([elem.typeS, elem.nameS]), elem.briefdescriptionE)
        self.__event(elem, "end")

    def sectiondef(self, elem):
        text = elem.headerS
        if not text:
            text = self.section_titles.get(elem.kindA, "")
        self.__title(text, 2)
        self.__description(elem.descriptionE)
        for memb in elem.memberdefL:
            self.memberdef(memb)

    def innerclass_section(self, elem):
        list = elem.innerclassL
        if list:
            self.__title("Structures", 2)
            for incl in list:
                comp = self.index[incl.refidA].element()
                self.compounddef(comp)

    def compounddef(self, elem):
        self.__event(elem, "begin")
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
        if "file" == elem.kindA:
            self.__copyright(self.copytext)
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
                self.setoutfile(ofile)
                self.compounddef(comp)
