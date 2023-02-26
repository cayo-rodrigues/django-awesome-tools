from custom_cache_page.cache import cache_page
from django.conf import settings
from django.http import HttpRequest
from django.utils.decorators import method_decorator

from .helpers import gen_cache_group, gen_cache_key, handle_delete_cache


def build_cache_mixins(
    cache_ttl: int = settings.CACHE_TTL,
    vary_on_headers: tuple = (),
    vary_on_user: bool = False,
):
    class SetCacheOnListMixin:
        @method_decorator(
            cache_page(
                timeout=cache_ttl,
                key_func=gen_cache_key(vary_on_headers, vary_on_user),
                group_func=gen_cache_group(vary_on_headers, vary_on_user),
            )
        )
        def list(self, request: HttpRequest, *args, **kwargs):
            return super().list(request, *args, **kwargs)

    class EraseCacheOnCreateMixin:
        def create(self, request: HttpRequest, *args, **kwargs):
            response = super().create(request, *args, **kwargs)
            handle_delete_cache(request, vary_on_headers, vary_on_user)
            return response

    class EraseCacheOnUpdateMixin:
        def update(self, request, *args, **kwargs):
            response = super().update(request, *args, **kwargs)
            handle_delete_cache(request, vary_on_headers, vary_on_user)
            return response

        def partial_update(self, request, *args, **kwargs):
            response = super().partial_update(request, *args, **kwargs)
            handle_delete_cache(request, vary_on_headers, vary_on_user)
            return response

    class EraseCacheOnDestroyMixin:
        def destroy(self, request, *args, **kwargs):
            response = super().destroy(request, *args, **kwargs)
            handle_delete_cache(request, vary_on_headers, vary_on_user)
            return response
    
    class EraseCacheOnDetailMixin(EraseCacheOnUpdateMixin, EraseCacheOnDestroyMixin):
        ...

    class ManageCacheMixin(SetCacheOnListMixin, EraseCacheOnCreateMixin):
        ...

    class FullManageCacheMixin(ManageCacheMixin, EraseCacheOnDetailMixin):
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
