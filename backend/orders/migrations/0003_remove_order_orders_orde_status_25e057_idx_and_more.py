# Generated by Django 5.2.1 on 2025-07-10 20:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_alter_order_tracking_number'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='order',
            name='orders_orde_status_25e057_idx',
        ),
        migrations.RemoveIndex(
            model_name='order',
            name='orders_orde_trackin_04edf9_idx',
        ),
    ]
