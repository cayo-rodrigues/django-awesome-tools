"""
Viewsets have the advantage of abstracting away the work of defining routes explicitly,
but routers have some limits. They can only go to a certain depth in producing urls.

For instance, let's imagine a simple application, where you have Bands and Albums.
In case you wish to list all Albums of a Band, you could make a request to an enpoint
like `/bands/<band_id>/albums/`. That's totally possible with routers. But what if you
want a detail route for an Album of a Band? A route like `/bands/<band_id>/albums/<album_id>/`
would make sense, right? But routers aren't able to go to such an extent. And you could
totally imagine bigger urls in real, bigger applications.

So defining our routes manually gives us a lot more control. Everything comes with a tradeoff
though. When manually defining routes for generic views, you can easily assign each view class
to their routes, using the `as_view` method. But viewsets are different. One viewset class can
be assigned to more than one route. So for that to work, you've gotta do something like [this](https://www.django-rest-framework.org/tutorial/6-viewsets-and-routers/#binding-viewsets-to-urls-explicitly).

In order to simplify things, and abstract away some boiler plate code, this module provides the
standard viewset actions mapped to their corresponding http method. Of course, you may have additional
actions, customized according to your own needs. In this case, you can config them on your own. But
the standard ones are all set here.

Usage example:

---

```python
# urls.py

from django.urls import path
from dj_drf_utils.action_patterns import STANDARD_DETAIL_PATTERN, STANDARD_PATTERN

from . import views

cinema_view = views.CinemaViewSet.as_view(STANDARD_PATTERN)
cinema_detail_view = views.CinemaViewSet.as_view(STANDARD_DETAIL_PATTERN)

urlpatterns = [
    path("", cinema_view),
    path("<cinema_id>/", cinema_detail_view),
]
```

---

But routers are still so cool and so simple to use. So a very good alternative is [drf-nested-routers](https://github.com/alanjds/drf-nested-routers).
It really makes it easier to deal with all of this. The `drf-nested-routers` library is designed to
solve exactly this problem, and even more.
"""

LIST_PATTERN = {"get": "list"}
CREATE_PATTERN = {"post": "create"}

RETRIEVE_PATTERN = {"get": "retrieve"}
UPDATE_PATTERN = {"put": "update"}
PARTIAL_UPDATE_PATTERN = {"patch": "partial_update"}
DESTROY_PATTERN = {"delete": "destroy"}

STANDARD_PATTERN = {**LIST_PATTERN, **CREATE_PATTERN}
STANDARD_DETAIL_PATTERN = {
    **RETRIEVE_PATTERN,
    **UPDATE_PATTERN,
    **PARTIAL_UPDATE_PATTERN,
    **DESTROY_PATTERN,
}

RETRIEVE_UPDATE_PATTERN = {
    **RETRIEVE_PATTERN,
    **UPDATE_PATTERN,
    **PARTIAL_UPDATE_PATTERN,
}
RETRIEVE_DESTROY_PATTERN = {**RETRIEVE_PATTERN, **DESTROY_PATTERN}
UPDATE_DESTROY_PATTERN = {**UPDATE_PATTERN, **DESTROY_PATTERN}
