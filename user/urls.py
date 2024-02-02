from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
   
    path('register/',views.LearnerSignUpView.as_view(),name='register'),
    path('login/',views.login_view,name='login'),
    path('logout/',views.logoutView,name='logout'),
    path('reset_password/',views.password,name='reset_password'),
    path('reset/<token>/',views.reset_confirm,name='reset'),
    
    path('admin_dashboard/',views.admin_dashboard,name='admin_dashboard'),
    path('addlearner/',views.AdminLeaner.as_view(),name='addlearner'),
    path('addadmin/',views.AdminSignUpView.as_view(),name='addadmin'),
    path('registeradmin/',views.AdminRegisterView.as_view(),name='registeradmin'),
    path('user_dashboard/',views.user_dashboard,name='user_dashboard'),
    path('alluser/',views.ListUserView.as_view(),name='alluser'),
    path('delete-user/<int:pk>/',views.ADeleteuser.as_view(), name='delete_user'),
    path('admin-profile/',views.admin_profile, name='admin_profile'),
    path('admin-profile-edit/',views.profile_update, name='admin_profile_edit'),
    path('learner-profile-edit/',views.profile_update_learner, name='learner_profile_edit'),
    path('learner-profile/',views.learner_profile, name='learner_profile'),


    path('course/',views.course,name='course'),
    path('create-quiz/',views.QuizCreateView.as_view(),name='create_quiz'),
    path('add-question/<int:quiz_pk>/', views.create_question, name='add_question'),
    path('choose-quiz/', views.choose_quiz, name='choose_quiz'),
    path('delete-quiz/<int:quiz_pk>/', views.delete_quiz, name='delete_quiz'),
    path('delete-question/<int:quiz_pk>/<int:question_pk>/', views.delete_question, name='delete_question'),
    path('delete-question-confirm/<int:quiz_pk>/<int:question_pk>/', views.delete_question_confirm, name='delete_question_confirm'),
    
    
    #path('edit-question/<int:quiz_pk>/<int:question_pk>/', views.edit_question1, name='edit_question'),
     path('edit-answer/<int:quiz_pk>/<int:question_pk>/<int:answer_pk>/',views.edit_answer, name='edit_answer'),
    path('edit-question/<int:quiz_pk>/<int:question_pk>/',views.edit_question, name='edit_question'),
    #path('accounts/signup/',views.LearnerSignUpView.as_view(), name='custom_signup'),
    ##learner
    path('quizzes/',views.quiz_list, name='quiz_list'),
    path('quizzes/<int:quiz_id>/',views.quiz_start, name='quiz_start'),
    path('quizzes/<int:quiz_id>/questions/<int:question_id>/',views.question_detail, name='question_detail'),
    path('quizzes/<int:quiz_id>/results/',views.quiz_results, name='quiz_results'),
    path('quizzes/<int:quiz_id>/retake/',views.retake_quiz, name='retake_quiz'),
    path('bookmarked-questions/',views.bookmarked_questions, name='bookmarked_questions'),
    path('delete_bookmark/<int:question_id>/',views.delete_bookmark, name='delete_bookmark'),
  
   ##resetpassword
    #path('password-reset/',auth_views.PasswordResetView.as_view(template_name='user/reset.html'),name='password_reset'),
    #path('password-reset/done/',auth_views.PasswordResetDoneView.as_view(template_name='user/password_reset_done.html'),name='password_reset_done'),
    #path('password-reset-confirm/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='user/reset_confirm.html'),name='password_reset_confirm'),
    #path('password-reset-complete/',auth_views.PasswordResetCompleteView.as_view(template_name='user/reset_complete.html'),name='password_reset_complete'),
    path('activate/<uidb64>/<token>',views.active_user,name='activate'),
     path('verify-otp/',views.verify_otp, name='verify_otp'),
    path('trial/',views.trial,name='trail')
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
