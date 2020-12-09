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
            "para":                     "%T%s",

            "parameterlist":            "%T%s",
            "parameteritem":            I("%T\n{prefix}- %s", +1),
            "parameternamelist":        "%T%s",
            "parametername":            "%T*%s*",
            "parameterdescription":     "%T - %s",
            "simplesect":               "%T%s",

            "itemizedlist":             I("%T\n{prefix}%s", 0),
            "listitem":                 I("%T\n{prefix}- %s", +1),

            "ulink":                    self.ulink,
            "bold":                     "**%s",
            "s":                        "<s>%s",
            "strike":                   "<s>%s",
            "underline":                "<u>%s",
            "emphasis":                 "*%s",
            "computeroutput":           "`%s",
            "subscript":                "<sub>%s",
            "superscript":              "<sup>%s",
            "center":                   "<center>%s",
            "small":                    "<small>%s",
            "del":                      "<del>%s",
            "ins":                      "<ins>%s",

            "mdash":                    "---%s",
            "ndash":                    "--%s",
        }
        self.__tailmap = {
            "para":                     I("%T\n\n{prefix}%s", 0),

            "parameterlist":            "%T%s",
            "parameteritem":            I("%T%s", -1),
            "parameternamelist":        "%T%s",
            "parametername":            "%T%s",
            "parameterdescription":     "%T%s",
            "simplesect":               "%T%s",

            "itemizedlist":             I("%T\n{prefix}%s", 0),
            "listitem":                 I("%T%s", -1),

            "ulink":                    "</a>%s",
            "bold":                     "**%s",
            "s":                        "</s>%s",
            "strike":                   "</s>%s",
            "underline":                "</u>%s",
            "emphasis":                 "*%s",
            "computeroutput":           "`%s",
            "subscript":                "</sub>%s",
            "superscript":              "</sup>%s",
            "center":                   "</center>%s",
            "small":                    "</small>%s",
            "del":                      "</del>%s",
            "ins":                      "</ins>%s",
        }
        self.__blockquote = []

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

    def ulink(self, elem):
        return '<a href="' + elem.get("url", "").replace("%", "%%").replace('"', '') + '">%s'

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
