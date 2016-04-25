from django.test import TestCase
from django.shortcuts import render_to_response

# Create your tests here.
def getPage():
   return render_to_response('test.html')