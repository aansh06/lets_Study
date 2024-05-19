from django.shortcuts import  render , redirect
from django.db.models import Q
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login , logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse

from .models import Room, Topic
from .forms import RoomForm
# Create your views here.


def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method=="POST":
        username=request.POST.get('username').lower()
        password=request.POST.get('password')

        try :
            user=User.objects.get(username=username)
        except:
            messages.error(request, "User Doesn't exist")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request, ' Username or Password incorrect')

    context={'page':page}
    return render(request,'study/login_register.html',context)


def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    page='register'
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user=form.save(commit = False)
            user.username = user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,"Register again")


    context={'page':page , 'form':form}
    return render(request, 'study/login_register.html',context)

def home(request):
    q= request.GET.get('q') if request.GET.get('q') != None else ''
    rooms_list= Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    topics = Topic.objects.all()
    room_count=rooms_list.count()
    context= {'rooms': rooms_list, 'topics':topics,'room_count':room_count}
    return render(request,'study/home.html', context)



def room(request,pk):
    room_l = Room.objects.get(id=pk)
    
    context = {'room':room_l}
    return render(request,'study/room.html',context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    if request.method == 'POST' :
        form= RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    context={'form': form}
    return render(request, 'study/room_form.html',context)


@login_required(login_url='login')
def updateRoom( request , pk):
    room = Room.objects.get(id=pk)

    form= RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse("You are not allowed Here!!!")

    if request.method == 'POST' :
        form= RoomForm(request.POST,instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')

    
    context= {'form':form}
    return render(request, 'study/room_form.html',context)


@login_required(login_url='login')
def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse("You are not allowed Here!!!")

    if request.method == "POST":
        room.delete()
        return redirect('home')


    return render(request,'study/delete.html',{'obj':room})