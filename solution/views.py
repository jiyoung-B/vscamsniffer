from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User

# Create your views here.
def solutions(request,user_id=None):
    user = get_object_or_404(User, id=user_id)
    if request.user.is_authenticated and request.user.id == user.id:
        user_id = request.user.id
        return render(request,"Solution.html",{"user_id":user_id})
    else:
        return HttpResponse("페이지에 대한 접근 권한이 없습니다.")
