# Generated by Django 5.1.7 on 2025-03-26 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carrito', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemcarrito',
            name='color',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='itemcarrito',
            name='talla',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
