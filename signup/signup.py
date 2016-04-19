from django.http import HttpResponse
from ..lookup.models import User

def sign_up_user(request):
    print request.META
    print request.META['Authorization']
    
    return HttpResponse('pageinfo', content_type='application/text')
