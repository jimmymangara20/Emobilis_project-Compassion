from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model

User = get_user_model()


# Create your views here.
# Show the registration form.
def register(request):
    # Initialize an empty context to hold form data
    context = {
        'username': '',
        'first_name': '',
        'second_name': '',
        'email': '',
        'error_message': ''
    }

    if request.method == 'POST':
        # Get data from the form
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        second_name = request.POST.get('second_name')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        email = request.POST.get('email')

        # Update context with user-submitted data
        context.update({
            'username': username,
            'first_name': first_name,
            'second_name': second_name,
            'email': email,
        })

        # Perform validations
        if password != confirm_password:
            context['error_message'] = 'Passwords do not match'
        elif User.objects.filter(username=username).exists():
            context['error_message'] = 'Username already taken'
        else:
            try:
                # Create the user if no errors were found
                user = User.objects.create_user(username=username, password=password)
                user.first_name = first_name
                user.last_name = second_name
                user.email = email
                user.is_supporter = True  # Custom field
                user.save()

                # Success message and redirect to login page
                messages.success(request, "Compassion Supporter account successfully created")
                return redirect('accounts:login')  # Adjust URL name if necessary
            except Exception as e:
                # In case of unexpected errors during user creation
                context['error_message'] = f"An error occurred: {str(e)}"

        # If there was any error (password mismatch or username taken), we set it to context
        if context['error_message']:
            messages.error(request, context['error_message'])

    # Render the registration form with context (including any errors and form data)
    return render(request, 'accounts/register.html', context)

#Beneficiary Login
def login_view(request):
    """ Login view """
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        # Check if the user exists
        if user is not None:
            login(request, user)
            messages.success(request, "You are now logged in!")
            return redirect("myapp:index")
        else:
            messages.error(request, "Invalid login credentials")
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('accounts:login')

