from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from items.models import Item


class ItemModelTest(TestCase):
    # Create an item
    def setUp(self):
        self.user = User.objects.create_user('seller', 'seller@example.com', 'pass')
        self.item = Item.objects.create(
            item_name='Test Item',
            item_price=Decimal('100.00'),
            item_category='electronics',
            item_quantity=10,
            item_weight=Decimal('1.0'),
            seller=self.user,
        )
    
    # TEST METHODS
   
    ''' Since the sku is empty, should be auto-generated ''' 
    def test_sku_auto_generation(self):
        item = Item.objects.create(
            item_name='Book',
            item_price=Decimal('20.00'),
            item_category='books_media',
            item_quantity=5,
            item_weight=Decimal('0.5'),
            seller=self.user,
        )
        self.assertTrue(item.item_sku.startswith('BOO'))

    ''' If on sale, should return sale price '''
    def test_current_price_returns_sale_price(self):
        self.item.is_on_sale = True
        self.item.sale_price = Decimal('80.00')
        self.item.save()
        
        self.assertEqual(self.item.current_price, Decimal('80.00'))
    
    
    ''' The sale price should be lower than the regular price '''
    def test_sale_price_validation(self):
        with self.assertRaises(ValidationError):
            item = Item(
                item_name='Test',
                item_price=Decimal('100.00'),
                is_on_sale=True,
                sale_price=Decimal('150.00'),  # Higher than regular price
                item_category='electronics',
                item_quantity=1,
                item_weight=Decimal('0.1'),
                seller=self.user,
            )
            item.full_clean()
    
    ''' Test if the stock items are reduced correctly'''
    def test_stock_reduction_works(self):
        result = self.item.reduce_stock(3)
        
        self.assertTrue(result)
        self.item.refresh_from_db()
        self.assertEqual(self.item.item_quantity, 7)
        self.assertEqual(self.item.times_purchased, 3)
    
    ''' Should fail if the user wants to reduce more than available stock '''
    def test_stock_reduction_fails_insufficient_stock(self):
        result = self.item.reduce_stock(20)  # More than available
        self.assertFalse(result)
    
    ''' When choose other category, custom_category should be required'''
    def test_custom_category_required_when_other(self):
        with self.assertRaises(ValidationError):
            Item(
                item_name='Test',
                item_price=Decimal('50.00'),
                item_category='other',  # Should require custom_category
                item_quantity=1,
                item_weight=Decimal('0.1'),
                seller=self.user,
            ).save()
    
    ''' Test if display_category returns the correct category name '''
    def test_display_category_shows_custom(self):
        self.item.item_category = 'other'
        self.item.custom_category = 'gaming gear'
        self.item.save()
        
        self.assertEqual(self.item.display_category, 'Gaming Gear')
    
    
    def test_search_filters_by_category(self):
        """Test search functionality works"""
        # Create item in different category
        Item.objects.create(
            item_name='Book',
            item_price=Decimal('20.00'),
            item_category='books_media',
            item_quantity=5,
            item_weight=Decimal('0.5'),
            seller=self.user,
        )
        
        results = Item.search_items(category='electronics')
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().item_category, 'electronics')
    
    def test_view_tracking_in_session(self):
        """Test view tracking updates session"""
        factory = RequestFactory()
        request = factory.get('/')
        request.session = {}
        
        Item.track_view(self.item.id, request)
        
        self.assertEqual(request.session['viewed_items'][0], self.item.id)
    
    def test_discount_percentage_calculation(self):
        """Test discount calculation is correct"""
        self.item.is_on_sale = True
        self.item.sale_price = Decimal('80.00')  # 20% off
        self.item.save()
        
        self.assertEqual(self.item.discount_percentage, 20)