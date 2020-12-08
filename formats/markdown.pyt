import html, re
from format import format

class nlstream(object):
    # nlstream will *NOT* write the last line if it does not end in newline (\n)
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

class markdown(format):
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
    def textfn(self, fmt, ind):
        if isinstance(ind, int) and 0 <= ind:
            def fn(elem):
                prefix = self.__prefix
                self.__prefix += " " * ind
                return fmt.replace("{prefix}", prefix)
        elif isinstance(ind, int) and 0 > ind:
            def fn(elem):
                prefix = self.__prefix
                self.__prefix = self.__prefix[:ind]
                return fmt.replace("{prefix}", prefix)
        elif isinstance(ind, str):
            def fn(elem):
                prefix = self.__prefix
                self.__prefix += ind
                return fmt.replace("{prefix}", prefix)
        return fn
    def Maptext(self, elem, filter = None):
        return elem.Maptext(self.escape, self.__textmap, self.__tailmap, filter)

    def reset(self, file):
        global _
        _ = nlstream(file)
        T = self.textfn
        self.__prefix = ""
        self.__textmap = {
            "parameteritem":            T("\n{prefix}- %s", +4),
            "parametername":            "*%s*",
            "parameterdescription":     " - %s",
            "itemizedlist":             T("\n{prefix}%s", 0),
            "listitem":                 T("\n{prefix}- %s", +4),
            "computeroutput":           " `%s",
            "ndash":                    "--%s",
        }
        self.__tailmap = {
            "para":                     T("\n\n{prefix}%s", 0),
            "parameteritem":            T("%s", -4),
            "itemizedlist":             T("\n{prefix}%s", 0),
            "listitem":                 T("%s", -4),
            "computeroutput":           "` %s",
        }

    def title(self, text, heading):
        : ${heading * "#"} ${self.escape(text)}
        :

    def copyright(self, text):
        : ---
        :
        : <small>Copyright ${html.escape(text)}</small>
        :

    def name(self, text, desc):
        if self.isdetailed():
            : <summary>
            if desc.T:
                : <b>${html.escape(text)}</b> - ${html.escape(desc.T)}
            else:
                : <b>${html.escape(text)}</b>
            : </summary>
            : <blockquote>
            : <br/>
            :
        else:
            if desc.T:
                : - *${self.escape(text)}* - ${self.escape(desc.T)}
            else:
                : - *${self.escape(text)}*
            :

    def syntax(self, text):
        : ```${self.language}
        : ${text}
        : ```
        :

    def parameters(self, parl):
        : **Parameters**
        :
        : ${self.Maptext(parl)}

    def returns(self, retv):
        : **Return Value**
        :
        : ${self.Maptext(retv)}

    def description(self, desc):
        : **Discussion**
        :
        : ${self.Maptext(desc, self.description_filter)}

    def event(self, elem, ev):
        if "begin" == ev:
            if self.isdetailed():
                : <details>
        elif "end" == ev:
            if self.isdetailed():
                # name() adds <blockquote>; remove it
                : </blockquote>
                : </details>
                :

def main(index, outdir):
    markdown(index, outdir, ".md").main()
