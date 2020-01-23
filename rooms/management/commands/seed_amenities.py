from django.core.management.base import BaseCommand
from rooms.models import Amenity

class Command(BaseCommand):

    help = 'This command creates amenities'

    # def add_arguments(self, parser):
    #     parser.add_argument("--times", help="How many times do you want me to tell you that I love you?")

    def handle(self, *args, **options):
        amenities = [
            "Air conditioning",
            "Alarm Clock",
            "Balcony",
            "Bathroom",
            "Bathtub",
            "Bed Linen",
            "Boating",
            "Cable TV",
            "Carbon monoxide detectors",
            "Stereo",
            "Sofa",
            "Smoke detectors",
            "Shower",
            "Restaurant",
            "Queen size bed",
            "Oven",
            "Outdoor Tennis",
            "Outdoor Pool",
            "Indoor Pool",
            "Hair Dryer",
            "Golf",
            "Fridge / Freezer",
            "Free Parking",
            "Double bed",
            "Dishwasher",
            "Cookware & Kitchen Utensils",
            "Children Area",
            "Chairs",
            "Shopping Mall",
            "Hot tub",
            "Heating",
            "Hair Dryer",
            "Coffee Maker in Room",
            "TV",
            "Towels",
            "Swimming pool",
            "Microwave",
            "Ironing Board",
            "En suite bathroom",
            "Free Parking",
            "Freezer",
            "Free Wireless Internet"
        ]

        for a in amenities:
            Amenity.objects.create(name=a)
        self.stdout.write(self.style.SUCCESS("Amenities created!"))