from django.http import HttpResponse
from ..lookup.models import User

def sign_up_user(request):
    print request.META
    print request.META['Authorization']
    if User.objects.filter(username)
