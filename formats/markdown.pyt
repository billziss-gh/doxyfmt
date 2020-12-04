import os

def description(elem):
    : ${elem}

def member(elem):
    : ${elem}
    for desc in elem["briefdescription%"]:
        description(desc)
    for desc in elem["detaileddescription%"]:
        description(desc)

def section(elem):
    : ${elem}
    for desc in elem["description%"]:
        description(desc)
    for memb in elem["memberdef%"]:
        member(memb)

def compound(elem):
    file = elem["location!"]["file@"]
    if not file or os.path.isabs(file):
        : # ${elem["compoundname$"]}
    else:
        : # ${file}
    for desc in elem["briefdescription%"]:
        description(desc)
    for desc in elem["detaileddescription%"]:
        description(desc)
    for sect in elem["sectiondef%"]:
        section(sect)

def main(index):
    for i in index:
        comp = index[i].element()
        if "file" != comp["kind@"]:
            continue
        compound(comp)
