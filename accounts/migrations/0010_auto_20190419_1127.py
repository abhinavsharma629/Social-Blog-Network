# Generated by Django 2.1.5 on 2019-04-19 05:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_auto_20190419_1122'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='postVid',
            field=models.FileField(blank=True, null=True, upload_to='account'),
        ),
        migrations.AlterField(
            model_name='post',
            name='postImg',
            field=models.ImageField(blank=True, null=True, upload_to='account'),
        ),
    ]
