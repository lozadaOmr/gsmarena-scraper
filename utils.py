from json import JSONEncoder


class PythonObjectEncoder(JSONEncoder):
    def default(self, obj):
        types = (list, dict, str, unicode, int, float, bool, type(None))

        if isinstance(obj, types):
            return JSONEncoder.default(self, obj)

        return {'_python_object': str(obj)}


def merge(*dicts):
    _d = {}

    for d in dicts:
        _d.update(d)

    return _d
