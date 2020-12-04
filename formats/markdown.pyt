from format import *

class markdown(format):
    def title(self, s):
        : # ${s}
    def name(self, s):
        : **${s}**
    def code(self, s):
        : ```${self.language}
        : ${s}
        : ```
    def description(self, elem):
        : ${elem}

def main(index):
    markdown(index).main()
