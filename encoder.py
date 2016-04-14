__author__ = 'Jian Xun'


def encode(target, encoding='utf-8'):
    """
    encode a unicode string or all unicode strings inside a list/dict recursively
    :param target: an object, could be a dict/list/string
    :param encoding: the encodings supported python
    :return: object
    """
    if isinstance(target, dict):
        return {encode(key, encoding): encode(value, encoding) for key, value in target.iteritems()}
    elif isinstance(target, list):
        return [encode(element, encoding) for element in target]
    elif isinstance(target, unicode):
        return target.encode(encoding)
    else:
        return target
