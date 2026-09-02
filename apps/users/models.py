from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class CustomUser(AbstractUser):

    class GenderChoices(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"

    gender = models.CharField(
        verbose_name="Gender",
        max_length=50,
        choices=GenderChoices.choices,
        default=GenderChoices.MALE
    )
    phone = PhoneNumberField(verbose_name="Phone number", unique=True)
    city = models.CharField(verbose_name="City", max_length=100, blank=True)
    birth_date = models.DateField(verbose_name="Date of birth", null=True, blank=True)
    is_registered = models.BooleanField(verbose_name="The user has registered", default=False)
    document = models.FileField(verbose_name="Document", upload_to='users_documents/', null=True, blank=True)
    photo = models.ImageField(verbose_name="Photo", upload_to='user_photos/', null=True, blank=True)
    slug = models.SlugField(verbose_name="Slug", blank=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self) -> str:
        return f'User: {self.id} | {self.username}'

    def get_phone(self):
        return str(self.phone)
