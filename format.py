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
    def name(self, text, brief):
        pass
    def syntax(self, text):
        pass
    def parameters(self, list):
        pass
    def returns(self, text):
        pass
    def members(self, list):
        pass
    def description(self, detail):
        pass

    def __title(self, text):
        if text:
            self.title(text)
    def __name(self, text, brief):
        if text:
            self.name(text, brief)
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
    def __description(self, detail):
        if detail["$"]:
            self.description(detail)

    def memberdef(self, elem):
        self.__name(elem["kind$"] + " " + elem["name$"], elem["briefdescription!"])
        self.__syntax(elem["definition$"] + elem["argsstring$"])
        self.__parameters(elem["param%"])
        self.__description(elem["detaileddescription!"])

    def sectiondef(self, elem):
        self.__description(elem["description!"])
        for memb in elem["memberdef%"]:
            self.memberdef(memb)

    def compounddef(self, elem):
        self.language = elem["language@"]
        if "file" == elem["kind@"]:
            text = elem["title$"]
            if not text:
                text = elem["location!"]["file@"]
                if not text or os.path.isabs(text):
                    text = elem["compoundname$"]
            self.__title(text)
        else:
            self.__name(elem["kind$"] + " " + elem["compoundname$"], elem["briefdescription!"])
        self.__description(elem["detaileddescription!"])
        for incl in elem["innerclass%"]:
            comp = self.index[incl["refid@"]].element()
            lang = self.language
            self.compounddef(comp)
            self.language = lang
        for sect in elem["sectiondef%"]:
            self.sectiondef(sect)

    def main(self):
        for i in self.index:
            comp = self.index[i].element()
            if "file" != comp["kind@"]:
                continue
            self.compounddef(comp)
