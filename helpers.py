from django.db.models import Model
from django.forms import ValidationError
from django.http import Http404
from rest_framework.exceptions import APIException


def get_object_or_error(klass: Model, exception: APIException = Http404, **kwargs):
    """
    Almost the same as `django.shortcuts.get_object_or_404`, but can raise any
    custom error class you want, allowing you to return more precise error messages.
    Another advantage of using this helper function, is that it prevents your application
    from crashing. For instance, in case you want to get an object by it's primary key, and
    it is of type `uuid`, but another data type is provided in the url, it will not crash,
    unlike the standard `get_object_or_404`.

    - `klass` -> The model that will be used for the query
    - `exception` -> An error class inheriting from `rest_framework.exceptions.APIException`.
    If no `exception` is provided, then the standard `django.http.Http404` class is used.
    - `**kwargs` -> Keyword arguments representing all fields that should be used for the
    search, as many as you please.

    I highly encorage you to have a quick look at the source code, it's quite a simple concept.
    """
    try:
        return klass.objects.get(**kwargs)
    except (klass.DoesNotExist, ValidationError):
        raise exception


def get_list_or_error(
    klass: Model,
    error_klass: APIException = Http404,
    accept_empty: bool = False,
    **kwargs
):
    """
    Almost the same as `django.shortcuts.get_list_or_404`, but can raise any
    custom error class you want, allowing you to return more precise error messages.
    Another advantage of using this helper function, is that it prevents your application
    from crashing. For instance, in case you want to get a list, filtering it by some foreign
    key field, which is of type `uuid`, but another data type is provided in the url, it will
    not crash, unlike the standard `get_list_or_404`. Also, this function gives you the possiblity
    of not raising an exception when no values are found, so you could just return an empty list.

    - `klass` -> The model that will be used for the query
    - `exception` -> An error class inheriting from `rest_framework.exceptions.APIException`.
    If no `exception` is provided, then the standard `django.http.Http404` class is used.
    - `accept_empty` -> A boolean argument, which defaults to `False`. When provided, determines
    if an empty result is acceptable or if it should raise `exception`.
    - `**kwargs` -> Keyword arguments representing all fields that should be used for the
    search, as many as you please.

    I highly encorage you to have a quick look at the source code, it's quite a simple concept.
    """
    try:
        result = klass.objects.filter(**kwargs)
    except ValidationError:
        raise error_klass

    if result or accept_empty:
        return result

    raise error_klass


def set_and_destroy(
    klass: Model, attr: str, value: list[Model], related_klass: Model, **kwargs
):
    """
    This function basically sets a new value in a foreign key field and erases any previous
    values that were related to `klass`. For it to work, **you must set `null=True` in your
    model**, otherwise, the values will not be subsitituted, they will only be added.

    - `klass` -> The model on the side 1 of a 1:N relationship, the owner of the relation,
    in which the new values will be set
    - `attr` -> A string version of the attribute corresponding to the `related_name` value
    in the foreign key field
    - `value` -> A list (or any other iterable), containing new created instances of `related_klass`
    - `related_klass` -> The model on the side N of a 1:N relationship, the one having the foreign
    key field
    - `**kwargs` -> Keyword arguments used in a filter to determine which objects should be destroyed.
    It could be really anything, but usually you will want it to be something like `klass=None`, so
    that all objects that are no part of the relationship anymore can be descarded.

    I highly encorage you to have a quick look at the source code, it's quite a simple concept.
    """
    getattr(klass, attr).set(value)
    related_klass.objects.filter(**kwargs).delete()
