# import requests
# from django.shortcuts import render
from django.http import HttpResponse
# from views import goToGoogleTop
from googleapiclient.discovery import build
from .models import Source
import pprint
import json
import urllib2

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

    # if Source.objects.filter(source_quote = text).exists():
    #     s = Source.objects.filter(source_quote = text)
    #     pageinfo = {
    #         'quote':s.source_quote, 'url':s.source_url, 'title':s.source_title, 'name':s.source_name
    #     }
    #     pageinfo = json.dumps(pageinfo)
    #     return HttpResponse(pageinfo, content_type='application/json')
    # else:

    service = build("customsearch", "v1", developerKey="AIzaSyABOiui8c_-sFGJSSXCk6tbBThZT2NI4Pc")

    stypes=["newsarticle", "webpage", "blogposting"]

    try:
        res = service.cse().list(q = text, cx='006173695502366383915:cqpxathvhhm',).execute()
        first = res["items"][0]
        pageinfo = {'quote':text, 'url': first["link"], 'title': first["title"], 'source': ' ', 'date': ' '}
        if first["pagemap"]["metatags"][0]: 
            meta = first["pagemap"]["metatags"][0]
            if "og:site_name" in meta.keys(): pageinfo["source"] = meta["og:site_name"]
        # else: pageinfo["source"] = ''
        for t in stypes:
            if first["pagemap"][t][0]:
                print t
                stype = first["pagemap"][t][0]
                if "datepublished" in stype.keys(): 
                    pageinfo["date"] = stype["datepublished"]
                    print stype["datepublished"]
                # else: pageinfo["date"] = ''
        pprint(pageinfo)


        # newSource = Source(source_quote=pageinfo['quote'],source_url=pageinfo['url'],source_title=pageinfo['title'],source_name=pageinfo['name'])
        # newSource.save()
        # quote_text = pageinfo['domain']


        pageinfo = json.dumps(pageinfo)
        pprint(pageinfo)
        return HttpResponse(pageinfo, content_type='application/json')
    except Exception as e:
        # print str(e)
        return HttpResponse(str(e))
        # JSON = '{"url": "http://www.theatlantic.com/entertainment/archive/2016/03/directors-without-borders/475122/", "title": "Directors Without Borders", "source": "The Atlantic", "date": "January 16, 2016 1:30 EST", "quote":"' + text + '"}'
        # return HttpResponse(JSON, content_type='application/json')

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
