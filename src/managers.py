from django.contrib.auth.models import BaseUserManager
from django.db.models import FieldDoesNotExist
from django.forms import ValidationError


class CustomUserManager(BaseUserManager):
    """
    A custom user manager that inherits from `django.contrib.auth.models.BaseUserManager`.
    It's purpouse in life is mainly to provide an easy and simple way to implement a login
    and register system that expects `email` and `password` fields, instead of `username`
    and `password` fields.

    But what if you desired to customize your users in a way that other info is required?
    No problem, this class is highly customizable. You could do all this overriding the
    `create` and `create_superuser` methods of `BaseUserManager`, but here all of this is
    handled for you.

    Besides that, you can define a class that inherits from `CustomUserManager` and set some
    class properties at your will. They work as follows:

    - `user_is_staff` -> Defaults to `False`. Defines the starting staff status of newly
    created users
    - `user_start_active` -> Defaults to `True`. Defines if a user account should start in
    active state. In cases where users have to confirm their account in some way before getting
    access, you may wish to set this property to `False`
    - `super_is_staff` -> Defaults to `False`. Defines the starting staff status of newly
    created superusers
    - `super_start_active` -> Defaults to `True`. Defines if a superuser account should start in
    active state. Usually you'll want this value to be `True`, but you're totally free to change
    it, depending on the situation.
    - `required_fields` -> Defaults to `[]`. It should be a `list` of `str`. This property defines
    which fields are required to be provided upon user creation, besides `email` and `password`.
    The fields `is_staff`, `is_superuser` and `is_active` should also not be present in this list.
    It is worth noting that all fields defined here, must also be defined in your user model.
    Otherwise, a `ValidationError` is raised.
    - `auto_required_fields` -> Defaults to `{}`. It should be a `dict[str, function]`. This property
    also defines which fields are required upon user creation, but having default values. These default
    values are determined by the return of a function. This comes in handy specially when you want to
    have a field with a date, for instance.

    Below is an example of how you may customize the behaviour of this class:

    ```
    from django.utils import timezone

    class MyOwnUserManager(CustomUserManager):
        user_start_active = False
        required_fields = ["first_name", "last_name"]
        auto_required_fields = {
            "created_at": timezone.now,
            "updated_at": timezone.now,
        }
    ```
    """

    user_is_staff: bool = False
    user_start_active: bool = True

    super_is_staff: bool = True
    super_start_active: bool = True

    required_fields: list[str] = []
    auto_required_fields: dict[str, function] = {}

    def create(self, email: str, password: str, **extra_fields):
        FORBIDDEN_FIELDS = ["email", "password", "is_staff", "is_superuser", "is_active"]

        required_values = {}
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

        for field, value in self.auto_required_fields.items():
            required_values.update({field: value()})

        user = self.model(
            email=email.lower(),
            is_active=self.user_start_active,
            is_staff=self.user_is_staff,
            **extra_fields,
            **required_values,
        )

        user.set_password(password)

        user.save(using=self._db)

        return user

    def create_superuser(self, email: str, password: str, **extra_fields):
        user = self.create(email, password, **extra_fields)

        user.is_superuser = True
        user.is_active = self.super_start_active
        user.is_staff = self.super_is_staff

        user.save(using=self._db)

        return user
