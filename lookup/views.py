# import requests
# from django.shortcuts import render
from django.http import HttpResponse
# from views import goToGoogleTop
from googleapiclient.discovery import build
import pprint
import json

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

# from .models import Source

# returns all sources in database
# def db(request):
#     sources = Source()
#     sources.save()
#     sources = Source.objects.all()

#     return render(request, 'db.html', {'sources': sources})

# JS guys need a get request
# def getSource(request):
#     newSource = Source()
#     newSource.name = "test"
#     jsonData = {
#         name:
#     }
#     newSource.save()
#     HttpResponse(json.dumps(jsonData), content_type='application/json')

#logic to check and see if in databse - would do a get all objects then iterate and check
#if this returns null - can't find anything - go to google, add to database

def results(request, quote):
    text = quote.replace('+', ' ')

    service = build("customsearch", "v1", developerKey="AIzaSyABOiui8c_-sFGJSSXCk6tbBThZT2NI4Pc")
    res = service.cse().list(q = text, cx='006173695502366383915:cqpxathvhhm',).execute()
    # pprint.pprint(res)
    # print type(res)
    first = res["items"][0]
    # print first
    if first["pagemap"]["metatags"][0]: meta = first["pagemap"]["metatags"][0]
    pageinfo = {
      'quote':text, 'title': first["title"], 'url': first["link"]
      # 'name': first["pagemap"]["metatags"][0]["og:site_name"]
    }
    if "og:site_name" in meta.keys():
      pageinfo["name"] = meta["og:site_name"]
    pageinfo = json.dumps(pageinfo)
    print type(pageinfo)
    # return pageinfo
    #create source out of google response and add to cache

    return HttpResponse(pageinfo, content_type='application/json')


#     newSource = Source()
#     newSource.url = results["url"]
#     newSource.title = results["title"]
#     newSource.author = results["author"]
#     newSource.name = results["name"]
#     newSource.date = results["date"]

#     newSource.save()


    # get all sources

    # iterate through sources

    # if matching source found, returns

    # else, go to google and look up source for text
    #      create new Source() object and save() to database

    # return source


# def goToGoogleFirst(text):


