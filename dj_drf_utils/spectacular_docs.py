from drf_spectacular.utils import OpenApiParameter, extend_schema


def build_list_docs(
    summary: str = " ",
    description: str = " ",
    parameters: list[OpenApiParameter] = [],
    *args,
    **kwargs
):
    class ListDocsMixin:
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
    class CreateDocsMixin:
        @extend_schema(summary=summary, description=description, *args, **kwargs)
        def post(self, request, *args, **kwargs):
            return super().post(request, *args, **kwargs)

    return CreateDocsMixin


def build_retrieve_docs(summary: str = " ", description: str = " ", *args, **kwargs):
    class RetrieveDocsMixin:
        @extend_schema(summary=summary, description=description, *args, **kwargs)
        def get(self, request, *args, **kwargs):
            return super().get(request, *args, **kwargs)

    return RetrieveDocsMixin


def build_update_docs(summary: str = " ", description: str = " ", *args, **kwargs):
    class UpdateDocsMixin:
        @extend_schema(summary=summary, description=description, *args, **kwargs)
        def put(self, request, *args, **kwargs):
            return super().put(request, *args, **kwargs)

        @extend_schema(summary=summary, description=description, *args, **kwargs)
        def patch(self, request, *args, **kwargs):
            return super().patch(request, *args, **kwargs)

    return UpdateDocsMixin


def build_destroy_docs(summary: str = " ", description: str = " ", *args, **kwargs):
    class DestroyDocsMixin:
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
