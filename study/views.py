from django.shortcuts import render
from django.http import HttpResponse
from .models import Room
# Create your views here.


def home(request):
    rooms_list= Room.objects.all()
    context= {'rooms': rooms_list}
    return render(request,'study/home.html', context)



def room(request,pk):
    room_l = Room.objects.get(id=pk)
    
    context = {'room':room_l}
    return render(request,'study/room.html',context)
