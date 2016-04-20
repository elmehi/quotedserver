# import requests
# from django.shortcuts import render
from django.http import HttpResponse
from googleapiclient.discovery import build
from .models import Source, Request, User
import json
from datetime import datetime, date, timedelta
import dateutil.parser
import urllib
import base64


# returns all sources in database
# def db(request):
#     sources = Source()
#     sources.save()
#     sources = Source.objects.all()

#     return render(request, 'db.html', {'sources': sources})

def getHistory(request):
    b64authorization = request.META['HTTP_AUTHORIZATION']
    u = b64authorization.decode('base64')

    r = Request.objects.filter(user_id=u)
    reqs = list(r)

    reqs = json.dumps(reqs)
    return HttpResponse(reqs, content_type='application/json')

def toggleDomain(request, d):
    domain = str(d.decode('base64'))
    
    b64authorization = request.META['HTTP_AUTHORIZATION']
    username = str(b64authorization.decode('base64'))
    
    user = User.objects.get(username=username)
    domains = []
    
    print('before', domains)
    
    if domain in domains:
        print 'found'
        while domain in domains:
            domains.remove(domain)
    else:
        print 'adding'
        domains.append(domain)
    user.domain_list = domains
    user.save()
        
    print('after', domains)

    return HttpResponse(str(user.domain_list), content_type='application/text')


def authenticate(request):
    print request.META
    b64authorization = request.META['HTTP_AUTHORIZATION']
    authorization = b64authorization.decode('base64')
    auths = str.split(authorization, ':')
    # print("auth", authorization)

    # return HttpResponse('Test', content_type='application/text')
    u = auths[0]
    p = auths[1]
    token = auths[2]

    if User.objects.filter(username=u).exists():
        user = User.objects.get(username=u)
        if user.password == p:
            return HttpResponse(token, content_type='application/text')
        else:
            return HttpResponse('Incorrect username or password', content_type='application/text')

    else:
        return HttpResponse('Incorrect username or password', content_type='application/text')


def signup(request):
    print request.META
    b64authorization = request.META['HTTP_AUTHORIZATION']
    authorization = b64authorization.decode('base64')
    # print("auth", authorization)
    auths = str.split(authorization, ':')

    # return HttpResponse('Test', content_type='application/text')

    u = auths[0]
    p = auths[1]
    token = auths[2]

    if User.objects.filter(username=u).exists():
        return HttpResponse(token, content_type='application/text')
    else:
        newUser = User(username=u, password=p, date_created=date.today())
        newUser.save()
        return HttpResponse(token, content_type='application/text')

def results(request, quote):
    text = urllib.unquote(quote).decode('utf8')
    print text

    #check if source in db, if so pull from db
    if Source.objects.filter(source_quote = text).exists():
        s = Source.objects.get(source_quote = text)

        #create request and put in db
        newRequest = Request(user_id=1, request_date=date.today(), request_source=s)
        newRequest.save()

        pageinfo = {
            'quote':s.source_quote, 'url':s.source_url, 'title':s.source_title, 'name':s.source_name, 'date':str(s.source_date)
        }
        pageinfo = json.dumps(pageinfo)
        # print "from db"
        return HttpResponse(pageinfo, content_type='application/json')

    #if not cached initiate API request
    else:
        # print "not from db"
        return googleTop(text)



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
        url = "https://www.googleapis.com/customsearch/v1?q=" + text + "&cx=006173695502366383915%3Acqpxathvhhm&exactTerms=" + text + "&sort=date%3Ar%3A%3A" + high.strftime('%Y%m%d') + "&key=AIzaSyABOiui8c_-sFGJSSXCk6tbBThZT2NI4Pc"
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

    #create source object and put in db
    newSource = Source(source_quote=text, source_url=first["link"], source_title=first["title"], source_name=' ', source_date=str(mindate))
    newSource.save()

    #create request and put in db
    newRequest = Request(user_id=1, request_date=date.today(), request_source=newSource)
    newRequest.save()

    pageinfo = json.dumps(pageinfo)
    return HttpResponse(pageinfo, content_type='application/json')




# by meir
def googleTop(text):
    service = build("customsearch", "v1", developerKey="AIzaSyABOiui8c_-sFGJSSXCk6tbBThZT2NI4Pc")

    stypes=["newsarticle", "webpage", "blogposting", "article"]
    ddate = date.today()
    try:
        res = service.cse().list(q = text, cx='006173695502366383915:cqpxathvhhm', exactTerms=text).execute()
        print res
        tot = res['queries']['request'][0]['totalResults']
        print tot
        print int(tot)
        
        if int(tot) == 0:
            print "NO EXACT MATCHES FOUND - RELAXING EXACT TERMS"
            res = service.cse().list(q = text, cx='006173695502366383915:cqpxathvhhm').execute()
        
        print res
        # print res
        first = res["items"][0]
        pageinfo = {'quote':text, 'url': first["link"], 'title': first["title"], 'name':' ', 'date':' '}
        if first["pagemap"]["metatags"][0]:
            meta = first["pagemap"]["metatags"][0]
            if "og:site_name" in meta.keys(): pageinfo["name"] = meta["og:site_name"]
        
        for t in stypes:
            if t in first["pagemap"].keys():
                print t + "is found"
                stype = first["pagemap"][t][0]
                if "datepublished" in stype.keys():
                    ddate = stype["datepublished"]
                    # print [int(ddate[:4]), int(ddate[5:7]), int(ddate[8:10])]
                    # ddate = datetime(int(ddate[:4]), int(ddate[5:7]), int(ddate[8:10]))
                    # pageinfo["date"] = ddate.strftime('%B %d %Y')
                    pageinfo["date"] = str(ddate)

                else:
                    print "date published not found"
                    ddate = date.today()
                    pageinfo["date"] = str(ddate)

        newSource = Source(source_quote=pageinfo['quote'], source_url=pageinfo['url'], source_title=pageinfo["title"], source_name=pageinfo['name'], source_date=pageinfo['date'])
        newSource.save()
        newRequest = Request(user_id=1, request_date=date.today(), request_source=newSource)
        newRequest.save()

        pageinfo = json.dumps(pageinfo)
        
        print "SUCCESS"
        print(pageinfo)
        print ddate
        
        return HttpResponse(pageinfo, content_type='application/json')
    except Exception as e:
        # http://stackoverflow.com/questions/9823936/python-how-do-i-know-what-type-of-exception-occured
        template = "An exception of type {0} occured. Arguments:\n{1!r}"
        message = template.format(type(e).__name__, e.args)
        print message
        print "FAIL"
        print e
        return HttpResponse(str(e))
        # JSON = '{"url": "http://www.theatlantic.com/entertainment/archive/2016/03/directors-without-borders/475122/", "title": "THIS IS AN ERROR", "source": "The Atlantic", "date": "January 16, 2016 1:30 EST", "quote":"' + text + '"}'
        # return HttpResponse(JSON, content_type='application/json')
