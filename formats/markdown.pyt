from format import *

class markdown(format):
    def description(self, elem):
        : ${elem}

def main(index):
    markdown(index).main()
