from format import *

class markdown(format):
    def title(self, text):
        : # ${text}
    def name(self, text, brief):
        if brief["$"]:
            : **${text}** - ${brief["$"]}
        else:
            : **${text}**
    def syntax(self, text):
        : ```${self.language}
        : ${text}
        : ```
    def parameters(self, list):
        pass
    def returns(self, text):
        pass
    def members(self, list):
        pass
    def description(self, detail):
        : ${detail}

def main(index):
    markdown(index).main()
