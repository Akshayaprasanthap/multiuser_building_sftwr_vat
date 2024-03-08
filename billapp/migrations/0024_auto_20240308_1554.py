# Generated by Django 3.2.20 on 2024-03-08 10:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('billapp', '0023_auto_20240307_1135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partytransactionhistory',
            name='party',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='billapp.party'),
        ),
        migrations.AlterField(
            model_name='salesinvoice',
            name='party',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='billapp.party'),
        ),
        migrations.AlterField(
            model_name='transactions_party',
            name='party',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='billapp.party'),
        ),
    ]
