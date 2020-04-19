from django.shortcuts import render, redirect, reverse
from django.views.generic import TemplateView
from rooms import models as room_models
from . import models

def toggle_room(request, room_pk):
    action = request.GET.get('action', None)
    room = room_models.Room.objects.get_or_none(pk=room_pk)
    if room is not None and action is not None:
        # get_or_create는 두가지 변수를 지정하지 않고 한가지로 정하면 튜플형태로 나온다. 그래서 _로 unpack해줌
        the_list, _ = models.List.objects.get_or_create( # get_or_create는 하나만 찾도록 돼있다 하나의 objects만 찾는다 만약 많은 리스트가 있으면 multiple objects error가 발생.
            user=request.user,
            name="My Favorite Houses",
        )
        if action == 'add':
            the_list.rooms.add(room)
        elif action == 'remove':
            the_list.rooms.remove(room)
    return redirect(reverse("rooms:detail", kwargs={
        "pk": room_pk,
    }))


class SeeFavsView(TemplateView):

    template_name = "lists/lists_detail.html"

