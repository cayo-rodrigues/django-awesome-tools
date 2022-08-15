from django.contrib.auth.models import AbstractUser

from .managers import CustomUserManager


class CustomAbstractUser(AbstractUser):
    """
    A custom user model that inherits from `django.contrib.auth.models.AbstractUser`.
    It's purpose in life is to provide a shortcut for some configurations that are
    needed when changing authentication system from `username/password` to `email/password`.

    There are some properties that it sets with default values. They are:

    - `username` -> Defaults to `None`. This essencially discards the `username` column. If
    you want to still have a username field, but continue to use the `email` for login, no
    problem, you can just override this property.
    - `USERNAME_FIELD` -> Defaults to `"email"`. This property defines which field should be
    required for login (besides `password`, of course). Highly recommend you not to change this.
    - `objects` -> Defaults to `CustomUserManager()`. Defines what manager class should be used
    with the model. In case you created a class that inherits from `CustomUserManager` class,
    customizing it to your own needs, you should set this new class of yours here instead.

    Below is an example of how you might go about using this class:

    ```
    class MyOwnUserModel(CustomAbstractUser):
        first_name = models.CharField(max_length=127)
        last_name = models.CharField(max_length=127)
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)

        date_joined = None

        objects = MyOwnUserManager()
    ```
    """

    username = None
    USERNAME_FIELD = "email"
    objects = CustomUserManager()
