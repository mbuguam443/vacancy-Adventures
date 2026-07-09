import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
from datetime import date, timedelta
from core.models import SiteSetting, Service, WhyChooseUs, Testimonial, Gallery, FAQ, ContactMessage, NewsletterSubscriber
from tours.models import Destination, Hotel, Vehicle, TourGuide, TourPackage, TourImage
from blog.models import BlogCategory, BlogPost
from bookings.models import Booking, Review
from payments.models import Payment
import os
from django.conf import settings
from shutil import copy2

class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')
        self.create_site_settings()
        self.create_services()
        self.create_why_choose_us()
        self.create_destinations()
        self.create_hotels()
        self.create_vehicles()
        self.create_guides()
        self.create_tours()
        self.create_testimonials()
        self.create_faqs()
        self.create_blog_categories()
        self.create_blog_posts()
        self.create_gallery()
        self.create_users()
        self.create_bookings()
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))

    def copy_img(self, src_name, dest_path):
        src = os.path.join(settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else os.path.join(settings.BASE_DIR, 'static'), 'images', src_name)
        full_dest = os.path.join(settings.MEDIA_ROOT, dest_path)
        os.makedirs(os.path.dirname(full_dest), exist_ok=True)
        if os.path.exists(src) and not os.path.exists(full_dest):
            copy2(src, full_dest)
        return dest_path

    def create_site_settings(self):
        if SiteSetting.objects.exists():
            return
        SiteSetting.objects.create(
            site_name='Vacay Adventure',
            tagline='Explore the World with Confidence',
            email='info@safaritours.com',
            phone='+254 700 123 456',
            address='Nairobi, Kenya',
            facebook='https://facebook.com/safaritours',
            twitter='https://twitter.com/safaritours',
            instagram='https://instagram.com/safaritours',
            linkedin='https://linkedin.com/company/safaritours',
            about_short='Vacay Adventure is your premier travel companion for exploring the wonders of Africa. We specialize in crafting unforgettable safari experiences, beach holidays, and cultural adventures.',
            trips_done=534,
            corporate_clients=424,
            visited_countries=35,
            team_members=15,
        )
        self.stdout.write('  Site settings created')

    def create_services(self):
        if Service.objects.exists():
            return
        services = [
            {'icon': 'lni lni-apartment', 'title': 'Hotel Booking', 'description': 'Book the best hotels and resorts at competitive rates with our easy booking system.', 'order': 1},
            {'icon': 'lni lni-plane', 'title': 'Flight Booking', 'description': 'Find and book flights to destinations worldwide with the best available prices.', 'order': 2},
            {'icon': 'lni lni-ship', 'title': 'Ship Booking', 'description': 'Experience luxury cruises and boat tours across the most beautiful waters.', 'order': 3},
            {'icon': 'lni lni-car-alt', 'title': 'Car Booking', 'description': 'Rent vehicles for your travels with our reliable car rental service.', 'order': 4},
        ]
        for s in services:
            Service.objects.create(**s)
        self.stdout.write('  Services created')

    def create_why_choose_us(self):
        if WhyChooseUs.objects.exists():
            return
        items = [
            {'icon': 'lni lni-user', 'title': 'Expert Local Guides', 'description': 'Our guides have years of experience and deep knowledge of wildlife, culture, and history.', 'order': 1},
            {'icon': 'lni lni-tag', 'title': 'Best Price Guarantee', 'description': 'We offer competitive prices without compromising on quality and service.', 'order': 2},
            {'icon': 'lni lni-headphone', 'title': '24/7 Customer Support', 'description': 'Our team is available round the clock to assist you before, during, and after your trip.', 'order': 3},
            {'icon': 'lni lni-diamond', 'title': 'Tailored Experiences', 'description': 'Every trip is customized to match your preferences, interests, and budget.', 'order': 4},
        ]
        for item in items:
            WhyChooseUs.objects.create(**item)
        self.stdout.write('  Why Choose Us created')

    def create_destinations(self):
        if Destination.objects.exists():
            return
        data = [
            {'name': 'Masai Mara', 'description': 'Experience the Great Migration and the Big Five in Kenya\'s most famous reserve. The Masai Mara National Reserve is renowned for its exceptional population of lions, leopards, cheetahs, and African bush elephants. It also hosts the Great Migration of wildebeest and zebras from Serengeti.', 'country': 'Kenya', 'best_season': 'July to October'},
            {'name': 'Amboseli National Park', 'description': 'Home to large herds of elephants with spectacular views of Mount Kilimanjaro. The park offers classic savannah landscapes and is one of the best places in Africa to view large herds of elephants up close.', 'country': 'Kenya', 'best_season': 'June to October'},
            {'name': 'Diani Beach', 'description': 'Pristine white sand beaches along Kenya\'s stunning Indian Ocean coast. Diani Beach is famous for its coral reefs, water sports, and luxurious beach resorts.', 'country': 'Kenya', 'best_season': 'December to March'},
            {'name': 'Lake Nakuru', 'description': 'Famous for its flamingo populations and diverse birdlife. The lake is surrounded by wooded and bushy grasslands, hosting a variety of wildlife including both black and white rhinos.', 'country': 'Kenya', 'best_season': 'January to March'},
            {'name': 'Tsavo National Park', 'description': 'One of the largest national parks in the world, known for its red elephants and dramatic landscapes. Tsavo is divided into Tsavo East and Tsavo West, each with unique features.', 'country': 'Kenya', 'best_season': 'June to October'},
            {'name': 'Watamu', 'description': 'A paradise for beach lovers with crystal clear waters and vibrant marine life. Watamu Marine National Park is a haven for snorkeling, diving, and deep-sea fishing.', 'country': 'Kenya', 'best_season': 'October to March'},
            {'name': 'Serengeti National Park', 'description': 'Tanzania\'s oldest and most popular national park, a UNESCO World Heritage site renowned for the annual migration of wildebeest and zebra.', 'country': 'Tanzania', 'best_season': 'June to September'},
            {'name': 'Zanzibar', 'description': 'A tropical paradise with pristine beaches, coral reefs, and rich Swahili history. Stone Town is a UNESCO World Heritage site.', 'country': 'Tanzania', 'best_season': 'June to October'},
            {'name': 'Victoria Falls', 'description': 'One of the Seven Natural Wonders of the World, offering breathtaking views and adventure activities like bungee jumping and white-water rafting.', 'country': 'Zimbabwe', 'best_season': 'April to October'},
            {'name': 'Cape Town', 'description': 'A stunning coastal city with Table Mountain, beautiful beaches, vibrant culture, and world-class wineries.', 'country': 'South Africa', 'best_season': 'November to March'},
        ]
        for d in data:
            dest = Destination.objects.create(**d)
            self.copy_img(f'destination_{len(Destination.objects.all())}.jpg', f'destinations/{dest.slug}.jpg')
            # Update with copied image
            img_path = self.copy_img(f'destination_{Destination.objects.count()}.jpg', f'destinations/{dest.slug}.jpg')
            if os.path.exists(os.path.join(settings.MEDIA_ROOT, img_path)):
                dest.featured_image = img_path
                dest.save()
        self.stdout.write('  Destinations created')

    def create_hotels(self):
        if Hotel.objects.exists():
            return
        names = [
            'Mara Serena Safari Lodge', 'Amboseli Serena Safari Lodge', 'Diani Reef Beach Resort',
            'Lake Nakuru Lodge', 'Sarova Salt Lick Game Lodge', 'Watamu Turtle Bay Resort',
            'Keekorok Lodge', 'Mountain Lodge'
        ]
        for i, name in enumerate(names):
            hotel = Hotel.objects.create(
                name=name,
                description=f'{name} offers comfortable accommodations with excellent service.',
                rating=random.randint(3, 5),
                address=f'{name}, Kenya',
            )
            img = self.copy_img(f'hotel_{i+1}.jpg', f'hotels/{slugify(name)}.jpg')
            if os.path.exists(os.path.join(settings.MEDIA_ROOT, img)):
                hotel.image = img
                hotel.save()
        self.stdout.write('  Hotels created')

    def create_vehicles(self):
        if Vehicle.objects.exists():
            return
        data = [
            {'name': 'Toyota Land Cruiser Safari Jeep', 'capacity': 7, 'vehicle_type': '4x4 Safari Jeep'},
            {'name': 'Toyota Hiace Minibus', 'capacity': 12, 'vehicle_type': 'Minibus'},
            {'name': 'Mercedes Sprinter', 'capacity': 18, 'vehicle_type': 'Luxury Van'},
            {'name': 'Range Rover Vogue', 'capacity': 5, 'vehicle_type': 'Luxury SUV'},
            {'name': 'Nissan Patrol', 'capacity': 7, 'vehicle_type': '4x4 SUV'},
        ]
        for i, v in enumerate(data):
            vehicle = Vehicle.objects.create(**v)
            img = self.copy_img(f'vehicle_{i+1}.jpg', f'vehicles/{slugify(v["name"])}.jpg')
            if os.path.exists(os.path.join(settings.MEDIA_ROOT, img)):
                vehicle.image = img
                vehicle.save()
        self.stdout.write('  Vehicles created')

    def create_guides(self):
        if TourGuide.objects.exists():
            return
        data = [
            {'name': 'John Kamau', 'bio': 'Expert wildlife guide with 15 years of experience in Masai Mara and Amboseli.', 'experience_years': 15},
            {'name': 'Grace Wanjiku', 'bio': 'Specialist in bird watching and botanical tours with extensive knowledge of Kenyan ecosystems.', 'experience_years': 10},
            {'name': 'Peter Omondi', 'bio': 'Cultural tour specialist fluent in multiple local languages and expert in East African history.', 'experience_years': 12},
            {'name': 'Sarah Akinyi', 'bio': 'Marine biologist and beach tour guide with expertise in Diani and Watamu marine parks.', 'experience_years': 8},
            {'name': 'David Mwangi', 'bio': 'Adventure tour leader specializing in hiking, climbing, and extreme sports.', 'experience_years': 7},
            {'name': 'Emily Chebet', 'bio': 'Photography tour guide helping travelers capture stunning wildlife and landscape shots.', 'experience_years': 9},
            {'name': 'James Kiprop', 'bio': 'Senior guide with expertise in Great Rift Valley geology and paleontology.', 'experience_years': 20},
            {'name': 'Faith Nyambura', 'bio': 'Luxury travel specialist providing premium tour experiences for discerning travelers.', 'experience_years': 6},
            {'name': 'Samuel Leken', 'bio': 'Maasai guide offering authentic cultural experiences and deep knowledge of Maasai traditions.', 'experience_years': 11},
            {'name': 'Diana Wambui', 'bio': 'Family tour specialist creating memorable and safe experiences for travelers of all ages.', 'experience_years': 5},
        ]
        for i, g in enumerate(data):
            guide = TourGuide.objects.create(**g)
            img = self.copy_img(f'tourguide_{i+1}.jpg', f'guides/{slugify(g["name"])}.jpg')
            if os.path.exists(os.path.join(settings.MEDIA_ROOT, img)):
                guide.image = img
                guide.save()
        self.stdout.write('  Guides created')

    def create_tours(self):
        if TourPackage.objects.exists():
            return
        dests = list(Destination.objects.all())
        hotels = list(Hotel.objects.all())
        vehicles = list(Vehicle.objects.all())
        guides = list(TourGuide.objects.all())

        tour_data = [
            {'title': 'Masai Mara Safari Adventure', 'destination': 'Masai Mara', 'duration_days': 5, 'duration_nights': 4, 'price': 120000, 'discount_price': 95000, 'max_guests': 20, 'difficulty': 'easy', 'category': 'safari', 'description': 'Experience the world-famous Masai Mara with game drives, cultural visits, and stunning sunsets. Witness the Big Five and the Great Migration.', 'included_services': 'Park entry fees\nGame drives\nFull-board accommodation\nProfessional guide\nAirport transfers', 'excluded_services': 'International flights\nVisa fees\nTravel insurance\nPersonal expenses', 'itinerary': 'Day 1: Arrival and transfer to Mara\nDay 2: Full day game drive\nDay 3: Morning game drive, afternoon village visit\nDay 4: Full day game drive\nDay 5: Departure'},
            {'title': 'Amboseli & Kilimanjaro Views', 'destination': 'Amboseli National Park', 'duration_days': 3, 'duration_nights': 2, 'price': 55000, 'max_guests': 15, 'difficulty': 'easy', 'category': 'safari', 'description': 'Witness majestic elephants against the backdrop of Mount Kilimanjaro. Perfect for photography enthusiasts.', 'included_services': 'Park fees\nAccommodation\nGame drives\nGuide services', 'excluded_services': 'Flights\nDrinks\nTips', 'itinerary': 'Day 1: Arrival and afternoon game drive\nDay 2: Full day game drive\nDay 3: Morning game drive, departure'},
            {'title': 'Diani Beach Holiday', 'destination': 'Diani Beach', 'duration_days': 7, 'duration_nights': 6, 'price': 85000, 'discount_price': 72000, 'max_guests': 25, 'difficulty': 'easy', 'category': 'beach', 'description': 'Relax on pristine beaches with crystal clear waters. Enjoy snorkeling, diving, and water sports.', 'included_services': 'Beach resort accommodation\nMeals\nSnorkeling equipment\nWater sports', 'excluded_services': 'Flights\nSpa treatments\nAlcoholic drinks', 'itinerary': 'Day 1: Arrival and beach relaxation\nDay 2: Snorkeling at marine park\nDay 3: Deep sea fishing\nDay 4: Island exploration\nDay 5: Water sports\nDay 6: Leisure day\nDay 7: Departure'},
            {'title': 'Great Rift Valley Explorer', 'destination': 'Lake Nakuru', 'duration_days': 2, 'duration_nights': 1, 'price': 35000, 'max_guests': 15, 'difficulty': 'moderate', 'category': 'wildlife', 'description': 'Explore the stunning Great Rift Valley with visits to Lake Nakuru, known for its flamingos and rhinos.', 'included_services': 'Park fees\nAccommodation\nTransport\nGuide', 'excluded_services': 'Meals not specified\nPersonal items', 'itinerary': 'Day 1: Drive to Nakuru, afternoon game drive\nDay 2: Morning game drive, return'},
            {'title': 'Tsavo Wilderness Safari', 'destination': 'Tsavo National Park', 'duration_days': 4, 'duration_nights': 3, 'price': 75000, 'max_guests': 15, 'difficulty': 'moderate', 'category': 'safari', 'description': 'Discover the raw wilderness of Tsavo, home to the famous red elephants and dramatic volcanic landscapes.', 'included_services': 'Park fees\nFull board accommodation\nGame drives\nGuide', 'excluded_services': 'Flights\nDrinks\nTips', 'itinerary': 'Day 1: Arrival Tsavo East\nDay 2: Full day Tsavo East\nDay 3: Transfer to Tsavo West\nDay 4: Morning game drive, departure'},
            {'title': 'Watamu Marine Escape', 'destination': 'Watamu', 'duration_days': 5, 'duration_nights': 4, 'price': 65000, 'max_guests': 20, 'difficulty': 'easy', 'category': 'beach', 'description': 'Explore the vibrant marine life of Watamu Marine National Park with exceptional snorkeling and diving.', 'included_services': 'Resort accommodation\nMeals\nMarine park fees\nSnorkeling gear', 'excluded_services': 'Flights\nDiving certification\nAlcoholic drinks', 'itinerary': 'Day 1: Arrival\nDay 2: Marine park snorkeling\nDay 3: Deep sea fishing\nDay 4: Beach relaxation\nDay 5: Departure'},
            {'title': 'Kenya Safari Highlights', 'destination': 'Masai Mara', 'duration_days': 10, 'duration_nights': 9, 'price': 250000, 'discount_price': 199000, 'max_guests': 12, 'difficulty': 'moderate', 'category': 'safari', 'description': 'The ultimate Kenyan safari experience covering Masai Mara, Amboseli, Lake Nakuru, and Tsavo.', 'included_services': 'All park fees\nFull board accommodation\nDomestic flights\nProfessional guide\nAll transfers\nGame drives', 'excluded_services': 'International flights\nVisa\nTravel insurance\nTips\nDrinks', 'itinerary': 'Day 1: Arrival Nairobi\nDay 2-3: Masai Mara\nDay 4-5: Lake Nakuru\nDay 6-7: Amboseli\nDay 8-9: Tsavo\nDay 10: Departure'},
        ]
        for i, t in enumerate(tour_data):
            dest = next((d for d in dests if d.name == t['destination']), None)
            tour = TourPackage.objects.create(
                destination=dest,
                title=t['title'],
                duration_days=t['duration_days'],
                duration_nights=t['duration_nights'],
                price=t['price'],
                discount_price=t.get('discount_price'),
                max_guests=t['max_guests'],
                available_seats=t['max_guests'],
                difficulty=t['difficulty'],
                category=t['category'],
                description=t['description'],
                included_services=t['included_services'],
                excluded_services=t['excluded_services'],
                itinerary=t['itinerary'],
                hotel=random.choice(hotels) if hotels else None,
                vehicle=random.choice(vehicles) if vehicles else None,
                guide=random.choice(guides) if guides else None,
                meeting_point='Nairobi, Kenya',
                is_featured=True,
                status='published',
            )
            main_img = self.copy_img(f'tour_{i+1}_main.jpg', f'tours/{tour.slug}_main.jpg')
            if os.path.exists(os.path.join(settings.MEDIA_ROOT, main_img)):
                TourImage.objects.create(tour=tour, image=main_img, is_main=True)
            # Add extra images
            for j in range(2, 4):
                extra = self.copy_img(f'tour_{i+1}_main.jpg', f'tours/{tour.slug}_extra_{j}.jpg')
                if os.path.exists(os.path.join(settings.MEDIA_ROOT, extra)):
                    TourImage.objects.create(tour=tour, image=extra)
        self.stdout.write('  Tours created')

    def create_testimonials(self):
        if Testimonial.objects.exists():
            return
        data = [
            {'name': 'Sarah Johnson', 'designation': 'Travel Blogger', 'content': 'Vacay Adventure made our Kenyan vacation absolutely unforgettable. The guides were knowledgeable, the accommodations were superb, and every detail was perfectly arranged.', 'rating': 5},
            {'name': 'Michael Chen', 'designation': 'Photographer', 'content': 'As a wildlife photographer, I\'ve been on many safaris. Vacay Adventure exceeded my expectations. They knew exactly where to go for the best shots.', 'rating': 5},
            {'name': 'Emma Williams', 'designation': 'Adventure Traveler', 'content': 'The Diani Beach package was incredible! Crystal clear waters, amazing snorkeling, and the resort was world-class. Can\'t wait to book my next trip.', 'rating': 5},
            {'name': 'James Ochieng', 'designation': 'Corporate Executive', 'content': 'Professional service from start to finish. The Great Rift Valley tour was well-organized and the guide was exceptionally knowledgeable.', 'rating': 4},
            {'name': 'Lisa Anderson', 'designation': 'Teacher', 'content': 'Our family trip to Masai Mara was magical. The kids loved every moment. Vacay Adventure made everything easy and stress-free.', 'rating': 5},
            {'name': 'David Kimani', 'designation': 'Entrepreneur', 'content': 'I\'ve traveled with many tour companies, but Vacay Adventure stands out for their attention to detail and genuine care for their customers.', 'rating': 5},
            {'name': 'Rachel Mwangi', 'designation': 'Doctor', 'content': 'The Kenya Safari Highlights tour was the trip of a lifetime. Every park offered something unique and the accommodations were excellent.', 'rating': 5},
            {'name': 'Tom Holland', 'designation': 'Engineer', 'content': 'Great value for money. The tour was well-planned and executed. Would definitely recommend Vacay Adventure to anyone visiting Kenya.', 'rating': 4},
            {'name': 'Grace Ouma', 'designation': 'Lawyer', 'content': 'The cultural tour was eye-opening. I learned so much about Kenyan traditions and history. The guide was fantastic.', 'rating': 5},
            {'name': 'Hassan Ali', 'designation': 'Business Owner', 'content': 'From booking to departure, everything was seamless. The team at Vacay Adventure really knows how to create a memorable experience.', 'rating': 4},
            {'name': 'Nancy Wairimu', 'designation': 'Nurse', 'content': 'Our honeymoon in Watamu was perfect. The resort was beautiful, the marine park was breathtaking, and the service was impeccable.', 'rating': 5},
            {'name': 'Kevin Brown', 'designation': 'Writer', 'content': 'I\'ve been to over 30 countries, but Kenya with Vacay Adventure was my best travel experience. The wildlife viewing was out of this world.', 'rating': 5},
            {'name': 'Catherine Nyambura', 'designation': 'Consultant', 'content': 'The Tsavo Wilderness Safari was an adventure like no other. Seeing the red elephants was a dream come true.', 'rating': 5},
            {'name': 'Brian Kipchumba', 'designation': 'IT Professional', 'content': 'Excellent organization and communication throughout. The vehicle was comfortable and the guide was very professional.', 'rating': 4},
            {'name': 'Margaret Waithera', 'designation': 'Accountant', 'content': 'Vacay Adventure made our group trip effortless. They handled all the logistics while we focused on enjoying the experience.', 'rating': 5},
            {'name': 'Steven Otieno', 'designation': 'Marketing Manager', 'content': 'The Amboseli tour was incredible. Watching elephants with Kilimanjaro in the background is an image I\'ll never forget.', 'rating': 5},
            {'name': 'Diana Kemunto', 'designation': 'Student', 'content': 'As a solo traveler, I felt safe and well-cared for throughout the trip. The guides were friendly and knowledgeable.', 'rating': 4},
            {'name': 'Patrick Muthomi', 'designation': 'Architect', 'content': 'The attention to detail in our itinerary was impressive. Every activity was timed perfectly and the recommendations were spot on.', 'rating': 5},
            {'name': 'Jane Wanjeri', 'designation': 'Hotelier', 'content': 'Having worked in hospitality, I have high standards. Vacay Adventure exceeded them all. Truly a world-class experience.', 'rating': 5},
            {'name': 'Samuel Njenga', 'designation': 'Pilot', 'content': 'The Kenya Safari Highlights tour covered all the major parks without feeling rushed. Perfectly paced itinerary.', 'rating': 4},
        ]
        for i, t in enumerate(data):
            testimonial = Testimonial.objects.create(**t)
            img = self.copy_img(f'testimonial_{(i%6)+1}.jpg', f'testimonials/{slugify(t["name"])}.jpg')
            if os.path.exists(os.path.join(settings.MEDIA_ROOT, img)):
                testimonial.image = img
                testimonial.save()
        self.stdout.write('  Testimonials created')

    def create_faqs(self):
        if FAQ.objects.exists():
            return
        faqs = [
            {'question': 'How do I book a tour?', 'answer': 'You can book a tour directly through our website by selecting your preferred tour package and filling out the booking form. You will need to create an account first.', 'order': 1},
            {'question': 'What is the payment process?', 'answer': 'We accept various payment methods including M-Pesa, credit cards, and bank transfers. Currently our system simulates payments, but we are integrating real payment gateways.', 'order': 2},
            {'question': 'Can I cancel my booking?', 'answer': 'Yes, you can cancel your booking from your dashboard. Approved bookings can be cancelled and you will receive a full refund.', 'order': 3},
            {'question': 'What should I pack for a safari?', 'answer': 'We recommend comfortable clothing in neutral colors, a hat, sunscreen, insect repellent, binoculars, a camera, and comfortable walking shoes. Detailed packing guides are available on our blog.', 'order': 4},
            {'question': 'Are meals included in the tour price?', 'answer': 'Most of our tours include full-board accommodation. Check the included services section on each tour page for details.', 'order': 5},
            {'question': 'Is travel insurance included?', 'answer': 'Travel insurance is not included in our tour prices. We strongly recommend purchasing comprehensive travel insurance for your trip.', 'order': 6},
            {'question': 'What is the maximum group size?', 'answer': 'Group sizes vary by tour package, typically ranging from 12 to 25 guests. Check the specific tour page for details.', 'order': 7},
            {'question': 'Can I customize my tour?', 'answer': 'Yes, we offer tailored experiences. Contact us with your preferences and we will create a custom itinerary for you.', 'order': 8},
            {'question': 'What languages do your guides speak?', 'answer': 'Our guides are fluent in English and Swahili. Some guides also speak French, German, and other languages upon request.', 'order': 9},
            {'question': 'Is it safe to travel to Kenya?', 'answer': 'Yes, Kenya is a safe destination for tourists. Our team ensures all safety measures are in place and we monitor travel advisories regularly.', 'order': 10},
        ]
        for f in faqs:
            FAQ.objects.create(**f)
        self.stdout.write('  FAQs created')

    def create_blog_categories(self):
        if BlogCategory.objects.exists():
            return
        categories = ['Travel Tips', 'Destination Guides', 'Wildlife', 'Culture', 'Adventure', 'Beach Holidays']
        for c in categories:
            BlogCategory.objects.create(name=c)
        self.stdout.write('  Blog categories created')

    def create_blog_posts(self):
        if BlogPost.objects.exists():
            return
        admin = User.objects.filter(is_superuser=True).first()
        if not admin:
            admin = User.objects.create_superuser('admin', 'admin@safaritours.com', 'admin123')
        categories = list(BlogCategory.objects.all())

        posts = [
            {'title': 'Top 10 Safari Destinations in Kenya', 'content': 'Kenya is home to some of the most incredible safari destinations in the world. From the vast plains of the Masai Mara to the elephant-filled Amboseli, each park offers a unique experience.\n\nThe Masai Mara National Reserve is undoubtedly the crown jewel of Kenyan safaris. Famous for the Great Migration, this reserve offers unparalleled wildlife viewing opportunities.\n\nAmboseli National Park, with its stunning views of Mount Kilimanjaro, is famous for its large elephant herds and provides some of the best photography opportunities in Africa.\n\nLake Nakuru National Park is a bird lover\'s paradise, especially famous for its flamingo populations. The park also hosts both black and white rhinos.\n\nTsavo National Park, one of the largest in the world, offers a more remote and wild safari experience with its famous red elephants.', 'category': 'Destination Guides', 'excerpt': 'Discover the most incredible safari destinations that Kenya has to offer.'},
            {'title': 'Essential Safari Packing Guide', 'content': 'Packing for a safari can be challenging, especially if it\'s your first time. Here\'s a comprehensive guide to ensure you have everything you need.\n\nClothing: Pack lightweight, breathable clothing in neutral colors (khaki, beige, olive). Avoid bright colors that can scare wildlife. Include a warm jacket for early morning game drives.\n\nFootwear: Comfortable walking shoes are essential. Also pack sandals for relaxing at the lodge.\n\nAccessories: Don\'t forget your hat, sunglasses, sunscreen, and insect repellent. A good pair of binoculars is essential for wildlife viewing.\n\nElectronics: Bring a camera with extra memory cards and batteries. A power bank is also useful.\n\nHealth: Pack any personal medications, a basic first-aid kit, and hand sanitizer.', 'category': 'Travel Tips', 'excerpt': 'Everything you need to pack for your African safari adventure.'},
            {'title': 'Best Time to Visit Kenya', 'content': 'Kenya is a year-round destination, but the best time to visit depends on what you want to see and do.\n\nFor wildlife viewing, the dry season (June to October) is ideal. Animals gather around water sources, making them easier to spot. This is also when the Great Migration occurs in the Masai Mara.\n\nThe wet season (November to May) offers lush green landscapes and fewer tourists. The short rains (November to December) and long rains (March to May) bring the bush to life.\n\nFor beach holidays on the coast, December to March offers the best weather with sunny days and calm seas.\n\nBird watching is excellent during the wet season when migratory birds are present.', 'category': 'Travel Tips', 'excerpt': 'Learn about the best seasons to visit Kenya for wildlife, beaches, and culture.'},
            {'title': 'Cultural Experiences in Kenya', 'content': 'Kenya is rich in cultural diversity with over 40 ethnic groups. Experiencing local cultures is an essential part of any visit.\n\nThe Maasai people are perhaps Kenya\'s most famous community, known for their vibrant clothing, jumping dances, and traditional way of life. Many tours offer visits to Maasai villages.\n\nIn coastal areas, Swahili culture reflects a blend of African, Arab, and Indian influences. Explore the historic streets of Mombasa\'s Old Town and sample delicious Swahili cuisine.\n\nThe Kikuyu, Luhya, Luo, and Kalenjin communities each have unique traditions, music, and ceremonies worth exploring.', 'category': 'Culture', 'excerpt': 'Immerse yourself in Kenya\'s rich cultural diversity.'},
            {'title': 'Adventure Activities in Kenya', 'content': 'Kenya is not just about safaris. The country offers a wide range of adventure activities for thrill-seekers.\n\nHot air balloon safaris over the Masai Mara offer a breathtaking perspective of the landscape and wildlife.\n\nWhite-water rafting on the Tana River provides an exhilarating experience through stunning gorges.\n\nDeep-sea fishing off the coast of Watamu and Diani offers the chance to catch marlin, sailfish, and tuna.\n\nHiking and mountain climbing opportunities include Mount Kenya, Mount Longonot, and the Aberdare Range.\n\nScuba diving and snorkeling in the marine parks reveal vibrant coral reefs and diverse marine life.', 'category': 'Adventure', 'excerpt': 'From balloon safaris to deep-sea fishing, adventure awaits.'},
            {'title': 'Kenya\'s Best Beach Destinations', 'content': 'Kenya\'s Indian Ocean coastline boasts some of the most beautiful beaches in Africa.\n\nDiani Beach is consistently rated as one of Africa\'s best beaches, with white sand, clear waters, and excellent resorts.\n\nWatamu offers a more laid-back atmosphere with its marine national park, perfect for snorkeling and diving.\n\nMalindi combines beautiful beaches with historical sites, including the Vasco da Gama pillar.\n\nLamu Island offers a unique cultural experience with its traditional Swahili architecture and dhow sailing.\n\nMombasa\'s north and south coast beaches provide easy access to the city\'s amenities and historical attractions.', 'category': 'Beach Holidays', 'excerpt': 'Paradise awaits on Kenya\'s stunning coastline.'},
            {'title': 'Wildlife Photography Tips for Safari', 'content': 'Capturing stunning wildlife photos requires patience, preparation, and the right techniques.\n\nEquipment: A camera with a good zoom lens (200-400mm) is ideal. Bring extra memory cards and batteries as opportunities can come unexpectedly.\n\nTiming: Early morning and late afternoon provide the best light for photography. Animals are also more active during these cooler hours.\n\nComposition: Use the rule of thirds, focus on the eyes, and include environmental context to tell a story.\n\nBehavior: Learn about animal behavior to anticipate action. Patience is key - sometimes waiting quietly yields the best shots.', 'category': 'Wildlife', 'excerpt': 'Expert tips for capturing incredible wildlife photographs.'},
            {'title': 'Sustainable Tourism in Kenya', 'content': 'Responsible travel is essential to preserve Kenya\'s natural heritage for future generations.\n\nChoose eco-friendly lodges and camps that prioritize sustainability and community involvement.\n\nRespect wildlife by maintaining a safe distance and never feeding animals.\n\nSupport local communities by buying authentic handicrafts and hiring local guides.\n\nReduce plastic waste by carrying a reusable water bottle and avoiding single-use plastics.\n\nConserve water and energy, especially in areas where these resources are scarce.', 'category': 'Travel Tips', 'excerpt': 'How to travel responsibly and preserve Kenya\'s natural heritage.'},
            {'title': 'Family Safari Guide', 'content': 'A family safari in Kenya can be an unforgettable experience for all ages with proper planning.\n\nChoose family-friendly lodges that offer activities for children and interconnecting rooms.\n\nPlan shorter game drives (2-3 hours) to keep children engaged and comfortable.\n\nMany lodges offer educational programs where children can learn about wildlife and conservation.\n\nConsider private safaris with a dedicated vehicle and guide for flexibility with children\'s schedules.\n\nPack entertainment for downtime - books, games, and tablets can be useful during rest periods.', 'category': 'Travel Tips', 'excerpt': 'Everything you need to know for an amazing family safari.'},
            {'title': 'Cuisine of Kenya', 'content': 'Kenyan cuisine is diverse and flavorful, reflecting the country\'s cultural richness.\n\nNyama Choma (roasted meat) is Kenya\'s national dish, often enjoyed with ugali (maize porridge) and kachumbari (tomato and onion salad).\n\nCoastal cuisine features coconut, seafood, and aromatic spices in dishes like biryani and pilau.\n\nStreet food includes samosas, mandazi (fried dough), and mutura (sausage).\n\nTea is the national drink, with Kenya being one of the world\'s largest tea producers.\n\nDon\'t miss trying fresh tropical fruits like mangoes, passion fruit, and avocados.', 'category': 'Culture', 'excerpt': 'Discover the diverse and delicious flavors of Kenya.'},
            {'title': 'Conservation Efforts in Kenya', 'content': 'Kenya is a global leader in wildlife conservation with numerous successful initiatives.\n\nThe Kenya Wildlife Service manages national parks and protects endangered species.\n\nCommunity conservancies like those in Maasai Mara involve local communities in conservation and benefit-sharing.\n\nAnti-poaching efforts have helped increase populations of elephants, rhinos, and other endangered species.\n\nMarine conservation protects coral reefs and marine ecosystems along the coast.\n\nTree planting initiatives combat deforestation and climate change.', 'category': 'Wildlife', 'excerpt': 'Learn about Kenya\'s pioneering conservation efforts.'},
            {'title': 'Luxury Safari Experiences', 'content': 'Kenya offers some of the world\'s most luxurious safari experiences.\n\nPrivate conservancies provide exclusive wildlife viewing away from crowds, with some of the finest lodges in Africa.\n\nHelicopter transfers offer spectacular aerial views and access to remote areas.\n\nPrivate dining under the stars, sundowners on the savannah, and spa treatments in the bush add to the luxury experience.\n\nPersonal butlers, private guides, and customized itineraries ensure every detail is perfect.\n\nSome luxury camps offer hot air balloon safaris followed by champagne breakfast in the bush.', 'category': 'Luxury', 'excerpt': 'Indulge in the ultimate luxury safari experience.'},
            {'title': 'Bird Watching in Kenya', 'content': 'Kenya is a paradise for bird watchers with over 1,100 recorded species.\n\nThe Great Rift Valley lakes are prime bird watching locations. Lake Nakuru is famous for its flamingos, while Lake Naivasha hosts numerous water birds.\n\nKakamega Forest is home to many forest species including the rare great blue turaco.\n\nThe coastal forests and marine parks attract seabirds and migratory species.\n\nEarly morning walks with expert guides offer the best bird viewing opportunities.', 'category': 'Wildlife', 'excerpt': 'Discover Kenya\'s incredible bird diversity.'},
            {'title': 'Health and Safety for Safari', 'content': 'Staying healthy and safe on safari requires some preparation.\n\nConsult your doctor about recommended vaccinations and malaria prophylaxis at least 4-6 weeks before travel.\n\nDrink only bottled or purified water. Avoid ice in drinks at unknown establishments.\n\nUse insect repellent containing DEET, especially during dawn and dusk when mosquitoes are active.\n\nFollow your guide\'s instructions during game drives. Never exit the vehicle unless told it is safe.\n\nKeep valuables in the lodge safe and be aware of your surroundings.', 'category': 'Travel Tips', 'excerpt': 'Essential health and safety tips for your safari.'},
            {'title': 'Photography Safari: Capturing Kenya', 'content': 'A photography-focused safari requires specialized planning to get the best shots.\n\nChoose lodges and camps located in areas with high wildlife density to maximize photography opportunities.\n\nPrivate vehicles allow more flexibility in positioning for photographs and spending time at sightings.\n\nProfessional photography guides can help with techniques and know the best locations and times.\n\nPost-processing is part of wildlife photography - bring a laptop with editing software for storage and processing.', 'category': 'Adventure', 'excerpt': 'Plan the ultimate photography safari in Kenya.'},
            {'title': 'Honeymoon in Kenya', 'content': 'Kenya is a romantic destination perfect for honeymooners seeking adventure and luxury.\n\nPrivate safari experiences offer intimate wildlife viewing and secluded accommodations.\n\nBeach resorts on Diani and Watamu provide luxurious relaxation after a safari.\n\nMany lodges offer honeymoon packages with special amenities like private dinners and spa treatments.\n\nSunset sundowners on the savannah and moonlit beach walks create unforgettable memories.', 'category': 'Beach Holidays', 'excerpt': 'Plan the perfect honeymoon combining safari and beach.'},
            {'title': 'Volunteering and Community Tourism', 'content': 'Community-based tourism allows travelers to give back while experiencing authentic Kenyan culture.\n\nVolunteer opportunities include teaching, conservation work, and community development projects.\n\nHomestays provide immersive cultural experiences with local families.\n\nCommunity-run camps and lodges directly benefit local economies.\n\nVisiting schools, health centers, and community projects offers meaningful connections.', 'category': 'Culture', 'excerpt': 'Make a positive impact while experiencing Kenya.'},
            {'title': 'Marine Life of the Kenyan Coast', 'content': 'Kenya\'s marine environment is rich with biodiversity waiting to be explored.\n\nThe coral reefs of Watamu and Malindi are part of a UNESCO Biosphere Reserve.\n\nSea turtles nest on Kenyan beaches, with conservation programs protecting nesting sites.\n\nDolphins are frequently spotted off the coast, with some areas offering dolphin-watching tours.\n\nHumpback whales pass through Kenyan waters during their migration season.\n\nThe marine parks protect over 150 species of reef fish and numerous coral species.', 'category': 'Wildlife', 'excerpt': 'Explore the rich marine biodiversity of Kenya\'s coast.'},
            {'title': 'Camping Safari Experience', 'content': 'For adventurous travelers, a camping safari offers a more immersive wilderness experience.\n\nMobile camping safaris move with the wildlife, offering flexibility in itinerary.\n\nMany camps provide comfortable tents with beds, linen, and ensuite bathrooms.\n\nFalling asleep to the sounds of the African bush is an unforgettable experience.\n\nCamping safaris are generally more affordable than lodge-based safaris.', 'category': 'Adventure', 'excerpt': 'Experience the wilderness up close with a camping safari.'},
            {'title': 'Kenya\'s National Parks: A Complete Guide', 'content': 'Kenya has over 50 national parks and reserves, each offering unique experiences.\n\nMasai Mara National Reserve is the most famous, known for the Great Migration and Big Five.\n\nAmboseli National Park offers classic savannah landscapes with Kilimanjaro views.\n\nTsavo National Park, split into East and West, is one of the largest in the world.\n\nAberdare National Park features mountainous terrain, waterfalls, and unique wildlife.\n\nMount Kenya National Park, a UNESCO site, offers climbing and hiking opportunities.\n\nNairobi National Park is unique for being a wildlife park within a major city.', 'category': 'Destination Guides', 'excerpt': 'A comprehensive guide to Kenya\'s incredible national parks.'},
        ]
        for i, p in enumerate(posts):
            cat = next((c for c in categories if c.name == p['category']), None)
            post = BlogPost.objects.create(
                title=p['title'],
                category=cat,
                author=admin,
                content=p['content'],
                excerpt=p['excerpt'],
                is_featured=(i < 3),
                status='published',
                created_at=timezone.now() - timedelta(days=i*3),
            )
            img = self.copy_img(f'blog_{(i%3)+1}.jpg', f'blog/{post.slug}.jpg')
            if os.path.exists(os.path.join(settings.MEDIA_ROOT, img)):
                post.featured_image = img
                post.save()
        self.stdout.write('  Blog posts created')

    def create_gallery(self):
        if Gallery.objects.exists():
            return
        categories = ['safari', 'beach', 'cultural', 'adventure']
        captions = [
            'Elephant herd in Amboseli', 'Sunset over Masai Mara', 'Diani Beach aerial view',
            'Maasai warrior jumping', 'Lion resting on savannah', 'Coral reef snorkeling',
            'Traditional Swahili door', 'Giraffe against sunset', 'Hot air balloon safari',
            'Zebra migration crossing', 'Crystal clear waters of Watamu', 'Mountain Kilimanjaro view',
            'Leopard in a tree', 'Dhow sailing at sunset', 'Lake Nakuru flamingos',
            'Mountain trekking adventure', 'Beach resort luxury', 'Cultural dance performance',
            'Rhino in natural habitat', 'Cheetah hunting',
        ]
        for i in range(20):
            cat = categories[i % len(categories)]
            caption = captions[i] if i < len(captions) else f'Gallery image {i+1}'
            gallery = Gallery.objects.create(
                caption=caption,
                category=cat,
            )
            self.copy_img(f'gallery_{(i%6)+1}.jpg', f'gallery/gallery_{i+1}.jpg')
            # Will be set below
            if os.path.exists(os.path.join(settings.MEDIA_ROOT, f'gallery/gallery_{i+1}.jpg')):
                gallery.image = f'gallery/gallery_{i+1}.jpg'
                gallery.save()
        self.stdout.write('  Gallery images created')

    def create_users(self):
        if User.objects.filter(is_superuser=False).count() > 1:
            return
        # Create admin if not exists
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@safaritours.com', 'admin123')

        customers = [
            {'username': 'john_doe', 'email': 'john@example.com', 'first_name': 'John', 'last_name': 'Doe'},
            {'username': 'jane_smith', 'email': 'jane@example.com', 'first_name': 'Jane', 'last_name': 'Smith'},
            {'username': 'peter_kamau', 'email': 'peter@example.com', 'first_name': 'Peter', 'last_name': 'Kamau'},
            {'username': 'mary_jane', 'email': 'mary@example.com', 'first_name': 'Mary', 'last_name': 'Jane'},
            {'username': 'david_gitau', 'email': 'david@example.com', 'first_name': 'David', 'last_name': 'Gitau'},
            {'username': 'sarah_akinyi', 'email': 'sarah@example.com', 'first_name': 'Sarah', 'last_name': 'Akinyi'},
            {'username': 'james_mwangi', 'email': 'james@example.com', 'first_name': 'James', 'last_name': 'Mwangi'},
            {'username': 'grace_otieno', 'email': 'grace@example.com', 'first_name': 'Grace', 'last_name': 'Otieno'},
            {'username': 'kevin_main', 'email': 'kevin@example.com', 'first_name': 'Kevin', 'last_name': 'Maina'},
            {'username': 'lisa_wambui', 'email': 'lisa@example.com', 'first_name': 'Lisa', 'last_name': 'Wambui'},
        ]
        for c in customers:
            user = User.objects.create_user(**c, password='password123')
            user.profile.phone = f'+254 7{random.randint(0,9)}{random.randint(10000000, 99999999)}'
            user.profile.city = random.choice(['Nairobi', 'Mombasa', 'Kisumu', 'Nakuru'])
            user.profile.country = 'Kenya'
            user.profile.save()
        self.stdout.write('  Users created')

    def create_bookings(self):
        if Booking.objects.exists():
            return
        users = list(User.objects.filter(is_superuser=False))
        tours = list(TourPackage.objects.all())
        statuses = ['pending', 'approved', 'cancelled', 'completed']
        for i in range(20):
            user = random.choice(users)
            tour = random.choice(tours)
            guests = random.randint(1, min(4, tour.max_guests))
            adults = max(1, guests - random.randint(0, 1))
            children = guests - adults
            price = (tour.discount_price if tour.discount_price else tour.price) * guests
            status = random.choice(statuses)
            travel_date = date.today() + timedelta(days=random.randint(-30, 90))
            booking = Booking.objects.create(
                user=user,
                tour=tour,
                travel_date=travel_date,
                adults=adults,
                children=children,
                total_price=price,
                status=status,
                special_requests='Please arrange airport pickup.' if random.random() > 0.5 else '',
            )
            if status != 'cancelled':
                Payment.objects.create(
                    booking=booking,
                    amount=price,
                    method='simulated',
                    reference_number=f'SIM-{timezone.now().strftime("%Y%m%d%H%M%S")}-{random.randint(10000, 99999)}',
                    status='completed' if status != 'pending' else 'pending',
                    paid_date=timezone.now() - timedelta(hours=random.randint(1, 48)) if status != 'pending' else None,
                )
            if status == 'completed' and random.random() > 0.5:
                if not Review.objects.filter(user=user, tour=tour).exists():
                    Review.objects.create(
                        user=user,
                        tour=tour,
                        booking=booking,
                        rating=random.randint(3, 5),
                        comment='Amazing experience! Would definitely recommend.',
                        is_active=True,
                    )
        self.stdout.write('  Bookings created')
