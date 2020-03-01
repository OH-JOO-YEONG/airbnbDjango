from django import forms
from django_countries.fields import CountryField
from . import models

class SearchForm(forms.Form):
    city = forms.CharField(initial="Anywhere")
    country = CountryField(default="KR").formfield()
    room_type = forms.ModelChoiceField(required=False, empty_label="Any Kind", queryset=models.RoomType.objects.all())
    price = forms.IntegerField(required=False)
    guests = forms.IntegerField(required=False)
    bedrooms = forms.IntegerField(required=False)
    beds = forms.IntegerField(required=False)
    baths = forms.IntegerField(required=False)
    instant_book = forms.BooleanField(required=False)
    superhost = forms.BooleanField(required=False)
    amenities = forms.ModelMultipleChoiceField(required=False, queryset=models.Amenity.objects.all(), widget=forms.CheckboxSelectMultiple)
    facilities = forms.ModelMultipleChoiceField(required=False, queryset=models.Facility.objects.all(), widget=forms.CheckboxSelectMultiple)

    # 폼을 가지고자 하는 목적
    """
    HTML을 엄청 빨리 만들어준다.
    데이터를 다 정리해준다.(이상한 데이터들을 필드에 와서 int형인지 str형인지 정리시켜줌)
    
    """

class CreatePhotoForm(forms.ModelForm):

    class Meta:
        model = models.Photo
        fields = (
            "caption",
            "file",
        )

    def save(self, pk, *args, **kwargs):
        photo = super().save(commit=False)
        room = models.Room.objects.get(pk=pk)
        photo.room = room
        photo.save()
