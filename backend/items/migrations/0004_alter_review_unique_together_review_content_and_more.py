# Generated by Django 5.2.1 on 2025-07-16 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0003_remove_item_items_item_view_co_b9e501_idx_and_more'),
        ('orders', '0003_remove_order_orders_orde_status_25e057_idx_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='review',
            unique_together={('order', 'item')},
        ),
        migrations.AddField(
            model_name='review',
            name='content',
            field=models.TextField(blank=True, help_text="Review's content"),
        ),
        migrations.AddField(
            model_name='review',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='times_purchased',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AlterField(
            model_name='item',
            name='view_count',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.RemoveField(
            model_name='review',
            name='comment',
        ),
    ]
