import os
import sys

sys.path.insert(0, r'd:\Projects\Meal Management\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mealmate.settings')

import django
django.setup()

from users.models import User, Address
from restaurants.models import Category, Restaurant, FoodItem, Review

print("1. Creating Users...")
admin_user, _ = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@mealmate.com',
        'role': 'Admin',
        'is_staff': True,
        'is_superuser': True,
        'first_name': 'System',
        'last_name': 'Admin'
    }
)
admin_user.set_password('admin123')
admin_user.role = 'Admin'
admin_user.is_staff = True
admin_user.is_superuser = True
admin_user.save()

customer_user, _ = User.objects.get_or_create(
    username='customer',
    defaults={
        'email': 'customer@mealmate.com',
        'role': 'Customer',
        'first_name': 'Rahul',
        'last_name': 'Sharma',
        'phone_number': '9876543210'
    }
)
customer_user.set_password('customer123')
customer_user.role = 'Customer'
customer_user.save()

Address.objects.get_or_create(
    user=customer_user,
    defaults={
        'street': '123 MG Road, Indiranagar',
        'city': 'Bengaluru',
        'state': 'Karnataka',
        'zip_code': '560038',
        'is_default': True
    }
)
print("Users created: admin / admin123, customer / customer123")

print("2. Creating Categories...")
cat_veg, _ = Category.objects.get_or_create(name='Veg')
cat_nonveg, _ = Category.objects.get_or_create(name='Non-Veg')
cat_colddrinks, _ = Category.objects.get_or_create(name='Cold Drinks')
cat_icecreams, _ = Category.objects.get_or_create(name='IceCreams')
print("Categories created: Veg, Non-Veg, Cold Drinks, IceCreams")

print("3. Creating Restaurants...")
restaurants_data = [
    {
        'name': 'Jamavar',
        'location': 'The Leela Palace, HAL Old Airport Rd, Bengaluru',
        'veg_nonveg': 'Both',
        'image': 'https://www.theleela.com/prod/content/assets/aio-banner/dekstop/Jamavar_1920x950.webp',
        'description': 'Award-winning royal Indian fine dining at The Leela Palace Bengaluru.'
    },
    {
        'name': 'Karavalli',
        'location': 'Taj Gateway, Residency Road, Bengaluru',
        'veg_nonveg': 'Both',
        'image': 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=800&q=80',
        'description': 'Iconic coastal dining with fresh seafood and traditional southern recipes.'
    },
    {
        'name': 'The Bangalore Cafe',
        'location': 'Shanti Nagar, Bengaluru',
        'veg_nonveg': 'Veg',
        'image': 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=800&q=80',
        'description': 'A vibrant vegetarian cafe serving traditional delicacies and modern snacks.'
    },
    {
        'name': 'Gufha Restaurant',
        'location': 'The President Hotel, Jayanagar, Bengaluru',
        'veg_nonveg': 'Both',
        'image': 'https://images.unsplash.com/photo-1550966871-3ed3cdb5ed0c?auto=format&fit=crop&w=800&q=80',
        'description': 'Unique cave-themed fine-dining offering rich Mughlai and North Indian cuisine.'
    },
    {
        'name': 'The Old House',
        'location': 'Vontikoppal, Mysuru & Bengaluru',
        'veg_nonveg': 'Veg',
        'image': 'https://images.unsplash.com/photo-1559339352-11d035aa65de?auto=format&fit=crop&w=800&q=80',
        'description': 'Serene courtyard cafe with delicious artisan desserts and drinks.'
    },
    {
        'name': 'Niyaaz Restaurant',
        'location': 'Club Road, Belagavi',
        'veg_nonveg': 'Both',
        'image': 'https://images.unsplash.com/photo-1590846406792-0adc7f938f1d?auto=format&fit=crop&w=800&q=80',
        'description': 'Legendary house of authentic Belagavi biryani and Mughlai specialties.'
    }
]

rest_objs = {}
for r_data in restaurants_data:
    r, _ = Restaurant.objects.get_or_create(
        name=r_data['name'],
        defaults={
            'owner': admin_user,
            'location': r_data['location'],
            'veg_nonveg': r_data['veg_nonveg'],
            'image': r_data['image'],
            'description': r_data['description'],
            'status': True
        }
    )
    rest_objs[r.name] = r
print(f"Created {len(rest_objs)} restaurants.")

print("4. Creating Food Items...")
foods_data = [
    # Veg Dishes
    {
        'restaurant': rest_objs['The Bangalore Cafe'],
        'category': cat_veg,
        'name': 'Paneer Butter Masala',
        'description': 'Cottage cheese simmered in a silky tomato butter gravy with aromatic spices.',
        'price': 240.00,
        'veg_nonveg': 'Veg',
        'cuisine_type': 'North Indian',
        'image': 'https://images.unsplash.com/photo-1631452180539-96aca7d48617?auto=format&fit=crop&w=800&q=80'
    },
    {
        'restaurant': rest_objs['The Bangalore Cafe'],
        'category': cat_veg,
        'name': 'Masala Dosa',
        'description': 'Crispy fermented crepe filled with spiced potato masala, served with sambar and coconut chutney.',
        'price': 90.00,
        'veg_nonveg': 'Veg',
        'cuisine_type': 'South Indian',
        'image': 'https://images.unsplash.com/photo-1668236543090-82eba5ee5976?auto=format&fit=crop&w=800&q=80'
    },
    {
        'restaurant': rest_objs['The Bangalore Cafe'],
        'category': cat_veg,
        'name': 'Chole Bhature',
        'description': 'Golden puffed bhature paired with spicy, tangy Punjabi chickpeas and pickles.',
        'price': 150.00,
        'veg_nonveg': 'Veg',
        'cuisine_type': 'Punjabi',
        'image': 'https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?auto=format&fit=crop&w=800&q=80'
    },
    {
        'restaurant': rest_objs['Jamavar'],
        'category': cat_veg,
        'name': 'Veg Biryani',
        'description': 'Fragrant basmati rice layered with fresh seasonal vegetables and saffron.',
        'price': 200.00,
        'veg_nonveg': 'Veg',
        'cuisine_type': 'Mughlai/Indian',
        'image': 'https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?auto=format&fit=crop&w=800&q=80'
    },
    {
        'restaurant': rest_objs['The Bangalore Cafe'],
        'category': cat_veg,
        'name': 'Palak Paneer',
        'description': 'Fresh soft paneer cubes cooked in a vibrant, spiced spinach purée with a touch of cream.',
        'price': 225.00,
        'veg_nonveg': 'Veg',
        'cuisine_type': 'North Indian',
        'image': 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?auto=format&fit=crop&w=800&q=80'
    },
    {
        'restaurant': rest_objs['The Bangalore Cafe'],
        'category': cat_veg,
        'name': 'Misal Pav',
        'description': 'Spicy sprout curry topped with farsan, onions, coriander, and served with butter toasted pav.',
        'price': 80.00,
        'veg_nonveg': 'Veg',
        'cuisine_type': 'Maharashtrian',
        'image': 'https://images.unsplash.com/photo-1606491956689-2ea866880c84?auto=format&fit=crop&w=800&q=80'
    },
    {
        'restaurant': rest_objs['The Bangalore Cafe'],
        'category': cat_veg,
        'name': 'Idli Vada',
        'description': 'Steamed pillow-soft idlis and crispy medu vada served with traditional lentil sambar.',
        'price': 80.00,
        'veg_nonveg': 'Veg',
        'cuisine_type': 'South Indian',
        'image': 'https://images.unsplash.com/photo-1589301760014-d929f3979dbc?auto=format&fit=crop&w=800&q=80'
    },
    {
        'restaurant': rest_objs['Jamavar'],
        'category': cat_veg,
        'name': 'Garlic Naan',
        'description': 'Freshly baked leavened clay-oven tandoor bread brushed with melted butter and roasted garlic.',
        'price': 70.00,
        'veg_nonveg': 'Veg',
        'cuisine_type': 'Indian Bread',
        'image': 'https://images.unsplash.com/photo-1565557623262-b51c2513a641?auto=format&fit=crop&w=800&q=80'
    },
    {
        'restaurant': rest_objs['The Bangalore Cafe'],
        'category': cat_veg,
        'name': 'Veg Fried Rice',
        'description': 'Wok-tossed aromatic long-grain rice with crisp garden vegetables and spring onions.',
        'price': 160.00,
        'veg_nonveg': 'Veg',
        'cuisine_type': 'Indo-Chinese',
        'image': 'https://images.unsplash.com/photo-1603133872878-684f208fb84b?auto=format&fit=crop&w=800&q=80'
    },

    # Non-Veg Dishes
    {
        'restaurant': rest_objs['Jamavar'],
        'category': cat_nonveg,
        'name': 'Butter Chicken',
        'description': 'Tender tandoori chicken cooked in an iconic smooth, spiced tomato and butter makhani sauce.',
        'price': 320.00,
        'veg_nonveg': 'Non-Veg',
        'cuisine_type': 'North Indian',
        'image': 'https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?auto=format&fit=crop&w=800&q=80'
    },
    {
        'restaurant': rest_objs['Niyaaz Restaurant'],
        'category': cat_nonveg,
        'name': 'Chicken Dum Biryani',
        'description': 'Signature slow-cooked marinated chicken layered with basmati rice, caramelized onions, and saffron.',
        'price': 280.00,
        'veg_nonveg': 'Non-Veg',
        'cuisine_type': 'Hyderabadi',
        'image': 'https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?auto=format&fit=crop&w=800&q=80'
    },
    {
        'restaurant': rest_objs['Gufha Restaurant'],
        'category': cat_nonveg,
        'name': 'Chicken Tikka',
        'description': 'Boneless chicken chunks marinated in yogurt and tandoori spices, flame-grilled on skewers.',
        'price': 260.00,
        'veg_nonveg': 'Non-Veg',
        'cuisine_type': 'Mughlai',
        'image': 'https://images.unsplash.com/photo-1599488615731-7e5c2823ff28?auto=format&fit=crop&w=800&q=80'
    },
    {
        'restaurant': rest_objs['Gufha Restaurant'],
        'category': cat_nonveg,
        'name': 'Mutton Rogan Josh',
        'description': 'Traditional tender Kashmiri lamb braised in a gravy flavored with garlic, ginger, and Kashmiri chilies.',
        'price': 380.00,
        'veg_nonveg': 'Non-Veg',
        'cuisine_type': 'Kashmiri',
        'image': 'https://images.unsplash.com/photo-1545247181-516773cae754?auto=format&fit=crop&w=800&q=80'
    },
    {
        'restaurant': rest_objs['Karavalli'],
        'category': cat_nonveg,
        'name': 'Fish Curry',
        'description': 'Fresh catch simmered in an authentic coastal red coconut gravy with kokum and curry leaves.',
        'price': 290.00,
        'veg_nonveg': 'Non-Veg',
        'cuisine_type': 'Coastal Indian',
        'image': 'https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=800&q=80'
    },
    {
        'restaurant': rest_objs['Niyaaz Restaurant'],
        'category': cat_nonveg,
        'name': 'Chicken Lollipop',
        'description': 'Crispy seasoned chicken winglets tossed in spicy Schezwan sauce with spring onion.',
        'price': 220.00,
        'veg_nonveg': 'Non-Veg',
        'cuisine_type': 'Chinese',
        'image': 'https://images.unsplash.com/photo-1527477396000-e27163b481c2?auto=format&fit=crop&w=800&q=80'
    },
    {
        'restaurant': rest_objs['The Old House'],
        'category': cat_nonveg,
        'name': 'Chicken Hakka Noodles',
        'description': 'Classic thin noodles stir-fried with shredded chicken, peppers, cabbage, and soy sauce.',
        'price': 190.00,
        'veg_nonveg': 'Non-Veg',
        'cuisine_type': 'Chinese',
        'image': 'https://images.unsplash.com/photo-1617622141675-d3005b9067c5?auto=format&fit=crop&w=800&q=80'
    },

    # Cold Drinks
    {
        'restaurant': rest_objs['The Bangalore Cafe'],
        'category': cat_colddrinks,
        'name': 'Coca-Cola',
        'description': 'Crisp, chilled carbonated soft drink served refreshingly cold.',
        'price': 40.00,
        'veg_nonveg': 'Veg',
        'cuisine_type': 'Cold Drinks',
        'image': 'https://images.unsplash.com/photo-1622483767028-3f66f32aef97?auto=format&fit=crop&w=800&q=80'
    },
    {
        'restaurant': rest_objs['The Bangalore Cafe'],
        'category': cat_colddrinks,
        'name': 'Pepsi',
        'description': 'Classic fizzy cola beverage served iced.',
        'price': 40.00,
        'veg_nonveg': 'Veg',
        'cuisine_type': 'Cold Drinks',
        'image': 'https://images.unsplash.com/photo-1553456558-aff63285bdd1?auto=format&fit=crop&w=800&q=80'
    },
    {
        'restaurant': rest_objs['The Old House'],
        'category': cat_colddrinks,
        'name': 'Sprite Zero',
        'description': 'Crisp, clear lemon-lime flavored sparkling soda with zero calories.',
        'price': 45.00,
        'veg_nonveg': 'Veg',
        'cuisine_type': 'Diet Drinks',
        'image': 'https://images.unsplash.com/photo-1625772299848-391b6a87d7b3?auto=format&fit=crop&w=800&q=80'
    },
    {
        'restaurant': rest_objs['The Old House'],
        'category': cat_colddrinks,
        'name': 'Diet Coke',
        'description': 'Light, crisp, sugar-free Coca-Cola beverage in a chilled can.',
        'price': 50.00,
        'veg_nonveg': 'Veg',
        'cuisine_type': 'Diet Drinks',
        'image': 'https://upload.wikimedia.org/wikipedia/commons/8/89/Diet_Coke_Can.jpg'
    },
    {
        'restaurant': rest_objs['The Bangalore Cafe'],
        'category': cat_colddrinks,
        'name': 'Sprite',
        'description': 'Sparkling lemon-lime refreshment with an invigorating burst of citrus flavor.',
        'price': 40.00,
        'veg_nonveg': 'Veg',
        'cuisine_type': 'Cold Drinks',
        'image': 'https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=800&q=80'
    },
    {
        'restaurant': rest_objs['The Old House'],
        'category': cat_colddrinks,
        'name': 'Coca-Cola Zero Sugar',
        'description': 'Iconic Coca-Cola taste with zero calories and zero sugar.',
        'price': 45.00,
        'veg_nonveg': 'Veg',
        'cuisine_type': 'Diet Drinks',
        'image': 'https://images.unsplash.com/photo-1554866585-cd94860890b7?auto=format&fit=crop&w=800&q=80'
    },

    # Ice Creams
    {
        'restaurant': rest_objs['The Old House'],
        'category': cat_icecreams,
        'name': "Kwality Wall's Cornetto Double Chocolate",
        'description': "Crispy waffle cone filled with creamy chocolate ice cream and topped with chocolate disc and nuts.",
        'price': 65.00,
        'veg_nonveg': 'Veg',
        'cuisine_type': 'Waffle Cone',
        'image': 'https://images.unsplash.com/photo-1549395156-e0c1fe6fc7a5?auto=format&fit=crop&w=800&q=80'
    },
    {
        'restaurant': rest_objs['The Old House'],
        'category': cat_icecreams,
        'name': 'Baskin Robbins Mississippi Mud Cone',
        'description': 'Rich dark chocolate fudge ice cream paired with chocolate cake pieces in a crunchy waffle cone.',
        'price': 120.00,
        'veg_nonveg': 'Veg',
        'cuisine_type': 'Premium Cone',
        'image': 'https://images.unsplash.com/photo-1501443762994-82bd5dace89a?auto=format&fit=crop&w=800&q=80'
    },
    {
        'restaurant': rest_objs['The Old House'],
        'category': cat_icecreams,
        'name': 'Amul Belgian Chocolate Tricone',
        'description': 'Crispy chocolate cone loaded with exotic real Belgian chocolate ice cream.',
        'price': 50.00,
        'veg_nonveg': 'Veg',
        'cuisine_type': 'Cone',
        'image': 'https://images.unsplash.com/photo-1580915411954-282cb1b0d780?auto=format&fit=crop&w=800&q=80'
    },
    {
        'restaurant': rest_objs['The Old House'],
        'category': cat_icecreams,
        'name': 'Naturals Tender Coconut Ice Cream',
        'description': 'Iconic artisanal cup prepared from real fresh tender coconut malai and creamy milk.',
        'price': 85.00,
        'veg_nonveg': 'Veg',
        'cuisine_type': 'Artisanal Cup',
        'image': 'https://images.unsplash.com/photo-1587314168485-3236d6710814?auto=format&fit=crop&w=800&q=80'
    },
    {
        'restaurant': rest_objs['The Bangalore Cafe'],
        'category': cat_icecreams,
        'name': 'Amul Real Milk Vanilla Cup',
        'description': 'Classic creamy vanilla ice cream prepared with pure wholesome milk.',
        'price': 25.00,
        'veg_nonveg': 'Veg',
        'cuisine_type': 'Classic Cup',
        'image': 'https://images.unsplash.com/photo-1570197788417-0e82375c9371?auto=format&fit=crop&w=800&q=80'
    },
    {
        'restaurant': rest_objs['The Old House'],
        'category': cat_icecreams,
        'name': 'Havmor Dark Chocolate Crunch',
        'description': 'Decadent dark chocolate ice cream loaded with chocolate crunch pearls.',
        'price': 45.00,
        'veg_nonveg': 'Veg',
        'cuisine_type': 'Chocolate Cup',
        'image': 'https://images.unsplash.com/photo-1563805042-7684c019e1cb?auto=format&fit=crop&w=800&q=80'
    },
]

created_count = 0
for f_data in foods_data:
    food, _ = FoodItem.objects.get_or_create(
        name=f_data['name'],
        restaurant=f_data['restaurant'],
        defaults={
            'category': f_data['category'],
            'description': f_data['description'],
            'price': f_data['price'],
            'veg_nonveg': f_data['veg_nonveg'],
            'cuisine_type': f_data['cuisine_type'],
            'image': f_data['image'],
            'is_available': True
        }
    )
    created_count += 1

print(f"Created {created_count} food items across all categories!")

# Add a sample review
Review.objects.get_or_create(
    user=customer_user,
    food_item=FoodItem.objects.filter(name='Butter Chicken').first(),
    defaults={'rating': 5, 'comment': 'Absolutely divine flavor! Must try.'}
)
Review.objects.get_or_create(
    user=customer_user,
    food_item=FoodItem.objects.filter(name='Paneer Butter Masala').first(),
    defaults={'rating': 5, 'comment': 'Creamy and flavorful with delicious paneer.'}
)

print("Database seeding completed successfully!")
