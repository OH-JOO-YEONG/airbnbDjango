from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from . import models

# Create your views here.
def all_rooms(request):
    page = request.GET.get("page", 1)
    room_list = models.Room.objects.all()
    paginator = Paginator(room_list, 10, orphans=5) # Paginator는 두개의 인자를 받음 1.객체의 목록 2.객체의 목록 개수
    try:
        rooms = paginator.page(int(page))
        return render(request, "rooms/home.html", context={
            "page": rooms,
        })
    except (EmptyPage, PageNotAnInteger):
        return redirect("/")
