from django.views.generic import ListView, View, UpdateView, DetailView, FormView
from django.http import Http404
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, reverse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users import mixins as user_mixins
from django.contrib.messages.views import SuccessMessageMixin
from . import models, forms


class HomeView(ListView):
    """ HomeView Definition """
    model = models.Room
    paginate_by = 12
    paginate_orphans = 5
    ordering = "created"
    context_object_name = "rooms"

def room_detail(request, pk):
    try:
        room = models.Room.objects.get(pk=pk)
        return render(request, "rooms/room_detail.html", context={
            'room': room,
        })
    except models.Room.DoesNotExist:
        raise Http404()

class SearchView(View):

    def get(self, request):
        country = request.GET.get("country")

        if country:
            form = forms.SearchForm(request.GET)
            if form.is_valid():
                city = form.cleaned_data.get("city")
                country = form.cleaned_data.get("country")
                room_type = form.cleaned_data.get("room_type")
                price = form.cleaned_data.get("price")
                guests = form.cleaned_data.get("guests")
                bedrooms = form.cleaned_data.get("bedrooms")
                beds = form.cleaned_data.get("beds")
                baths = form.cleaned_data.get("baths")
                instant_book = form.cleaned_data.get("instant_book")
                superhost = form.cleaned_data.get("superhost")
                amenities = form.cleaned_data.get("amenities")
                facilities = form.cleaned_data.get("facilities")

                filter_args = {}

                if city != "Anywhere":
                    filter_args["city__startswith"] = city

                filter_args["country"] = country

                if room_type is not None:
                    filter_args["room_type"] = room_type

                if price is not None:
                    filter_args["price__lte"] = price  # less than and equals

                if guests is not None:
                    filter_args["guests__gte"] = guests  # greater than and equals

                if bedrooms is not None:
                    filter_args["bedrooms__gte"] = bedrooms

                if beds is not None:
                    filter_args["beds__gte"] = beds

                if baths is not None:
                    filter_args["baths__gte"] = baths

                if instant_book is True:
                    filter_args["instant_book"] = True

                if superhost is True:
                    filter_args["host__superhost"] = True

                qs = models.Room.objects.filter(**filter_args).order_by("-created")

                for amenity in amenities:
                    qs = qs.filter(amenities__pk=amenity.pk)

                for facility in facilities:
                    qs = qs.filter(facilities__pk=facility.pk)

                paginator = Paginator(qs, 10, orphans=5)

                page = request.GET.get("page", 1)

                rooms = paginator.get_page(page)

                get_copy = request.GET.copy()

                parameters = get_copy.pop('page', True) and get_copy.urlencode()

                return render(request, "rooms/search.html", {
                    "form": form,
                    "rooms": rooms,
                    "parameters": parameters,
                })

        else:
            form = forms.SearchForm()

        return render(request, "rooms/search.html", {
            "form": form,
        })


class EditRoomView(user_mixins.LoggedInOnlyView, UpdateView):

    """ 방 정보 변경 """

    model = models.Room
    fields = (
        "name",
        "description",
        "country",
        "city",
        "price",
        "address",
        "guests",
        "beds",
        "bedrooms",
        "baths",
        "check_in",
        "check_out",
        "instant_book",
        "room_type",
        "amenities",
        "facilities",
        "house_rules",
    )
    template_name = "rooms/rooms_edit.html"

    def get_object(self, queryset=None):
        room = super().get_object(queryset=queryset)
        if room.host.pk != self.request.user.pk:
            raise Http404()
        return room

class RoomPhotosView(user_mixins.LoggedInOnlyView, DetailView):

    """ 방 사진 목록 """

    model = models.Room
    template_name = "rooms/room_photos.html"

    def get_object(self, queryset=None):
        room = super().get_object(queryset=queryset)
        if room.host.pk != self.request.user.pk:
            raise Http404()
        return room

@login_required
def delete_photos(request, room_pk, photo_pk):
    user = request.user
    try:
        room = models.Room.objects.get(pk=room_pk)
        if room.host.pk != user.pk:
            messages.error(request, "Can't delete that photo")
        else:
            models.Photo.objects.filter(pk=photo_pk).delete()
            messages.success(request, "Photo Deleted")
        return redirect(reverse("rooms:photos", kwargs={"pk": room_pk}))
    except models.Room.DoesNotExist:
        return redirect(reverse("core:home"))

def delete_rooms(request, pk):
    room = models.Room.objects.get(pk=pk)

    if request.method == 'POST':
        room.delete()
        return redirect(reverse("core:home"))

    return render(request, "rooms/rooms_delete.html", {
        "room": room,
    })

class EditPhotoView(user_mixins.LoggedInOnlyView, SuccessMessageMixin, UpdateView):

    """ 방 사진의 Caption 변화 """

    model = models.Photo
    template_name = "rooms/photo_edit.html"
    pk_url_kwarg = 'photo_pk' # UpdateView 는 argument를 찾아서 바꿔야하는데(pk형식만 찾음) 이걸 지정안하면 Photo pk 값을 찾을 수 없다 그래서 pk url을 찾는 방법임
    success_message = "Photo Update"
    fields = (
        "caption",
    )

    def get_success_url(self): # 성공하면 돌아가는 페이지
        room_pk = self.kwargs.get("room_pk") #room_pk argument 얻는 방법
        return reverse("rooms:photos", kwargs={"pk": room_pk})

class AddPhotoView(user_mixins.LoggedInOnlyView, FormView):

    """ 방 사진 추가 """

    template_name = "rooms/photo_create.html"
    form_class = forms.CreatePhotoForm

    def form_valid(self, form):
        pk = self.kwargs.get('pk')
        form.save(pk)
        messages.success(self.request, "Photo Uploaded")
        return redirect(reverse("rooms:photos", kwargs={'pk': pk}))

class CreateRoomView(user_mixins.LoggedInOnlyView, FormView):

    form_class = forms.CreateRoomForm
    template_name = "rooms/room_create.html"

    def form_valid(self, form): # interception 기법인데 폼에서 save를 commit=False로 해서 인스턴스에 저장 후 반환해서 이 뷰에서 받은 것
        room = form.save() # forms.py의 room을 반환한걸 받은 것
        room.host = self.request.user
        room.save() # 호스트를 저장했으니 세이브
        form.save_m2m() # forms.py에서 commit=False 했기 때문에 save()메서드로는 ManytoMany필드 양식이 저장 안됐었음. 그래서 save_m2m() 메서드를 한번 더 해주는 것
        messages.success(self.request, "Room Created")
        return redirect(reverse("rooms:detail", kwargs={'pk': room.pk}))




















