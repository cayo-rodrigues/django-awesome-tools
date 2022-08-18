"""
This module provides useful mixins to be used in Django Rest Framework **generic views** and **viewsets**.
"""

from rest_framework.serializers import Serializer


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
