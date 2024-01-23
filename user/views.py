from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.forms.utils import ValidationError
from django.core.validators import EmailValidator
from django.db.models import Max
from django.db import models 
from django import forms
from django.http import HttpResponseServerError
import time
import math
from django.core.validators import validate_email
from django.db.models import Avg, Count
from django.forms.models import inlineformset_factory
from django.urls import reverse_lazy
from .add import LearnerSignUpForm,AdminSignUpForm,Infoupdateform,Profileupdateform,Question_Form,AnswerFormSet,OTPVerificationForm
from django.views.generic.edit import CreateView,DeleteView,UpdateView
from user.models import Learner, Usercutsom , profile,Course,Quiz,Question,Answer,User_Answer,UserQuizProgress
from django.contrib.auth import login,authenticate,get_user_model,logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import auth
from django import template
from django.contrib import messages
from django.shortcuts import render
from django.core.management import call_command
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from functools import wraps
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.http import HttpResponse
from django.urls import reverse
from django.forms import modelformset_factory
from django.db import IntegrityError
from django.http import Http404
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from .utils import generate_token
from django.core.mail import EmailMessage,get_connection
from smtplib import SMTPRecipientsRefused
from django.conf import settings
import logging
import random
from validate_email_address import validate_email
import dns.resolver
import threading
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from datetime import timedelta,datetime
from django.utils import timezone
User = get_user_model()



def has_valid_mx_records(email):
    try:
        domain = email.split('@')[1]
        answers = dns.resolver.query(domain, 'MX')
        return len(answers) > 0
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers) as e:
        print(f"Error checking MX records: {e}")
        return False
    
def send_email(user,request):
    current_site = get_current_site(request)
    email_subject = 'Activate Your Account to log in'
    email_body = render_to_string('user/active.html',{
        'user':user,
        'domain':current_site,
        'uid':urlsafe_base64_encode(force_bytes(user.pk)),
        'token':generate_token.make_token(user)

    })
    
    
   
    #email = EmailMessage(subject=email_subject, body=email_body,to=[user.email])
    
    
   
    email = EmailMessage(subject=email_subject, body=email_body, to=[user.email])
    email.send()
   
    
    
    
    
    
    
    
    
    
    
def active_user(request,uidb64,token):
    try:
        uid=force_str(urlsafe_base64_decode(uidb64))
        user= Usercutsom.objects.get(pk=uid)
    except Exception as e:
        user=None
    if user and generate_token.check_token(user,token):
           
            user.email_verified=True
            user.save()
            messages.add_message(request,messages.SUCCESS,'Email verified')
            return redirect(reverse('login'))
    return render(request,'user/fail.html',{"user":user})

def send_otp(user):
        
        otp = str(random.randint(100000, 999999))
        user.otp_secret = otp
        user.otp_created_at = timezone.now()
       

        # Send OTP via email
        subject = 'Your One-Time Password'
        message = f'Your OTP for login is: {otp}'
        from_email = 'captainluffy7890@gmail.com'
        to_email = user.email

        send_mail(subject, message, from_email, [to_email])

        
'''
def trial(request):
    call_command('dbbackup')
    return HttpResponse('db created')
'''

class LearnerSignUpView(CreateView):
    model = Usercutsom
    form_class = LearnerSignUpForm
    template_name = 'user/register.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'learner'
        return super().get_context_data(**kwargs)

 
    def form_valid(self,form):
       
        user = form.save()
        send_email(user,self.request)
       
        
        messages.success(self.request, 'Activation email senting.')
        try:
                    profile_instance = profile.objects.get(user=user)
        except profile.DoesNotExist:
                    # If a profile doesn't exist, create a new one
                    profile_instance = profile(user=user)
                    profile_instance.save()
                
        except IntegrityError:
                    # Handle the case where there is a unique constraint violation
                    messages.error(self.request, "A profile already exists for this user.")
              
        if not user.email_verified:
            threading.Timer(60, delete_unverified_user, args=[user.id]).start()
            messages.warning(self.request, 'User will be deleted if email is not verified.')
            return redirect('register')
        return redirect('login')
    

def delete_unverified_user(user_id):
            try:
                user = Usercutsom.objects.get(pk=user_id, email_verified=False)
                user.delete()
                print(f"User {user_id} deleted successfully.")
            except Usercutsom.DoesNotExist:
                print(f"User {user_id} doesn't exist or is already verified.")
            except Exception as e:
                print(f"An error occurred while deleting user {user_id}: {e}")     


 


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # OTP authentication is not performed here

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_learner and user.email_verified:
                # Generate and send OTP via email
                send_otp(user)
                # Redirect to OTP entry page
                return render(request, 'user/otp_send.html', {'user_id': user.id,'username': username, 'password': password})
            elif user.is_lectuer:
                login(request, user) 
                return redirect('admin_dashboard')
            else:
                messages.error(request, "Invalid user role.")
        else:
            messages.error(request, "Invalid credentials.")

    return render(request, 'user/login.html')


def verify_otp(request):
    if request.method == 'POST':
        user_id = request.POST['user_id']
        entered_otp = request.POST['otp']
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password, otp=entered_otp)
        if user is not None:
            # Save the OTP to the database only when the user enters it
              # Mark OTP as used
            user.save()

            # Authenticate the user with OTP
            login(request, user)
            return redirect('user_dashboard')
        else:
            messages.error(request, 'Invalid OTP or OTP has expired.')
            return redirect('login')

    return redirect('login')


@login_required
def logoutView(request):
    if request.user.is_authenticated:
        user = Usercutsom.objects.get(id=request.user.id)
        user.otp_secret = None
        user.save()
    logout(request)
    return redirect('1learn1cert-home')

def is_admin(user):
    return user.is_authenticated and user.is_lectuer
def is_user(user):
    return user.is_authenticated 

def user_passes_test(test_func):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            else:
                # Redirect or handle unauthorized access
                return redirect('unauthorized_access')  # Adjust the redirect URL as needed
        return _wrapped_view
    return decorator

@user_passes_test(is_admin)
def admin_dashboard(request):
    return render(request, 'dashboard/admin_dash.html')

@user_passes_test(is_user)
def user_dashboard(request):
    return render(request, 'user_dashboard/user.html')

@method_decorator(user_passes_test(is_admin), name='dispatch')
class AdminLeaner(CreateView):
    model = User
    form_class = LearnerSignUpForm
    template_name = 'dashboard/learner_add.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'learner'
        return super().get_context_data(**kwargs)

    def form_valid(self,form):
        user = form.save()
        messages.success(self.request,'ILearner was added successful')

        return redirect('addlearner')
    
class AdminSignUpView(CreateView):
    model = User
    form_class = AdminSignUpForm
    template_name = 'dashboard/admin_add.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'instructor'
        return super().get_context_data(**kwargs)

    def form_valid(self,form):
        user = form.save()
        messages.success(self.request,'Instructor was added successful')

        return redirect('addadmin')
    
class AdminRegisterView(CreateView):
    model = User
    form_class = AdminSignUpForm
    template_name = 'user/admin_add.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'instructor'
        return super().get_context_data(**kwargs)

    def form_valid(self,form):
        user = form.save()
        messages.success(self.request,'Instructor was added successful')

        return redirect('addadmin')
    
class ListUserView(LoginRequiredMixin, ListView):
    model = Usercutsom
    template_name = 'dashboard/user_list.html'
    context_object_name = 'users'
    paginated_by = 10


    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Usercutsom.objects.filter(
                Q(username__icontains=query) | Q(email__icontains=query)
            ).order_by('-id')
        else:
            return Usercutsom.objects.order_by('-id')
    
class ADeleteuser(SuccessMessageMixin, DeleteView):
    model = Usercutsom
    template_name = 'dashboard/delete_user.html'
    success_url = reverse_lazy('alluser')
    success_message = "User Was Deleted Successfully"
    
    def test_func(self):
        # Check if the user has the necessary permissions to delete (e.g., admin)
        return self.request.user.is_authenticated and self.request.user.is_admin

    def handle_no_permission(self):
        # Redirect to a custom page or show a message when the user doesn't have permission
        messages.error(self.request, "You don't have permission to delete this user.")
        return super().handle_no_permission()
    

def admin_profile(request):
    current_user = request.user

    try:
        user_profile = profile.objects.get(user=current_user)
        print(f"User Profile Image URL: {user_profile.image.url}")
    except profile.DoesNotExist:
        user_profile = None
    
    return render(request, 'dashboard/admin_profile.html')

 
def learner_profile(request):
    current_user = request.user
    all_quiz_results = User_Answer.objects.filter(user=request.user)

    # Use Python to filter out duplicate quizzes
    unique_quizzes = set(result.question.quiz for result in all_quiz_results)

    # Use Python to filter out duplicate quizzes
    

    try:
        user_profile = profile.objects.get(user=current_user)
        print(f"User Profile Image URL: {user_profile.image.url}")
    except profile.DoesNotExist:
        user_profile = None
    
    return render(request, 'user_dashboard/learner_profile.html', {
        'unique_quizzes': unique_quizzes,
        'all_quiz_results': all_quiz_results,  # Pass all_quiz_results to the template
        'user_profile': user_profile,
    })
def profile_update(request):
    if request.method=='POST' :
        u_form=Infoupdateform(request.POST,instance=request.user)
        p_form=Profileupdateform(request.POST,request.FILES,instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request,f'Your profile is updated')
            return redirect('admin_profile')
    else:
        u_form=Infoupdateform(instance=request.user)
        p_form=Profileupdateform(instance=request.user.profile)
    context ={
        'u_form': u_form,
        'p_form' : p_form
    }
    return render(request, 'dashboard/admin_profile_edit.html',context)


def course(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        color = request.POST.get('color', '')  # Fix: use 'color' instead of 'name'

        if name and color:  # Check if both name and color are provided
            course_instance = Course(name=name, color=color)
            course_instance.save()
            messages.success(request, 'Course was registered successfully')
        else:
            messages.error(request, 'Please provide both name and color for the course')

        return redirect('course')

    # This part should be at the same indentation level as the first if statement
    courses = Course.objects.all()
    return render(request, 'dashboard/course.html', {'courses': courses})
   

class QuizCreateView(CreateView):
    model = Quiz
    fields = ('name', 'course', 'level')
    template_name = 'dashboard/create_quiz.html'

    def form_valid(self, form):
        quiz = form.save(commit=False)
        quiz.owner = self.request.user
        quiz.save()
        
        messages.success(self.request, 'Quiz created. Go ahead and add questions.')
        
        return redirect('create_quiz')
    
def choose_quiz(request):

    quizzes = Quiz.objects.filter(owner=request.user)
    return render(request, 'dashboard/choose_quiz.html', {'quizzes': quizzes})

def delete_quiz(request, quiz_pk):
    quiz = get_object_or_404(Quiz, pk=quiz_pk)

    if request.method == 'POST':
        quiz.delete()
        messages.success(request, 'Quiz deleted successfully.')
        return redirect('choose_quiz')

    return render(request, 'dashboard/delete_quiz.html', {'quiz': quiz})

def create_question(request, quiz_pk):
    quiz = get_object_or_404(Quiz, pk=quiz_pk, owner=request.user)

    if request.method == 'POST':
        form = Question_Form(request.POST)
        formset = AnswerFormSet(request.POST, instance=Question())
        if form.is_valid() and formset.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            formset.instance = question
            formset.save()
            messages.success(request, 'Question and answers added successfully.')
            return redirect('add_question', quiz_pk=quiz.pk)
    else:
        form = Question_Form()
        formset = AnswerFormSet(instance=Question())

    return render(request, 'dashboard/add_question.html', {'quiz': quiz, 'form': form, 'formset': formset})




   

def delete_question(request, quiz_pk, question_pk):
    quiz = get_object_or_404(Quiz, pk=quiz_pk, owner=request.user)
    question = get_object_or_404(Question, pk=question_pk, quiz=quiz)

    if request.method == 'POST':
        # Redirect to the confirmation page
        return redirect('delete_question_confirm', quiz_pk=quiz.pk, question_pk=question.pk)

    return render(request, 'dashboard/add_question.html', {'quiz': quiz, 'question': question})

def delete_question_confirm(request, quiz_pk, question_pk):
    quiz = get_object_or_404(Quiz, pk=quiz_pk, owner=request.user)
    question = get_object_or_404(Question, pk=question_pk, quiz=quiz)

    if request.method == 'POST':
        # Delete the question and its related answers
        question.delete()
        messages.success(request, 'Question and answers deleted successfully.')
        return redirect('add_question', quiz_pk=quiz.pk)

    return render(request, 'dashboard/delete_question_confirm.html', {'quiz': quiz, 'question': question})


def edit_question1(request, quiz_pk, question_pk):
    quiz = get_object_or_404(Quiz, pk=quiz_pk, owner=request.user)
    question = get_object_or_404(Question, pk=question_pk, quiz=quiz)

    if request.method == 'POST':
        form = Question_Form(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question updated successfully.')
            return redirect('add_question', quiz_pk=quiz.pk)
    else:
        form = Question_Form(instance=question)

    return render(request, 'dashboard/edit_question.html', {'quiz': quiz, 'question': question, 'form': form})


def edit_answer(request, quiz_pk, question_pk, answer_pk):
    quiz = get_object_or_404(Quiz, pk=quiz_pk, owner=request.user)
    question = get_object_or_404(Question, pk=question_pk, quiz=quiz)
    answer = get_object_or_404(Answer, pk=answer_pk, question=question)

    if request.method == 'POST':
        form =Question_Form(data=request.POST, instance=answer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Answer updated successfully.')
            return redirect('add_question', quiz_pk=quiz.pk)
    else:
        form = Question_Form(instance=answer)

    return render(request, 'dashboard/edit_answer.html', {'quiz': quiz, 'question': question, 'form': form})

def edit_question(request, quiz_pk, question_pk):
    quiz = get_object_or_404(Quiz, pk=quiz_pk, owner=request.user)
    question = get_object_or_404(Question, pk=question_pk, quiz=quiz)

    if request.method == 'POST':
        form = Question_Form(data=request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question updated successfully.')
            return redirect('add_question', quiz_pk=quiz.pk)
    else:
        form = Question_Form(instance=question)

    return render(request, 'dashboard/edit_question.html', {'quiz': quiz, 'form': form, 'question': question})


def home_learner(request):
    learner = User.objects.filter(is_learner=True).count()
   
    course = Course.objects.all().count()
    users = User.objects.all().count()

    context = {'learner':learner, 'course':course, 'users':users}

    return render(request, 'dashboard/learner_home.html', context)


def quiz_list(request):
    courses = Course.objects.all()
    quizzes = Quiz.objects.all()
    level_filter = request.GET.get('level', None)
    if level_filter:
        quizzes = quizzes.filter(level=level_filter)
    return render(request, 'user_dashboard/quiz_list.html', {'courses': courses, 'quizzes': quizzes,'selected_level': level_filter})

   

def quiz_start(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Convert queryset to a list before shuffling
    questions = list(quiz.questions.all())
    random.shuffle(questions)

    # Store the shuffled list of questions in the session
    request.session['shuffled_questions'] = [question.id for question in questions]
    request.session['quiz_start_time'] = time.time()
    # Remove previous answers for this quiz
    User_Answer.objects.filter(user=request.user, question__quiz=quiz).delete()
    request.session['quiz_time_limit'] = 180  # 30 minutes
    request.session['remaining_time'] = request.session['quiz_time_limit']

    return render(request, 'user_dashboard/quiz_start.html', {'quiz': quiz, 'questions': questions})\


def question_detail(request, quiz_id, question_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    question = get_object_or_404(Question, id=question_id)
    answers = question.answers.all()

    shuffled_question_ids = request.session.get('shuffled_questions', [])

    if not shuffled_question_ids:
        # If the shuffled list of questions is not found in the session, redirect to an error page
        return HttpResponseServerError("Shuffled list of questions not found in the session.")
    
    quiz_start_time = request.session.get('quiz_start_time', 0)
    quiz_time_limit = request.session.get('quiz_time_limit', 0)
    current_time = time.time()
    if current_time - quiz_start_time > quiz_time_limit:
        # Time limit reached, redirect to quiz results
        return redirect('quiz_results', quiz_id=quiz.id)

    remaining_time = max(0, quiz_start_time + quiz_time_limit - current_time)
    request.session['remaining_time'] = remaining_time
    remaining_minutes = math.floor(remaining_time / 60)
    remaining_seconds = math.floor(remaining_time % 60)
    if remaining_time <= 0:
        # Time limit reached, redirect to quiz results
        return redirect('quiz_results', quiz_id=quiz.id)
    
    if remaining_minutes == 0 and remaining_seconds == 0:
        # Time limit reached, redirect to quiz results
        return redirect('quiz_results', quiz_id=quiz.id)
    if request.method == 'POST':
        chosen_answer_id = request.POST.get('chosen_answer')
        chosen_answer = get_object_or_404(Answer, id=chosen_answer_id)

        # Save the user's answer
        User_Answer.objects.create(user=request.user, question=question, chosen_answer=chosen_answer)

        # Get the index of the current question in the shuffled list
        current_question_index = shuffled_question_ids.index(question.id)

        # Get the next question by advancing to the next index
        next_question_index = current_question_index + 1
        next_question_id = shuffled_question_ids[next_question_index] if next_question_index < len(shuffled_question_ids) else None
        #next_question_id = shuffled_question_ids.pop(0) if shuffled_question_ids else None

       
       
        if next_question_id:
            request.session['remaining_time'] = remaining_time
            return redirect('question_detail', quiz_id=quiz.id, question_id=next_question_id)
            #return redirect('question_detail', quiz_id=quiz.id, question_id=next_question_id)
        else:
            # Calculate and show results
            return redirect('quiz_results', quiz_id=quiz.id)
        

    return render(request, 'user_dashboard/question_detail.html', {'quiz': quiz, 'question': question, 'answers': answers,'remaining_minutes': remaining_minutes, 'remaining_seconds': remaining_seconds})


def quiz_results(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()

    # Retrieve user's answers for the quiz
    user_answers = User_Answer.objects.filter(user=request.user, question__quiz=quiz)

    # Calculate the user's score and total mark
    total_mark = len(questions)  # Each question is worth 1 mark
    user_score = 0
    incorrect_answers = []

    for question in questions:
        user_answer = user_answers.filter(question=question).first()

        # Check if the user's answer is correct
        if user_answer and user_answer.chosen_answer.is_correct:
            user_score += 1

        # Add incorrect answer details to the list
        elif user_answer:
            incorrect_answers.append({
                'question': question,
                'user_answer': user_answer.chosen_answer,
                'correct_answer': question.answers.filter(is_correct=True).first(),
            })

    # Calculate the user's mark after checking correctness
    if total_mark > 0:
        user_mark = (user_score / total_mark) * 100
    else:
        user_mark = 0

    # Save the updated user marks in the UserAnswer model
    for user_answer in user_answers:
        user_answer.user_mark = user_mark
        user_answer.save()

    # Calculate the percentage score
    if total_mark > 0:
        percentage_score = (user_score / total_mark) * 100
    else:
        percentage_score = 0

    return render(request, 'user_dashboard/quiz_results.html', {
        'quiz': quiz,
        'total_mark': total_mark,
        'user_score': user_score,
        'percentage_score': percentage_score,
        'user_mark': user_mark,
        'incorrect_answers': incorrect_answers,
    })
def retake_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Delete the user's previous answers for this quiz
    User_Answer.objects.filter(user=request.user, question__quiz=quiz).delete()

    # Redirect to the first question of the quiz
    first_question = quiz.questions.first()
    return redirect('question_detail', quiz_id=quiz.id, question_id=first_question.id)