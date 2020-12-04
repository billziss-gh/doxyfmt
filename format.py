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

    def title(self, s):
        pass
    def __title(self, s):
        if s:
            self.title(s)

    def name(self, s):
        pass
    def __name(self, s):
        if s:
            self.name(s)

    def code(self, s):
        pass
    def __code(self, s):
        if s:
            self.code(s)

    def description(self, elem):
        pass
    def __description(self, elem):
        if elem["$"]:
            self.description(elem)

    def param(self, elem):
        pass

    def member(self, elem):
        self.__name(elem["kind$"] + " " + elem["name$"])
        self.__code(elem["definition$"] + elem["argsstring$"])
        for parm in elem["param%"]:
            self.param(parm)
        self.__description(elem["briefdescription!"])
        self.__description(elem["detaileddescription!"])

    def section(self, elem):
        self.__description(elem["description!"])
        for memb in elem["memberdef%"]:
            self.member(memb)

    def compound(self, elem):
        self.language = elem["language@"]
        if "file" == elem["kind@"]:
            title = elem["title$"]
            if title:
                self.__title(title)
            else:
                title = elem["location!"]["file@"]
                if title and not os.path.isabs(title):
                    self.__title(title)
                else:
                    self.__title(elem["compoundname$"])
        else:
            self.__name(elem["kind$"] + " " + elem["compoundname$"])
        self.__description(elem["briefdescription!"])
        self.__description(elem["detaileddescription!"])
        for incl in elem["innerclass%"]:
            comp = self.index[incl["refid@"]].element()
            lang = self.language
            self.compound(comp)
            self.language = lang
        for sect in elem["sectiondef%"]:
            self.section(sect)

    def main(self):
        for i in self.index:
            comp = self.index[i].element()
            if "file" != comp["kind@"]:
                continue
            self.compound(comp)
