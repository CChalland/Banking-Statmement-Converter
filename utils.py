import gvars


def credit_highlighter(x):
    is_negative = x < 0
    return ["color: {}".format(gvars.COLOR_GREEN) if i else "color: #000000" for i in is_negative]


def nenegative_highligher(x):
    is_negative = x < 0
    return ["color: {}".format(gvars.COLOR_RED) if i else "color: #000000" for i in is_negative]