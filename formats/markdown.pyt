# formats/markdown.pyt
#
# Copyright (c) 2014-2020, Bill Zissimopoulos. All rights reserved.
#
# This file is part of Doxyfmt.
#
# It is licensed under the MIT license. The full license text can be found
# in the License.txt file at the root of this project.

import html, re
import doxylib

class markdown(doxylib.format):

    def reset(self, file):
        global _
        _ = doxylib.ostream(file)
        I = self.indent
        self.__prefix = ""
        self.__textmap = {
            "parameteritem":            I("\n{prefix}- %s", +1),
            "parametername":            "*%s*",
            "parameterdescription":     " - %s",
            "itemizedlist":             I("\n{prefix}%s", 0),
            "listitem":                 I("\n{prefix}- %s", +1),
            "computeroutput":           " `%s",
            "ndash":                    "--%s",
        }
        self.__tailmap = {
            "para":                     I("\n\n{prefix}%s", 0),
            "parameteritem":            I("%s", -1),
            "itemizedlist":             I("\n{prefix}%s", 0),
            "listitem":                 I("%s", -1),
            "computeroutput":           "` %s",
        }
        self.__blockquote = []

    def indent(self, fmt, ind):
        if 0 < ind:
            def fn(elem):
                prefix = self.__prefix
                self.__prefix += " " * (ind * 4)
                return fmt.replace("{prefix}", prefix)
        elif 0 > ind:
            def fn(elem):
                prefix = self.__prefix
                self.__prefix = self.__prefix[:ind * 4]
                return fmt.replace("{prefix}", prefix)
        else:
            def fn(elem):
                prefix = self.__prefix
                return fmt.replace("{prefix}", prefix)
        return fn

    reC = re.compile
    escape_re = [
        reC(r"([\\`*_])"),              r"\\\1",
        reC(r"\[(.*]\()"),              r"\\[\1",
        reC(r"^([ \t]*)>"),             r"\1\\>",
        reC(r"^([ \t]*)([#+-][ \t])"),  r"\1\\\2",
        reC(r"^([ \t]*)([0-9])([.)][ \t])"),r"\1\2\\\3",
    ]
    def escape(self, text):
        for i in range(0, len(self.escape_re), 2):
            text = self.escape_re[i].sub(self.escape_re[i + 1], text)
        return text

    def maptext(self, elem, filter = None):
        return elem.Maptext(self.escape, self.__textmap, self.__tailmap, filter)

    def heading(self, text, level):
        self.blockquote()
        : ${level * "#"} ${self.escape(text)}
        :

    def summary(self, elem):
        self.blockquote()
        : ${self.maptext(elem, self.summary_filter)}
        :

    def copyright(self, text):
        self.blockquote()
        : ---
        :
        : <small>Copyright ${html.escape(text)}</small>
        :

    def name(self, kind, text, desc):
        : <summary>
        if desc.T:
            : <b>${html.escape(text)}</b> - ${html.escape(desc.T)}
        else:
            : <b>${html.escape(text)}</b>
        : </summary>
        :

    def syntax(self, text):
        self.blockquote()
        : ```${self.language}
        : ${text}
        : ```
        :

    def parameters(self, elst):
        self.blockquote()
        : **Parameters**
        :
        : ${self.maptext(elst)}
        :

    def returns(self, elem):
        self.blockquote()
        : **Return Value**
        :
        : ${self.maptext(elem)}
        :

    def enumvalues(self, elst):
        self.blockquote()
        : **Values**
        :
        for e in elst:
            if e.briefdescriptionT:
                : - *${self.escape(e.nameS)}* - ${self.escape(e.briefdescriptionT)}
            else:
                : - *${self.escape(e.nameS)}*
        :

    def description(self, elem):
        self.blockquote()
        : **Discussion**
        :
        : ${self.maptext(elem, self.description_filter)}
        :

    def blockquote(self):
        if self.__blockquote and not self.__blockquote[-1]:
            : <blockquote>
            : <br/>
            :
            self.__blockquote[-1] = True

    def event(self, elem, ev):
        n = elem.N
        k = elem.kindA
        if ("compounddef" == n and "file" != k) or "memberdef" == n:
            if "begin" == ev:
                : <details>
                self.__blockquote.append(False)
            elif "end" == ev:
                if self.__blockquote[-1]:
                    : <br/>
                    : </blockquote>
                : </details>
                :
                self.__blockquote.pop()

def main(index, outdir):
    markdown(index, outdir, ".md").main()
