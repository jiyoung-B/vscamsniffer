from django.shortcuts import render
import speech_recognition as sr
from pynput import keyboard 

def index(request):
    return render(request, 'index.html')




