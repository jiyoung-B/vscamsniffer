from django.urls import path
from . import views


urlpatterns = [
    path('<str:user_id>/',views.solutions,name='solutionroom'),
]