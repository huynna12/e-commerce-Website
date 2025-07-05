from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from items.models import Item
from items.data.sample_items import ALL_SAMPLE_ITEMS
import random
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Create comprehensive test items with diverse sellers'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=50, help='Number of items to create')
        parser.add_argument('--clear', action='store_true', help='Clear existing items first')

    def handle(self, *args, **options):
        count = options['count']
        
        if options['clear']:
            Item.objects.all().delete()
            self.stdout.write(self.style.WARNING('Cleared all existing items'))
        
        # Create diverse sellers
        sellers = self.create_test_sellers()
        
        self.stdout.write(f"Using {len(ALL_SAMPLE_ITEMS)} item templates with {len(sellers)} sellers")
        
        created_count = 0
        for i in range(count):
            try:
                item_data = random.choice(ALL_SAMPLE_ITEMS)
                seller = self.assign_seller_by_category(item_data['category'], sellers)
                
                item = self.create_item_from_template(item_data, seller, i)
                created_count += 1
                
                if created_count % 10 == 0:
                    self.stdout.write(f"Created {created_count}/{count} items...")
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating item {i+1}: {str(e)}'))
        
        self.show_summary(created_count)

    def create_test_sellers(self):
        """Create 20 diverse sellers with specializations"""
        seller_profiles = [
            # Electronics Specialists
            {'username': 'techguru_electronics', 'first_name': 'Tech', 'last_name': 'Guru', 'email': 'tech@techguru.com'},
            {'username': 'gadget_central', 'first_name': 'Gadget', 'last_name': 'Central', 'email': 'sales@gadgetcentral.com'},
            {'username': 'apple_store_official', 'first_name': 'Apple', 'last_name': 'Store', 'email': 'info@applestore.com'},
            {'username': 'samsung_retailer', 'first_name': 'Samsung', 'last_name': 'Retailer', 'email': 'samsung@retailer.com'},
            
            # Fashion Specialists
            {'username': 'fashion_forward_shop', 'first_name': 'Fashion', 'last_name': 'Forward', 'email': 'hello@fashionforward.com'},
            {'username': 'streetwear_hub', 'first_name': 'Street', 'last_name': 'Wear', 'email': 'orders@streetwear.com'},
            {'username': 'nike_official_store', 'first_name': 'Nike', 'last_name': 'Official', 'email': 'nike@official.com'},
            {'username': 'vintage_clothing_co', 'first_name': 'Vintage', 'last_name': 'Clothing', 'email': 'vintage@clothing.com'},
            
            # Book Specialists
            {'username': 'bookworm_paradise', 'first_name': 'Book', 'last_name': 'Paradise', 'email': 'books@paradise.com'},
            {'username': 'tech_books_store', 'first_name': 'Tech', 'last_name': 'Books', 'email': 'info@techbooks.com'},
            {'username': 'digital_learning_hub', 'first_name': 'Digital', 'last_name': 'Learning', 'email': 'learn@digital.com'},
            
            # Home & Garden Specialists
            {'username': 'home_essentials_store', 'first_name': 'Home', 'last_name': 'Essentials', 'email': 'home@essentials.com'},
            {'username': 'green_thumb_gardens', 'first_name': 'Green', 'last_name': 'Thumb', 'email': 'plants@greenthumb.com'},
            
            # Sports & Fitness Specialists
            {'username': 'fitlife_equipment', 'first_name': 'Fit', 'last_name': 'Life', 'email': 'gear@fitlife.com'},
            {'username': 'outdoor_adventure_co', 'first_name': 'Outdoor', 'last_name': 'Adventure', 'email': 'outdoor@adventure.com'},
            
            # General/Multi-category Stores
            {'username': 'mega_marketplace', 'first_name': 'Mega', 'last_name': 'Marketplace', 'email': 'support@mega.com'},
            {'username': 'quality_goods_co', 'first_name': 'Quality', 'last_name': 'Goods', 'email': 'sales@quality.com'},
            {'username': 'discount_depot', 'first_name': 'Discount', 'last_name': 'Depot', 'email': 'deals@discount.com'},
            
            # Individual Sellers
            {'username': 'john_tech_seller', 'first_name': 'John', 'last_name': 'Smith', 'email': 'john@email.com'},
            {'username': 'sarah_fashion_blog', 'first_name': 'Sarah', 'last_name': 'Johnson', 'email': 'sarah@fashion.com'},
        ]
        
        sellers = []
        for seller_info in seller_profiles:
            user, created = User.objects.get_or_create(
                username=seller_info['username'],
                defaults=seller_info
            )
            sellers.append(user)
            if created:
                self.stdout.write(f"Created seller: {user.username}")
        
        return sellers

    def assign_seller_by_category(self, category, sellers):
        """Assign sellers based on their specialization"""
        # Define which sellers specialize in which categories
        specialists = {
            'electronics': ['techguru_electronics', 'gadget_central', 'apple_store_official', 'samsung_retailer', 'john_tech_seller'],
            'clothing': ['fashion_forward_shop', 'streetwear_hub', 'nike_official_store', 'vintage_clothing_co', 'sarah_fashion_blog'],
            'books': ['bookworm_paradise', 'tech_books_store', 'digital_learning_hub'],
            'home_garden': ['home_essentials_store', 'green_thumb_gardens'],
            'sports_fitness': ['fitlife_equipment', 'outdoor_adventure_co'],
        }
        
        # 80% chance to use specialist, 20% chance any seller
        category_specialists = specialists.get(category, [])
        
        if category_specialists and random.random() < 0.8:
            specialist_sellers = [s for s in sellers if s.username in category_specialists]
            return random.choice(specialist_sellers)
        else:
            # Use general stores or any seller
            general_stores = ['mega_marketplace', 'quality_goods_co', 'discount_depot']
            general_sellers = [s for s in sellers if s.username in general_stores]
            return random.choice(general_sellers + sellers[:5])  # Mix of general + random

    def create_item_from_template(self, item_data, seller, index):
        """Create item with realistic variations"""
        # Price variation
        price_variation = random.uniform(0.85, 1.15)
        final_price = round(item_data['price'] * price_variation, 2)
        
        # Unique name
        variants = ['Pro', 'Standard', 'Premium', 'Basic', 'Plus', 'Max', 'Elite', 'Deluxe']
        item_name = f"{item_data['name']} {random.choice(variants)} #{index+1:03d}"
        
        # Random attributes
        is_featured = random.choice([True] + [False] * 6)  # ~14% chance
        is_on_sale = random.choice([True] + [False] * 2)   # ~33% chance
        condition = random.choice(['new'] * 4 + ['used', 'refurbished'])  # 66% new
        
        # Sale logic
        sale_price = None
        sale_start_date = None
        sale_end_date = None
        
        if is_on_sale:
            discount = random.uniform(0.1, 0.4)
            sale_price = round(final_price * (1 - discount), 2)
            
            start_days_ago = random.randint(1, 30)
            sale_duration = random.randint(7, 60)
            sale_start_date = timezone.now() - timedelta(days=start_days_ago)
            sale_end_date = sale_start_date + timedelta(days=sale_duration)
        
        # Create item
        return Item.objects.create(
            item_name=item_name,
            item_summary=item_data['summary'],
            item_description=item_data['description'],
            item_price=Decimal(str(final_price)),
            item_quantity=random.randint(1, 100),
            item_category=item_data['category'],
            item_origin=item_data['origin'],
            item_condition=condition,
            item_weight=Decimal(str(item_data['weight'])) if item_data['weight'] > 0 else None,
            item_dimensions=item_data['dimensions'],
            technical_specs=item_data['specs'],
            is_featured=is_featured,
            is_available=True,
            is_on_sale=is_on_sale,
            is_digital=item_data['is_digital'],
            seller=seller,
            sale_price=Decimal(str(sale_price)) if sale_price else None,
            sale_start_date=sale_start_date,
            sale_end_date=sale_end_date,
            view_count=random.randint(0, 1000),
            times_purchased=random.randint(0, 50),
        )

    def show_summary(self, created_count):
        """Show creation summary"""
        self.stdout.write(self.style.SUCCESS(f'✅ Created {created_count} items!'))
        
        # Stats
        total_items = Item.objects.count()
        featured = Item.objects.filter(is_featured=True).count()
        on_sale = Item.objects.filter(is_on_sale=True).count()
        
        self.stdout.write(f"📊 Total items: {total_items}")
        self.stdout.write(f"⭐ Featured: {featured}")
        self.stdout.write(f"🏷️ On sale: {on_sale}")
        
        # Category breakdown
        self.stdout.write("\n📈 Items per category:")
        for category, _ in Item.CATEGORY_CHOICES:
            count = Item.objects.filter(item_category=category).count()
            if count > 0:
                self.stdout.write(f"  {category}: {count}")
        
        # Seller breakdown
        seller_counts = {}
        for item in Item.objects.select_related('seller'):
            seller = item.seller.username
            seller_counts[seller] = seller_counts.get(seller, 0) + 1
        
        self.stdout.write(f"\n👥 Top sellers:")
        for seller, count in sorted(seller_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            self.stdout.write(f"  {seller}: {count} items")