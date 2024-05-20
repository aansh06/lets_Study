from django.shortcuts import  render , redirect
from django.db.models import Q
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login , logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse

from .models import Room, Topic, Message
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

    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q))[0:3]

    context= {'rooms': rooms_list, 'topics':topics,'room_count':room_count,"room_messages":room_messages}
    return render(request,'study/home.html', context)



def room(request,pk):
    room_l = Room.objects.get(id=pk)
    room_messages = room_l.message_set.all().order_by('-created')
    participants = room_l.participants.all()
    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room_l,
            body=request.POST.get('body')
        )
        room_l.participants.add(request.user)
        return redirect('room',pk=room_l.id)
    context = {'room':room_l,'room_messages':room_messages ,"participants":participants}
    return render(request,'study/room.html',context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    if request.method == 'POST' :
        form= RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit= False)
            room.host = request.user
            room.save()
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

@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'study/delete.html', {'obj': message})


def userProfile(request,pk):
    user = User.objects.get(id=pk)

    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms,
               'room_messages': room_messages, 'topics': topics}
    
    return render(request, 'study/profile.html', context)