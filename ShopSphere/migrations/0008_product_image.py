# Generated by Django 2.2.28 on 2025-03-21 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ShopSphere', '0007_auto_20250321_1439'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='product_images/'),
        ),
    ]
