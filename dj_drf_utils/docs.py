from drf_spectacular.utils import OpenApiParameter, extend_schema


def build_list_docs(
    summary: str = " ",
    description: str = " ",
    parameters: list[OpenApiParameter] = [],
    *args,
    **kwargs
):
    """
    Create a mixin class that applies the `drf_spectacular.utils.extend_schema` decorator to the
    `get` method of views. `drf-spectacular` library already builds the whole documentation using
    swagger, but some details may not be totally correct, or maybe you want to add more information to it.
    They provide ways to handle this. When that is the case, you can easily use this function to generate
    a mixin that can be used to set these kind of customizations. It receives the following arguments:
    
    `summary` -> A `str`, which is a brief description of what that endpoint does.
    `description` -> Also a `str`, which can be used to provide further details on the behavior of the
    endpoint.
    `parameters` -> A `list` filled with values of type `OpenApiParameter`.
    `*args, **kwargs` -> Any other parameters that `@extend_schema` expects.
    """
    class ListDocsMixin:
        """
        Documentation for `get` requests on views that are used to list data
        """
        @extend_schema(
            summary=summary,
            description=description,
            parameters=parameters,
            *args,
            **kwargs
        )
        def get(self, request, *args, **kwargs):
            return super().get(request, *args, **kwargs)

    return ListDocsMixin


def build_create_docs(summary: str = " ", description: str = " ", *args, **kwargs):
    """
    Create a mixin class that applies the `drf_spectacular.utils.extend_schema` decorator to the
    `post` method of views. `drf-spectacular` library already builds the whole documentation using
    swagger, but some details may not be totally correct, or maybe you want to add more information to it.
    They provide ways to handle this. When that is the case, you can easily use this function to generate
    a mixin that can be used to set these kind of customizations. It receives the following arguments:
    
    `summary` -> A `str`, which is a brief description of what that endpoint does.
    `description` -> Also a `str`, which can be used to provide further details on the behavior of the
    endpoint.
    `*args, **kwargs` -> Any other parameters that `@extend_schema` expects.
    """
    class CreateDocsMixin:
        """
        Documentation for `post` requests on views that are used to create data
        """
        @extend_schema(summary=summary, description=description, *args, **kwargs)
        def post(self, request, *args, **kwargs):
            return super().post(request, *args, **kwargs)

    return CreateDocsMixin


def build_retrieve_docs(summary: str = " ", description: str = " ", *args, **kwargs):
    """
    Create a mixin class that applies the `drf_spectacular.utils.extend_schema` decorator to the
    `get` method of views, but that return a single result (`retrieve`). `drf-spectacular` library already
    builds the whole documentation using swagger, but some details may not be totally correct, or maybe you
    want to add more information to it. They provide ways to handle this. When that is the case, you can
    easily use this function to generate a mixin that can be used to set these kind of customizations. It
    receives the following arguments:
    
    `summary` -> A `str`, which is a brief description of what that endpoint does.
    `description` -> Also a `str`, which can be used to provide further details on the behavior of the
    endpoint.
    `*args, **kwargs` -> Any other parameters that `@extend_schema` expects.
    """
    class RetrieveDocsMixin:
        """
        Documentation for `get` requests on views that are used to retrieve a single instance of data
        """
        @extend_schema(summary=summary, description=description, *args, **kwargs)
        def get(self, request, *args, **kwargs):
            return super().get(request, *args, **kwargs)

    return RetrieveDocsMixin


def build_update_docs(summary: str = " ", description: str = " ", *args, **kwargs):
    """
    Create a mixin class that applies the `drf_spectacular.utils.extend_schema` decorator to the
    `put` and `patch` methods of views. `drf-spectacular` library already builds the whole documentation using
    swagger, but some details may not be totally correct, or maybe you want to add more information to it.
    They provide ways to handle this. When that is the case, you can easily use this function to generate
    a mixin that can be used to set these kind of customizations. It receives the following arguments:
    
    `summary` -> A `str`, which is a brief description of what that endpoint does.
    `description` -> Also a `str`, which can be used to provide further details on the behavior of the
    endpoint.
    `*args, **kwargs` -> Any other parameters that `@extend_schema` expects.
    """
    class UpdateDocsMixin:
        """
        Documentation for `put` and `patch` requests on views that are used to update data
        """
        @extend_schema(summary=summary, description=description, *args, **kwargs)
        def put(self, request, *args, **kwargs):
            return super().put(request, *args, **kwargs)

        @extend_schema(summary=summary, description=description, *args, **kwargs)
        def patch(self, request, *args, **kwargs):
            return super().patch(request, *args, **kwargs)

    return UpdateDocsMixin


def build_destroy_docs(summary: str = " ", description: str = " ", *args, **kwargs):
    """
    Create a mixin class that applies the `drf_spectacular.utils.extend_schema` decorator to the
    `delete` method of views. `drf-spectacular` library already builds the whole documentation using
    swagger, but some details may not be totally correct, or maybe you want to add more information to it.
    They provide ways to handle this. When that is the case, you can easily use this function to generate
    a mixin that can be used to set these kind of customizations. It receives the following arguments:
    
    `summary` -> A `str`, which is a brief description of what that endpoint does.
    `description` -> Also a `str`, which can be used to provide further details on the behavior of the
    endpoint.
    `*args, **kwargs` -> Any other parameters that `@extend_schema` expects.
    """
    class DestroyDocsMixin:
        """
        Documentation for `delete` requests on views that are used to destroy data
        """
        @extend_schema(summary=summary, description=description, *args, **kwargs)
        def delete(self, request, *args, **kwargs):
            return super().delete(request, *args, **kwargs)

    return DestroyDocsMixin


def build_list_create_docs(
    summaries: dict = {},
    descriptions: dict = {},
    parameters: list[OpenApiParameter] = [],
    *args,
    **kwargs
):
    """
    Just a combination of `build_list_docs` and `build_create_docs`. Returns a single mixin, that combine
    both `ListDocsMixin` and `CreateDocsMixin`, which are the return values of these two functions, respectively.
    It may come in handy for `ListCreate` views. It receives the following arguments:
    
    `summaries` -> A `dict`, containing the summaries of each endpoint, where the keys are any of `["list", "create"]`, 
    and the values are the summaries.
    `description` -> A `dict`, containing the desciptions of each endpoint, where the keys are any of `["list", "create"]`, 
    and the values are the desciptions.
    `parameters` -> A `list` filled with values of type `OpenApiParameter`, to be used on the `list` endpoint.
    `*args, **kwargs` -> Any other parameters that `@extend_schema` expects (note that this will be applied to both methods).
    """
    actions = ["list", "create"]
    _check_keys_by_action(summaries, descriptions, actions)

    ListDocsMixin = build_list_docs(
        summaries["list"], descriptions["list"], parameters, *args, **kwargs
    )
    CreateDocsMixin = build_create_docs(
        summaries["create"], descriptions["create"], *args, **kwargs
    )

    class ListCreateDocsMixin(ListDocsMixin, CreateDocsMixin):
        ...

    return ListCreateDocsMixin


def build_retrieve_update_destroy_docs(
    summaries: dict = {}, descriptions: dict = {}, *args, **kwargs
):
    """
    Just a combination of `build_retrieve_docs` and `build_update_docs` and `build_destroy_docs`. Returns a single
    mixin, that combine `RetrieveDocsMixin`, `UpdateDocsMixin` and `DestroyDocsMixin`, which are the return values
    of these three functions, respectively. It may come in handy for `RetrieveUpdateDestroy` views. It receives the
    following arguments:
    
    `summaries` -> A `dict`, containing the summaries of each endpoint, where the keys are any of `["retrieve", "update", "destroy"]`, 
    and the values are the summaries.
    `description` -> A `dict`, containing the desciptions of each endpoint, where the keys are any of `["retrieve", "update", "destroy"]`, 
    and the values are the desciptions.
    `*args, **kwargs` -> Any other parameters that `@extend_schema` expects (note that this will be applied to all methods).
    """
    actions = ["retrieve", "update", "destroy"]
    _check_keys_by_action(summaries, descriptions, actions)

    RetrieveDocsMixin = build_retrieve_docs(summaries["retrieve"], *args, **kwargs)
    UpdateDocsMixin = build_update_docs(summaries["update"], *args, **kwargs)
    DestroyDocsMixin = build_destroy_docs(
        summaries["destroy"], descriptions["destroy"], *args, **kwargs
    )

    class RetrieveUpdateDestroyDocsMixin(
        RetrieveDocsMixin, UpdateDocsMixin, DestroyDocsMixin
    ):
        ...

    return RetrieveUpdateDestroyDocsMixin


def build_docs(
    summaries: dict = {},
    descriptions: dict = {},
    parameters: list[OpenApiParameter] = [],
    *args,
    **kwargs
):
    """
    Return a tuple of five mixins, each of which are built using `build_list_docs`, `build_create_docs`
    `build_retrieve_docs`, `build_update_docs` and `build_destroy_docs`, respectively. It receives the following arguments:
    
    `summaries` -> A `dict`, containing the summaries of each endpoint, where the keys are any of
    `["list", "create", "retrieve", "update", "destroy"]`, and the values are the summaries.
    `description` -> A `dict`, containing the desciptions of each endpoint, where the keys are any of
    `["list", "create", "retrieve", "update", "destroy"]`, and the values are the desciptions.
    `parameters` -> A `list` filled with values of type `OpenApiParameter`, to be used on the `list` endpoint.
    `*args, **kwargs` -> Any other parameters that `@extend_schema` expects (note that this will be applied to all methods).
    """
    actions = ["list", "create", "retrieve", "update", "destroy"]
    _check_keys_by_action(summaries, descriptions, actions)

    ListDocsMixin = build_list_docs(
        summaries["list"], descriptions["list"], parameters, *args, **kwargs
    )

    CreateDocsMixin = build_create_docs(
        summaries["create"], descriptions["create"], *args, **kwargs
    )

    RetrieveDocsMixin = build_retrieve_docs(
        summaries["retrieve"], descriptions["retrieve"], *args, **kwargs
    )

    UpdateDocsMixin = build_update_docs(
        summaries["update"], descriptions["update"], *args, **kwargs
    )

    DestroyDocsMixin = build_destroy_docs(
        summaries["destroy"], descriptions["destroy"], *args, **kwargs
    )

    return (
        ListDocsMixin,
        CreateDocsMixin,
        RetrieveDocsMixin,
        UpdateDocsMixin,
        DestroyDocsMixin,
    )


def build_docs_by_group(
    summaries: dict = {},
    descriptions: dict = {},
    parameters: list[OpenApiParameter] = [],
    *args,
    **kwargs
):
    """
    Return a tuple with two mixins, which of which are built using `build_list_create_docs` and
    `build_retrieve_update_destroy_docs`, respectively. This may come in handy in those cases where
    you have two classes, one is a `ListCreateView` and the other is a `RetrieveUpdateDestroyView`.
    It receives the following arguments:
    
    `summaries` -> A `dict`, containing the summaries of each endpoint, where the keys are any of
    `["list", "create", "retrieve", "update", "destroy"]`, and the values are the summaries.
    `description` -> A `dict`, containing the desciptions of each endpoint, where the keys are any of
    `["list", "create", "retrieve", "update", "destroy"]`, and the values are the desciptions.
    `parameters` -> A `list` filled with values of type `OpenApiParameter`, to be used on the `list` endpoint.
    `*args, **kwargs` -> Any other parameters that `@extend_schema` expects (note that this will be applied to all methods).
    """
    ListCreateDocs = build_list_create_docs(
        summaries, descriptions, parameters, *args, **kwargs
    )
    RetrieveUpdateDestroyDocs = build_retrieve_update_destroy_docs(
        summaries, descriptions, *args, **kwargs
    )

    return (ListCreateDocs, RetrieveUpdateDestroyDocs)


def build_full_docs(
    summaries: dict = {},
    descriptions: dict = {},
    parameters: list[OpenApiParameter] = [],
    *args,
    **kwargs
):
    """
    Return a single mixin, that is a combination of both `ListCreateDocs` and `RetrieveUpdateDestroyDocs`,
    which `build_docs_by_group` returns. It receives the following arguments:
    
    `summaries` -> A `dict`, containing the summaries of each endpoint, where the keys are any of
    `["list", "create", "retrieve", "update", "destroy"]`, and the values are the summaries.
    `description` -> A `dict`, containing the desciptions of each endpoint, where the keys are any of
    `["list", "create", "retrieve", "update", "destroy"]`, and the values are the desciptions.
    `parameters` -> A `list` filled with values of type `OpenApiParameter`, to be used on the `list` endpoint.
    `*args, **kwargs` -> Any other parameters that `@extend_schema` expects (note that this will be applied to all methods).
    """
    (ListCreateDocs, RetrieveUpdateDestroyDocs) = build_docs_by_group(
        summaries, descriptions, parameters, *args, **kwargs
    )

    class FullDocsMixin(ListCreateDocs, RetrieveUpdateDestroyDocs):
        ...

    return FullDocsMixin


def _check_keys_by_action(summaries: dict, descriptions: dict, actions_list: list[str]):
    for action in actions_list:
        try:
            summaries[action]
        except KeyError:
            summaries[action] = " "
        try:
            descriptions[action]
        except KeyError:
            descriptions[action] = " "
