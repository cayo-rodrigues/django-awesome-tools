"""
This module provides a set of useful mixins that may be used for cache management. It also provides a function
for building your own custom mixins.
"""

from custom_cache_page.cache import cache_page
from django.conf import settings
from django.http import HttpRequest
from django.utils.decorators import method_decorator

from .helpers import gen_cache_group, gen_cache_key, handle_delete_cache


def build_cache_mixins(
    cache_ttl: int = getattr(settings, "CACHE_TTL", 60 * 10),
    vary_on_headers: tuple = (),
    vary_on_user: bool = False,
):
    """
    This function returns a tuple of mixins used for cache management. It receives the following arguments:

    - `cache_ttl` -> The ttl(time to live) for the cache is by default whatever you
    set in the `CACHE_TTL` variable at your project's `settings.py`, but you can totally override this here.
    In case `CACHE_TTL` is not present in `settings.py`, then it defaults to 10 minutes.
    The value of `cache_ttl` must be an `int`. It represents the time that the cache will persist, **in seconds**.
    - `vary_on_headers` -> This argument is a `tuple` that refers to which headers should be used when generating
    the cache key and cache group.
    - `vary_on_user` -> A boolean value that determines if the cache key and cache group should be isolated for each user.

    It is important to note that, besides the value of `vary_on_headers` and `vary_on_user`, cache keys are generated
    based on the request path and query params, and cache groups are generated based on the request path.

    Here is a simple example of how you could use it:

    ```python

    from awesome_tools.cache import build_cache_mixins

    (
        SetCacheOnListByMyCoolHeaderMixin,
        EraseCacheOnCreateByMyCoolHeaderMixin,
        EraseCacheOnUpdateByMyCoolHeaderMixin,
        EraseCacheOnDestroyByMyCoolHeaderMixin,
        EraseCacheOnDetailByMyCoolHeaderMixin,
        ManageCacheByMyCoolHeaderMixin,
        FullManageCacheByMyCoolHeaderMixin,
    ) = build_cache_mixins(vary_on_headers=("my-cool-header",))

    ```

    ---

    In the example above, if the same request is made again on a cached view, but with a different value on `"my-cool-header"`
    header, then the view will not use the cached value, rather, it will cache the results also based on this header.

    Actually, that's just how the cache management mixins on this package are generated.
    """

    class SetCacheOnListMixin:
        """
        Caches the results of the `list` method of generic views and viewsets. After setting the cache,
        if the same request is fired again, then it will return the cached value, instead of doing the
        whole thing again.

        The cache ttl (time to live) is determined automatically by the `CACHE_TTL` value in your project's
        `settings.py` file, or by whatever ttl is passed to the `build_cache_mixins` function. It is important
        to note that the cache key is generated based on the request path and query params. Cache groups are
        generated based on the request path too. These things are also based on the `build_cache_mixins` function
        `vary_on_headers` and `vary_on_user` arguments values.

        Here is a simple example of how you could use this mixin.

        ```python

        from awesome_tools.cache import SetCacheOnListMixin
        from rest_framework.generics import ListAPIView


        class MyAwesomeListView(SetCacheOnListMixin, ListAPIView):
            # my awesome view stuff
            ...

        ```
        """

        @method_decorator(
            cache_page(
                timeout=cache_ttl,
                key_func=gen_cache_key(vary_on_headers, vary_on_user, timeout=cache_ttl),
                group_func=gen_cache_group(vary_on_headers, vary_on_user),
            )
        )
        def list(self, request: HttpRequest, *args, **kwargs):
            return super().list(request, *args, **kwargs)

    class EraseCacheOnCreateMixin:
        """
        Upon calling the `create` method of generic views and viewsets, erase the cache. But what cache?
        The cache related to the group this mixin belongs to. It is by default determined by the url path,
        but may vary based on user or any headers on the request, if these arguments are passed to the
        `build_cache_mixins` function.

        Here is an example:

        ```python

        from awesome_tools.cache import SetCacheOnListMixin, EraseCacheOnCreateMixin
        from rest_framework.generics import ListAPIView, CreateAPIView


        class MyAwesomeListView(SetCacheOnListMixin, ListAPIView):
            # my awesome view stuff
            ...

        class MyAwesomeCreateView(EraseCacheOnCreateMixin, CreateAPIView):
            # my awesome view stuff
            ...

        ```

        In the example above, when the create view is called, then it will erase any cache keys that were set
        by the list view, if there are any, but **only within the scope of the cache group**.
        """

        def create(self, request: HttpRequest, *args, **kwargs):
            response = super().create(request, *args, **kwargs)
            handle_delete_cache(request, vary_on_headers, vary_on_user)
            return response

    class EraseCacheOnUpdateMixin:
        """
        Upon calling the `update` or `partial_update` method of generic views and viewsets, erase the cache.
        But what cache? The cache related to the group this mixin belongs to. It is by default determined by
        the url path, but may vary based on user or any headers on the request, if these arguments are passed
        to the `build_cache_mixins` function.

        Here is an example:

        ```python

        from awesome_tools.cache import SetCacheOnListMixin, EraseCacheOnUpdateMixin
        from rest_framework.generics import ListAPIView, UpdateAPIView


        class MyAwesomeListView(SetCacheOnListMixin, ListAPIView):
            # my awesome view stuff
            ...

        class MyAwesomeUpdateView(EraseCacheOnUpdateMixin, UpdateAPIView):
            # my awesome view stuff
            ...

        ```

        In the example above, when the update view is called, then it will erase any cache keys that were set
        by the list view, if there are any, but **only within the scope of the cache group**.
        """

        def update(self, request, *args, **kwargs):
            response = super().update(request, *args, **kwargs)
            handle_delete_cache(request, vary_on_headers, vary_on_user)
            return response

        def partial_update(self, request, *args, **kwargs):
            response = super().partial_update(request, *args, **kwargs)
            handle_delete_cache(request, vary_on_headers, vary_on_user)
            return response

    class EraseCacheOnDestroyMixin:
        """
        Upon calling the `destroy`method of generic views and viewsets, erase the cache.
        But what cache? The cache related to the group this mixin belongs to. It is by default determined by
        the url path, but may vary based on user or any headers on the request, if these arguments are passed
        to the `build_cache_mixins` function.

        Here is an example:

        ```python

        from awesome_tools.cache import SetCacheOnListMixin, EraseCacheOnDestroyMixin
        from rest_framework.generics import ListAPIView, DestroyAPIView


        class MyAwesomeListView(SetCacheOnListMixin, ListAPIView):
            # my awesome view stuff
            ...

        class MyAwesomeDestroyView(EraseCacheOnDestroyMixin, DestroyAPIView):
            # my awesome view stuff
            ...

        ```

        In the example above, when the destroy view is called, then it will erase any cache keys that were set
        by the list view, if there are any, but **only within the scope of the cache group**.
        """

        def destroy(self, request, *args, **kwargs):
            response = super().destroy(request, *args, **kwargs)
            handle_delete_cache(request, vary_on_headers, vary_on_user)
            return response

    class EraseCacheOnDetailMixin(EraseCacheOnUpdateMixin, EraseCacheOnDestroyMixin):
        """
        Upon calling the `update`, `partial_update` or `destroy` method of generic views and viewsets, erase the cache.
        But what cache? The cache related to the group this mixin belongs to. It is by default determined by
        the url path, but may vary based on user or any headers on the request, if these arguments are passed
        to the `build_cache_mixins` function.

        Here is an example:

        ```python

        from awesome_tools.cache import SetCacheOnListMixin, EraseCacheOnDetailMixin
        from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView


        class MyAwesomeListView(SetCacheOnListMixin, ListAPIView):
            # my awesome view stuff
            ...

        class MyAwesomeDetailView(EraseCacheOnDetailMixin, RetrieveUpdateDestroyAPIView):
            # my awesome view stuff
            ...

        ```

        In the example above, when the detail view is called, then it will erase any cache keys that were set
        by the list view, if there are any, but **only within the scope of the cache group**.
        """

        ...

    class ManageCacheMixin(SetCacheOnListMixin, EraseCacheOnCreateMixin):
        """
        Upon calling the `list` method of the view, set the cache, but when calling the `create` method, then erase the cache.
        This mixin is essentially just a combination of both `SetCacheOnListMixin` and `EraseCacheOnCreateMixin`.

        Here is an example:

        ```python

        from awesome_tools.cache import ManageCacheMixin
        from rest_framework.generics import ListCreateAPIView


        class MyAwesomeView(ManageCacheMixin, ListCreateAPIView):
            # my awesome view stuff
            ...

        ```

        In the example above, when the `list` method of the view is called, then it will set the cache, but when the `create`
        method is called, then it will erase any cache keys that were set on the `list` method, if there are any, but
        **only within the scope of the cache group**. The cache group is by default determined by the url path, but may vary
        based on user or any headers on the request, if these arguments are passed to the `build_cache_mixins` function.
        """

        ...

    class FullManageCacheMixin(ManageCacheMixin, EraseCacheOnDetailMixin):
        """
        Upon calling the `list` method of the view, set the cache, but when calling `create`, `update`, `partial_update` and
        `destroy` methods, then erase the cache. This mixin is essentially just a combination of both `ManageCacheMixin` and
        `EraseCacheOnDetailMixin`.

        Here is an example:

        ```python

        from awesome_tools.cache import FullManageCacheMixin
        from rest_framework.viewsets import ModelViewSet


        class MyAwesomeViewSet(FullManageCacheMixin, ModelViewSet):
            # my awesome viewset stuff
            ...

        ```

        In the example above, when the `list` method of the viewset is called, then it will set the cache, but when any of
        `create`, `update`, `partial_update` and `destroy` methods is called, then it will erase any cache keys that were
        set on the `list` method, if there are any, but **only within the scope of the cache group**. The cache group is
        by default determined by the url path, but may vary based on user or any headers on the request, if these arguments
        are passed to the `build_cache_mixins` function.
        """

        ...

    return (
        SetCacheOnListMixin,
        EraseCacheOnCreateMixin,
        EraseCacheOnUpdateMixin,
        EraseCacheOnDestroyMixin,
        EraseCacheOnDetailMixin,
        ManageCacheMixin,
        FullManageCacheMixin,
    )


(
    SetCacheOnListMixin,
    EraseCacheOnCreateMixin,
    EraseCacheOnUpdateMixin,
    EraseCacheOnDestroyMixin,
    EraseCacheOnDetailMixin,
    ManageCacheMixin,
    FullManageCacheMixin,
) = build_cache_mixins()

(
    SetCacheOnListByAuthTokenMixin,
    EraseCacheOnCreateByAuthTokenMixin,
    EraseCacheOnUpdateByAuthTokenMixin,
    EraseCacheOnDestroyByAuthTokenMixin,
    EraseCacheOnDetailByAuthTokenMixin,
    ManageCacheByAuthTokenMixin,
    FullManageCacheByAuthTokenMixin,
) = build_cache_mixins(vary_on_headers=("Authorization",))

(
    SetCacheOnListByUserMixin,
    EraseCacheOnCreateByUserMixin,
    EraseCacheOnUpdateByUserMixin,
    EraseCacheOnDestroyByUserMixin,
    EraseCacheOnDetailByUserMixin,
    ManageCacheByUserMixin,
    FullManageCacheByUserMixin,
) = build_cache_mixins(vary_on_user=True)
