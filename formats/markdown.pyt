from format import *

class markdown(format):

    def title(self, text):
        : # ${text}

    def name(self, text, desc):
        if desc.S:
            : **${text}** - ${desc.S}
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

    def description(self, desc):
        : ${desc}

def main(index):
    markdown(index).main()
