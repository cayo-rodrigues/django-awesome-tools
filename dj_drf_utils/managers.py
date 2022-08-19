"""
This module provides a custom user manager as a shortcut for whoever wants to customize
django's authentication system to use a different field instead of username for login.
It can be really anything, like email, phone, cpf, etc.
"""

from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import FieldDoesNotExist, ValidationError


class CustomUserManager(BaseUserManager):
    """
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

    ---

    ```python

    # managers.py

    from dj_drf_utils.managers import CustomUserManager

    class MyOwnUserManager(CustomUserManager):
        user_start_active = False
        required_fields = ["first_name", "last_name"]
    ```

    ---

    In order to implement a login with email feature, for instance, you have to make some minor
    changes to your user model. Below are some settings that may come in handy for you to define
    in your model:

    ---

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

    ---

    The `email` property is defined as unique, since it's gonna be used for login (as per the `USERNAME_FIELD`
    property). The `objects` property may be either the standard `dj_drf_utils.managers.CustomUserManager`
    or your own manager that inherits from it. In the example above, we are using our own user manager,
    with some minor customizations. `REQUIRED_FIELDS` refer to the fields you are prompted when creating a
    superuser(it must not include the value defined for `USERNAME_FIELD` or "password"). Defining it to
    `objects.required_fields` prevents you from making mistakes and being redundant. Note that in the example
    above we are droping the `username` column, but that's not necessary if you still want to have a username
    in your user model.
    """

    auth_field_name: str = "email"

    user_is_staff: bool = False
    user_start_active: bool = True

    super_is_staff: bool = True
    super_start_active: bool = True

    required_fields: list[str] = []

    def create(self, password: str, **extra_fields):
        FORBIDDEN_FIELDS = [
            self.auth_field_name,
            "password",
            "is_staff",
            "is_superuser",
            "is_active",
        ]

        try:
            auth_field = extra_fields.pop(self.auth_field_name)
        except KeyError:
            raise ValidationError(f"Missing {self.auth_field_name} field")

        required_values = {self.auth_field_name: auth_field.lower()}

        for field in self.required_fields:
            if field in FORBIDDEN_FIELDS:
                raise ValidationError(
                    f"Field {field} should not be in self.required_fields"
                )
            try:
                self.model._meta.get_field(field)
                required_values[field] = extra_fields.pop(field)
            except FieldDoesNotExist:
                raise ValidationError(f"Field {field} does not exist in {self.model}")
            except KeyError:
                raise ValidationError(f"Missing {field} field")

        user = self.model(
            is_active=self.user_start_active,
            is_staff=self.user_is_staff,
            **extra_fields,
            **required_values,
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, password: str, **extra_fields):
        user = self.create(password, **extra_fields)

        user.is_superuser = True
        user.is_active = self.super_start_active
        user.is_staff = self.super_is_staff

        user.save(using=self._db)

        return user
