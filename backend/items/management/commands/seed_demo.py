from __future__ import annotations

import os
import random
import secrets
from dataclasses import dataclass
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from items.models import Item, Review
from items.models.item import ItemImage
from orders.models import Order, OrderItem, OrderItemCancellation


@dataclass(frozen=True)
class DemoUsers:
    sellers: list[User]
    buyers: list[User]


class Command(BaseCommand):
    help = (
        "Seed a small, login-friendly demo dataset: demo sellers/buyers, items with image URLs, "
        "a couple of orders, and a pending item-cancellation request."
    )

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Delete existing demo_* data before seeding")
        parser.add_argument("--sellers", type=int, default=2, help="Number of demo sellers to create (default: 2)")
        parser.add_argument("--buyers", type=int, default=1, help="Number of demo buyers to create (default: 1)")
        parser.add_argument("--items", type=int, default=16, help="Total number of demo items to create (default: 16)")
        parser.add_argument("--orders", type=int, default=2, help="Number of demo orders to create (default: 2)")
        parser.add_argument(
            "--password",
            type=str,
            default="",
            help=(
                "Password to set for all demo users (recommended). If omitted, uses DEMO_PASSWORD env var; "
                "if that is also missing, a random password is generated and printed once."
            ),
        )

    @transaction.atomic
    def handle(self, *args, **options):
        reset: bool = bool(options["reset"])
        sellers_count: int = int(options["sellers"])
        buyers_count: int = int(options["buyers"])
        items_total: int = int(options["items"])
        orders_count: int = int(options["orders"])

        if sellers_count < 1:
            raise CommandError("--sellers must be >= 1")
        if buyers_count < 1:
            raise CommandError("--buyers must be >= 1")
        if items_total < 1:
            raise CommandError("--items must be >= 1")
        if orders_count < 1:
            raise CommandError("--orders must be >= 1")

        password = (options.get("password") or "").strip() or os.getenv("DEMO_PASSWORD", "").strip()
        generated_password = ""
        if not password:
            generated_password = self._generate_password()
            password = generated_password

        if reset:
            self._reset_demo_data()

        users = self._ensure_demo_users(sellers_count=sellers_count, buyers_count=buyers_count, password=password)
        self._ensure_demo_items(users.sellers, total=items_total)
        self._ensure_demo_orders(users.buyers, users.sellers, count=orders_count)

        self.stdout.write(self.style.SUCCESS("Demo data seeded."))
        self.stdout.write("Demo usernames:")
        for user in users.sellers + users.buyers:
            self.stdout.write(f"- {user.username}")

        if generated_password:
            self.stdout.write(self.style.WARNING("A random demo password was generated (store it somewhere safe):"))
            self.stdout.write(generated_password)
        else:
            self.stdout.write("Demo password: (the one you supplied via --password or DEMO_PASSWORD)")

    def _generate_password(self) -> str:
        # 16 chars with enough variety for most password rules.
        return secrets.token_urlsafe(12)

    def _reset_demo_data(self) -> None:
        demo_users = User.objects.filter(username__startswith="demo_")

        # Delete dependent data in a safe order.
        Review.objects.filter(reviewer__in=demo_users).delete()
        OrderItemCancellation.objects.filter(order_item__order__user__in=demo_users).delete()
        OrderItem.objects.filter(order__user__in=demo_users).delete()
        Order.objects.filter(user__in=demo_users).delete()

        ItemImage.objects.filter(item__seller__in=demo_users).delete()
        Item.objects.filter(seller__in=demo_users).delete()

        # Remove demo users last.
        demo_users.delete()

    def _ensure_demo_users(self, *, sellers_count: int, buyers_count: int, password: str) -> DemoUsers:
        sellers: list[User] = []
        buyers: list[User] = []

        for idx in range(1, sellers_count + 1):
            username = f"demo_seller{idx}"
            user, created = User.objects.get_or_create(username=username, defaults={"email": f"{username}@example.com"})
            if created or not user.has_usable_password():
                user.set_password(password)
                user.save(update_fields=["password"])
            # Ensure seller flag for UI even before items are created.
            if hasattr(user, "profile") and not user.profile.is_seller:
                user.profile.is_seller = True
                user.profile.save(update_fields=["is_seller"])
            sellers.append(user)

        for idx in range(1, buyers_count + 1):
            username = f"demo_buyer{idx}"
            user, created = User.objects.get_or_create(username=username, defaults={"email": f"{username}@example.com"})
            if created or not user.has_usable_password():
                user.set_password(password)
                user.save(update_fields=["password"])
            buyers.append(user)

        return DemoUsers(sellers=sellers, buyers=buyers)

    def _ensure_demo_items(self, sellers: list[User], *, total: int) -> None:
        # If items already exist for demo sellers, don't spam duplicates.
        existing = Item.objects.filter(seller__in=sellers).count()
        if existing >= total:
            return

        categories = [c for (c, _label) in Item.CATEGORY_CHOICES if c != "other"]
        conditions = [c for (c, _label) in Item.CONDITION_CHOICES]
        name_words = [
            "Wireless",
            "Vintage",
            "Premium",
            "Compact",
            "Ergonomic",
            "Smart",
            "Eco",
            "Classic",
            "Portable",
            "Pro",
        ]
        products = [
            "Headphones",
            "Jacket",
            "Coffee Maker",
            "Backpack",
            "Keyboard",
            "Lamp",
            "Sneakers",
            "Water Bottle",
            "Camera",
            "Book",
        ]

        to_create = total - existing
        now = timezone.now()

        for i in range(1, to_create + 1):
            seller = random.choice(sellers)
            category = random.choice(categories)
            condition = random.choice(conditions)
            price = Decimal(str(round(random.uniform(12, 300), 2)))

            item = Item.objects.create(
                item_name=f"{random.choice(name_words)} {random.choice(products)} {i}",
                item_summary="Demo item for portfolio showcase",
                item_desc="This is seeded demo data to showcase browsing, cart/checkout, orders, and seller flows.",
                item_price=price,
                item_quantity=random.randint(5, 40),
                item_category=category,
                custom_category="",
                item_origin="Demo",
                item_condition=condition,
                is_available=True,
                is_on_sale=(i % 5 == 0),
                sale_price=(price * Decimal("0.85")).quantize(Decimal("0.01")) if i % 5 == 0 else None,
                sale_start_date=now - timezone.timedelta(days=1) if i % 5 == 0 else None,
                sale_end_date=now + timezone.timedelta(days=7) if i % 5 == 0 else None,
                is_digital=False,
                seller=seller,
            )

            # Use a public placeholder image so the deployed demo looks good without persistent media storage.
            # picsum.photos is fine for a demo.
            ItemImage.objects.create(item=item, image_url=f"https://picsum.photos/seed/{item.id}/800/800")

    def _ensure_demo_orders(self, buyers: list[User], sellers: list[User], *, count: int) -> None:
        buyer = buyers[0]

        # Avoid creating duplicates on repeated runs.
        existing = Order.objects.filter(user=buyer).count()
        if existing >= count:
            return

        items = list(Item.objects.filter(seller__in=sellers, is_available=True))
        if not items:
            raise CommandError("No demo items found; cannot create demo orders.")

        # Create up to `count` orders. Make one delivered and one processing.
        statuses = ("delivered", "processing")
        for idx in range(existing, count):
            status = statuses[idx] if idx < len(statuses) else random.choice(["processing", "shipped", "delivered"])
            order = Order.objects.create(
                user=buyer,
                status=status,
                total_price=Decimal("0.01"),
                shipping_address="123 Demo Street",
                shipping_city="Demo City",
                shipping_postal_code="00000",
                shipping_country="Demo Land",
                payment_method="credit_card",
                payment_status="paid",
            )

            total = Decimal("0.00")
            chosen_items = random.sample(items, k=min(3, len(items)))
            for it in chosen_items:
                quantity = random.randint(1, 2)
                line_price = Decimal(str(it.current_price))
                OrderItem.objects.create(order=order, item=it, quantity=quantity, price=line_price)
                total += line_price * quantity

            order.total_price = max(total, Decimal("0.01"))
            order.save(update_fields=["total_price"])

            # Add a pending cancellation request on one processing order item to showcase seller workflow.
            if status == "processing":
                oi = order.items.select_related("item").first()
                if oi:
                    OrderItemCancellation.objects.get_or_create(
                        order_item=oi,
                        defaults={
                            "seller": oi.item.seller,
                            "status": "pending",
                            "message": "Demo: requesting cancellation for this item.",
                        },
                    )

            # Add 1 review for delivered items to make pages richer.
            if status == "delivered":
                for oi in order.items.select_related("item").all()[:1]:
                    Review.objects.get_or_create(
                        order=order,
                        item=oi.item,
                        reviewer=buyer,
                        defaults={
                            "rating": 5,
                            "content": "Great quality — seeded demo review.",
                            "is_verified_purchase": True,
                        },
                    )
