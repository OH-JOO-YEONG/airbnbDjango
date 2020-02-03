from django.db import models
from django.urls import reverse
from django_countries.fields import CountryField
from core import models as core_models
from users import models as user_models

class AbstractItem(core_models.TimeStampedModel):
    """ Abstract Item """

    name = models.CharField(max_length=80)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

class RoomType(AbstractItem):
    """ RoomType Model Definition """

    class Meta:
        verbose_name = "Room Type"

class Amenity(AbstractItem):
    """ Amenity Model Definition """

    class Meta:
        verbose_name_plural = "Amenities"

class Facility(AbstractItem):
    """ Facility Model Definition """

    class Meta:
        verbose_name_plural = "Facilities"

class HouseRule(AbstractItem):
    """ HouseRule Model Definition """

    class Meta:
        verbose_name = "House Rule"

class Photo(core_models.TimeStampedModel):
    """ Photo Model Definition """

    caption = models.CharField(max_length=80)
    file = models.ImageField(upload_to="room_photos") # upload_to는 폴더를 만들면서 그 경로에 저장하는 것
    room = models.ForeignKey("Room", related_name="photos", on_delete=models.CASCADE) # 포린키를 String으로 연결하는 방법도 있다.(모델이 많거나, 위에서 아래로 읽는 파이썬의 방식이 마음에 안들면 쓴다.

    def __str__(self):
        return self.caption

class Room(core_models.TimeStampedModel):
    """ Room Model Definition"""
    name = models.CharField(max_length=140)
    description = models.TextField()
    country = CountryField()
    city = models.CharField(max_length=80)
    price = models.IntegerField()
    address = models.CharField(max_length=140)
    guests = models.IntegerField()
    beds = models.IntegerField()
    bedrooms = models.IntegerField()
    baths = models.IntegerField()
    check_in = models.TimeField()
    check_out = models.TimeField()
    instant_book = models.BooleanField(default=False)
    host = models.ForeignKey(user_models.User, related_name="rooms", on_delete=models.CASCADE) # 다른 모델에 있는 것을 String으로 연결할 때는 "users.user" 로 연결
    room_type = models.ForeignKey(RoomType, related_name="rooms", on_delete=models.SET_NULL, null=True)
    amenities = models.ManyToManyField(Amenity, related_name="rooms", blank=True)
    facilities = models.ManyToManyField(Facility, related_name="rooms", blank=True)
    house_rules = models.ManyToManyField(HouseRule, related_name="rooms", blank=True)

    def save(self, *args, **kwargs):
        self.city = str.capitalize(self.city)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("rooms:detail", kwargs={'pk': self.pk})

    def __str__(self):
        return self.name

    def total_rating(self):
        all_reviews = self.reviews.all()
        all_ratings = 0
        if len(all_reviews) > 0:
            for review in all_reviews:
                all_ratings += review.rating_average()
            return round(all_ratings / len(all_reviews), 2)
        return 0


