"""
This module provides useful mixins to be used in Django Rest Framework **generic views** and **viewsets**.
"""

from django.http import Http404
from rest_framework.serializers import Serializer

from .helpers import get_list_or_error


class SerializerByMethodMixin:
    """
    This mixin overrides the `get_serializer_class` method of generic views. It's
    purpose is to dinamically define which serializer to use, depending on the request
    method. For this to be possible, a new class property should be set, it is:

    - `method_serializers` -> It should be a dictionary having it's keys with the names
    of http methods and values as the serializer classes corresponding to each method.
    If the request method does not match any of the dict keys, it will return the value
    of `self.serializer_class`.

    Below is an example:

    ---

    ```python

    # views.py

    class MyBeautifulGenericView(SerializerByMethodMixin, ListCreateAPIView):
        queryset = MyWonderfulModel.objects.all()
        serializer_class = MyDefaultSerializer
        method_serializers = {
            "GET": MySerialzerToUseInGetRequests,
        }
    ```
    """

    method_serializers: dict[str, Serializer] = None

    def get_serializer_class(self):
        return self.method_serializers.get(self.request.method, self.serializer_class)


class SerializerByActionMixin:
    """
    This mixin overrides the `get_serializer_class` method of viewsets. It's
    purpose is to dinamically define which serializer to use, depending on the viewset
    action. For this to be possible, a new class property should be set, it is:

    - `action_serializers` -> It should be a dictionary having it's keys with the names
    of viewset actions and values as the serializer classes corresponding to each action.
    If the viewset action does not match any of the dict keys, it will return the value
    of `self.serializer_class`.

    Below is an example:

    ---

    ```python

    # views.py

    class MyBeautifulViewSet(SerializerByActionMixin, ModelViewSet):
        queryset = MyWonderfulModel.objects.all()
        serializer_class = MyDefaultSerializer
        action_serializers = {
            "create": MySerializerToUseInCreateActions,
            "update": MySerialzerToUseInUpdateActions,
            "partial_update": MySerialzerToUseInPartialUpdateActions,
        }
    ```
    """

    action_serializers: dict[str, Serializer] = None

    def get_serializer_class(self):
        return self.action_serializers.get(self.action, self.serializer_class)


class SerializerByDetailActionsMixin:
    """
    This mixin overrides the `get_serializer_class` method of viewsets. It's
    purpose is to dinamically define which serializer to use, depending on the viewset
    action. If it is a detail action, that is, one of `retrieve`, `update`, `partial_update`
    and `destroy`, then `self.detail_serializer_class` will be returned. Else, the default
    `self.serializer_class` is used. For this to be possible, a new class property should
    be set, it is:

    - `detail_serializer_class` -> It's value should be a serializer class. This property defines
    which serializer to use in detail actions.

    Below is an example:

    ---

    ```python

    # views.py

    class MyBeautifulViewSet(SerializerByDetailActionsMixin, ModelViewSet):
        queryset = MyWonderfulModel.objects.all()
        serializer_class = MyDefaultSerializer
        detail_serializer_class = MyDetailSerializer
    ```
    """

    detail_serializer_class: Serializer = None

    def get_serializer_class(self):
        DETAIL_ACTIONS = ["retrieve", "update", "partial_update", "destroy"]

        if self.action in DETAIL_ACTIONS:
            return self.detail_serializer_class

        return self.serializer_class


class SerializerBySafeActionsMixin:
    """
    This mixin overrides the `get_serializer_class` method of viewsets. It's
    purpose is to dinamically define which serializer to use, depending on the viewset
    action. If it is a _safe action_, then `self.safe_serializer_class` will be returned.
    Else, the default `self.serializer_class` is returned. A safe action is an action
    listed in the `safe_actions` class property. For this to be possible, a new class
    property should be set, it is:

    - `safe_serializer_class` -> Its value should be a serializer class. This property defines
    which serializer to use in safe actions.

    You can totally customize what is a "safe action". For that, you could change the value
    of `self.safe_actions`.

    - `safe_actions` -> It should be a `list[str]`, which each item representing a viewset action,
    considered safe for that viewset. The default value is `["list", "retrieve"]`

    Below is an example:

    ---

    ```python

    # views.py

    class MyBeautifulViewSet(SerializerBySafeActionsMixin, ModelViewSet):
        queryset = MyWonderfulModel.objects.all()
        serializer_class = MyDefaultSerializer
        safe_serializer_class = MySafeSerializer
    ```
    """

    safe_actions: list[str] = ["list", "retrieve"]
    safe_serializer_class: Serializer = None

    def get_serializer_class(self):
        if self.action in self.safe_actions:
            return self.safe_serializer_class

        return self.serializer_class


class FilterQuerysetMixin:
    """
    This mixin overrides the `get_queryset` method of class based views. It's main goal is
    to make it easier and simpler to filter and/or narrow down results. You may use it to
    attach results to the logged in user, to filter the queryset by route params (or `kwargs`)
    and by query params.

    These are the class properties that this mixin accepts:

    - `filter_user_key` -> A `str` representing which keyword argument should be used for filtering by
    user. The default is `None`, meaning that the queryset will not be filtered by the logged in user, that
    is, `self.request.user`. If in your queryset there is a `FK` pointing to your project's auth user model, then this property should
    have the same name as this `FK` field.
    - `filter_kwargs` -> A `dict[str, str]`, where the **key** represents the name of the **field** to be searched,
    and the **value** is the **url param**.
    - `filter_query_params` -> A `dict[str, str]`, where the **key** is the name of the **field** to be searched,
    and the **value** represents the **query param** received in the request.
    - `filter_exception_klass` -> Should be an `exception` inheriting from `rest_framework.exceptions.APIException`. The
    default value is `django.http.Http404`. In case any kind of error occurs, this exception will be raised.
    - `filter_accept_empty` -> A `bool`, which defaults to `True`. If `False`, then the `filter_exception_klass` will be raised
    in case the results are empty. Otherwise, an empty value will be returned normaly.

    Below is an example of how this might be useful:

    ---

    ```python

    # request endpoint

    "/categories/<category_id>/transactions/"


    # views.py

    from power_tools.mixins import FilterQuerysetMixin

    class TransactionView(FilterQuerysetMixin, ListCreateAPIView):
        serializer_class = TransactionSerializer
        permission_classes = [IsAuthenticated]
        filter_user_key = "user"
        filter_kwargs = {"category": "category_id"}
        filter_query_params = {
            "month_id": "month_id",
            "month__number": "month_number",
            "month__name__icontains": "month_name",
            "month__year": "year",
            "description__icontains": "description",
            "value": "value",
            "value__gte": "value_gte",
            "value__lte": "value_lte",
            "is_income": "is_income",
            "is_recurrent": "is_recurrent",
            "installments": "installments",
        }

    ```

    ---

    In the example above, we are defining a view for monetary transactions. We don't want
    users to see other user's transactions, so we attach all transactions to the logged in
    user. By using the `filter_user_key` class property, we tell the mixin that when filtering the
    queryset, it should use `user=self.request.user`.

    Also, all transactions have categories. And we want them always to be listed by category.
    So in the url, we receive the `<category_id>` param. So that's why we declare `filter_kwargs`
    in that way.

    As for the `filter_query_params` property, please note how interesting it is. In the keys of
    the dictionary, we pass in the keys that will be used for filtering the queryset, just as if
    we were filtering the queryset manually. None of these query params are mandatory.

    We are not declaring `filter_accept_empty`, which means that we will not raise `filter_exception_klass` in
    any case. So that's why we don't need to define `filter_exception_klass` too.

    You may have noticed that the `queryset` class property haven't been defined. That's not a
    problem, because this mixin guesses what is the apropriated model by accessing `self.serializer_class.Meta.model`.
    So as long as you define you model in that way, everything is OK.

    """

    filter_user_key = None
    filter_kwargs = {}
    filter_query_params = {}
    filter_exception_klass = Http404
    filter_accept_empty = True

    def get_queryset(self, **extra_filters):
        klass = self.serializer_class.Meta.model

        queryset_filters = (
            {self.filter_user_key: self.request.user} if self.filter_user_key else {}
        )

        queryset_filters.update(
            {key: self.kwargs.get(value) for key, value in self.filter_kwargs.items()},
        )

        for key, query_param in self.filter_query_params.items():
            value = self.request.GET.get(query_param)
            if value:
                queryset_filters.update({key: value})

        queryset_filters.update(**extra_filters)

        return get_list_or_error(
            klass=klass,
            error_klass=self.filter_exception_klass,
            accept_empty=self.filter_accept_empty,
            **queryset_filters
        )


class AttachUserOnCreateMixin:
    """
    This mixin overrides the `perform_create` method of generic views, and simply passes to the serializer
    `save` method an additional keyword argument. This attaches the current user to the `validated_data`
    argument on the serializer's `create` method. You can pass the following class property:

    `attach_user_key` -> A `str`, which defaults to `None`. It represents which is the name of the field
    that points to the user on your model. If ommited, it will try to get the value of `self.filter_user_key`.

    So in case you are already using this module's `FilterQuerysetMixin`, and is using this property, then there
    is no need to repeat yourself here. But in case neither `self.attach_user_key` or `self.filter_user_key` are
    found, then `"user"` is used by default.

    Here is a quick example:

    ```python

    from power_tools.mixins import AttachUserOnCreateMixin
    from rest_framework import generics
    from rest_framework import permissions

    from .serializers import CinemaSerializer

    class CinemaView(AttachUserOnCreateMixin, generics.ListCreateAPIView):
        serializer_class = CinemaSerializer
        permission_classes = [permissions.IsAuthenticated]
        attach_user_key = "owner"

    ```

    This simple trick makes it possible to attach an user to a `Cinema` instance very easily. In this case, we are
    defining `attach_user_key` as `"owner"`, because on the `Cinema` model, the foreign key field that relates to
    the user model, has this name.
    """

    attach_user_key: str = None

    def perform_create(self, serializer):
        user_key = self.attach_user_key or self.filter_user_key or "user"
        serializer.save(**{user_key: self.request.user})


class AttachUserOnUpdateMixin:
    """
    This mixin overrides the `perform_update` method of generic views, and simply passes to the serializer
    `save` method an additional keyword argument. This attaches the current user to the `validated_data`
    argument on the serializer's `update` method. You can pass the following class property:

    `attach_user_key` -> A `str`, which defaults to `None`. It represents which is the name of the field
    that points to the user on your model. If ommited, it will try to get the value of `self.filter_user_key`.

    So in case you are already using this module's `FilterQuerysetMixin`, and is using this property, then there
    is no need to repeat yourself here. But in case neither `self.attach_user_key` or `self.filter_user_key` are
    found, then `"user"` is used by default.

    Here is a quick example:

    ```python

    from power_tools.mixins import AttachUserOnUpdateMixin
    from rest_framework import generics
    from rest_framework import permissions

    from .serializers import CinemaSerializer

    class CinemaView(AttachUserOnUpdateMixin, generics.ListCreateAPIView):
        serializer_class = CinemaSerializer
        permission_classes = [permissions.IsAuthenticated]
        attach_user_key = "owner"

    ```

    This simple trick makes it possible to attach an user to a `Cinema` instance very easily. In this case, we are
    defining `attach_user_key` as `"owner"`, because on the `Cinema` model, the foreign key field that relates to
    the user model, has this name.
    """

    attach_user_key: str = None

    def perform_update(self, serializer):
        user_key = self.attach_user_key or self.filter_user_key or "user"
        serializer.save(**{user_key: self.request.user})


class AttachUserToReqDataMixin(AttachUserOnCreateMixin, AttachUserOnUpdateMixin):
    """
    This mixin overrides both the `perform_create` and `perform_update` methods of generic views, and simply passes
    to the serializer's `save` method an additional keyword argument. This attaches the current user to the `validated_data`
    argument on the serializer's `update` method. You can pass the following class property:

    `attach_user_key` -> A `str`, which defaults to `None`. It represents which is the name of the field
    that points to the user on your model. If ommited, it will try to get the value of `self.filter_user_key`.

    So in case you are already using this module's `FilterQuerysetMixin`, and is using this property, then there
    is no need to repeat yourself here. But in case neither `self.attach_user_key` or `self.filter_user_key` are
    found, then `"user"` is used by default.

    Here is a quick example:

    ```python

    from power_tools.mixins import AttachUserOnUpdateMixin
    from rest_framework import generics
    from rest_framework import permissions

    from .serializers import CinemaSerializer

    class CinemaView(AttachUserOnUpdateMixin, generics.ListCreateAPIView):
        serializer_class = CinemaSerializer
        permission_classes = [permissions.IsAuthenticated]
        attach_user_key = "owner"

    ```

    This simple trick makes it possible to attach an user to a `Cinema` instance very easily. In this case, we are
    defining `attach_user_key` as `"owner"`, because on the `Cinema` model, the foreign key field that relates to
    the user model, has this name.
    """
