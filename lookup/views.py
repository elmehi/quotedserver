# import requests
# from django.shortcuts import render
from django.http import HttpResponse
# from views import goToGoogleTop
from googleapiclient.discovery import build
from .models import Source
import json
from datetime import datetime, date, timedelta
import dateutil.parser
import urllib


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
    # return  googleFirst(text)
    return  googleTop(text)

    # if Source.objects.filter(source_quote = text).exists():
    #     s = Source.objects.filter(source_quote = text)
    #     pageinfo = {
    #         'quote':s.source_quote, 'url':s.source_url, 'title':s.source_title, 'name':s.source_name
    #     }
    #     pageinfo = json.dumps(pageinfo)
    #     return HttpResponse(pageinfo, content_type='application/json')
    # else:
    # newSource = Source()
    # newSource.url = results["url"]
    # newSource.title = results["title"]
    # newSource.author = results["author"]
    # newSource.name = results["name"]
    # newSource.date = results["date"]
    # newSource.save()
    # get all sources
    # iterate through sources
    # if matching source found, returns
    # else, go to google and look up source for text
    #      create new Source() object and save() to database
    # return source




# by josh
def googleFirst(text):
    #metatags related to dates:
    datekeys = {'article:published_time','Pubdate', 'ptime', 'utime', 'displaydate', 'dat', 'date', 'datetime', 'datePublished', 'datepublished', 'dc.date', 'og:pubdate', 'pubdate', 'datecreated', 'pud', 'pdate'}

    low = date(1970, 01, 01) # lower bound for date search
    today = date.today()
    high = low + (today - low)/2 # begin with midpoint between lower bound and today
    day = timedelta(days=1) # one-day increment
    first = {}
    mindate = today # earliest date mentioned in metatags of search results

    #old method:  service = build("customsearch", "v1", developerKey="AIzaSyDFUxKEogS82DTdGIMqOs8SmvtVAmsDvkY")
    # res = service.cse().list(q = text, cx='000898682532264933795:0fmbuakszua', lowRange = '19000101', highRange =high.strftime('%Y%m%d'),).execute()

    # binary search
    for i in range(0, 15): # temporarily limit the number of searches for each quote

        # end loop if range has been maximally narrowed
        if low >= high: break

        #get JSON of results from google with appropriate max date
        url = "https://www.googleapis.com/customsearch/v1?q=" + text + "&cx=006173695502366383915%3Acqpxathvhhm&sort=date%3Ar%3A%3A" + high.strftime('%Y%m%d') + "&key=AIzaSyDFUxKEogS82DTdGIMqOs8SmvtVAmsDvkY"
        res = json.loads((urllib.urlopen(url)).read())
        rescount = int(res["searchInformation"]["totalResults"]) #number of results

        # for debugging:
        print rescount
        print 'low: ' + str(low) + ' high: ' + str(high)

        # if upper bound date is too early, make upper bound the earliest date of a hit already encountered
        if rescount < 1:
            low = high + day
            high = low + (mindate - low)/2

        elif rescount == 1:
            first = res["items"][0]
            break

        # for multiple hits and non-maximally narrowed range, find earliest hit
        else:
            for entry in res["items"]:
                #search for date in two common locations
                if "pagemap" in entry:
                    if entry["pagemap"]["metatags"]:
                        meta = entry["pagemap"]["metatags"]
                        for key in datekeys:
                            if key in meta[0]:
                                try:
                                    currdate = (dateutil.parser.parse(meta[0][key])).date()
                                    print currdate # for debugging purposes

                                    #update earliest date & earliest hit
                                    if currdate < mindate:
                                        mindate = currdate
                                        first = entry

                                # catch error for unintelligible datestamp
                                except ValueError: print ('error at ' + key + ' in metatags, parsing ' + meta[0][key])

                    if "newsarticle" in entry["pagemap"]:
                        article = entry["pagemap"]["newsarticle"]
                        for key in datekeys:
                            if key in article[0]:
                                try:
                                    currdate = (dateutil.parser.parse(article[0][key])).date()
                                    print currdate
                                    if currdate < mindate:
                                        mindate = currdate
                                        first = entry

                                # catch error for unintelligible datestamp
                                except ValueError: print ('error at ' + key + ' in newsarticle, parsing ' + article[0][key])

                    print mindate # for debugging purposes
                else: print 'no pagemap'

            # for next search, reduce upper bound by binary method or earliest date
            mid = low + (high - low)/2
            high = mid - day if mid <= mindate else mindate - day

            #for debugging purposes:
            print mid <= mindate

    print 'earliest entry: '

    pageinfo = {'quote':text, 'title': first["title"], 'url': first["link"], 'source': ' ', 'date': str(mindate)}
    pageinfo = json.dumps(pageinfo)
    return HttpResponse(pageinfo, content_type='application/json')




# by meir
def googleTop(text):
    service = build("customsearch", "v1", developerKey="AIzaSyABOiui8c_-sFGJSSXCk6tbBThZT2NI4Pc")

    stypes=["newsarticle", "webpage", "blogposting"]

    try:
        res = service.cse().list(q = text, cx='006173695502366383915:cqpxathvhhm',).execute()
        first = res["items"][0]
        pageinfo = {'quote':text, 'url': first["link"], 'title': first["title"], 'source':' ', 'date':' '}
        if first["pagemap"]["metatags"][0]:
            meta = first["pagemap"]["metatags"][0]
            if "og:site_name" in meta.keys(): pageinfo["source"] = meta["og:site_name"]
        for t in stypes:
            if first["pagemap"][t][0]:
                print t
                stype = first["pagemap"][t][0]
                if "datepublished" in stype.keys():
                    ddate = stype["datepublished"]
                    print [int(ddate[:4]), int(ddate[5:7]), int(ddate[8:10])]
                    ddate = datetime(int(ddate[:4]), int(ddate[5:7]), int(ddate[8:10]))
                    pageinfo["date"] = ddate.strftime('%B %d %Y')
                break
        print(pageinfo)


        pageinfo = json.dumps(pageinfo)
        print(pageinfo)
        return HttpResponse(pageinfo, content_type='application/json')
    except Exception as e:
        print str(e)
        # return HttpResponse(str(e))
        JSON = '{"url": "http://www.theatlantic.com/entertainment/archive/2016/03/directors-without-borders/475122/", "title": "THIS IS AN ERROR", "source": "The Atlantic", "date": "January 16, 2016 1:30 EST", "quote":"' + text + '"}'
        return HttpResponse(JSON, content_type='application/json')
