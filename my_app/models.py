from django.contrib.auth import get_user_model
from django.db import models

from accounts_app.models import Child

User = get_user_model()


class Appointment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    date = models.DateField()

    def __str__(self):
        return f'{self.user.username} Appointment {self.date}'


class SupportLater(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_later')
    child = models.ForeignKey(Child, on_delete=models.CASCADE)


class Sponsorship(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Assuming sponsor is a User
    sponsor_name = models.CharField(max_length=100)
    sponsor_email = models.EmailField()
    sponsor_phone = models.CharField(max_length=100)
    sponsored_child = models.ForeignKey(Child, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        if self.sponsored_child and self.sponsored_child.user:
            return f"Sponsor {self.sponsor_name} to {self.sponsored_child.user.first_name}"
        return f"Sponsor {self.sponsor_name} (No child assigned)"


# XAMPP
class UploadedImage(models.Model):
    title = models.CharField(max_length=100)  # Title for the image
    image = models.ImageField(upload_to='Uploaded_images/')  # Save images to this

    def __str__(self):
        return self.title


class LNMOnline(models.Model):
    CheckoutRequestID = models.CharField(max_length=100)
    MerchantRequestID = models.CharField(max_length=50)
    ResultCode = models.IntegerField()
    ResultDesc = models.CharField(max_length=120)
    Amount = models.FloatField()
    MpesaReceiptNumber = models.CharField(max_length=15)
    TransactionDate = models.DateTimeField()
    PhoneNumber = models.CharField(max_length=13)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return self.PhoneNumber
