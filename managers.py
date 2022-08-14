from django.contrib.auth.models import BaseUserManager
from django.db.models import FieldDoesNotExist
from django.forms import ValidationError


class CustomUserManager(BaseUserManager):
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
