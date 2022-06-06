from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponse


# Create your views here.


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

        myuser = User.objects.create_user(username, email, password)
        myuser.first_name = fname
        myuser.first_name = lname
        # myuser.is_active = False
        myuser.save()
        messages.success(request, "Your Account Has been successfully Created !")
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
