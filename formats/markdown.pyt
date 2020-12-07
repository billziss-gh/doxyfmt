import html, re
from format import *

class markdown(format):
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
    escape_re = [
        re.compile(r"([\\`*_])"),                   r"\\\1",
        re.compile(r"\[(.*]\()"),                   r"\\[\1",
        re.compile(r"^([ \t]*)>"),                  r"\1\\>",
        re.compile(r"^([ \t]*)([#+-][ \t])"),       r"\1\\\2",
        re.compile(r"^([ \t]*)([0-9])([.)][ \t])"), r"\1\2\\\3",
    ]

    @classmethod
    def escape(cls, text):
        for i in range(0, len(cls.escape_re), 2):
            text = cls.escape_re[i].sub(cls.escape_re[i + 1], text)
        return text

    def setoutfile(self, file):
        global _
        _ = file

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
        : ${parl.Maptext(self.escape, self.textmap, self.tailmap)}

    def returns(self, retv):
        : **Return Value**
        :
        : ${retv.Maptext(self.escape, self.textmap, self.tailmap)}

    def description(self, desc):
        : **Discussion**
        :
        : ${desc.Maptext(self.escape, self.textmap, self.tailmap, self.description_filter)}

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
