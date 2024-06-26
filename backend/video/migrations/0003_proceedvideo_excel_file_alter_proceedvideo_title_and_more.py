# Generated by Django 5.0.6 on 2024-05-26 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0002_proceedvideo_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='proceedvideo',
            name='excel_file',
            field=models.FileField(blank=True, upload_to='excels/'),
        ),
        migrations.AlterField(
            model_name='proceedvideo',
            name='title',
            field=models.CharField(default='Processed', max_length=100),
        ),
        migrations.AlterField(
            model_name='proceedvideo',
            name='version',
            field=models.IntegerField(verbose_name='Версия нейросети'),
        ),
    ]
