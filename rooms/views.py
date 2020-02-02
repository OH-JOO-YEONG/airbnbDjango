from math import ceil
from django.shortcuts import render
from django.core.paginator import Paginator
from . import models

# Create your views here.
def all_rooms(request):
    page = request.GET.get("page")
    room_list = models.Room.objects.all()
    paginator = Paginator(room_list, 10, orphans=5) # Paginator는 두개의 인자를 받음 1.객체의 목록 2.객체의 목록 개수
    rooms = paginator.get_page(page)
    return render(request, "rooms/home.html", context={
        "page": rooms,
    })
