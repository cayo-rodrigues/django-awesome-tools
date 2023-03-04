"""
This module provides a set of useful and simple to use functions for building documentation mixins.
But wait, what is a "documentation mixin"? The `drf-spectacular` package has a wonderful feature of
automatically generating a swagger documentation, based on your project views, with minimum configurations
on `settings.py` and `urls.py`. But maybe you want to give more details on how each view and endpoint works,
such as a brief summary, a detailed description, or maybe specify which query parameters it accepts. For that,
`drf-spectacular` library provides some ways for us to apply such customizations.

Among them, is the `drf_spectacular.utils` module. It has a decorator called `extend_schema`, which can be used
to decorate view methods that correspond to http methods, like `get`, `post` and so forth. It accepts many arguments.

The functions defined in this module use this decorator to build mixins that can be easily aplied to any class based view.
It is recommended to put these mixins on the far left of your views inheritance list, as show in the examples below.
"""

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
    `get` method of views. It receives the following arguments:
    
    `summary` -> A `str`, which is a brief description of what that endpoint does.
    `description` -> Also a `str`, which can be used to provide further details on the behavior of the
    endpoint.
    `parameters` -> A `list` filled with values of type `OpenApiParameter`.
    `*args, **kwargs` -> Any other parameters that `@extend_schema` expects.
    
    Here's an example:
    
    ```python
    
    from dj_drf_utils.docs import build_list_docs
    from drf_spectacular.utils import OpenApiParameter

    summary = "A wonderful and brief description of the list action on an endpoint"

    description = (
        "A more detailed description of the list action and some tips on how to use it. "
        "Here I could add anything more that I may wish to appear on swagger."
    )
    
    parameters = [
        OpenApiParameter("param1", int, description="A brief description of my int query param"),
        OpenApiParameter("param2", bool, description="A brief description of my bool query param"),
    ]

    MyListViewDocsMixin = build_list_docs(summary, description, parameters)
    ```
    
    ---
    
    ```python
    
    # views.py
    
    class MyListView(MyListViewDocsMixin, ListAPIView):
        # view stuff
        ...
    ```
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
    `post` method of views. It receives the following arguments:
    
    `summary` -> A `str`, which is a brief description of what that endpoint does.
    `description` -> Also a `str`, which can be used to provide further details on the behavior of the
    endpoint.
    `*args, **kwargs` -> Any other parameters that `@extend_schema` expects.
    
    Here's an example:
    
    ```python
    
    from dj_drf_utils.docs import build_create_docs

    summary = "A wonderful and brief description of the create action on an endpoint"

    description = (
        "A more detailed description of the create action and some tips on how to use it. "
        "Here I could add anything more that I may wish to appear on swagger."
    )

    MyCreateViewDocsMixin = build_create_docs(summary, description)
    ```
    
    ---
    
    ```python
    
    # views.py
    
    class MyCreateView(MyCreateViewDocsMixin, CreateAPIView):
        # view stuff
        ...
    ```
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
    
    Here's an example:
    
    ```python
    
    from dj_drf_utils.docs import build_retrieve_docs

    summary = "A wonderful and brief description of the retrieve action on an endpoint"

    description = (
        "A more detailed description of the retrieve action and some tips on how to use it. "
        "Here I could add anything more that I may wish to appear on swagger."
    )

    MyRetrieveViewDocsMixin = build_retrieve_docs(summary, description)
    ```
    
    ---
    
    ```python
    
    # views.py
    
    class MyRetrieveView(MyRetrieveViewDocsMixin, RetrieveAPIView):
        # view stuff
        ...
    ```
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
    `put` and `patch` methods of views. It receives the following arguments:
    
    `summary` -> A `str`, which is a brief description of what that endpoint does.
    `description` -> Also a `str`, which can be used to provide further details on the behavior of the
    endpoint.
    `*args, **kwargs` -> Any other parameters that `@extend_schema` expects.
    
    Here's an example:
    
    ```python
    
    from dj_drf_utils.docs import build_update_docs

    summary = "A wonderful and brief description of the update action on an endpoint"

    description = (
        "A more detailed description of the update action and some tips on how to use it. "
        "Here I could add anything more that I may wish to appear on swagger."
    )

    MyUpdateViewDocsMixin = build_update_docs(summary, description)
    ```
    
    ---
    
    ```python
    
    # views.py
    
    class MyUpdateView(MyUpdateViewDocsMixin, UpdateAPIView):
        # view stuff
        ...
    ```
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
    `delete` method of views. It receives the following arguments:
    
    `summary` -> A `str`, which is a brief description of what that endpoint does.
    `description` -> Also a `str`, which can be used to provide further details on the behavior of the
    endpoint.
    `*args, **kwargs` -> Any other parameters that `@extend_schema` expects.
    
    Here's an example:
    
    ```python
    
    from dj_drf_utils.docs import build_destroy_docs

    summary = "A wonderful and brief description of the destroy action on an endpoint"

    description = (
        "A more detailed description of the destroy action and some warnings about its use. "
        "Here I could add anything more that I may wish to appear on swagger."
    )

    MyDestroyViewDocsMixin = build_destroy_docs(summary, description)
    ```
    
    ---
    
    ```python
    
    # views.py
    
    class MyDestroyView(MyDestroyViewDocsMixin, DestroyAPIView):
        # view stuff
        ...
    ```
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
    `descriptions` -> A `dict`, containing the desciptions of each endpoint, where the keys are any of `["list", "create"]`, 
    and the values are the desciptions.
    `parameters` -> A `list` filled with values of type `OpenApiParameter`, to be used on the `list` endpoint.
    `*args, **kwargs` -> Any other parameters that `@extend_schema` expects (note that this will be applied to both methods).
    
    Here's an example:
    
    ```python
    
    from dj_drf_utils.docs import build_list_create_docs
    from drf_spectacular.utils import OpenApiParameter

    summaries = {
        "list": "A wonderful and brief description of the list action on an endpoint",
        "create": "A wonderful and brief description of the create action on an endpoint",
    }

    descriptions = {
        "create": (
            "A more detailed description of the create action and some tips on how to use it. "
            "Here I could add anything more that I may wish to appear on swagger."
        )
    }
    
    parameters = [
        OpenApiParameter("param1", int, description="A brief description of my int query param"),
        OpenApiParameter("param2", bool, description="A brief description of my bool query param"),
    ]

    MyViewDocsMixin = build_list_create_docs(summaries, descriptions, parameters)
    ```
    
    ---
    
    ```python
    
    # views.py
    
    class MyView(MyViewDocsMixin, ListCreateAPIView):
        # view stuff
        ...
    ```
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
    `descriptions` -> A `dict`, containing the desciptions of each endpoint, where the keys are any of `["retrieve", "update", "destroy"]`, 
    and the values are the desciptions.
    `*args, **kwargs` -> Any other parameters that `@extend_schema` expects (note that this will be applied to all methods).
    
    Here's an example:
    
    ```python
    
    from dj_drf_utils.docs import build_retrieve_update_destroy_docs

    summaries = {
        "retrieve": "A wonderful and brief description of the retrieve action on an endpoint",
        "update": "A wonderful and brief description of the update action on an endpoint",
        "destroy": "A wonderful and brief description of the delete action on an endpoint",
    }

    descriptions = {
        "destroy": (
            "A long description of the destroy action and a warning about its consequences"
            "Here I could add anything more that I may wish to appear on swagger."
        )
    }

    MyDetailViewDocsMixin = build_retrieve_update_destroy_docs(summaries, descriptions)
    ```
    
    ---
    
    ```python
    
    # views.py
    
    class MyDetailView(MyDetailViewDocsMixin, RetrieveUpdateDestroyAPIView):
        # view stuff
        ...
    ```
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
    `descriptions` -> A `dict`, containing the desciptions of each endpoint, where the keys are any of
    `["list", "create", "retrieve", "update", "destroy"]`, and the values are the desciptions.
    `parameters` -> A `list` filled with values of type `OpenApiParameter`, to be used on the `list` endpoint.
    `*args, **kwargs` -> Any other parameters that `@extend_schema` expects (note that this will be applied to all methods).
    
    Here's an example:
    
    ```python
    
    from dj_drf_utils.docs import build_docs
    from drf_spectacular.utils import OpenApiParameter

    summaries = {
        "list": "A wonderful and brief description of the list action on an endpoint",
        "create": "A wonderful and brief description of the create action on an endpoint",
        "retrieve": "A wonderful and brief description of the retrieve action on an endpoint",
        "update": "A wonderful and brief description of the update action on an endpoint",
        "destroy": "A wonderful and brief description of the delete action on an endpoint",
    }

    descriptions = {
        "destroy": (
            "A long description of the destroy action and a warning about its consequences"
            "Here I could add anything more that I may wish to appear on swagger."
        )
    }
    
    parameters = [
        OpenApiParameter("param1", int, description="A brief description of my int query param"),
        OpenApiParameter("param2", bool, description="A brief description of my bool query param"),
    ]

    (
        MyListViewDocsMixin,
        MyCreateViewDocsMixin,
        MyRetrieveViewDocsMixin
        MyUpdateViewDocsMixin,
        MyDestroyViewDocsMixin,
    ) = build_docs(summaries, descriptions, parameters)
    ```
    
    ---
    
    ```python
    
    # views.py
    
    class MyListView(MyListViewDocsMixin, ListAPIView):
        # view stuff
        ...
    
    class MyCreateView(MyCreateViewDocsMixin, CreateAPIView):
        # view stuff
        ...
    
    # and so forth...
    ```
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
    `descriptions` -> A `dict`, containing the desciptions of each endpoint, where the keys are any of
    `["list", "create", "retrieve", "update", "destroy"]`, and the values are the desciptions.
    `parameters` -> A `list` filled with values of type `OpenApiParameter`, to be used on the `list` endpoint.
    `*args, **kwargs` -> Any other parameters that `@extend_schema` expects (note that this will be applied to all methods).
    
    Here's an example:
    
    ```python
    
    from dj_drf_utils.docs import build_docs_by_group
    from drf_spectacular.utils import OpenApiParameter

    summaries = {
        "list": "A wonderful and brief description of the list action on an endpoint",
        "create": "A wonderful and brief description of the create action on an endpoint",
        "retrieve": "A wonderful and brief description of the retrieve action on an endpoint",
        "update": "A wonderful and brief description of the update action on an endpoint",
        "destroy": "A wonderful and brief description of the delete action on an endpoint",
    }

    descriptions = {
        "destroy": (
            "A long description of the destroy action and a warning about its consequences"
            "Here I could add anything more that I may wish to appear on swagger."
        )
    }
    
    parameters = [
        OpenApiParameter("param1", int, description="A brief description of my int query param"),
        OpenApiParameter("param2", bool, description="A brief description of my bool query param"),
    ]

    (
        MyViewDocsMixin,
        MyDetailViewDocsMixin,
    ) = build_docs_by_group(summaries, descriptions, parameters)
    ```
    
    ---
    
    ```python
    
    # views.py
    
    class MyView(MyViewDocsMixin, ListCreateAPIView):
        # view stuff
        ...
    ```
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
    `descriptions` -> A `dict`, containing the desciptions of each endpoint, where the keys are any of
    `["list", "create", "retrieve", "update", "destroy"]`, and the values are the desciptions.
    `parameters` -> A `list` filled with values of type `OpenApiParameter`, to be used on the `list` endpoint.
    `*args, **kwargs` -> Any other parameters that `@extend_schema` expects (note that this will be applied to all methods).
    
        
    Here's an example:
    
    ```python
    
    from dj_drf_utils.docs import build_full_docs
    from drf_spectacular.utils import OpenApiParameter

    summaries = {
        "list": "A wonderful and brief description of the list action on an endpoint",
        "create": "A wonderful and brief description of the create action on an endpoint",
        "retrieve": "A wonderful and brief description of the retrieve action on an endpoint",
        "update": "A wonderful and brief description of the update action on an endpoint",
        "destroy": "A wonderful and brief description of the delete action on an endpoint",
    }

    descriptions = {
        "destroy": (
            "A long description of the destroy action and a warning about its consequences"
            "Here I could add anything more that I may wish to appear on swagger."
        )
    }
    
    parameters = [
        OpenApiParameter("param1", int, description="A brief description of my int query param"),
        OpenApiParameter("param2", bool, description="A brief description of my bool query param"),
    ]

    MyViewFullDocsMixin = build_full_docs(summaries, descriptions, parameters)

    ```
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
