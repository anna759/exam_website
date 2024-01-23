from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.html import escape, mark_safe
from django.contrib.auth import get_user_model
from embed_video.fields import EmbedVideoField
from django.utils import timezone
from django.db.models.signals import pre_delete
from django.dispatch import receiver

class Usercutsom(AbstractUser):
    
    is_learner = models.BooleanField(default=False)
   
    is_lectuer = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    otp_secret = models.CharField(max_length=16, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

class profile(models.Model):
    user =models.OneToOneField(Usercutsom,on_delete=models.CASCADE)
    image = models.ImageField(default='profile_pics/default.png',upload_to='profile_pics')
    




class Learner(models.Model):
   
    user = models.OneToOneField(Usercutsom, on_delete=models.CASCADE, primary_key=True)
    def get_unanswered_questions(self, quiz):
        answered_questions = self.quiz_answers \
            .filter(answer__question__quiz=quiz) \
            .values_list('answer__question__pk', flat=True)
        questions = quiz.questions.exclude(pk__in=answered_questions).order_by('text')
        return questions

    def __str__(self):
        return self.user.username
    



    def __str__(self):
        return f'{self.user.username} profile - {self.image.url}'

class Instructor(models.Model):
    user = models.OneToOneField(Usercutsom, on_delete=models.CASCADE)
    #interest = models.ManyToManyField(Course, related_name="more_locations")

class Course(models.Model):
    name = models.CharField(max_length=30)
    color = models.CharField(max_length=7, default='#007bff')

    def __str__(self):
        return self.name

    def get_html_badge(self):
        escaped_name = escape(self.name)
        escaped_color = escape(self.color)
        html = f'<span class="badge badge-primary" style="background-color: {escaped_color}">{escaped_name}</span>'
        return mark_safe(html)

class Quiz(models.Model):
    LEVEL_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    owner = models.ForeignKey(Usercutsom, on_delete=models.CASCADE, related_name='quizzes')
    name = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='medium')
    
    time_limit = models.IntegerField('Time Limit (seconds)', default=300)
    def __str__(self):
        return self.name

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField('Question', max_length=255)

    def __str__(self):
        return self.text

class Answer(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    text = models.CharField('Answer', max_length=255)
    is_correct = models.BooleanField('Correct answer', default=False)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'



class User_Answer(models.Model):
    user = models.ForeignKey(Usercutsom, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    chosen_answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)
    user_mark = models.DecimalField('User Mark', max_digits=5, decimal_places=2, null=True, blank=True)

class UserQuizProgress(models.Model):
    user = models.ForeignKey(Usercutsom, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    current_question_index = models.IntegerField(default=0)
   

    def __str__(self):
        return f"{self.user.username}'s progress in {self.quiz.name}"

Usercutsom._meta.get_field('groups').remote_field.related_name = 'usercutsom_groups'
Usercutsom._meta.get_field('user_permissions').remote_field.related_name = 'usercutsom_user_permissions'

