import random
from faker import Faker


import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'builder_hub.settings')
django.setup()
from auth.models import User
# Replace 'your_app' with the actual app name where UserAddress lives
from user.models import UserAddress 

fake = Faker()


def seed_all_gujarat_addresses():
    users = User.objects.all()
    if not users.exists():
        print("No users found! Please seed users first.")
        return

    print(f"Generating random Gujarat addresses for {users.count()} users...")
    addresses_to_create = []

    # Comprehensive Gujarat Regional Dataset
    gujarat_locations = [
        {
            "city": "Ahmedabad", "pincode": "380015",
            "areas": ["Satellite", "Vastrapur", "Bodakdev", "Prahladnagar", "Navrangpura"],
            "landmarks": ["Near Alpha One Mall", "Opposite Vastrapur Lake", "Behind Iscon Temple"]
        },
        {
            "city": "Junagadh", "pincode": "362001",
            "areas": ["Zanzarda Road", "Kalwa Chowk", "Joshipura", "Motibaug"],
            "landmarks": ["Near Bhavnath Taleti", "Opposite Mahabat Maqbara", "Near Girnar Darwaja"]
        },
        {
            "city": "Surat", "pincode": "395007",
            "areas": ["Vesu", "Adajan", "Dumas Road", "Varachha", "Katargam"],
            "landmarks": ["Near VR Mall", "Opposite Aquamagicaa", "Near Tapi River Front"]
        },
        {
            "city": "Vadodara", "pincode": "390007",
            "areas": ["Alkapuri", "Akota", "Gotri", "Fatehgunj", "Waghodia Road"],
            "landmarks": ["Near Sayaji Baug", "Opposite Inorbit Mall", "Behind Laxmi Vilas Palace"]
        },
        {
            "city": "Rajkot", "pincode": "360001",
            "areas": ["Kalawad Road", "Yagnik Road", "Raiya Road", "Mavdi"],
            "landmarks": ["Near Race Course Ground", "Opposite Crystal Mall", "Near Kaba Gandhi No Delo"]
        },
        {
            "city": "Gandhinagar", "pincode": "382010",
            "areas": ["Sector 11", "Sector 21", "Sargasan", "Kudasan"],
            "landmarks": ["Near Akshardham Temple", "Opposite Mahatma Mandir", "Near Infocity"]
        },
        {
            "city": "Bhavnagar", "pincode": "364001",
            "areas": ["Kaliabid", "Waghawadi Road", "Takhteshwar", "Chitra"],
            "landmarks": ["Near Takhteshwar Temple", "Opposite Victoria Park", "Near Nilambag Palace"]
        },
        {
            "city": "Jamnagar", "pincode": "361001",
            "areas": ["Digvijay Plot", "Park Colony", "Khodiyar Colony", "Samarpan"],
            "landmarks": ["Near Lakhota Lake", "Opposite Bala Hanuman Temple", "Near Khijadiya Sanctuary"]
        },
        {
            "city": "Anand", "pincode": "388001",
            "areas": ["Vallabh Vidyanagar", "Amul Dairy Road", "Karamsad"],
            "landmarks": ["Near Amul Dairy Plant", "Opposite Shastri Maidan", "Near Bhaikaka Statue"]
        },
        {
            "city": "Bhuj", "pincode": "370001",
            "areas": ["Mirzapar Road", "Madhapar", "Hospital Road"],
            "landmarks": ["Near Aina Mahal", "Opposite Prag Mahal", "Near Hamirsar Lake"]
        }
    ]

    street_names = ["MG Road", "Station Road", "High Street", "Bypass Road", "Main Bazaar", "Link Road"]
    society_suffixes = ["Society", "Appartment", "Residency", "Tenement", "Enclave"]

    for user in users:
        # Determine unique address allocation count (1 to 3) per profile loop
        user_home_city = random.choice(gujarat_locations)
        num_addresses = random.randint(1, 3)
        
        for i in range(num_addresses):
            # Select a random town profile from our database matrix
            loc = user_home_city
            area = random.choice(loc["areas"])
            
            # Construct a realistic context-based street name string layout
            house_num = f"{random.randint(1, 250)}, Flat-{random.randint(101, 404)}"
            address_line_1 = f"{house_num}, {fake.word().capitalize()} {random.choice(society_suffixes)}"
            address_line_2 = f"{random.choice(street_names)}, {area}"

            # Structural configuration rule ensuring only the baseline row handles default priority flags
            is_default = (i == 0)

            address = UserAddress(
                user=user,
                address_type=random.choice(["home", "work", "other"]),
                full_name=f"{user.first_name} {user.last_name}".strip() or fake.name(),
                phone_number=str(random.randint(6000000000, 9999999999)),
                address_line_1=address_line_1,
                address_line_2=address_line_2,
                landmark=random.choice(loc["landmarks"]),
                pincode=loc["pincode"],
                area=area,
                city=loc["city"],
                is_default=is_default,
                # Safe boundary limits pinning general latitude & longitude positioning fields within Gujarat
                latitude=round(random.uniform(20.1, 24.5), 6),
                longitude=round(random.uniform(68.5, 74.3), 6)
            )
            addresses_to_create.append(address)

    # Fast operational array dump executed directly into the SQL workspace database
    UserAddress.objects.bulk_create(addresses_to_create)
    print(f"Successfully generated {len(addresses_to_create)} user address points distributed across Gujarat!")

if __name__ == "__main__":
    seed_all_gujarat_addresses()