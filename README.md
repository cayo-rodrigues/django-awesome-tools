# dj-drf-utils

This package provides useful functions and classes to be used in [Django](https://www.djangoproject.com/) projects, specially when working with [Django Rest Framework](https://www.django-rest-framework.org/). Below are some further explation about how to use this package and what each module inside it does.

The examples on this documentation are about movies and cinemas, having entities like `Movie`, `Cinema`, `Room`, and `MovieSession`.

## Installation

First, run:

```bash
pip install dj-drf-utils
```

That's it!

## `helpers.py`

This module provides three useful functions. Two of them are a more powerful and versatille version of `get_object_or_404` and `get_list_or_404`, and the other is a handy shortcut.

### `get_object_or_error`

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


### `get_list_or_error`

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


### `set_and_destroy`

This function basically sets a new list of values in of a foreign key field and erases any
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


## `mixins.py`

This module provides useful mixins to be used in Django Rest Framework **generic views** and **viewsets**.

### `SerializerByMethodMixin`

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

### `SerializerByActionMixin`

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

### `SerializerByDetailActionsMixin`

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

### `SerializerBySafeActionsMixin`

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

## `managers.py`

This module provides a custom user manager as a shortcut for whoever wants to customize
django's authentication system to use a different field instead of username for login.
It can be really anything, like email, phone, cpf, etc.

### `CustomUserManager`

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


## `action_patterns.py`

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

But routers are still so cool and so simple to use. So a very good alternative is [drf-nested-routers](https://github.com/alanjds/drf-nested-routers).
It really makes it easier to deal with all of this. The `drf-nested-routers` library is designed to
solve exactly this problem, and even more.

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