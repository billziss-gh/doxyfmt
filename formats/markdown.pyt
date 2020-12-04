from format import *

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
        for para in desc.paraL:
            for elem in para.XMLElement.iter():
                : ${elem.tag}--${elem.text}--${elem.tail}..

def main(index):
    markdown(index).main()
