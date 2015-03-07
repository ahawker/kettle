"""
    kettle.meta
    ~~~~~~~~~~~

    Common utilities for dealing with object/type reflection.
"""
__all__ = ['resolve_class', 'resolve_module', 'resolve_type', 'resolve_type_meta']


import inspect


def resolve_class(obj):
    """
    Return class name for the given object.
    """
    if inspect.isclass(obj):
        return obj.__name__
    return getattr(obj, '__class__', obj).__name__


def resolve_module(obj):
    """
    Return module name of for the given object.
    """
    return getattr(obj, '__module__', '__main__')


def resolve_type(obj):
    """
    Return the fully qualified type string for the given object. The fully-qualified type
    is a period separated string of module name and class name.

    Example: my.package.module.class
    """
    cls = resolve_class(obj)
    module = resolve_module(obj)
    return '{}.{}'.format(module, cls)


def resolve_type_meta(name, attrs):
    """
    Return the fully qualified type string for the class being created by
    a meta class.
    """
    module = attrs.get('__module__', '__main__')
    return '{}.{}'.format(module, name)
