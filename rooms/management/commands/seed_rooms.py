import random
from django.core.management.base import BaseCommand
from django.contrib.admin.utils import flatten
from django_seed import Seed
from rooms import models as room_models
from users import models as user_models


class Command(BaseCommand):

    help = 'This command creates rooms'

    def add_arguments(self, parser):
        parser.add_argument("--number", default=2, type=int, help="How many rooms do you want me to create?")


    def handle(self, *args, **options):
        number = options.get("number")
        seeder = Seed.seeder()
        all_users = user_models.User.objects.all()
        room_types = room_models.RoomType.objects.all()
        seeder.add_entity(room_models.Room, number, {
            "name": lambda x: seeder.faker.address(),
            "host": lambda x: random.choice(all_users),
            "room_type": lambda x: random.choice(room_types),
            "guests": lambda x: random.randint(1, 20),
            "price": lambda x: random.randint(1, 300),
            "beds": lambda x: random.randint(1, 5),
            "bedrooms": lambda x: random.randint(1, 5),
            "baths": lambda x: random.randint(1, 5),
        })
        created_photos = seeder.execute()
        created_clean = flatten(list(created_photos.values()))
        amenities = room_models.Amenity.objects.all()
        facilities = room_models.Facility.objects.all()
        rules = room_models.HouseRule.objects.all()
        for pk in created_clean: #생성된 모든 room을 pk로 그 room을 찾고
            room = room_models.Room.objects.get(pk=pk) #room의 인스턴스를 찾고
            for i in range(3, random.randint(10, 30)): # 3~최대 30개의 사진을 넣어주는데
                room_models.Photo.objects.create(
                    caption=seeder.faker.sentence(),
                    room=room,
                    file=f"room_photos/{random.randint(1, 31)}.webp"
                )

            #Many to Many 필드에다 fake시드를 넣어줄때
            for a in amenities:
                magic_number = random.randint(0, 15)
                if magic_number % 2 == 0:
                    room.amenities.add(a)
            for f in facilities:
                magic_number = random.randint(0, 15)
                if magic_number % 2 == 0:
                    room.facilities.add(f)
            for r in rules:
                magic_number = random.randint(0, 15)
                if magic_number % 2 == 0:
                    room.house_rules.add(r)
        self.stdout.write(self.style.SUCCESS(f'{number} rooms created!'))