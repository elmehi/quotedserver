# encoding=utf8  
# import requests
# from django.shortcuts import render
from django.http import HttpResponse
from googleapiclient.discovery import build
from .models import Source, Request, User
import json
from datetime import date, timedelta
from django.utils.dateparse import parse_datetime
import urllib
import base64
import embedly

def userFromRequest(request):
    b64authorization = request.META['HTTP_AUTHORIZATION']
    username = str(b64authorization.decode('base64')).split(':')[0]
    print b64authorization.decode('base64')
    print username
    
    return User.objects.get(username=username)
    
def getTrustedSources(request):
    user = userFromRequest(request)
    return HttpResponse(json.dumps(user.trusted_sources), content_type='application/json')
    
def getUntrustedSources(request):
    user = userFromRequest(request)
    return HttpResponse(json.dumps(user.untrusted_sources), content_type='application/json')

def addTrustedSource(request, trusted):
    trusted = str(trusted.decode('base64'))
    user = userFromRequest(request)
    
    user.trusted_sources.append(trusted)
    user.save()
    
    return HttpResponse(json.dumps(user.trusted_sources), content_type='application/json')

def toggleTrustedSource(request, trusted):
    print "TRUSTED TOGGLE"
    print trusted
    trusted = str(trusted.decode('base64'))
    print trusted
    user = userFromRequest(request)
    
    if trusted in user.trusted_sources:
        user.trusted_sources.remove(trusted)
    else:
        user.trusted_sources.append(trusted)
        
    user.save()
    
    return HttpResponse(json.dumps(user.trusted_sources), content_type='application/json')

def removeTrustedSource(request, trusted):
    trusted = str(trusted.decode('base64'))
    user = userFromRequest(request)
    
    if trusted in user.trusted_sources:
        user.trusted_sources.remove(trusted)
    
    user.save()
    
    return HttpResponse(json.dumps(user.trusted_sources), content_type='application/json')

def addUntrustedSource(request, untrusted):
    untrusted = str(untrusted.decode('base64'))
    user = userFromRequest(request)
    
    user.untrusted_sources.append(untrusted)
    user.save()
    
    return HttpResponse(json.dumps(user.untrusted_sources), content_type='application/json')

def toggleUntrustedSource(request, untrusted):
    untrusted = str(untrusted.decode('base64'))
    user = userFromRequest(request)
    
    if untrusted in user.untrusted_sources:
        user.untrusted_sources.remove(untrusted)
    else:
        user.untrusted_sources.append(untrusted)
    
    user.save()
    
    return HttpResponse(json.dumps(user.untrusted_sources), content_type='application/json')

def removeUntrustedSource(request, untrusted):
    untrusted = str(untrusted.decode('base64'))
    user = userFromRequest(request)
    
    if untrusted in user.untrusted_sources:
        user.untrusted_sources.remove(untrusted)
    
    user.save()
    
    return HttpResponse(json.dumps(user.untrusted_sources), content_type='application/json')

def getHighlightingState(request):
    u = userFromRequest(request)
    return HttpResponse(str(u.highlighting_state), content_type='application/text')

def setHighlightingState(request, state):
    u = userFromRequest(request)
    u.highlighting_state = int(state)
    u.save()
    return HttpResponse(str(u.highlighting_state), content_type='application/text')

def getHistory(request):
    user = userFromRequest(request)
    r = Request.objects.filter(user=user)
    reqs = [{'url': req.request_source.source_url, 'date': str(req.request_date)} for req in list(r)]
    print reqs

    return HttpResponse(json.dumps(reqs), content_type='application/json')

def getValidDomains(request):
    user = userFromRequest(request)
    
    return HttpResponse(json.dumps(user.domains), content_type='application/text')

def toggleDomain(request, d):
    domain = str(d.decode('base64'))
    user = userFromRequest(request)
    
    if domain in user.domains:
        user.domains.remove(domain)
    else:
        user.domains.append(domain)
        
    user.save()

    return HttpResponse(json.dumps(user.domains), content_type='application/text')

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
    quote_text = str(quote.decode('base64'))

    #check if source in db, if so pull from db
    if Source.objects.filter(source_quote = quote_text).exists():
        s = Source.objects.get(source_quote = quote_text)

        #create request and put in db
        newRequest = Request(user=userFromRequest(request), request_date=date.today(), request_source=s)
        newRequest.save()

        pageinfo = {
            'quote':                s.source_quote, 
            'url':                  s.source_url, 
            'title':                s.source_title, 
            'name':                 s.source_name, 
            'date':                 s.source_date.strftime('%c'),
            'other_article_urls':   s.other_article_urls,
            'other_article_titles': s.other_article_titles,
            'cached':               'y'
        }
        
        pageinfo = json.dumps(pageinfo)
        
        return HttpResponse(pageinfo, content_type='application/json')

    #if not cached initiate API request
    else:
        # print "not from db"
        b64URL = request.META['RequestOriginURL']
        print b64URL
        URL = b64URL.decode('base64')
        print URL
        
        metadata = None
        if Metadata.objects.filter(url = URL).exists():
            metadata = Metadata.objects.get(url = URL)
        else:
            client = Embedly('6b216564e304429090c3f15fccde1b3e')
            print client
            embedly_response = client.extract(URL)
            
            print embedly_response
            
            keyword_list = [k['name'] for k in embedly_response['keywords']]
            entity_list = [e['name'] for e in embedly_response['entities']]
            
            print keyword_list
            print entity_list
            
            metadata = Metadata(url = URL, keywords = keyword_list, entities = entity_list)
            metadata.save()
        
        return googleTop(quote_text, userFromRequest(request))



# by josh
def googleFirst(text, u):
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
                                    currdate = (parse_datetime(meta[0][key])).date()
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
                                    currdate = (parse_datetime(article[0][key])).date()
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

    # TODO - Also return top hits
    pageinfo = {
                'quote':    text, 
                'title':    first["title"], 
                'url':      first["link"], 
                'source':   ' ', 
                'date':     mindate.strftime('%c'),
                'cached':   'n'
                }

    #create source object and put in db
    newSource = Source(source_quote=text, 
                        source_url=first["link"], 
                        source_title=first["title"], 
                        source_name=' ', 
                        source_date=mindate)
    newSource.save()

    #create request and put in db
    newRequest = Request(user=u, request_date=date.today(), request_source=newSource)
    newRequest.save()

    pageinfo = json.dumps(pageinfo)
    return HttpResponse(pageinfo, content_type='application/json')


# by meir
def googleTop(quote_text, u):
    service = build("customsearch", "v1", developerKey="AIzaSyABOiui8c_-sFGJSSXCk6tbBThZT2NI4Pc")

    site_types=["newsarticle", "webpage", "blogposting", "article"]

    try:
        res = service.cse().list(q = quote_text, cx='006173695502366383915:cqpxathvhhm', exactTerms=quote_text).execute()
        tot = res['queries']['request'][0]['totalResults']
        
        if int(tot) == 0:
            print "NO EXACT MATCHES FOUND - RELAXING EXACT TERMS"
            res = service.cse().list(q = quote_text, cx='006173695502366383915:cqpxathvhhm').execute()
        
        first = res["items"][0]
        pagemap = first['pagemap']
        date_published_est = date.today()
        source_name = ' '
        
        if pagemap["metatags"][0]:
            meta = pagemap["metatags"][0]
            if "og:site_name" in meta.keys(): 
                source_name = meta["og:site_name"]
                
        for type in site_types:
            if type in pagemap:
                site_type_data = pagemap[type][0]
                if "datepublished" in site_type_data:
                    # Attempt to parse the date string - break only if successful
                    date_published_est = parse_datetime(site_type_data["datepublished"])
                    if date_published_est == None:
                        print site_type_data["datepublished"]
                        date_published_est = date.today()
                        continue
                    break

        # This creates an array of tuples containing (article_title, url) for each source
        other_urls = [item['link'] for item in res['items'][1:max(1, len(res['items']))]]
        other_titles = [item['title'] for item in res['items'][1:max(1, len(res['items']))]]
        print "length = ", len(other_titles), len(other_urls)
        
        pageinfo = {
                    'quote':                quote_text, 
                    'url':                  first["link"], 
                    'title':                first["title"], 
                    'name':                 source_name, 
                    'date':                 date_published_est.strftime('%c'),
                    'other_article_urls':   other_urls,
                    'other_article_titles': other_titles,
                    'cached':               'n'
                    }
        
        newSource = Source(source_quote=            pageinfo['quote'], 
                            source_url=             pageinfo['url'], 
                            source_title=           pageinfo["title"], 
                            source_name=            pageinfo['name'], 
                            source_date=            date_published_est.date(),
                            other_article_urls=     pageinfo['other_article_urls'],
                            other_article_titles=   pageinfo['other_article_titles']
                            )
        newSource.save()
        newRequest = Request(user=u, request_date=date_published_est, request_source=newSource)
        newRequest.save()

        pageinfo_text = json.dumps(pageinfo)
        
        return HttpResponse(pageinfo_text, content_type='application/json')
    except Exception as e:
        # http://stackoverflow.com/questions/9823936/python-how-do-i-know-what-type-of-exception-occured
        print str(e)
        
        print "FAIL"
        print e
        return HttpResponse(str(e))
