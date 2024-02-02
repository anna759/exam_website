from django.shortcuts import render

def user_dash(request):
    return render(request, 'user/user_dashboard.html')