"""
This module provides a `CustomUserAdmin` class. It inherits from `django.contrib.auth.admin.UserAdmin`.
Have you ever created a custom user model, added it to admin and then realized that your users passwords
were being created unhashed? Then you searched the internet and found out that django provides a UserAdmin
class that does the job. But what if you customized your authentication system, and you're using another
field instead of `username`? In this case, it throws an error, saying that there is no `username` field.

In order to make things easier, this module provides a class that abstracts away all the boring 
configurations you would need to do.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(UserAdmin):
    """
    This class inherits from `django.contrib.auth.admin.UserAdmin`. It's purpose in life is to abstract
    away some boring configurations you may need, when you're using a custom user model. The advantage is
    to have the same features that Django standard `UserAdmin` class provides, but in a custom user model,
    having a field other than `username` used for authentication.

    This class automaticaly figures out what is your user model, as long as it is pointed to by `AUTH_USER_MODEL`
    setting in `settings.py`. Also, it takes the care of first checking for the fields you set in your user
    model before referencing them. But the **password field is mandatory**.

    Below is an usage example:

    ---

    ```python

    # admin.py

    from dj_drf_utils.admin import CustomUserAdmin
    from .models import User

    admin.site.register(User, CustomUserAdmin)
    ```

    ---

    In case you want to customize some kind of behaviour, you totally can, either by overwriting the properties
    entirely (by inheriting this class), or by using one of the class methods defined in this class. For instance,
    if you added some columns that are not default of auth user model, but still want them to appear in the admin,
    you could do something like this:

    ---

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

    ---

    Not so bad.
    """

    auth_user_class = get_user_model()

    important_dates_fields = ()
    personal_info_fields = ()
    permissions_fields = ()
    list_display_columns = [auth_user_class.USERNAME_FIELD]
    search_fields_values = (auth_user_class.USERNAME_FIELD,)

    if auth_user_class.last_login:
        important_dates_fields += ("last_login",)
    if auth_user_class.date_joined:
        important_dates_fields += ("date_joined",)

    if auth_user_class.first_name:
        personal_info_fields += ("first_name",)
        list_display_columns += ["first_name"]
        search_fields_values += ("first_name",)
    if auth_user_class.last_name:
        personal_info_fields += ("last_name",)
        list_display_columns += ["last_name"]
        search_fields_values += ("last_name",)

    if auth_user_class.is_active:
        permissions_fields += ("is_active",)
    if auth_user_class.is_staff:
        permissions_fields += ("is_staff",)
        list_display_columns += ["is_staff"]
    if auth_user_class.is_superuser:
        permissions_fields += ("is_superuser",)
        list_display_columns += ["is_superuser"]
    if auth_user_class.groups:
        permissions_fields += ("groups",)
    if auth_user_class.user_permissions:
        permissions_fields += ("user_permissions",)

    list_display = list_display_columns
    fieldsets = (
        (None, {"fields": (auth_user_class.USERNAME_FIELD, "password")}),
        (("Personal info"), {"fields": personal_info_fields}),
        (
            ("Permissions"),
            {
                "fields": permissions_fields,
            },
        ),
        (("Important dates"), {"fields": important_dates_fields}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (auth_user_class.USERNAME_FIELD, "password1", "password2"),
            },
        ),
    )
    search_fields = search_fields_values
    ordering = (auth_user_class.USERNAME_FIELD,)

    @classmethod
    def add_creation_fields(cls, fields: tuple[str]):
        cls.add_fieldsets[0][1]["fields"] += fields

    @classmethod
    def add_list_display(cls, fields: list[str]):
        cls.list_display += fields

    @classmethod
    def add_personal_info(cls, fields: tuple[str]):
        cls.fieldsets[1][1]["fields"] += fields
