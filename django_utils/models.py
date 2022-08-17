"""
This module provides a custom user model with some boilerplate simple configurations that
are needed when customizing authentication system to accept email instead of username.
"""

from django.contrib.auth.models import AbstractUser
from django.db.models import EmailField

from .managers import CustomUserManager


class CustomAbstractUser(AbstractUser):
    """
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

    ---

    ```python

    # managers.py

    class MyOwnUserManager(CustomUserManager):
        user_start_active = False
        required_fields = ["first_name", "last_name"]
    ```

    ---

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
    """

    email = EmailField(unique=True)
    username = None

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = objects.required_fields
