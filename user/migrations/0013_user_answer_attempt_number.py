# Generated by Django 5.0.1 on 2024-01-19 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0012_remove_user_answer_attempt_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_answer',
            name='attempt_number',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
