# Generated by Django 3.2.5 on 2022-03-19 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookclub', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rating',
            name='isbn',
            field=models.CharField(max_length=12),
        ),
    ]
