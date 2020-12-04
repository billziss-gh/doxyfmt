# format.py
#
# Copyright (c) 2014-2020, Bill Zissimopoulos. All rights reserved.
#
# This file is part of Doxyover.
#
# It is licensed under the MIT license. The full license text can be found
# in the License.txt file at the root of this project.

import os

class format(object):
    def __init__(self, index):
        self.index = index
        self.language = ""

    def title(self, text):
        pass
    def name(self, text, desc):
        pass
    def syntax(self, text):
        pass
    def parameters(self, list):
        pass
    def returns(self, text):
        pass
    def members(self, list):
        pass
    def description(self, desc):
        pass

    def __title(self, text):
        if text:
            self.title(text)
    def __name(self, text, desc):
        if text:
            self.name(text, desc)
    def __syntax(self, text):
        if text:
            self.syntax(text)
    def __parameters(self, list):
        if list:
            self.parameters(list)
    def __returns(self, text):
        if text:
            self.returns(text)
    def __members(self, list):
        if list:
            self.members(list)
    def __description(self, desc):
        if desc.T:
            self.description(desc)

    def memberdef(self, elem):
        self.__name(elem.kindA + " " + elem.nameS, elem.briefdescriptionE)
        self.__syntax(elem.definitionS + elem.argsstringS)
        self.__parameters(elem.paramL)
        self.__description(elem.detaileddescriptionE)

    def sectiondef(self, elem):
        self.__description(elem.descriptionE)
        for memb in elem.memberdefL:
            self.memberdef(memb)

    def compounddef(self, elem):
        self.language = elem.languageA
        if "file" == elem.kindA:
            text = elem.titleS
            if not text:
                text = elem.locationE.fileA
                if not text or os.path.isabs(text):
                    text = elem.compoundnameS
            self.__title(text)
        else:
            self.__name(elem.kindS + " " + elem.compoundnameS, elem.briefdescriptionE)
        self.__description(elem.detaileddescriptionE)
        for incl in elem.innerclassL:
            comp = self.index[incl.refidA].element()
            lang = self.language
            self.compounddef(comp)
            self.language = lang
        for sect in elem.sectiondefL:
            self.sectiondef(sect)

    def main(self):
        for i in self.index:
            comp = self.index[i].element()
            if "file" != comp.kindA:
                continue
            self.compounddef(comp)
