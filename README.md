# django-utils

This package provides useful functions and classes to be used in [Django]() projects, specially when working with [Django Rest Framework](). Below are some further explation about how to use this package and what each module inside it does.

The examples on this documentation are about movies and cinemas, having entities like `Movie`, `Cinema`, `Room`, and `MovieSession`.

## Installation

First, run:

```bash
pip install django-utils
```

Then, in your `INSTALLED_APPS`, register the `django_utils` app:

```python
INSTALLED_APPS = [
  "django_utils",
  ...
]
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

from django_utils.helpers import get_object_or_error


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

from django_utils.helpers import get_object_or_error, get_list_or_error


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

from django_utils.helpers import set_and_destroy


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

from django_utils.mixins import SerializerByMethodMixin


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

from django_utils.mixins import SerializerByActionMixin


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

from django_utils.mixins import SerializerByDetailActionsMixin


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

from django_utils.mixins import SerializerBySafeActionsMixin


class MyBeautifulViewSet(SerializerBySafeActionsMixin, ModelViewSet):
    queryset = MyWonderfulModel.objects.all()
    serializer_class = MyDefaultSerializer
    safe_serializer_class = MySafeSerializer
```

## `managers.py`

This module provides a custom user manager as a shortcut whoever wants to customize django's
authentication system for an email login instead of username login.

### `CustomUserManager`

A custom user manager that inherits from `django.contrib.auth.models.BaseUserManager`.
Its purpouse in life is mainly to provide an easy and simple way to implement a login
and register system that expects `email` and `password` fields, instead of `username`
and `password` fields.

But what if you desired to customize your users in a way that other info is also required?
No problem, this class is highly customizable. You could do all this by overriding the
`create` and `create_superuser` methods of `BaseUserManager`, but here all of this is
handled for you.

Besides that, you can define a class that inherits from `CustomUserManager` and set some
class properties at your will. They work as follows:

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
which fields are required to be provided upon user creation, besides `email` and `password`.
The fields `is_staff`, `is_superuser` and `is_active` should also not be present in this list.
It is worth noting that **all fields defined here, must also be defined in your user model**.
Otherwise, a `ValidationError` is raised.

Below is an example of how you may customize the behaviour of this class:

```python
# managers.py

from django_utils.managers import CustomUserManager


class MyOwnUserManager(CustomUserManager):
    user_start_active = False
    required_fields = ["first_name", "last_name"]
```

**Remember that when doing this, you have to manually set this manager in your user model**.


## `models.py`

This module provides a custom user model with some boilerplate simple configurations that
are needed when customizing authentication system to accept email instead of username.

### `CustomAbstractUser`

A custom user model that inherits from `django.contrib.auth.models.AbstractUser`.
Its purpose in life is to provide a shortcut for some configurations that are
needed when changing authentication system from `username/password` to `email/password`.

There are some properties that it sets with default values. They are:

- `email` -> Defaults to `django.db.models.EmailField(unique=True)`. This property overrides
the default email property that comes from `AbstractUser`, setting the unique constraint to
`True`. This is necessary, since the email will be used for login.
- `username` -> Defaults to `None`. This essencially discards the `username` column. If
you want to still have a username field, but continue to use the `email` for login, no
problem, you can just override this property.
- `USERNAME_FIELD` -> Defaults to `"email"`. This property defines which field should be
required for login (besides `password`, of course). Highly recommend you not to change this.
- `REQUIRED_FIELDS` -> Defaults to `objects.required_fields`. This property defines which
fields are required when creating a superuser via terminal, besides the `USERNAME_FIELD`
and `password`, of course. Highly recommend you not to change it, since it automatically picks
the values defined in the `required_fields` property of the manager class.
- `objects` -> Defaults to `CustomUserManager()`. Defines what manager class should be used
with the model. **In case you created a manager class that inherits from `CustomUserManager`**,
**customizing it to your own needs, you should set this new class of yours here instead**.

Below is an example of how you might go about using this class:

```python
# managers.py

from django_utils.managers import CustomUserManager


class MyOwnUserManager(CustomUserManager):
    user_start_active = False
    required_fields = ["first_name", "last_name"]
```

```python
# models.py

from django.db import models
from django_utils.models import CustomAbstractUser

from .managers import MyOwnUserManager


class MyOwnUserModel(CustomAbstractUser):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    date_joined = None

    objects = MyOwnUserManager()
```


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
from django_utils.action_patterns import STANDARD_DETAIL_PATTERN, STANDARD_PATTERN

from . import views


cinema_view = views.CinemaViewSet.as_view(STANDARD_PATTERN)
cinema_detail_view = views.CinemaViewSet.as_view(STANDARD_DETAIL_PATTERN)

urlpatterns = [
    path("", cinema_view),
    path("<cinema_id>/", cinema_detail_view),
]
```