# Generated by Django 3.1.5 on 2021-02-09 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20210208_1441'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicalmodel',
            name='date1',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='medicalmodel',
            name='date2',
            field=models.DateField(null=True),
        ),
    ]
