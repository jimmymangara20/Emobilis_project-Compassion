import base64
from datetime import datetime

import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction

from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import FileSystemStorage

from django_daraja.mpesa.core import MpesaClient
from rest_framework import status
from django.http import JsonResponse

from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from compassionProject.settings import MPESA_SHORTCODE, MPESA_CONSUMER_KEY, MPESA_PASSKEY, MPESA_CONSUMER_SECRET
from .models import UploadedImage, Sponsorship, LNMOnline, SupportLater
from .models import Appointment
from .models import Child
from .serializer import LNMOnlineSerializer

User = get_user_model()

unformatted_time = datetime.now()
formatted_time = unformatted_time.strftime("%Y%m%d%H%M%S")

data_to_encode = MPESA_SHORTCODE + MPESA_PASSKEY + formatted_time
encoded_string_p = base64.b64encode(data_to_encode.encode())
decoded_password = encoded_string_p.decode('utf-8')

consumer_key = MPESA_CONSUMER_KEY
consumer_secret = MPESA_CONSUMER_SECRET




# noinspection PyCompatibility
def generate_access_token(consumer_key_p, consumer_secret_p):
    token_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    credentials = f"{consumer_key_p}:{consumer_secret_p}"
    base64_credentials = base64.b64encode(credentials.encode()).decode()
    headers = {'Authorization': f'Basic {base64_credentials}'}

    try:
        response = requests.get(token_url, headers=headers)
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")

        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        access_token = data.get('access_token')
        if not access_token:
            raise ValueError("Failed to obtain access token.")
        return access_token
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except ValueError as e:
        print(f"Error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def lipa_na_mpesa(amount, phone_number):
    cl = MpesaClient()
    account_reference = "10101010"  # Use a unique reference per transaction if needed
    transaction_desc = "Support A Child"
    callback_url = "https://2cf4-41-89-22-3.ngrok-free.app/callback/"  # Ensure this is accessible

    # Initiate STK Push with the `django_daraja` MpesaClient
    try:
        response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)
        print("STK Push Response:", response)  # Log or return the response if needed
        return response
    except Exception as e:
        print(f"STK Push request failed: {e}")
        return None


def confirm_support(request):
    if request.method == "POST":
        sponsor_number = request.POST.get('sponsor_number')
        receipt_number = request.POST.get('receipt_number')

        # Check if the payment transaction exists and is unused
        support = LNMOnline.objects.filter(PhoneNumber=sponsor_number, MpesaReceiptNumber=receipt_number,
                                           is_used=False).first()

        if support:
            try:
                # Start a transaction to ensure all operations succeed or fail together
                with transaction.atomic():
                    # Mark the payment as used
                    support.is_used = True
                    support.save()

                    # Retrieve the corresponding sponsorship record
                    sponsorship = Sponsorship.objects.filter(sponsor_phone=sponsor_number, is_completed=False).first()
                    sponsorship.is_completed = True
                    sponsorship.save()

                    # Deduct the sponsorship amount from the child's required amount
                    amount = sponsorship.amount
                    child = sponsorship.sponsored_child
                    child.amount_needed -= amount
                    child.amount_supported += amount
                    child.save()

                    # Render success page
                    return render(request, 'successful_support.html', {'amount': amount, 'child': child})

            except Sponsorship.DoesNotExist:
                # Handle the case where the sponsorship is not found
                return render(request, "confirm_support.html",
                              {'message': 'No active sponsorship found for this sponsor number.'})
            except Exception as e:
                # Catch any other errors
                return render(request, "confirm_support.html", {'message': f'An error occurred: {str(e)}'})
        else:
            # Handle case where the transaction was not found or already used
            return render(request, "confirm_support.html", {
                'message': 'A transaction with such details does not exist or has already been used. Please check again.'})

    # If not a POST request, render the confirmation page
    return render(request, "confirm_support.html", {})


class LNMCallbackUrlAPIView(CreateAPIView):
    queryset = LNMOnline.objects.all()
    serializer_class = LNMOnlineSerializer

    def create(self, request, *args, **kwargs):
        print("Callback Data:", request.data)
        try:
            merchant_request_id = request.data['Body']['stkCallback']['MerchantRequestID']
            checkout_request_id = request.data['Body']['stkCallback']['CheckoutRequestID']
            result_code = request.data['Body']['stkCallback']['ResultCode']
            result_description = request.data['Body']['stkCallback']['ResultDesc']
            amount = request.data['Body']['stkCallback']['CallbackMetadata']['Item'][0]['Value']
            mpesa_receipt_number = request.data['Body']['stkCallback']['CallbackMetadata']['Item'][1]['Value']
            transaction_date = request.data['Body']['stkCallback']['CallbackMetadata']['Item'][3]['Value']
            phone_number = request.data['Body']['stkCallback']['CallbackMetadata']['Item'][4]['Value']

            str_transaction_date = str(transaction_date)
            transaction_datetime = datetime.strptime(str_transaction_date, "%Y%m%d%H%M%S")

            model = LNMOnline.objects.create(
                CheckoutRequestID=checkout_request_id, MerchantRequestID=merchant_request_id,
                ResultCode=result_code, ResultDesc=result_description, Amount=amount,
                MpesaReceiptNumber=mpesa_receipt_number, TransactionDate=transaction_datetime,
                PhoneNumber=phone_number
            )
            model.save()
            return Response({"status": "Success"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"Callback handling failed: {e}")
            return Response({"status": "Failed"}, status=status.HTTP_400_BAD_REQUEST)


# Create your views here.
def index(request):
    return render(request, "index.html")


def about(request):
    return render(request, "about.html")


def sponsor_a_child(request):
    children = Child.objects.all()
    return render(request, "sponsor_a_child.html", {'children': children})


def team(request):
    return render(request, "team.html")


def sponsor(request):
    return render(request, "sponsor.html")


def account(request):
    return render(request, "account.html")


def gallery(request):
    return render(request, "gallery.html", {})


def form(request):
    return render(request, "form.html")


def show_appointments(request):
    appointments = Appointment.objects.filter(user=request.user)
    return render(request, "show_appointments.html", {'appointments':appointments})


def support_later(request, id):
    # Fetch the child object using the provided ID
    try:
        child = Child.objects.get(id=id)  # Using get() will raise an exception if the child is not found
    except Child.DoesNotExist:
        return JsonResponse({'message': 'Child not found'}, status=404)

    supporter = request.user

    # Check if the support entry already exists for the user and the child
    if SupportLater.objects.filter(user=supporter, child=child).exists():
        # If it exists, delete it and return a message
        SupportLater.objects.filter(user=supporter, child=child).delete()
        return JsonResponse({'message': 'Child removed form support later successfully', 'color': 'red'}, status=200)
    else:
        # If it doesn't exist, create the entry and return a success message
        SupportLater.objects.create(user=supporter, child=child)
        return JsonResponse({'message': 'Child added form support later successfully', 'color': 'green'}, status=201)


def show_sponsorship(request):
    sponsorships = Child.objects.all()
    return render(request, "show_sponsorship.html", {'sponsorships': sponsorships})


@login_required
def get_support_laters(request):
    children = []
    support_laters = SupportLater.objects.filter(user=request.user)
    for support_later in support_laters:
        children.append(support_later.child)
    return render(request, "show_supportlaters.html", {'children':children})


# function to push appointments
@login_required
def appointment(request):
    if request.method == "POST":
        new_appointment = Appointment(
            user=request.user,
            date=request.POST["appointment_date"],
            message=request.POST["message"],
        )
        new_appointment.save()
        return render(request, "appointment_success.html")
    else:
        return render(request, "contact.html")


# Retrieve all appointments
@login_required
def retrieve_appointments(request):
    # Create a variable to store these appointments
    appointments = Appointment.objects.filter(user=request.user)
    context = {"appointments": appointments}
    return render(request, 'show_appointments.html', context)


# delete
def delete_appointments(request, id):
    appointment = Appointment.objects.get(id=id)
    appointment.delete()
    return redirect('myapp:show_appointments')


# Update
def edit_appointments(request, appointment_id):
    # update the appointments
    # Retrieve the appointment object or return a 404 error
    appointment = get_object_or_404(Appointment, id=appointment_id)
    # Put the condition for the form to update
    # Check if the request method is POST (form submission)
    if request.method == "POST":
        appointment.phone = request.POST.get("phone")
        appointment.date = request.POST.get("date")
        appointment.message = request.POST.get("message")
        appointment.save()
        return redirect('myapp:show_appointments')
    context = {"appointment": appointment}
    return render(request, 'edit_appointments.html', context)


# Functions to push sponsorship
def sponsorship_form(request, id):
    child = Child.objects.get(id=id)
    sponsor = None
    if request.user.is_authenticated:
        sponsor = request.user
    if request.method == "POST":
        child_id = request.POST.get("child_id")
        sponsor_f_name = request.POST.get("f_name")
        sponsor_l_name = request.POST.get("l_name")
        sponsor_email = request.POST.get("email")
        sponsor_phone = request.POST.get("number")
        amount = int(request.POST.get("amount"))
        support = Sponsorship.objects.create(
            user=sponsor,
            sponsored_child=Child.objects.get(id=child_id),
            sponsor_name=sponsor_f_name + ' ' + sponsor_l_name,
            sponsor_email=sponsor_email,
            sponsor_phone=sponsor_phone,
            amount=amount,
        )
        support.save()
        lipa_na_mpesa(amount, sponsor_phone)
        return redirect('myapp:confirm_support')
    else:
        return render(request, 'sponsorship_form.html', {'child': child, 'sponsor': sponsor})


# Retrieve all the sponsorship
def retrieve_sponsorship(request):
    sponsorship = Child.objects.all()
    context = {"sponsorship": sponsorship}
    return render(request, 'edit_sponsorship.html', context)


# Delete
def delete_sponsorship(request, id):
    sponsor = Child.objects.get(id=id)
    sponsor.delete()
    return redirect('myapp:show_sponsorship')


# Update
def edit_sponsorship(request, sponsor_id):
    sponsor = get_object_or_404(Child, id=sponsor_id)
    if request.method == "POST":
        sponsor.name = request.POST.get("name")
        sponsor.age = request.POST.get("age")
        sponsor.gender = request.POST.get("gender")
        sponsor.Religion = request.POST.get("religion")
        sponsor.save()
        return redirect('myapp:show_sponsorship')
    context = {"sponsor": sponsor}
    return render(request, 'edit_sponsorship.html', context)


# XAMPP
def upload_image(request):
    if request.method == "POST":
        title = request.POST["title"]
        uploaded_file = request.FILES["image"]
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_url = fs.url(filename)
        image = UploadedImage.objects.create(title=title, image=filename)
        image.save()
        return render(request, 'upload_success.html', {'file_url': file_url})
    return render(request, 'upload_image.html')

# #A sponsor can select a child to sponsor and update their sponsorship details
# @login_required
# def sponsor_child(request, child_id):
#     child = get_object_or_404(Child, id=child_id)
#     if request.method == 'POST':
#         sponsor, created = Sponsor.objects.get_or_create(user=request.user)
#         sponsor.sponsored_child = child
#         sponsor.save()
#
#         # Mark child as sponsored
#         child.sponsored = True
#         child.save()
#
#         return redirect('children:child_list')  # Redirect back to the child list
#     return render(request, 'sponsor_a_child.html', {'child': child})
