# from django.test import TestCase
from django.shortcuts import render


# Create your tests here.
def getPage(request):
   return render(request, 'tests/one.html')