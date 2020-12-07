import html, re
from format import *

textmap = {
    "listitem": "- %s",
    "ndash": "--%s",
    "parameteritem": "- %s",
    "parametername": "*%s*",
    "parameterdescription": " - %s",
}
tailmap = {
    "para": "\n\n%s",
}
descflt = {
    "para": lambda e: e.find("parameterlist") is None,
}

escape_re = [
    re.compile(r"([\\`*_])"),                   r"\\\1",
    re.compile(r"\[(.*]\()"),                   r"\\[\1",
    re.compile(r"^([ \t]*)>"),                  r"\1\\>",
    re.compile(r"^([ \t]*)([#+-][ \t])"),       r"\1\\\2",
    re.compile(r"^([ \t]*)([0-9])([.)][ \t])"), r"\1\2\\\3",
]
def escape(text):
    for i in range(0, len(escape_re), 2):
        text = escape_re[i].sub(escape_re[i + 1], text)
    return text

class markdown(format):
    def setoutfile(self, file):
        global _
        _ = file

    def title(self, text, heading):
        : #${heading * "#"} ${escape(text)}
        :

    def name(self, kind, text, desc):
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
                : **${escape(text)}** - ${escape(desc.T)}
            else:
                : **${escape(text)}**
            :

    def syntax(self, text):
        : ```${self.language}
        : ${text}
        : ```
        :

    def parameters(self, parl):
        : **Parameters**
        :
        : ${parl.Maptext(escape, textmap, tailmap)}

    def returns(self, retv):
        : **Return Value**
        :
        : ${retv.Maptext(escape, textmap, tailmap)}

    def members(self, list):
        pass

    def description(self, desc):
        : **Discussion**
        :
        : ${desc.Maptext(escape, textmap, tailmap, descflt)}

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
