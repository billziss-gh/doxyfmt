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

    def title(self, s):
        pass

    def description(self, elem):
        pass

    def member(self, elem):
        for desc in elem["briefdescription%"]:
            self.description(desc)
        for desc in elem["detaileddescription%"]:
            self.description(desc)

    def section(self, elem):
        for desc in elem["description%"]:
            self.description(desc)
        for memb in elem["memberdef%"]:
            self.member(memb)

    def compound(self, elem):
        file = elem["location!"]["file@"]
        if not file or os.path.isabs(file):
            self.title(elem["compoundname$"])
        else:
            self.title(file)
        for desc in elem["briefdescription%"]:
            self.description(desc)
        for desc in elem["detaileddescription%"]:
            self.description(desc)
        for sect in elem["sectiondef%"]:
            self.section(sect)

    def main(self):
        for i in self.index:
            comp = self.index[i].element()
            if "file" != comp["kind@"]:
                continue
            self.compound(comp)
