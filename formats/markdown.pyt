from format import *

textmap = {
    "listitem": "- %s",
    "ndash": "--%s",
}
tailmap = {
    "para": "\n\n%s",
}

class markdown(format):

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

    def parameters(self, list):
        pass

    def returns(self, text):
        pass

    def members(self, list):
        pass

    def description(self, desc):
        : **Discussion**
        :
        : ${desc.Maptext(textmap, tailmap)}
        :

def main(index):
    markdown(index).main()
