from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail, EmailMessage
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from ecom import settings
from django.utils.encoding import force_bytes

# Create your views here.
from .tokens import generate_token


def home(request):
    return render(request, 'App/index.html')


def signup(request):
    if request.method == 'POST':
        # username = request.POST.get('username')
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username):
            messages.error(request, "Username already exists! ")
            return redirect('home')

        if User.objects.filter(email=email):
            messages.error(request, "email already exists! ")
            return redirect('home')

        myuser = User.objects.create_user(username, email, password)
        myuser.first_name = fname
        myuser.first_name = lname
        myuser.is_active = False
        myuser.save()
        messages.success(request,
                         "Your Account Has been successfully Created ! \n we have sent you a confirmation mail.\n Please confirm your email in order to activate your account.")

        # Welcome email
        subject = "Welcome to our ecommerce site !"
        message = "hello " + myuser.first_name + " !! \n\n " + " wellcome here"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        # email Adress Confirmation Email
        current_site = get_current_site(request)
        email_subject = "Confirm Your Email @ ecom - Django Login!!"
        message2 = render_to_string('email_confirmation.html', {
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = True
        email.send()
        return redirect('signin')
    return render(request, 'App/signup.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        print(user)
        if user is not None:
            login(request, user)
            fname = user.first_name
            return render(request, "App/index.html", {'fname': fname})
        else:
            messages.error(request, "Wrong Crendentials")
            return redirect('home')
    return render(request, 'App/signin.html')


def signout(request):
    logout(request)
    messages.success(request, "Logged out Successfully")
    return redirect('home')


def activate(request, uidb64, token):
    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DorsNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active = True
        myuser.save()
        login(request,myuser)
        return redirect('home')
    else:
        return render(request,'activation_fail.html')
