__author__ = 'nzinfo'


def load_class(sName):
    import importlib
    pos = sName.rfind('.')
    module_name = sName[:pos]
    cName = sName[pos+1:]
    try:
        m = importlib.import_module(module_name)
        c = getattr(m, cName)
        return c
    except ImportError, e:
        print e
        return None