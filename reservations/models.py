import datetime
from django.db import models
from django.utils import timezone
from core import models as core_models
from . import managers

class BookedDay(core_models.TimeStampedModel):

    day = models.DateTimeField()
    reservation = models.ForeignKey("Reservation", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Booked Day"
        verbose_name_plural = "Booked Days"

    def __str__(self):
        return str(self.day)

class Reservation(core_models.TimeStampedModel):
    """ Reservation Model Defintion """

    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELED = "canceled"

    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_CANCELED, "Canceled"),
    )

    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_PENDING)
    check_in = models.DateField()
    check_out = models.DateField()
    guest = models.ForeignKey("users.User", related_name="reservations", on_delete=models.CASCADE)
    room = models.ForeignKey("rooms.Room", related_name="reservations", on_delete=models.CASCADE)

    objects = managers.CustomReservationManager()

    def __str__(self):
        return f'{self.room} - {self.check_in}'

    def in_progress(self):
        now = timezone.now().date()
        return now >= self.check_in and now <= self.check_out

    in_progress.boolean = True #어드민 상에서 O인지 X인지 구별해주는 메서드

    def is_finished(self):
        now = timezone.now().date()
        return now > self.check_out

    is_finished.boolean = True

    def save(self, *args, **kwargs):
        if self.pk is None: # 이 조건은 새로운 예약이라는 뜻
            start = self.check_in
            end = self.check_out
            difference = end - start
            existing_booked_day = BookedDay.objects.filter(day__range=(start, end), reservation__room=self.room).exists() # 사이에 예약된 일자가 있는지 찾아보는 것
            if not existing_booked_day:
                super().save(*args, **kwargs) # reservation이 미리 save되어 있지 않으면 BookedDay에 reservation을 포린키로 저장할수 없기 때문
                for i in range(difference.days + 1):
                    day = start + datetime.timedelta(days=i)
                    BookedDay.objects.create(day=day, reservation=self)
                return
        return super().save(*args, **kwargs)


