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

class markdown(format):

    def setoutfile(self, file):
        global _
        _ = file

    def title(self, text):
        : # ${text}
        :

    def name(self, text, desc):
        if desc.T:
            : **${text}** - ${desc.T}
            :
        else:
            : **${text}**
            :

    def syntax(self, text):
        : ```${self.language}
        : ${text}
        : ```
        :

    def parameters(self, parl):
        : **Parameters**
        :
        : ${parl.Maptext(textmap, tailmap)}

    def returns(self, retv):
        : **Return Value**
        :
        : ${retv.Maptext(textmap, tailmap)}

    def members(self, list):
        pass

    def description(self, desc):
        : **Discussion**
        :
        : ${desc.Maptext(textmap, tailmap, descflt)}

def main(index, outdir):
    markdown(index, outdir, ".md").main()
