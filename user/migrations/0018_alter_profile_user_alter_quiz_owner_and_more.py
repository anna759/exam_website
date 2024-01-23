# Generated by Django 5.0.1 on 2024-01-21 22:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0017_usercutsom_otp_created_at_usercutsom_otp_secret'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='user.usercutsom'),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quizzes', to='user.usercutsom'),
        ),
        migrations.AlterField(
            model_name='user_answer',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.usercutsom'),
        ),
    ]