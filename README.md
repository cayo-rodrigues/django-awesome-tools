# dj-drf-utils

This package provides useful functions and classes to be used in [Django](https://www.djangoproject.com/) projects, specially when working with [Django Rest Framework](https://www.django-rest-framework.org/). Below are some further explation about how to use this package and what each module inside it does.

The examples on this documentation are about movies and cinemas, having entities like `Movie`, `Cinema`, `Room`, and `MovieSession`.

- [Installation](#installation)
- [helpers](#helpers)
  - [get\_object\_or\_error](#get_object_or_error)
  - [get\_list\_or\_error](#get_list_or_error)
  - [set\_and\_destroy](#set_and_destroy)
  - [bulk\_get\_or\_create](#bulk_get_or_create)
- [mixins](#mixins)
  - [SerializerByMethodMixin](#serializerbymethodmixin)
  - [SerializerByActionMixin](#serializerbyactionmixin)
  - [SerializerByDetailActionsMixin](#serializerbydetailactionsmixin)
  - [SerializerBySafeActionsMixin](#serializerbysafeactionsmixin)
  - [FilterQuerysetMixin](#filterquerysetmixin)
  - [AttachUserOnCreateMixin](#attachuseroncreatemixin)
  - [AttachUserOnUpdateMixin](#attachuseronupdatemixin)
  - [AttachUserToReqDataMixin](#attachusertoreqdatamixin)
- [managers](#managers)
  - [CustomUserManager](#customusermanager)
- [cache](#cache)
  - [build\_cache\_mixins](#build_cache_mixins)
  - [SetCacheOnListMixin](#setcacheonlistmixin)
  - [EraseCacheOnCreateMixin](#erasecacheoncreatemixin)
  - [EraseCacheOnUpdateMixin](#erasecacheonupdatemixin)
  - [EraseCacheOnDestroyMixin](#erasecacheondestroymixin)
  - [EraseCacheOnDetailMixin](#erasecacheondetailmixin)
  - [EraseCacheOnDetailMixin](#erasecacheondetailmixin)
  - [ByAuthToken Variations](#byauthtoken-variations)
  - [ByUser Variations](#byuser-variations)
- [action\_patterns](#action_patterns)
- [admin](#admin)
  - [CustomUserAdmin](#customuseradmin)

## Installation

First, run:

```bash
pip install dj-drf-utils
```

That's it!

---

## helpers

This module provides three useful functions. Two of them are a more powerful and versatille version of `get_object_or_404` and `get_list_or_404`, and the other is a handy shortcut.

### get_object_or_error

Almost the same as `django.shortcuts.get_object_or_404`, but can raise any
custom error class you want, allowing you to return more precise error messages.
Another advantage of using this helper function, is that it prevents your application
from crashing. For instance, in case you want to get an object by it's primary key, and
it is of type `uuid`, but another data type is provided in the url, it will not crash,
unlike the standard `get_object_or_404`. It expects the following arguments:

- `klass` -> The model that will be used for the query
- `exception` -> An error class inheriting from `rest_framework.exceptions.APIException`.
If no `exception` is provided, then the standard `django.http.Http404` class is used.
- `**kwargs` -> Keyword arguments representing all fields that should be used for the
search, as many as you please.

For instance, in case you want to get a `Room` of a `Cinema`:

```python
# exceptions.py

from rest_framework.exceptions import APIException, status


class CinemaNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Cinema not found"


class RoomNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Room not found in this cinema"
```

```python
# request endpoint

"/cinemas/<cinema_id>/rooms/<room_id>/"
```

```python
# views.py

from dj_drf_utils.helpers import get_object_or_error


cinema = get_object_or_error(Cinema, CinemaNotFoundError, pk=self.kwargs['cinema_id'])
room = get_object_or_error(Room, RoomNotFoundError, pk=self.kwargs['room_id'], cinema=cinema)
```

Note that in case a room id is valid, but the cinema id is not, an appropriated message will be
returned. In case you would use `get_object_or_404`, you would get just a `"Not found."`. Having
more than one lookup field, `get_object_or_error` makes much clearer what is the problem.

I highly encorage you to have a quick look at the source code, it's quite a simple concept.

##

### get_list_or_error

Almost the same as `django.shortcuts.get_list_or_404`, but can raise any
custom error class you want, allowing you to return more precise error messages.
Another advantage of using this helper function, is that it prevents your application
from crashing. For instance, in case you want to get a list, filtering it by some foreign
key field, which is of type `uuid`, but another data type is provided in the url, it will
not crash, unlike the standard `get_list_or_404`. Also, this function gives you the possiblity
of not raising an exception when no values are found, so you could just return an empty list.
It expects the following arguments:

- `klass` -> The model that will be used for the query
- `exception` -> An error class inheriting from `rest_framework.exceptions.APIException`.
If no `exception` is provided, then the standard `django.http.Http404` class is used.
- `accept_empty` -> A boolean argument, which defaults to `False`. When provided, determines
if an empty result is acceptable or if it should raise `exception`.
- `**kwargs` -> Keyword arguments representing all fields that should be used for the
search, as many as you please.

For instance, in case you want to list all `MovieSession`s of a `Room` in a `Cinema`:

```python
# exceptions.py

from rest_framework.exceptions import APIException, status


class NoMovieSessionsError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "This room has no scheduled movie sessions"
```

```python
# request endpoint

"/cinemas/<cinema_id>/rooms/<room_id>/movie-sessions/"
```

```python
# views.py

from dj_drf_utils.helpers import get_object_or_error, get_list_or_error


cinema = get_object_or_error(Cinema, CinemaNotFoundError, pk=self.kwargs['cinema_id'])
room = get_object_or_error(Room, RoomNotFoundError, pk=self.kwargs['room_id'], cinema=cinema)
movie_sessions = get_list_or_error(MovieSession, NoMovieSessionsError, room=room)
```

I highly encorage you to have a quick look at the source code, it's quite a simple concept.

##

### set_and_destroy

This function basically sets a new list of values in a foreign key field and erases any
previous values that were related to `klass`. For it to work, **you must set `null=True`
in your model**, otherwise, the values will not be subsitituted, they will only be added.
It accepts the following parameters:

- `klass` -> The model on the side `1` of a `1:N` relationship, the owner of the relation,
in which the new values will be set
- `attr` -> A string version of the attribute corresponding to the `related_name` value
in the foreign key field
- `value` -> A list (or any other iterable), containing new created instances of `related_klass`
- `related_klass` -> The model on the side `N` of a `1:N` relationship, the one having the foreign
key field
- `**kwargs` -> Keyword arguments used in a filter to determine which objects should be destroyed.
It could be really anything, but usually you will want it to be something like `klass=None`, so
that all objects that are no part of the relationship anymore can be descarded.

For instance, a `Movie` may have many `Video`s related to it, like teasers and trailers. In case
you want to update a `Movie`, reseting its `Video`s:

```python
# models.py

class Movie(models.Model):
    ...


class Video(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    title = models.CharField(max_length=127)
    url = models.URLField()

    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="videos", null=True)
```

```python
# serializers.py

from dj_drf_utils.helpers import set_and_destroy


class MovieSerializer(serializers.ModelSerializer):
    ...

    def update(self, instance: Movie, validated_data: dict):
      ...

      videos_data = validated_data.pop("videos", None)
      if videos_data:
          videos = [
            Video.get_or_create(**video, movie=instance)[0]
            for video in videos_data
          ]
          set_and_destroy(
              klass=instance,
              attr="videos",
              value=videos,
              related_klass=Video,
              movie=None,
          )
```

In the example above, we are first getting or creating video instances, in order to reuse the ones
passed in the body of the request that may already be in our db. Each video can only be related to
one movie, since it doesn't make sense that two movies have the same trailer or teaser. So when
assigning this new list of videos to a movie, the `set_and_destroy` function safely deletes all
videos having their `movie` foreign key equal to `None`.

I highly encorage you to have a quick look at the source code, it's quite a simple concept.

##

### bulk_get_or_create

Despite the name of this function, it does not translate into a single database hit,
unfortunatelly. But it is still better than a loop executing `Model.objects.get_or_create`
in every iteration.

That's because this function **combines filters and the bulk_create method**.
Django querysets are lazy, but in this function they are evaluated on every iteration.
However, in the end **only one** `INSERT` query is performed.

---

#### Important!
Django's `Model.objects.bulk_create` method returns a list of newly created instances **without ids**
when working with _SQLite_. Please, make sure to use _PostgreSQL_ to avoid problems.

---

It expects the following parameters:

- `klass` -> The model whose values will be retrieved or created
- `values` -> A list of dictionaries having key value pairs demanded by `klass`
- `only_create` -> A boolean value. Defaults to `False`. In case you don't care about getting
existing values, and just wants to create them, then you can set this arguments to `True`. It
will result in just one database hit.
- `kwargs` -> Key value pairs with extra fields you want to use for filtering/creating instances
of `klass`. It can be useful for foreign key fields

Usage example:

```python
# serializers.py

from dj_drf_utils.helpers import bulk_get_or_create, set_and_destroy


class MovieSerializer(serializers.ModelSerializer):
    # ...

    def create(self, validated_data: dict) -> Movie:
        # ...

        videos_data = validated_data.pop("videos")

        # ...

        bulk_get_or_create(Video, videos_data, movie=movie)

        # ...

    def update(self, instance: Movie, validated_data: dict) -> Movie:
        # ...

        videos = validated_data.pop("videos", None)

        # ...

        if videos:
            set_and_destroy(
                klass=instance,
                attr="videos",
                value=bulk_get_or_create(Video, videos, movie=instance),
                related_klass=Video,
                movie=None,
            )

        # ...
```

Note that in the `update` method, we are combining `set_and_destroy` with `bulk_get_or_create`.
That's totally a thing.

I highly encourage you to have a look at the source code, so that you can better understand what's
happening under the hood. It's not complicated.

---

## mixins

This module provides useful mixins to be used in Django Rest Framework **generic views** and **viewsets**.

### SerializerByMethodMixin

This mixin overrides the `get_serializer_class` method of generic views. It's
purpose is to dinamically define which serializer to use, depending on the request
method. For this to be possible, a new class property should be set, it is:

- `method_serializers` -> It should be a dictionary having it's keys with the names
of http methods and values as the serializer classes corresponding to each method.
If the request method does not match any of the dict keys, it will return the value
of `self.serializer_class`.

Below is an example:

```python
# views.py

from dj_drf_utils.mixins import SerializerByMethodMixin


class MyBeautifulGenericView(SerializerByMethodMixin, ListCreateAPIView):
    queryset = MyWonderfulModel.objects.all()
    serializer_class = MyDefaultSerializer
    method_serializers = {
        "GET": MySerialzerToUseInGetRequests,
    }
```

##

### SerializerByActionMixin

This mixin overrides the `get_serializer_class` method of viewsets. It's
purpose is to dinamically define which serializer to use, depending on the viewset
action. For this to be possible, a new class property should be set, it is:

- `action_serializers` -> It should be a dictionary having it's keys with the names
of viewset actions and values as the serializer classes corresponding to each action.
If the viewset action does not match any of the dict keys, it will return the value
of `self.serializer_class`.

Below is an example:

```python
# views.py

from dj_drf_utils.mixins import SerializerByActionMixin


class MyBeautifulViewSet(SerializerByActionMixin, ModelViewSet):
    queryset = MyWonderfulModel.objects.all()
    serializer_class = MyDefaultSerializer
    action_serializers = {
        "create": MySerializerToUseInCreateActions,
        "update": MySerialzerToUseInUpdateActions,
        "partial_update": MySerialzerToUseInPartialUpdateActions,
    }
```

##

### SerializerByDetailActionsMixin

This mixin overrides the `get_serializer_class` method of viewsets. It's
purpose is to dinamically define which serializer to use, depending on the viewset
action. If it is a detail action, that is, one of `retrieve`, `update`, `partial_update`
and `destroy`, then `self.detail_serializer_class` will be returned. Else, the default
`self.serializer_class` is used. For this to be possible, a new class property should
be set, it is:

- `detail_serializer_class` -> It's value should be a serializer class. This property defines
which serializer to use in detail actions.

Below is an example:

```python
# views.py

from dj_drf_utils.mixins import SerializerByDetailActionsMixin


class MyBeautifulViewSet(SerializerByDetailActionsMixin, ModelViewSet):
    queryset = MyWonderfulModel.objects.all()
    serializer_class = MyDefaultSerializer
    detail_serializer_class = MyDetailSerializer
```

##

### SerializerBySafeActionsMixin

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

```python
# views.py

from dj_drf_utils.mixins import SerializerBySafeActionsMixin


class MyBeautifulViewSet(SerializerBySafeActionsMixin, ModelViewSet):
    queryset = MyWonderfulModel.objects.all()
    serializer_class = MyDefaultSerializer
    safe_serializer_class = MySafeSerializer
```

##

### FilterQuerysetMixin

This mixin overrides the `get_queryset` method of class based views. It's main goal is
to make it easier and simpler to filter and/or narrow down results. You may use it to
attach results to the logged in user, to filter the queryset by route params (or `kwargs`)
and by query params.

These are the class properties that this mixin accepts:

- `user_key` -> A `str` representing which keyword argument should be used for filtering by
user. The default is `None`, meaning that the queryset will not be filtered by the logged in user, that
is, `self.request.user`. If in your queryset there is a `FK` pointing to your project's auth user model, then this property should
have the same name as this `FK` field.
- `filter_kwargs` -> A `dict[str, str]`, where the **key** represents the name of the **field** to be searched,
and the **value** is the **url param**.
- `filter_query_params` -> A `dict[str, str]`, where the **key** is the name of the **field** to be searched,
and the **value** represents the **query param** received in the request.
- `exception_klass` -> Should be an `exception` inheriting from `rest_framework.exceptions.APIException`. The
default value is `django.http.Http404`. In case no value is returned or another kind of error occurs, this
exception will be raised.
- `accept_empty` -> A `bool`, which defaults to `True`. If `False`, then the `exception_klass` will be raised
in case the results are empty. Otherwise, an empty value will be returned normaly.

Below is an example of how this might be useful:

```python

# request endpoint

"/categories/<category_id>/transactions/"

```

```python

# views.py

from dj_drf_utils.mixins import FilterQuerysetMixin

class TransactionView(FilterQuerysetMixin, ListCreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    user_key = "user"
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

In the example above, we are defining a view for monetary transactions. We don't want
users to see other user's transactions, so we attach all transactions to the logged in
user. By using the `user_key` class property, we tell the mixin that when filtering the
queryset, it should use `user=self.request.user`.

Also, all transactions have categories. And we want them always to be listed by category.
So in the url, we receive the `<category_id>` param. So that's why we declare `filter_kwargs`
in that way.

As for the `filter_query_params` property, please note how interesting it is. In the keys of
the dictionary, we pass in the keys that will be used for filtering the queryset, just as if
we were filtering the queryset manually. None of these query params are mandatory.

We are not declaring `accept_empty`, which means that we will not raise `exception_klass` in any
case. So that's why we don't need to define `exception_klass` too.

You may have noticed that the `queryset` class property haven't been defined. That's not a
problem, because this mixin guesses what is the apropriated model by accessing `self.serializer_class.Meta.model`.
So as long as you define you model in that way, everything is OK.

##

### AttachUserOnCreateMixin

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

from dj_drf_utils.mixins import AttachUserOnUpdateMixin
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

##

### AttachUserOnUpdateMixin

Exactly the same as [AttachUserOnCreateMixin](#attachuseroncreatemixin), but overrides the `perform_update`
method.

##

### AttachUserToReqDataMixin

A combination of [AttachUserOnCreateMixin](#attachuseroncreatemixin) and [AttachUserOnUpdateMixin](#attachuseronupdatemixin), 
overriding both `perform_create` and `perform_update` methods of generic views.


---

## managers

This module provides a custom user manager as a shortcut for whoever wants to customize
django's authentication system to use a different field instead of username for login.
It can be really anything, like email, phone, cpf, etc.

### CustomUserManager

A custom user manager that inherits from `django.contrib.auth.models.BaseUserManager`.
Its purpouse in life is mainly to provide an easy and simple way to implement a login
and register system that expects another field instead of `username`.

But what if you desired to customize your users in a way that other info is also required
for user creation? No problem, this class is highly customizable.

Instead of having to override the `create` and `create_superuser` methods of `BaseUserManager`,
you can inherit from `CustomUserManager` and then simply set some class properties at your will.
They work as follows:

- `auth_field_name` -> Defaults to `"email"`. Defines what is the name of the field that
should be used for login (besides password, of course). Note that this field **must**
exist in your user model, **having a unique constraint**.
- `user_is_staff` -> Defaults to `False`. Defines the starting staff status of newly
created users
- `user_start_active` -> Defaults to `True`. Defines if a user account should start in
active state. In cases where users have to confirm their account in some way before getting
access, you may wish to set this property to `False`
- `super_is_staff` -> Defaults to `True`. Defines the starting staff status of newly
created superusers
- `super_start_active` -> Defaults to `True`. Defines if a superuser account should start in
active state. Usually you'll want this value to be `True`, but you're totally free to change
it, depending on your needs.
- `required_fields` -> Defaults to `[]`. It should be a `list[str]`. This property defines
which fields are required to be provided upon user creation, besides `self.auth_field_name` and
`password`. The fields `is_staff`, `is_superuser` and `is_active` should also not be present in
this list. It is worth noting that **all fields defined here, must also be defined in your user model**.
Otherwise, a `ValidationError` is raised.

Below is an example of how you may customize the behaviour of this class:

```python
# managers.py

from dj_drf_utils.managers import CustomUserManager


class MyOwnUserManager(CustomUserManager):
    user_start_active = False
    required_fields = ["first_name", "last_name"]
```

In order to implement a login with email feature, for instance, you have to make some minor
changes to your user model. Below are some settings that may come in handy for you to define
in your model:

```python
# models.py

from .managers import MyOwnUserManager
from django.db import models
from django.contrib.auth.models import AbstractUser


class MyUser(AbstractUser):
    email = models.EmailField(unique=True)

    username = None

    objects = MyOwnUserManager()

    USERNAME_FIELD = objects.auth_field_name
    REQUIRED_FIELDS = objects.required_fields
```

The `email` property is defined as unique, since it's gonna be used for login (as per the `USERNAME_FIELD`
property). The `objects` property may be either the standard `dj_drf_utils.managers.CustomUserManager`
or your own manager that inherits from it. In the example above, we are using our own user manager,
with some minor customizations. `REQUIRED_FIELDS` refer to the fields you are prompted when creating a
superuser (it must not include the value defined for `USERNAME_FIELD` or `"password"`). Defining it to
`objects.required_fields` prevents you from making mistakes and being redundant. Note that in the example
above we are droping the `username` column, but that's not necessary if you still want to have a username
in your user model.

---

## cache

This subpackage provides a set of useful mixins that may be used for cache management. It also provides a function
for building your own custom mixins.

### build_cache_mixins

This function returns a tuple of mixins used for cache management. It receives the following arguments:
    
- `cache_ttl` -> The ttl(time to live) for the cache is by default whatever you
set in the `CACHE_TTL` variable at your project's `settings.py`, but you can totally override this here.
The value of `cache_ttl` must be an `int`. It represents the time that the cache will persist, **in seconds**.
In case `CACHE_TTL` is not present in `settings.py`, then it defaults to 10 minutes.
- `vary_on_headers` -> This argument is a `tuple` that refers to which headers should be used when generating
the cache key and cache group.
- `vary_on_user` -> A boolean value that determines if the cache key and cache group should be isolated for each user.

It is important to note that, besides the value of `vary_on_headers` and `vary_on_user`, cache keys are generated
based on the request path and query params, and cache groups are generated based on the request path.

Here is a simple example of how you could use it:

```python

from dj_drf_utils.cache import build_cache_mixins

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

Actually, this illustrates exactly how the cache management mixins on this package are generated.

##

### SetCacheOnListMixin

Caches the results of the `list` method of generic views and viewsets. After setting the cache,
if the same request is fired again, then it will return the cached value, instead of doing the
whole thing again.

Here is a simple example of how you could use this mixin.

```python

from dj_drf_utils.cache import SetCacheOnListMixin
from rest_framework.generics import ListAPIView


class MyAwesomeListView(SetCacheOnListMixin, ListAPIView):
    # my awesome view stuff
    ...

```

##

### EraseCacheOnCreateMixin

Upon calling the `create` method of generic views and viewsets, erase the cache. But what cache?
The cache related to the group this mixin belongs to. It is by default determined by the url path,
but may vary based on user or any headers on the request, if these arguments are passed to the
`build_cache_mixins` function.

Here is an example:

```python

from dj_drf_utils.cache import SetCacheOnListMixin, EraseCacheOnCreateMixin
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

##

### EraseCacheOnUpdateMixin

Exactly the same as [EraseCacheOnCreateMixin](#erasecacheoncreatemixin), but with `update` and `partial_update`
methods of generic views and viewsets.

##

### EraseCacheOnDestroyMixin

Exactly the same as [EraseCacheOnCreateMixin](#erasecacheoncreatemixin) and [EraseCacheOnUpdateMixin](#erasecacheonupdatemixin),
but with the `destroy` method of generic views and viewsets.

##

### EraseCacheOnDetailMixin

This is just a combination of both [EraseCacheOnUpdateMixin](#erasecacheonupdatemixin) and [EraseCacheOnDestroyMixin](#erasecacheondestroymixin).

Here is an example:
        
```python

from dj_drf_utils.cache import SetCacheOnListMixin, EraseCacheOnDetailMixin
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

##

### ManageCacheMixin

Upon calling the `list` method of the view, set the cache, but when calling the `create` method, then erase the cache.
This mixin is essensially just a combination of both [SetCacheOnListMixin](#setcacheonlistmixin) and [EraseCacheOnCreateMixin](#erasecacheoncreatemixin).

Here is an example:

```python

from dj_drf_utils.cache import ManageCacheMixin
from rest_framework.generics import ListCreateAPIView


class MyAwesomeView(ManageCacheMixin, ListCreateAPIView):
    # my awesome view stuff
    ...

```

In the example above, when the `list` method of the view is called, then it will set the cache, but when the `create`
method is called, then it will erase any cache keys that were set on the `list` method, if there are any, but
**only within the scope of the cache group**. The cache group is by default determined by the url path, but may vary
based on user or any headers on the request, if these arguments are passed to the `build_cache_mixins` function.

##

### FullManageCacheMixin

Upon calling the `list` method of the view, set the cache, but when calling `create`, `update`, `partial_update` and
`destroy` methods, then erase the cache. This mixin is essensially just a combination of both [ManageCacheMixin](#managecachemixin)
and [EraseCacheOnDetailMixin](#erasecacheondetailmixin).

Here is an example:

```python

from dj_drf_utils.cache import FullManageCacheMixin
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

##

### ByAuthToken Variations

### SetCacheOnListByAuthTokenMixin

Exactly the same as [SetCacheOnListMixin](#setcacheonlistmixin), but grouping the cache by the `"Authorization"` header.
This means that the cache will be isolated by the value of the auth token, even within the scope of the same user.

The following mixins are all variations of the mixins described until now, just like the one above. They all group the
cache by `"Authorization"` header. They are as follows:

- ### EraseCacheOnCreateByAuthTokenMixin
- ### EraseCacheOnUpdateByAuthTokenMixin
- ### EraseCacheOnDestroyByAuthTokenMixin
- ### EraseCacheOnDetailByAuthTokenMixin
- ### ManageCacheByAuthTokenMixin
- ### FullManageCacheByAuthTokenMixin

##

### ByUser Variations

### SetCacheOnListByUserMixin

Exactly the same as [SetCacheOnListMixin](#setcacheonlistmixin), but grouping the cache by `request.user`. This means that
the cache will be isolated by user, even if the authorization token may expire.

The following mixins are all variations of the mixins described until now, just like the one above. They all group the
cache by `request.user`. They are as follows:

- ### EraseCacheOnCreateByUserMixin
- ### EraseCacheOnUpdateByUserMixin
- ### EraseCacheOnDestroyByUserMixin
- ### EraseCacheOnDetailByUserMixin
- ### ManageCacheByUserMixin
- ### FullManageCacheByUserMixin

---

## action_patterns

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

But routers are still so cool and so simple to use. So a very good alternative is [drf-nested-routers](https://github.com/alanjds/drf-nested-routers).
It really makes it easier to deal with all of this. The `drf-nested-routers` library is designed to
solve exactly this problem, and even more.

---

## admin

This module provides a `CustomUserAdmin` class. It inherits from `django.contrib.auth.admin.UserAdmin`.
Have you ever created a custom user model, added it to admin and then realized that your users passwords
were being created unhashed? Then you searched the internet and found out that django provides a `UserAdmin`
class that does the job. But what if you customized your authentication system, and you're using another
field instead of `username`? In this case, it throws an error, saying that there is no `username` field.

In order to make things easier, this module provides a class that abstracts away all the boring 
configurations you would need to do.

### CustomUserAdmin

This class inherits from `django.contrib.auth.admin.UserAdmin`. It's purpose in life is to abstract
away some boring configurations you may need, when you're using a custom user model. The advantage is
to have the same features that Django standard `UserAdmin` class provides, but in a custom user model,
having a field other than `username` used for authentication.

This class automaticaly figures out what is your user model, as long as it is pointed to by `AUTH_USER_MODEL`
setting in `settings.py`. Also, it takes the care of first checking for the fields you set in your user
model before referencing them. But the **password field is mandatory**.

Below is an usage example:

```python
# admin.py

from dj_drf_utils.admin import CustomUserAdmin
from .models import User

admin.site.register(User, CustomUserAdmin)
```

In case you want to customize some kind of behaviour, you totally can, either by overwriting the properties
entirely (by inheriting this class), or by using one of the class methods defined in this class. For instance,
if you added some columns that are not default of auth user model, but still want them to appear in the admin,
you could do something like this:

```python

# admin.py

from dj_drf_utils.admin import CustomUserAdmin
from .models import User

fields = ("cpf", "phone")

# add fields to the user creation form
CustomUserAdmin.add_creation_fields(fields)
# append fields to list_display
CustomUserAdmin.add_list_display(fields)
# add fields to personal info screen
CustomUserAdmin.add_personal_info(fields)

admin.site.register(User, CustomUserAdmin)
```

Not so bad.