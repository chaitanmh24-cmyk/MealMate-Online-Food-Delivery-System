from decimal import Decimal
from django.core.management.base import BaseCommand
from restaurants.models import Cuisine, Restaurant
from menu.models import Category, FoodItem
from orders.models import Order, OrderItem, Payment
from cart.models import Cart, CartItem

class Command(BaseCommand):
    help = "Clean and seed database with 10+ restaurants and 50+ realistic food items across all cuisines and categories."

    def handle(self, *args, **options):
        self.stdout.write("--- Starting Clean Database Seeding ---")

        # Clear dependent records first to respect on_delete=models.PROTECT
        Payment.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        CartItem.objects.all().delete()
        Cart.objects.all().delete()

        # Clear existing menu and restaurant data for a clean rebuild
        FoodItem.objects.all().delete()
        Restaurant.objects.all().delete()
        Category.objects.all().delete()
        Cuisine.objects.all().delete()

        # 1. Cuisines
        cuisines_data = [
            ("South Indian", "Traditional dosas, idlis, vadas, sambar and aromatic filter coffee."),
            ("North Indian", "Rich gravies, paneer specialties, tandoori breads and dal makhani."),
            ("Mughlai", "Royal biryanis, kebabs, kormas, and fragrant spices."),
            ("Chinese", "Wok-tossed noodles, fried rice, manchurian, and schezwan delicacies."),
            ("Italian", "Wood-fired pizzas, creamy pastas, garlic breads and risottos."),
            ("Street Food", "Mumbai-style pav bhaji, vada pav, chaats, and crispy samosas."),
            ("Fast Food", "Burgers, wraps, loaded fries, and quick bites."),
            ("Desserts & Beverages", "Artisanal ice cream sundaes, chilled sodas, and thick shakes."),
        ]
        cuisines_map = {}
        for name, desc in cuisines_data:
            c = Cuisine.objects.create(name=name, description=desc)
            cuisines_map[name] = c
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(cuisines_map)} cuisines."))

        # 2. Categories
        categories_data = [
            ("Veg", "veg", "100% wholesome pure vegetarian meals and delicacies", "🥦"),
            ("Non-Veg", "non-veg", "Tender chicken, mutton, seafood, and egg specialties", "🍗"),
            ("Snacks / Street-Style Food", "street-food", "Iconic street-style snacks from premium hotel kitchens", "🥪"),
            ("Desserts", "desserts", "Artisanal ice creams, sundaes, and dessert cups", "🍦"),
            ("Beverages", "beverages", "Chilled sodas, fizzy cold drinks, and refreshments", "🥤"),
        ]
        cat_map = {}
        for name, slug, desc, icon in categories_data:
            cat = Category.objects.create(name=name, slug=slug, description=desc, icon=icon)
            cat_map[slug] = cat
        cat_map["snacks"] = cat_map["street-food"]
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(categories_data)} categories."))

        # 3. Restaurants
        restaurants_data = [
            {
                "name": "Jamavar",
                "restaurant_type": "Both",
                "address": "The Leela Palace, HAL Old Airport Rd, Kodihalli",
                "city": "Bengaluru",
                "rating": Decimal("4.8"),
                "image": "https://www.theleela.com/prod/content/assets/aio-banner/dekstop/Jamavar_1920x950.webp",
                "cuisines": ["North Indian", "Mughlai", "Desserts & Beverages"]
            },
            {
                "name": "Karavalli",
                "restaurant_type": "Both",
                "address": "The Gateway Hotel, 66 Residency Road",
                "city": "Bengaluru",
                "rating": Decimal("4.7"),
                "image": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=800&q=80",
                "cuisines": ["South Indian", "Street Food", "Desserts & Beverages"]
            },
            {
                "name": "The Bangalore Cafe",
                "restaurant_type": "Veg",
                "address": "4 Kengal Hanumanthaiah Rd, Shanti Nagar",
                "city": "Bengaluru",
                "rating": Decimal("4.5"),
                "image": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=800&q=80",
                "cuisines": ["North Indian", "Street Food", "Italian", "Desserts & Beverages"]
            },
            {
                "name": "Gufha Restaurant",
                "restaurant_type": "Both",
                "address": "The President Hotel, 79/8 Diagonal Rd, 3rd Block, Jayanagar",
                "city": "Bengaluru",
                "rating": Decimal("4.4"),
                "image": "https://images.unsplash.com/photo-1550966871-3ed3cdb5ed0c?auto=format&fit=crop&w=800&q=80",
                "cuisines": ["North Indian", "Mughlai", "Desserts & Beverages"]
            },
            {
                "name": "The Old House",
                "restaurant_type": "Veg",
                "address": "451 Vontikoppal & 100ft Rd Indiranagar",
                "city": "Bengaluru",
                "rating": Decimal("4.6"),
                "image": "https://images.unsplash.com/photo-1559339352-11d035aa65de?auto=format&fit=crop&w=800&q=80",
                "cuisines": ["Italian", "Street Food", "Desserts & Beverages"]
            },
            {
                "name": "Niyaaz Restaurant",
                "restaurant_type": "Both",
                "address": "Club Road & High Street",
                "city": "Bengaluru",
                "rating": Decimal("4.4"),
                "image": "https://images.unsplash.com/photo-1552566626-52f8b828add9?auto=format&fit=crop&w=800&q=80",
                "cuisines": ["Mughlai", "North Indian", "Desserts & Beverages"]
            },
            {
                "name": "Meghana Foods",
                "restaurant_type": "Both",
                "address": "124 1st Cross, 5th Block, Koramangala",
                "city": "Bengaluru",
                "rating": Decimal("4.6"),
                "image": "https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&w=800&q=80",
                "cuisines": ["Mughlai", "South Indian", "North Indian", "Desserts & Beverages"]
            },
            {
                "name": "Vidyarthi Bhavan",
                "restaurant_type": "Veg",
                "address": "32 Gandhi Bazaar Main Rd, Basavanagudi",
                "city": "Bengaluru",
                "rating": Decimal("4.8"),
                "image": "https://images.unsplash.com/photo-1610192244261-3f33de3f55e4?auto=format&fit=crop&w=800&q=80",
                "cuisines": ["South Indian", "Street Food", "Desserts & Beverages"]
            },
            {
                "name": "Empire Restaurant",
                "restaurant_type": "Both",
                "address": "36 Church Street, Shanthala Nagar, Ashok Nagar",
                "city": "Bengaluru",
                "rating": Decimal("4.3"),
                "image": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80",
                "cuisines": ["North Indian", "Mughlai", "Chinese", "Desserts & Beverages"]
            },
            {
                "name": "Corner House Ice Cream",
                "restaurant_type": "Veg",
                "address": "No. 4, 100ft Road, HAL 2nd Stage, Indiranagar",
                "city": "Bengaluru",
                "rating": Decimal("4.9"),
                "image": "https://images.unsplash.com/photo-1501443762994-82bd5dace89a?auto=format&fit=crop&w=800&q=80",
                "cuisines": ["Desserts & Beverages"]
            },
            {
                "name": "Chowman",
                "restaurant_type": "Both",
                "address": "403, 1st Cross Rd, 7th Block, Koramangala",
                "city": "Bengaluru",
                "rating": Decimal("4.5"),
                "image": "https://images.unsplash.com/photo-1552611052-33e04de081de?auto=format&fit=crop&w=800&q=80",
                "cuisines": ["Chinese", "Desserts & Beverages"]
            },
            {
                "name": "Truffles",
                "restaurant_type": "Both",
                "address": "93 St. Marks Road, Ashok Nagar",
                "city": "Bengaluru",
                "rating": Decimal("4.7"),
                "image": "https://images.unsplash.com/photo-1550547660-d9450f859349?auto=format&fit=crop&w=800&q=80",
                "cuisines": ["Fast Food", "Italian", "Desserts & Beverages"]
            },
        ]

        rest_map = {}
        for r_data in restaurants_data:
            cuisines_list = r_data.pop("cuisines")
            rest = Restaurant.objects.create(**r_data)
            rest.cuisines.set([cuisines_map[c] for c in cuisines_list if c in cuisines_map])
            rest_map[rest.name] = rest
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(rest_map)} partner restaurants."))

        # 4. Food Items (50+ items)
        foods_data = [
            # --- VEG DISHES ---
            (
                "Jamavar", "veg", "North Indian", "Paneer Butter Masala",
                "Silky cottage cheese cubes simmered in a velvet tomato, butter, and cashew gravy.",
                Decimal("340.00"), "Veg",
                "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Jamavar", "veg", "North Indian", "Dal Jamavar",
                "Signature black lentils slow-cooked overnight with fresh cream and country butter.",
                Decimal("290.00"), "Veg",
                "https://images.unsplash.com/photo-1546833999-b9f581a1996d?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Jamavar", "veg", "North Indian", "Subz Dum Biryani",
                "Fragrant basmati rice layered with garden vegetables, saffron and royal spices.",
                Decimal("320.00"), "Veg",
                "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "The Bangalore Cafe", "veg", "North Indian", "Palak Paneer",
                "Fresh tender paneer simmered in pureed farm spinach spiced with roasted cumin and garlic.",
                Decimal("240.00"), "Veg",
                "https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "The Bangalore Cafe", "veg", "North Indian", "Butter Garlic Naan",
                "Pillowy leavened flatbread glazed with melted butter and fresh minced garlic.",
                Decimal("60.00"), "Veg",
                "https://images.unsplash.com/photo-1533777857889-4be7c70b33f7?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Vidyarthi Bhavan", "veg", "South Indian", "Crispy Masala Dosa",
                "World-famous golden crispy butter dosa filled with spiced potato palya and coconut chutney.",
                Decimal("90.00"), "Veg",
                "https://images.unsplash.com/photo-1668236543090-82eba5ee5976?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Vidyarthi Bhavan", "veg", "South Indian", "Idli Vada Combo",
                "Steamed fluffy rice idlis and crispy medu vada served with hot sambar and chutney.",
                Decimal("80.00"), "Veg",
                "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "The Old House", "veg", "Italian", "Classic Margherita Pizza",
                "San Marzano tomato base topped with fresh buffalo mozzarella, olive oil, and basil.",
                Decimal("320.00"), "Veg",
                "https://images.unsplash.com/photo-1604382355076-af4b0eb60143?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "The Old House", "veg", "Italian", "Creamy Alfredo Penne",
                "Al dente penne tossed in rich parmesan garlic white sauce with sautéed mushrooms.",
                Decimal("290.00"), "Veg",
                "https://images.unsplash.com/photo-1621996346565-e3d5d628178d?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Gufha Restaurant", "veg", "North Indian", "Paneer Tikka Angare",
                "Tandoor roasted cottage cheese cubes marinated in fiery red spices and hung curd.",
                Decimal("270.00"), "Veg",
                "https://images.unsplash.com/photo-1599488615731-7e5c2823ff28?auto=format&fit=crop&w=800&q=80"
            ),

            # --- NON-VEG DISHES ---
            (
                "Jamavar", "non-veg", "North Indian", "Murgh Makhani (Butter Chicken)",
                "Smoked shredded tandoori chicken cooked in velvety, butter-enriched spiced tomato gravy.",
                Decimal("420.00"), "Non-Veg",
                "https://images.unsplash.com/photo-1588166524941-3bf61a9c41db?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Jamavar", "non-veg", "Mughlai", "Gosht Dum Biryani",
                "Tender prime mutton cuts slow-cooked with aged fragrant basmati rice under purdah.",
                Decimal("490.00"), "Non-Veg",
                "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Karavalli", "non-veg", "South Indian", "Mangalorean Fish Curry",
                "Fresh kingfish fillets simmered in roasted Byadagi chilies, ground coconut and kokum.",
                Decimal("380.00"), "Non-Veg",
                "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Karavalli", "non-veg", "South Indian", "Koli Ghee Roast",
                "Succulent chicken morsels roasted in pure country ghee with aromatic Kundapur spices.",
                Decimal("350.00"), "Non-Veg",
                "https://images.unsplash.com/photo-1610057099443-fde8c4d50f91?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Meghana Foods", "non-veg", "Mughlai", "Meghana Special Chicken Biryani",
                "Iconic spicy boneless Andhra-style chicken layered over steaming hot biryani rice.",
                Decimal("320.00"), "Non-Veg",
                "https://images.unsplash.com/photo-1589302168068-964664d93dc0?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Meghana Foods", "non-veg", "North Indian", "Chicken 65",
                "Crispy fried boneless chicken tossed with curry leaves, crushed pepper and green chilies.",
                Decimal("260.00"), "Non-Veg",
                "https://images.unsplash.com/photo-1610057099431-d73a1c9d2f2f?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Gufha Restaurant", "non-veg", "Mughlai", "Rogan Josh Kashmiri",
                "Traditional Kashmiri slow-cooked lamb curry infused with fennel, ginger and ratanjot.",
                Decimal("410.00"), "Non-Veg",
                "https://images.unsplash.com/photo-1545247181-516773ca83e3?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Gufha Restaurant", "non-veg", "North Indian", "Tandoori Chicken Platter",
                "Whole tender chicken marinated in spiced yogurt and roasted in traditional clay oven.",
                Decimal("360.00"), "Non-Veg",
                "https://images.unsplash.com/photo-1599488615731-7e5c2823ff28?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Niyaaz Restaurant", "non-veg", "Mughlai", "Belagavi Mutton Biryani",
                "Heritage Belagavi biryani cooked on firewood with succulent mutton pieces and ghee.",
                Decimal("390.00"), "Non-Veg",
                "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Empire Restaurant", "non-veg", "Chinese", "Chicken Hakka Noodles",
                "Thin egg noodles wok-tossed with shredded chicken, crunchy scallions and soy.",
                Decimal("210.00"), "Non-Veg",
                "https://images.unsplash.com/photo-1617622141675-d3005b9067c5?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Empire Restaurant", "non-veg", "North Indian", "Empire Butter Chicken & Coin Parotta",
                "Rich mildly sweet chicken gravy served with 2 flaky layered Malabar coin parottas.",
                Decimal("280.00"), "Non-Veg",
                "https://images.unsplash.com/photo-1588166524941-3bf61a9c41db?auto=format&fit=crop&w=800&q=80"
            ),

            # --- SNACKS / STREET-STYLE FOOD (Registered Restaurants Only!) ---
            (
                "The Bangalore Cafe", "street-food", "Street Food", "Mumbai Pav Bhaji",
                "Mashed spiced seasonal vegetables cooked on tawa with generous dollops of Amul butter and pav.",
                Decimal("160.00"), "Veg",
                "https://images.unsplash.com/photo-1606491956689-2ea866880c84?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "The Bangalore Cafe", "street-food", "Street Food", "Classic Vada Pav (2 Pcs)",
                "Golden spiced potato batata vada stuffed in soft buttered pav with dry garlic red chutney.",
                Decimal("90.00"), "Veg",
                "https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "The Bangalore Cafe", "street-food", "Street Food", "Punjabi Samosa with Chole",
                "Crispy golden pastry triangles filled with spiced potatoes, served with tangy chole gravy.",
                Decimal("120.00"), "Veg",
                "https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "The Old House", "street-food", "Street Food", "Dahi Puri Chaat",
                "Crispy puris stuffed with boiled potatoes, chilled yogurt, sweet tamarind and spicy mint chutneys.",
                Decimal("110.00"), "Veg",
                "https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "The Old House", "street-food", "Street Food", "Cheese Chilli Toast",
                "Crisp sourdough slices loaded with cheddar cheese, green chilies, and bell peppers.",
                Decimal("150.00"), "Veg",
                "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Vidyarthi Bhavan", "street-food", "Street Food", "Special Misal Pav",
                "Sprouted lentils in fiery Kolhapuri gravy topped with crunchy farsan, chopped onions, and soft pav.",
                Decimal("120.00"), "Veg",
                "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Vidyarthi Bhavan", "street-food", "Street Food", "Amritsari Chole Bhature",
                "Puffed golden bhature served with slow-cooked dark spiced chickpeas and pickled onions.",
                Decimal("160.00"), "Veg",
                "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Meghana Foods", "street-food", "Street Food", "Paneer Pakoda Basket",
                "Batter-fried fresh cottage cheese cubes seasoned with chaat masala and mint chutney.",
                Decimal("140.00"), "Veg",
                "https://images.unsplash.com/photo-1599488615731-7e5c2823ff28?auto=format&fit=crop&w=800&q=80"
            ),

            # --- DESSERTS (ICE CREAMS) ---
            (
                "Corner House Ice Cream", "desserts", "Desserts & Beverages", "Death By Chocolate (DBC)",
                "Legendary dessert: rich chocolate cake crowned with vanilla ice cream, hot chocolate fudge, and nuts.",
                Decimal("220.00"), "Veg",
                "https://images.unsplash.com/photo-1563805042-7684c019e1cb?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Corner House Ice Cream", "desserts", "Desserts & Beverages", "Mississippi Mud Sundae",
                "Fudge brownies layered with creamy dark chocolate ice cream and warm melted fudge.",
                Decimal("180.00"), "Veg",
                "https://images.unsplash.com/photo-1501443762994-82bd5dace89a?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Corner House Ice Cream", "desserts", "Desserts & Beverages", "Hot Butterscotch Sundae",
                "Creamy vanilla scoops smothered in buttery warm butterscotch sauce and roasted cashews.",
                Decimal("160.00"), "Veg",
                "https://images.unsplash.com/photo-1570197788417-0e82375c9371?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Corner House Ice Cream", "desserts", "Desserts & Beverages", "Tender Coconut Ice Cream Scoop",
                "Subtle, natural and refreshing artisanal ice cream crafted with real fresh tender coconut malai.",
                Decimal("110.00"), "Veg",
                "https://images.unsplash.com/photo-1587314168485-3236d6710814?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "The Old House", "desserts", "Desserts & Beverages", "Belgian Chocolate Tricone",
                "Crisp cocoa waffle cone filled with real Belgian chocolate ice cream and choco chips.",
                Decimal("90.00"), "Veg",
                "https://images.unsplash.com/photo-1580915411954-282cb1b0d780?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "The Bangalore Cafe", "desserts", "Desserts & Beverages", "Kwality Wall's Cornetto Double Choc",
                "Iconic crispy cone with dense chocolate ice cream topped with a solid chocolate disc.",
                Decimal("70.00"), "Veg",
                "https://images.unsplash.com/photo-1549395156-e0c1fe6fc7a5?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Jamavar", "desserts", "Desserts & Beverages", "Royal Shahi Tukda with Rabri",
                "Ghee-fried brioche soaked in saffron cardamom syrup, smothered in thickened reduced milk.",
                Decimal("220.00"), "Veg",
                "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=800&q=80"
            ),

            # --- BEVERAGES (COLD DRINKS & REFRESHMENTS) ---
            (
                "The Bangalore Cafe", "beverages", "Desserts & Beverages", "Chilled Coca-Cola (330ml Can)",
                "Crisp, bubbly and refreshingly cold classic Coca-Cola can.",
                Decimal("40.00"), "Veg",
                "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "The Bangalore Cafe", "beverages", "Desserts & Beverages", "Diet Coke (Chilled Can)",
                "Light, crisp, sugar-free Coca-Cola beverage served chilled.",
                Decimal("50.00"), "Veg",
                "https://upload.wikimedia.org/wikipedia/commons/8/89/Diet_Coke_Can.jpg"
            ),
            (
                "The Old House", "beverages", "Desserts & Beverages", "Sprite Zero (330ml)",
                "Lemon-lime flavored sparkling zero-calorie cold soda served with ice.",
                Decimal("45.00"), "Veg",
                "https://images.unsplash.com/photo-1625772299848-391b6a87d7b3?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "The Old House", "beverages", "Desserts & Beverages", "Sprite (Chilled Bottle)",
                "Invigorating citrus sparkling beverage served icy cold.",
                Decimal("40.00"), "Veg",
                "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Empire Restaurant", "beverages", "Desserts & Beverages", "Pepsi Chilled (330ml)",
                "Classic fizzy cola beverage served iced.",
                Decimal("40.00"), "Veg",
                "https://images.unsplash.com/photo-1553456558-aff63285bdd1?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Empire Restaurant", "beverages", "Desserts & Beverages", "Fresh Lime Soda (Sweet & Salt)",
                "Freshly squeezed key limes with chilled club soda, rock salt and pure cane syrup.",
                Decimal("70.00"), "Veg",
                "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Vidyarthi Bhavan", "beverages", "Desserts & Beverages", "South Indian Filter Coffee",
                "Traditional freshly brewed chicory-infused decoction with frothed whole milk in davara tumbler.",
                Decimal("45.00"), "Veg",
                "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Meghana Foods", "beverages", "Desserts & Beverages", "Masala Chaas (Spiced Buttermilk)",
                "Refreshing churned yogurt cooler infused with roasted cumin, fresh coriander, ginger, and curry leaves.",
                Decimal("50.00"), "Veg",
                "https://images.unsplash.com/photo-1546833999-b9f581a1996d?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Empire Restaurant", "beverages", "Desserts & Beverages", "Thums Up (Chilled 330ml Can)",
                "Bold, fizzy and strong Indian cola served chilled.",
                Decimal("40.00"), "Veg",
                "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Corner House Ice Cream", "desserts", "Desserts & Beverages", "Chocolate Fudge Fantasy",
                "Warm chocolate cake base crowned with vanilla ice cream, hot chocolate fudge and roasted peanuts.",
                Decimal("170.00"), "Veg",
                "https://images.unsplash.com/photo-1572490122747-3968b75cc699?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Corner House Ice Cream", "desserts", "Desserts & Beverages", "Royal Mango Kulfi",
                "Rich reduced milk frozen kulfi infused with Alfonso mango pulp and slivered pistachios.",
                Decimal("120.00"), "Veg",
                "https://images.unsplash.com/photo-1587314168485-3236d6710814?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Chowman", "veg", "Chinese", "Crispy Chilli Babycorn",
                "Wok-tossed crunchy baby corn fingers coated with garlic, scallions, and spicy oriental red chili sauce.",
                Decimal("220.00"), "Veg",
                "https://images.unsplash.com/photo-1541696432-82c6da8ce7bf?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Chowman", "non-veg", "Chinese", "Chicken Manchow Soup",
                "Spicy soy broth simmered with minced chicken, mushrooms, and topped with crisp fried noodles.",
                Decimal("180.00"), "Non-Veg",
                "https://images.unsplash.com/photo-1547592166-23ac45744acd?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Truffles", "veg", "Fast Food", "Classic Veggie Supreme Burger",
                "Crispy vegetable patty layered with cheddar cheese slice, fresh lettuce, tomato, and house mayo.",
                Decimal("160.00"), "Veg",
                "https://images.unsplash.com/photo-1550547660-d9450f859349?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "The Bangalore Cafe", "snacks", "Snacks & Street Food", "Kolkata Kathi Paneer Roll",
                "Flaky paratha rolled with spicy marinated paneer cubes, crunchy sliced onions and tangy green mint chutney.",
                Decimal("140.00"), "Veg",
                "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Karavalli", "non-veg", "South Indian", "Prawns Sukka",
                "Coastal fresh tiger prawns pan-tossed in dry roasted coconut, curry leaves, and Malabar spices.",
                Decimal("420.00"), "Non-Veg",
                "https://images.unsplash.com/photo-1565557623262-b51c2513a641?auto=format&fit=crop&w=800&q=80"
            ),
        ]

        food_count = 0
        for rest_name, cat_slug, cuisine_name, item_name, desc, price, food_type, image in foods_data:
            rest = rest_map.get(rest_name)
            cat = cat_map.get(cat_slug)
            cuisine = cuisines_map.get(cuisine_name)
            if not rest or not cat:
                continue

            FoodItem.objects.create(
                restaurant=rest,
                category=cat,
                cuisine=cuisine,
                name=item_name,
                description=desc,
                price=price,
                food_type=food_type,
                image=image,
                is_available=True
            )
            food_count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {food_count} food items across all restaurants!"))
        self.stdout.write("--- Seeding Complete ---")
