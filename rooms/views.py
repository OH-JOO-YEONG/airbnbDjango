from math import ceil
from django.shortcuts import render
from . import models

# Create your views here.
def all_rooms(request):
    page = request.GET.get("page", 1) # page의 값을 받는 것
    page = int(page or 1) # page 값이 빈 값이면 1을 받아오기
    page_size = 10 # page 값 정하기
    limit = page_size * page # page 당 리스트 값 제한
    offset = limit - page_size # page 당 오프셋 값
    all_rooms = models.Room.objects.all()[offset:limit]
    page_count = ceil(models.Room.objects.count() / page_size) # 전체 페이지 수 구하기
    return render(request, "rooms/home.html", context={
        "rooms": all_rooms,
        "page": page,
        "page_count": page_count,
        "page_range": range(1, page_count + 1),
    })
