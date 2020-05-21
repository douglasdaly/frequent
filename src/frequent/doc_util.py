# -*- coding: utf-8 -*-
#
#   This module is part of the Frequent project, Copyright (C) 2020,
#   Douglas Daly.  The Frequent package is free software, licensed under
#   the MIT License.
#
#   Source Code:
#       https://github.com/douglasdaly/frequent-py
#   Documentation:
#       https://frequent-py.readthedocs.io/en/latest
#   License:
#       https://frequent-py.readthedocs.io/en/latest/license.html
#
"""
Documentation helper utilities.

> This code was inspired by code in the
> `Static-Frame <https://github.com/InvestmentSystems/static-frame>`_
> project.

"""
from abc import ABC
from abc import abstractmethod
from functools import partial
from textwrap import indent
import typing as tp


class _BaseTemplate(ABC):
    """
    Base template for default docstring templates.
    """
    __ordering__: tp.Tuple[str, ...] = (
        'summary', 'description', 'notes', 'parameters', 'attributes',
        'yields', 'returns', 'raises', 'examples', 'see_also', 'todo'
    )

    @abstractmethod
    @classmethod
    def _get(cls, name: str, template: str) -> str:
        """Returns the sub-template string for further formatting."""
        pass

    @classmethod
    def format(cls, **kwargs) -> str:
        """Returns the template string to use.

        Parameters
        ----------
        kwargs : optional
            The dictionary of sub-templates to insert.

        Returns
        -------
        str
            The template string to format further.

        """
        rv = ""
        for k in cls.__ordering__:
            if k not in kwargs:
                continue
            v = kwargs[k]
            rv += f"{cls._get(k, v)}\n"
        return rv


class GOOGLE(_BaseTemplate):
    """
    Google docstring default template.
    """

    @classmethod
    def _get(cls, name: str, template: str) -> str:
        if name in ('summary', 'description'):
            return f"{template}\n"
        elif name == 'parameters':
            header = 'Args'
        else:
            header = ' '.join(x[0].upper() + x[1:] for x in name.split('_'))
        return (
            f"{header}:\n"
            f"{indent(template, '    ')}\n"
        )


class NUMPY(_BaseTemplate):
    """
    Numpy docstring default template.
    """

    @classmethod
    def _get(cls, name: str, template: str) -> str:
        if name in ('summary', 'description'):
            return f"{template}\n"
        else:
            header = ' '.join(x[0].upper() + x[1:] for x in name.split('_'))
        return (
            f"{header}\n"
            f"{'-' * len(header)}\n"
            f"{template}\n"
        )


def _doc_inject_base(
    templates: tp.Mapping[str, str],
    template_name: tp.Optional[str] = None,
    default_template: tp.Optional[tp.Union[str, _BaseTemplate]] = None,
    **kwargs: dict
) -> tp.Callable[[tp.Callable], tp.Callable]:
    """Injects a function with documentation from a template.

    Parameters
    ----------
    templates : Mapping
        The available templates which can be chosen from.
    template_name : str, optional
        The name of the documentation template (from ``templates``) to
        use.
    default_template : :obj:`str` or :obj:`_BaseTemplate`, optional
        The default template to use if the decorated function doesn't
        have a ``__doc__`` attribute.  This can either be a format
        string or one of:
         - :obj:`doc_util.GOOGLE` for Google-style docstrings
         - :obj:`doc_util.NUMPY` for Numpy-style docstrings
        If one of the above is used then whatever keys are populated in
        the template dictionary are inserted appropriately into the
        resulting docstring.
    kwargs : optional
        The key-value pairs to inject into the template.

    Returns
    -------
    Callable
        The function with documentation injected into it.

    Raises
    ------
    KeyError
        If the specified template ``name`` doesn't exist in the
        ``templates`` given.
    ValueError
        If the function to decorate does not have a docstring already
        but requires one (when using ``dict``-based templates).
    NotImplementedError
        If the type of template specified is not a supported type.

    """
    def _decorator(func: tp.Callable) -> tp.Callable:
        has_doc = func.__doc__ is not None
        nonlocal templates
        nonlocal template_name
        template_name = template_name if template_name else func.__name__

        doc_temp = templates[template_name]
        if isinstance(doc_temp, tuple) and not has_doc:
            func.__doc__ = doc_temp[0]
            has_doc = True
            doc_temp = doc_temp[1]
        if isinstance(doc_temp, str):
            doc_temp = doc_temp.format(**kwargs)
            if has_doc:
                func.__doc__ = func.__doc__.format(doc_temp)
            else:
                func.__doc__ = doc_temp
        elif isinstance(doc_temp, dict):
            if not has_doc:
                if default_template is None:
                    raise ValueError(f"{func} must have a docstring.")
                func.__doc__ = default_template
            func.__doc__ = func.__doc__.format(**doc_temp).format(**kwargs)
        else:
            raise NotImplementedError(
                f"Unsupported template type: {type(doc_temp)}."
            )
        return func

    return _decorator


def create_injector(
    templates: tp.Mapping[str, tp.Union[tp.Tuple[str, dict], str, dict]],
    default_template: tp.Optional[str] = None,
    **defaults: tp.Mapping[str, str]
) -> tp.Callable:
    """Creates a new documentation injection decorator function.

    Avoids having to re-write the same (or very similar) documentation
    over and over again.

    Templates can either be strings with format-strings embedded in them
    (for which the ``kwargs`` passed to the decorator will be used)
    or dictionaries.  When a dictionary is used it's a two-step process:

     #. Insert the template string(s) for any key-values in the
        decorated functions docstring.
     #. Insert the ``kwargs`` into the docstring template generated from
        the first step.

    If the template is a ``tuple`` then the first element must be a
    string (which will be used as the docstring template if no docstring
    is found) and the second is a `dict`` (see above).

    Parameters
    ----------
    templates : :obj:`Mapping` of :obj:`str` to :obj:`tuple`, :obj:`str`
    or :obj:`dict`
        The docstring templates to use for the new injector decorator.
    default_template : str, optional
        The default docstring template to use for dictionary-based
        ``templates`` if the decorated function doesn't have a
        ``__doc__``.
    defaults : optional
        Any default values to use in the ``templates`` (which can be
        over-written by those in the ``kwargs`` passed to the resulting
        decorator function).

    Returns
    -------
    :obj:`Callable`
        The new decorator to use for docstring injection.

    Examples
    --------
    To create a new docstring-injector decorator first specify the
    templates:

    .. code-block:: python
        _MY_TEMPLATES = {
            'get_fn': "My documentation template for {name}.",
            'set_fn': dict(
                parameters=(
                    "{parameter} : {param_type}\n"
                    "   The value to set for the parameter."
                ),
                returns=(
                    "{return_type}\n"
                    "   The value set to the given {parameter}."
                ),
            ),
        }

    Then create the decorator like this:

    .. code-block:: python
        doc_inject = create_injector(_MY_TEMPLATES)

    Then you can decorate your functions with ``@doc_inject``:

    .. code-block:: python
        @doc_inject('get_fn', name='some function')
        def some_get_function():
            ...

    .. code-block:: python
        @doc_inject(parameter='x', param_type='float')
        def set_fn(self, x):
            \"\"\"Sets the value for {parameter} on this object.

            Parameters
            ----------
            {parameters}

            \"\"\"
            self.x = x
            return

    """
    return partial(
        _doc_inject_base,
        templates,
        default_template=default_template,
        **defaults,
    )
