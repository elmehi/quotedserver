def authenticate(request):
    print request.META
    print request.META['Authorization']
    
    return HttpResponse('pageinfo', content_type='application/text')
