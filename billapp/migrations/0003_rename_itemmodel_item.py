# Generated by Django 4.2.3 on 2024-01-01 06:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("billapp", "0002_unitmodel_itemmodel"),
    ]

    operations = [
        migrations.RenameModel(old_name="ItemModel", new_name="Item",),
    ]
