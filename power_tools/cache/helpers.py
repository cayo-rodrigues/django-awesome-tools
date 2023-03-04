from custom_cache_page.utils import hash_key
from django.core.cache import cache
from django.http import HttpRequest


def gen_cache_group(vary_on_headers: tuple = (), vary_on_user: bool = False):
    def _gen_cache_group(request: HttpRequest):
        group = request.path.split("/")[1]
        for header in vary_on_headers:
            group += f"_{request.META.get(header, None)}"
        if vary_on_user:
            group += f"_{request.user.__str__()}_{request.user.pk}"
        return group

    return _gen_cache_group


def gen_cache_key(
    vary_on_headers: tuple = (), vary_on_user: bool = False, use_group: bool = True
):
    def _gen_cache_key(request: HttpRequest):
        key = f"{request.path}_{request.GET.dict()}"
        for header in vary_on_headers:
            key += f"_{request.META.get(header, None)}"

        if use_group:
            group = gen_cache_group(vary_on_headers, vary_on_user)(request)
            hashed_key = hash_key(f"{None}:{group}:{0}:{key}")
            cache.get_or_set(f"{group}:{key}", hashed_key)

        return key

    return _gen_cache_key


def handle_delete_cache(
    request: HttpRequest,
    vary_on_headers: tuple = (),
    vary_on_user: bool = False,
    del_group: bool = True,
):
    cache_group = gen_cache_group(vary_on_headers, vary_on_user)(request)

    if del_group:
        group_keys = cache.keys(f"*{cache_group}*")
        hashed_keys = list(cache.get_many(group_keys).values())
        cache.delete_many(hashed_keys + group_keys)
    else:
        cache_key = gen_cache_key(vary_on_headers, vary_on_user)(request)
        hashed_key = hash_key(f"{None}:{cache_group}:{0}:{cache_key}")
        cache.delete(hashed_key)
