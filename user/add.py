
from django import forms

from django.contrib.auth.forms import UserCreationForm

from django.db import transaction
from user.models import Usercutsom,Learner,profile,Question,Answer
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from django.contrib import messages


class LearnerSignUpForm(UserCreationForm):

    email = forms.EmailField()
   
    
   
    class Meta(UserCreationForm.Meta):
       
        model = Usercutsom
        fields=['username','email','password1','password2']
    
    

    def __init__(self, *args, **kwargs):
            super(LearnerSignUpForm, self).__init__(*args, **kwargs)

            for fieldname in ['username','email', 'password1', 'password2']:
                self.fields[fieldname].help_text = None 
    

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_learner = True
        user.save()
        learner = Learner.objects.create(user=user)
       
        return user
    
class OTPVerificationForm(forms.Form):
    otp = forms.IntegerField(
        label='Enter OTP',
        widget=forms.TextInput(attrs={'placeholder': 'Enter your OTP'}),
    )
class AdminSignUpForm(UserCreationForm):
    email = forms.EmailField()
    class Meta(UserCreationForm.Meta):
        model = Usercutsom
        fields=['username','email','password1','password2']

    def __init__(self, *args, **kwargs):
            super(AdminSignUpForm, self).__init__(*args, **kwargs)

            for fieldname in ['username','email', 'password1', 'password2']:
                self.fields[fieldname].help_text = None
                    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_lectuer = True
        if commit:
            user.save()
        return user

class Infoupdateform(forms.ModelForm):
     email=forms.EmailField()

     class  Meta:
        model = Usercutsom
        fields =['username','email']

class Question_Form(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('text',)

class Profileupdateform(forms.ModelForm):
    class Meta:
        model =profile
        fields =['image']

AnswerFormSet = inlineformset_factory(
    Question,
    Answer,
    formset=forms.BaseInlineFormSet,
    fields=['text', 'is_correct'],
    min_num=2,
    validate_min=True,
    max_num=10,
    
    validate_max=True,
    can_delete=False  # Set to True if you want to allow deletion of answers
)

