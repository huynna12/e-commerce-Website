from datetime import timedelta
from django.utils import timezone
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from decimal import Decimal
from orders.models import Order, OrderItem
from items.models import Item, Review, Promotion

# ITEM MODEL TESTS
class ItemModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('seller', 'seller@example.com', 'pass')
        self.item = Item.objects.create(
            item_name='Test Item', 
            item_price=Decimal('100.00'),
            item_category='electronics',
            item_quantity=10, item_weight=Decimal('1.0'), 
            seller=self.user
        )

    def test_sku_auto_generation(self):
        self.assertTrue(self.item.item_sku.startswith('ELE'))

    def test_current_price_and_discount(self):
        # Without sale
        self.assertEqual(self.item.current_price, Decimal('100.00'))

        # With sale
        self.item.is_on_sale = True
        self.item.sale_price = Decimal('80.00')
        self.item.save()
        self.assertEqual(self.item.current_price, Decimal('80.00'))
        self.assertEqual(self.item.discount_percentage, 20)
    
    # Sale price must be lower than regular price
    def test_sale_price_validation(self):
        with self.assertRaises(ValidationError):
            Item(
                item_name='Test',
                item_price=Decimal('100.00'),
                is_on_sale=True,
                sale_price=Decimal('150.00'),   # Higher than regular price
                item_category='electronics',
                item_quantity=10,
                seller=self.user
            ).full_clean()
    
    def test_stock_reduction(self):   
        # Successful reduction
        result = self.item.reduce_stock(3)
        self.assertTrue(result)
        self.item.refresh_from_db()
        self.assertEqual(self.item.item_quantity, 7)
        self.assertEqual(self.item.times_purchased, 3)
        
        # Insufficient stock
        result = self.item.reduce_stock(20)
        self.assertFalse(result)
    
    def test_custom_category_handling(self):        
        # Missing custom_category for 'other' category
        with self.assertRaises(ValidationError):
            Item(
                item_name='Test',
                item_price=Decimal('50.00'),
                item_category='other',
                item_quantity=1,
                seller=self.user
            ).save()
        
        # Test display_category 
        self.item.item_category = 'other'
        self.item.custom_category = 'gaming gear'
        self.item.save()
        self.assertEqual(self.item.display_category, 'Gaming Gear')

    def test_search_and_tracking(self):      
        results = Item.search_items(category='electronics')
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().item_category, 'electronics')
        
        # Test view tracking
        factory = RequestFactory()
        request = factory.get('/')
        request.session = {}
        Item.track_view(self.item.id, request, 5)
        self.assertEqual(request.session['viewed_items'][0], self.item.id)

# REVIEW MODEL TESTS
class ReviewModelTest(TestCase):
    def setUp(self):
        self.reviewer = User.objects.create_user('reviewer', 'reviewer@example.com', 'pass')
        self.seller = User.objects.create_user('seller', 'seller@example.com', 'pass')
        self.item = Item.objects.create(
            item_name='Test Item', item_price=Decimal('100.00'), item_category='electronics',
            item_quantity=10, item_weight=Decimal('1.0'), seller=self.seller
        )
        self.order = Order.objects.create(user=self.reviewer, total_price=Decimal('100.00'), status='delivered')
        OrderItem.objects.create(order=self.order, item=self.item, quantity=1, price=Decimal('100.00'))
        self.review = Review.objects.create(
            item=self.item, reviewer=self.reviewer, rating=4, comment='Great!', order=self.order
        )
    
    def test_review_validation(self):
        # Test prevent self-review
        with self.assertRaises(ValidationError):
            Review(item=self.item, reviewer=self.seller, rating=5, comment='Self review').full_clean()
    
    def test_verified_purchase_logic(self):
        # Create new buyer with delivered order
        buyer = User.objects.create_user('buyer', 'buyer@example.com', 'pass')
        order = Order.objects.create(user=buyer, total_price=Decimal('100.00'), status='delivered')
        OrderItem.objects.create(order=order, item=self.item, quantity=1, price=Decimal('100.00'))
        
        review = Review.objects.create(item=self.item, reviewer=buyer, rating=5, order=order)
        self.assertTrue(review.is_verified_purchase)
        
        # Test validation prevents non-delivered order review
        buyer2 = User.objects.create_user('buyer2', 'buyer2@example.com', 'pass')
        processing_order = Order.objects.create(user=buyer2, total_price=Decimal('100.00'), status='processing')
        OrderItem.objects.create(order=processing_order, item=self.item, quantity=1, price=Decimal('100.00'))
        
        with self.assertRaises(ValidationError):
            Review.objects.create(item=self.item, reviewer=buyer2, rating=3, order=processing_order)
    
    def test_helpful_and_response_functionality(self):
        # Test mark helpful
        initial_count = self.review.helpful_count
        self.review.mark_helpful()
        self.assertEqual(self.review.helpful_count, initial_count + 1)
        
        # Test seller response
        result = self.review.add_seller_response("Thanks!", self.seller)
        self.assertTrue(result)
        self.review.refresh_from_db()
        self.assertEqual(self.review.seller_response, "Thanks!")
        self.assertIsNotNone(self.review.response_date)
        
        # Test non-seller cannot respond
        other_user = User.objects.create_user('other', 'other@example.com', 'pass')
        result = self.review.add_seller_response("Unauthorized", other_user)
        self.assertFalse(result)
    
    def test_item_stats_calculation(self):
        # Create additional reviews using existing setup
        buyer2 = User.objects.create_user('buyer2', 'buyer2@example.com', 'pass')
        order2 = Order.objects.create(user=buyer2, total_price=Decimal('100.00'), status='delivered')
        OrderItem.objects.create(order=order2, item=self.item, quantity=1, price=Decimal('100.00'))
        
        buyer3 = User.objects.create_user('buyer3', 'buyer3@example.com', 'pass')
        order3 = Order.objects.create(user=buyer3, total_price=Decimal('100.00'), status='delivered')
        OrderItem.objects.create(order=order3, item=self.item, quantity=1, price=Decimal('100.00'))
        
        # Create additional reviews
        Review.objects.create(item=self.item, reviewer=buyer2, rating=5, order=order2)
        Review.objects.create(item=self.item, reviewer=buyer3, rating=3, order=order3)
        
        stats = Review.get_item_stats(self.item)
        self.assertEqual(stats['total_reviews'], 3)
        self.assertEqual(stats['average_rating'], 4.0)
        self.assertEqual(stats['percentage_recommend'], 66.7)  
        
        # Test item with no reviews
        new_item = Item.objects.create(
            item_name='New Item', item_price=Decimal('50.00'), item_category='electronics',
            item_quantity=5, item_weight=Decimal('0.5'), seller=self.seller
        )
        stats = Review.get_item_stats(new_item)
        self.assertIsNone(stats)  # Returns None for no reviews
    
    def test_reviews_with_media(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        # Verify no media reviews exist initially
        initial_media_reviews = Review.get_reviews_with_media(self.item)
        self.assertEqual(initial_media_reviews.count(), 0)
        
        # Create review with media
        buyer2 = User.objects.create_user('buyer2', 'buyer2@example.com', 'pass')
        order2 = Order.objects.create(user=buyer2, total_price=Decimal('100.00'), status='delivered')
        OrderItem.objects.create(order=order2, item=self.item, quantity=1, price=Decimal('100.00'))
        
        # Create mock media file
        test_file = SimpleUploadedFile("test.jpg", b"fake image content", content_type="image/jpeg")
        
        Review.objects.create(
            item=self.item, reviewer=buyer2, rating=5, order=order2, 
            media=test_file, comment="Great with photo!"
        )
        
        # Test getting reviews with media
        media_reviews = Review.get_reviews_with_media(self.item)
        self.assertEqual(media_reviews.count(), 1)
        
        # Test with limit
        limited_reviews = Review.get_reviews_with_media(self.item, limit=5)
        self.assertEqual(limited_reviews.count(), 1)

# PROMOTION MODEL TEST
class PromotionModelTest(TestCase):
    def setUp(self):
        self.seller = User.objects.create_user(username='seller', password='testpass')
        self.item = Item.objects.create(
            item_name='Test Item',
            item_price=100,
            seller=self.seller,
            item_category='electronics'  # Use a valid category from CATEGORY_CHOICES
        )
        now = timezone.now()
        self.promo = Promotion.objects.create(
            promo_type='item',
            code='PROMO10',
            discount_method='percent',
            discount_amount=10,
            start_at=now - timedelta(days=1),
            end_at=now + timedelta(days=1),
        )
        self.promo.items.add(self.item)
        self.promo.sellers.add(self.seller)

    def test_is_valid(self):
        self.assertTrue(self.promo.is_valid())

    def test_is_applicable_to_item(self):
        class DummyOrderItem:
            item = self.item
        order_item = DummyOrderItem()
        self.assertTrue(self.promo.is_applicable_to_item(order_item))

    def test_calculate_discounted_amount_percent(self):
        self.assertEqual(self.promo.calculate_discounted_amount(100), 90.0)

    def test_calculate_discounted_amount_fixed(self):
        self.promo.discount_method = 'fixed'
        self.promo.discount_amount = 15
        self.assertEqual(self.promo.calculate_discounted_amount(100), 85.0)