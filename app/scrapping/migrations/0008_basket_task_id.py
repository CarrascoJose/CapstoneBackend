# Generated by Django 4.1.2 on 2022-10-21 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scrapping', '0007_basket_basket_basket_ranking'),
    ]

    operations = [
        migrations.AddField(
            model_name='basket',
            name='task_id',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
