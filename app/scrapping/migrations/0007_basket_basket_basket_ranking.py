# Generated by Django 4.1.2 on 2022-10-20 22:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scrapping', '0006_remove_basket_basket_remove_basket_ranking'),
    ]

    operations = [
        migrations.AddField(
            model_name='basket',
            name='basket',
            field=models.JSONField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='basket',
            name='ranking',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
    ]
