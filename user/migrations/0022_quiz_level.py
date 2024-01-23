# Generated by Django 5.0.1 on 2024-01-23 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0021_quiz_time_limit'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='level',
            field=models.CharField(choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')], default='medium', max_length=10),
        ),
    ]
