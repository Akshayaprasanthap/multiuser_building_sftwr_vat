# Generated by Django 4.2.3 on 2024-01-02 15:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("billapp", "0008_alter_company_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="company",
            name="user",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="company_profile",
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
    ]
