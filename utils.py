def merge(*dicts):
    _d = {}
    for d in dicts:
        _d.update(d)
    return _d
