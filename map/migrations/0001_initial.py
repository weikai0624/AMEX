# Generated by Django 4.1.3 on 2022-12-01 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DiscountData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('place', models.CharField(max_length=99999)),
                ('discount_type', models.CharField(max_length=99999, null=True)),
                ('discount_url', models.URLField()),
                ('place_web_url', models.URLField(null=True)),
                ('phone', models.CharField(max_length=99999, null=True)),
                ('address', models.CharField(max_length=99999, null=True)),
                ('longitude', models.FloatField(null=True)),
                ('latitude', models.FloatField(null=True)),
                ('google_map_url', models.URLField(null=True)),
                ('udpate_datetime', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
