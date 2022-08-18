"""
This module provides three useful functions. Two of them are a more powerful and versatille version
of `get_object_or_404` and `get_list_or_404`, and the other is a handy shortcut.
"""

from django.core.exceptions import FieldError, ValidationError
from django.db.models import Model
from django.http import Http404
from rest_framework.exceptions import APIException


def get_object_or_error(klass: Model, exception: APIException = Http404, **kwargs):
    """
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

    ---

    ```python

    # exceptions.py

    class CinemaNotFoundError(APIException):
        status_code = status.HTTP_404_NOT_FOUND
        default_detail = "Cinema not found"


    class RoomNotFoundError(APIException):
        status_code = status.HTTP_404_NOT_FOUND
        default_detail = "Room not found in this cinema"

    ```

    ---

    ```python

    # request endpoint

    "/cinemas/<cinema_id>/rooms/<room_id>/"

    ```

    ---

    ```python

    # views.py

    cinema = get_object_or_error(Cinema, CinemaNotFoundError, pk=self.kwargs['cinema_id'])
    room = get_object_or_error(Room, RoomNotFoundError, pk=self.kwargs['room_id'], cinema=cinema)

    ```

    ---

    Note that in case a room id is valid, but the cinema id is not, an appropriated message will be
    returned. In case you would use `get_object_or_404`, you would get just a `"Not found."`. Having
    more than one lookup field, `get_object_or_error` makes much clearer what is the problem.

    I highly encorage you to have a quick look at the source code, it's quite a simple concept.
    """
    try:
        return klass.objects.get(**kwargs)
    except (klass.DoesNotExist, ValidationError, ValueError, FieldError):
        raise exception


def get_list_or_error(
    klass: Model,
    error_klass: APIException = Http404,
    accept_empty: bool = False,
    **kwargs
):
    """
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

    ---

    ```python

    # exceptions.py

    class NoMovieSessionsError(APIException):
        status_code = status.HTTP_404_NOT_FOUND
        default_detail = "This room has no scheduled movie sessions"

    ```

    ---

    ```python

    # request endpoint

    "/cinemas/<cinema_id>/rooms/<room_id>/movie-sessions/"

    ```

    ---

    ```python

    # views.py

    cinema = get_object_or_error(Cinema, CinemaNotFoundError, pk=self.kwargs['cinema_id'])
    room = get_object_or_error(Room, RoomNotFoundError, pk=self.kwargs['room_id'], cinema=cinema)
    movie_sessions = get_list_or_error(MovieSession, NoMovieSessionsError, room=room)

    ```

    ---

    I highly encorage you to have a quick look at the source code, it's quite a simple concept.
    """
    try:
        result = klass.objects.filter(**kwargs)
    except (ValidationError, ValueError, FieldError):
        raise error_klass

    if result or accept_empty:
        return result

    raise error_klass


def set_and_destroy(
    klass: Model, attr: str, value: list[Model], related_klass: Model, **kwargs
):
    """
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

    ---

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

    ---

    ```python

    # serializers.py

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

    ---

    In the example above, we are first getting or creating video instances, in order to reuse the ones
    passed in the body of the request that may already be in our db. Each video can only be related to
    one movie, since it doesn't make sense that two movies have the same trailer or teaser. So when
    assigning this new list of videos to a movie, the `set_and_destroy` function safely deletes all
    videos having their `movie` foreign key equal to `None`.

    I highly encorage you to have a quick look at the source code, it's quite a simple concept.
    """
    getattr(klass, attr).set(value)
    related_klass.objects.filter(**kwargs).delete()
