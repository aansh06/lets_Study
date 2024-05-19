from django.shortcuts import  render , redirect
from django.db.models import Q
from django.http import HttpResponse
from .models import Room, Topic
from .forms import RoomForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login , logout
from django.contrib import messages

# Create your views here.


def loginPage(request):

    if request.method=="POST":
        username=request.POST.get('username')
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

    context={}
    return render(request,'study/login_register.html',context)


def logoutUser(request):
    logout(request)
    return redirect('home')

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


def createRoom(request):
    form = RoomForm()
    if request.method == 'POST' :
        form= RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    context={'form': form}
    return render(request, 'study/room_form.html',context)

def updateRoom( request , pk):
    room = Room.objects.get(id=pk)

    form= RoomForm(instance=room)

    if request.method == 'POST' :
        form= RoomForm(request.POST,instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')

    
    context= {'form':form}
    return render(request, 'study/room_form.html',context)



def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)
    if request.method == "POST":
        room.delete()
        return redirect('home')


    return render(request,'study/delete.html',{'obj':room})