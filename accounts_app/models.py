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
    age = models.IntegerField(null=True)
    gender = models.CharField(max_length=100, null=True)
    address = models.CharField(max_length=100, null=True)
    religion = models.CharField(max_length=100, null=True)
    photo = models.ImageField(upload_to='children_photos/', null=True)
    need = models.CharField(max_length=100, null=True)
    need_description = models.TextField(max_length=300, null=True)
    amount_needed = models.IntegerField(null=True)
    amount_supported = models.IntegerField(null=True)
    sponsored = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.user.first_name + self.user.last_name


@receiver(post_save, sender=CustomUser)
def create_child_for_beneficiary(sender, instance, created, **kwargs):
    if created and instance.is_beneficiary:
        Child.objects.create(user=instance)
