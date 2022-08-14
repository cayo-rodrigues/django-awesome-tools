class SerializerByMethodMixin:
    def get_serializer_class(self):
        return self.method_serializers.get(self.request.method, self.serializer_class)


class SerializerByActionMixin:
    def get_serializer_class(self):
        return self.action_serializers.get(self.action, self.serializer_class)


class SerializerByDetailActionsMixin:
    def get_serializer_class(self):
        DETAIL_ACTIONS = ["retrieve", "update", "partial_update", "destroy"]

        if self.action in DETAIL_ACTIONS:
            return self.detail_serializer_class

        return self.serializer_class


class SerializerBySafeActionsMixin:
    def get_serializer_class(self):
        SAFE_ACTIONS = self.safe_actions or ["list", "retrieve"]

        if self.action in SAFE_ACTIONS:
            return self.safe_serializer_class

        return self.serializer_class
