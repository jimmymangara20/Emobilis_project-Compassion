from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomUser(AbstractUser):
    is_admin = models.BooleanField(default=False)
    is_beneficiary = models.BooleanField(default=False)
    is_supporter = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Child(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='child')
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    religion = models.CharField(max_length=100, null=True, blank=True)
    photo = models.ImageField(upload_to='children_photos/', null=True, blank=True)
    need = models.CharField(max_length=100, null=True, blank=True)
    need_description = models.TextField(max_length=300, null=True, blank=True)
    amount_needed = models.IntegerField(null=True, blank=True)
    amount_supported = models.IntegerField(null=True, blank=True)
    sponsored = models.BooleanField(default=False, null=True, blank=True)

    def is_fully_filled(self):
        return all([
            self.age is not None,
            bool(self.gender),
            bool(self.address),
            bool(self.religion),
            self.photo,
            bool(self.need),
            bool(self.need_description),
            self.amount_needed is not None,
            self.amount_supported is not None
        ])

    def __str__(self):
        return self.user.first_name + self.user.last_name


@receiver(post_save, sender=CustomUser)
def create_child_for_beneficiary(sender, instance, created, **kwargs):
    if created and instance.is_beneficiary:
        Child.objects.create(user=instance)
