# encoding=utf8  
# import requests
# from django.shortcuts import render
from django.http import HttpResponse
from googleapiclient.discovery import build
from .models import Source, Request, User, Metadata
import json
from datetime import timedelta, datetime
from dateutil.parser import parse
# from django.utils.dateparse import parse_datetime
# from django.utils import timezone
import urllib
import embedly
import pprint


DEVKEY = "AIzaSyBj-V7LxIVjkKuUTOyCp-mX7GcjXNcuUSU"

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
        newUser = User(username=u, password=p, date_created=datetime.now().replace(tzinfo=None))
        newUser.save()
        return HttpResponse(token, content_type='application/text')

def results(request, quote):
    quote_text = str(quote.decode('base64'))

    #check if source in db, if so pull from db
    if Source.objects.filter(source_quote = quote_text).exists():
        s = Source.objects.get(source_quote = quote_text)

        #create request and put in db
        newRequest = Request(user=userFromRequest(request), request_date=datetime.now().replace(tzinfo=None), request_source=s)
        newRequest.save()

        pageinfo = {
            'quote':                s.source_quote, 
            'url':                  s.source_url, 
            'title':                s.source_title, 
            'name':                 s.source_name, 
            'date':                 s.source_date.strftime('%c'),
            'other_article_urls':   s.other_article_urls,
            'other_article_titles': s.other_article_titles,
            'cached':               'true'
        }
        
        return HttpResponse(json.dumps(pageinfo), content_type='application/json')

    # #if not cached initiate API request
    else:
        b64URL = request.META['HTTP_REQUESTORIGINURL']
        URL = b64URL.decode('base64')
        
        metadata = None
    if Metadata.objects.filter(url = URL).exists():
        metadata = Metadata.objects.get(url = URL)
        
        print 'metadata from cache', metadata
    else:
        client = embedly.Embedly('6b216564e304429090c3f15fccde1b3e')
        embedly_response = client.extract(URL)
        
        keyword_list = [k['name'] for k in embedly_response['keywords']]
        entity_list = [e['name'] for e in embedly_response['entities']]
        
        print keyword_list
        print entity_list
        
        metadata = Metadata(url = URL, keywords = keyword_list, entities = entity_list)
        metadata.save()
        
        print metadata
    
    return googleEarliestWithTop(quote_text, metadata, userFromRequest(request))

def findDate(pagemap):
    print "===========PAGEMAP=============="
    pprint.pprint(pagemap)
    print "==============="
    site_types=["newsarticle", "webpage", "blogposting", "article"]
    articleDate = None

    # if "metatags" in pagemap:
    metatag = pagemap["metatags"][0]
    if "citation_cover_date" in metatag.keys(): articleDate= metatag["citation_cover_date"] 
    elif "citation_publication_date" in metatag.keys(): articleDate == metatag["citation_publication_date"]

    for type in site_types:
        if type in pagemap.keys():
            typeData = pagemap[type][0]
            # print "===========TYPEDATA=============="
            # pprint.pprint(typeData)
            # print "==============="
            if "datecreated" in typeData: articleDate = typeData["datecreated"]
            elif "datepublished" in typeData: articleDate = typeData["datepublished"]
            print "articleDate:", articleDate
    if articleDate: return parse(articleDate).replace(tzinfo=None)
    else: return datetime.now().replace(tzinfo=None)

# temp binary search
def page_info_for_earliest(quote):
    first = {}
    day = timedelta(days=1) # one-day increment
    low = datetime(1970, 01, 01).replace(tzinfo=None) # lower bound for date search
    today = datetime.now().replace(tzinfo=None)
    mindate = datetime.now().replace(tzinfo=None)
    high = low + (low + today) / 2 # begin with midpoint between lower bound and today
    
    # binary search
    for i in range(0, 12): # temporarily limit the number of searches for each quote
        
        # end loop if range has been maximally narrowed
        if low >= high: break

        # get JSON of results from google with appropriate max date
        url = "https://www.googleapis.com/customsearch/v1?q=" + quote + "&cx=006173695502366383915%3Acqpxathvhhm&exactTerms=" + quote + "&sort=date%3Ar%3A%3A" + high.strftime('%Y%m%d') + "&key=" + DEVKEY
        res = json.loads((urllib.urlopen(url)).read())
        rescount = int(res["searchInformation"]["totalResults"]) #number of results
        
        print "ittr: ", i, "rescount: ", rescount, 'low: ' + str(low) + ' high: ' + str(high) # for debugging

        if not rescount:
            print "no results", 
            low = high + day
            high = low + (mindate - low)/2

        elif rescount == 1:
            print "one result",
            first = res["items"][0]
            break

        # for multiple hits and non-maximally narrowed range, find earliest hit
        else:
            for i, pagemap in enumerate(res["items"]):
                print "NO PAGEMAP"
                print pagemap
                if "pagemap" in pagemap:
                    currdate = findDate(pagemap["pagemap"])
                    print "pagemap num:", i, "currdate:", currdate, "mindate", mindate
                    
                    if currdate:
                        if currdate < mindate:
                            mindate = currdate
                            first = pagemap

            # for next search, reduce upper bound by binary method or earliest date
            mid = low + (high - low)/2
            high = mid - day if mid <= mindate else mindate - day

    # DEFAULT SHOULD BE EMPTY STRING
    source_name = ' '
    if "pagemap" in first and "metatags" in first:
        # if first["pagemap"]["metatags"][0]:
        meta = first["pagemap"]["metatags"][0]
        if "og:site_name" in meta.keys(): 
            source_name = meta["og:site_name"]   
    
    if not first or len(first.keys()) == 0:
        first["title"] = " "
        first["link"] = " "

    pageinfo = {
                'quote':    quote, 
                'title':    first["title"], 
                'url':      first["link"], 
                'name':     source_name, 
                'date':     mindate,
                'cached':   'n'
                }

    return pageinfo

def googleEarliestWithTop(quote_text, metadata, u):
    service = build("customsearch", "v1", developerKey = DEVKEY)

    
    NUM_KEYWORDS_TO_USE = 3
    NUM_ENTITIES_TO_USE = 2
    
    metadata_query = ' '.join(metadata.keywords[:NUM_KEYWORDS_TO_USE]) + ' ' + ' '.join(metadata.entities[:NUM_ENTITIES_TO_USE])

    # try:
    res = service.cse().list(q = metadata_query, cx='006173695502366383915:cqpxathvhhm', exactTerms=quote_text).execute()
    tot = res['queries']['request'][0]['totalResults']
    
    if int(tot) == 0:
        print "NO EXACT MATCHES FOUND - RELAXING EXACT TERMS"
        res = service.cse().list(q = quote_text + ' ' + metadata_query, cx='006173695502366383915:cqpxathvhhm').execute()
        tot = res['queries']['request'][0]['totalResults']
        
        if int(tot) == 0:
            print "NO MATCHES FOUND WITH KEYWORDS - SEARCHING QUOTE ONLY"
            res = service.cse().list(q = quote_text, cx='006173695502366383915:cqpxathvhhm').execute()
                   

    # This creates an array of tuples containing (article_title, url) for each source
    other_urls = [item['link'] for item in res['items'][0:max(1, len(res['items']))]]
    other_titles = [item['title'] for item in res['items'][0:max(1, len(res['items']))]]
    

    earliest = page_info_for_earliest(quote_text)

    pageinfo = {
                'quote':                quote_text, 
                'url':                  earliest["url"], 
                'title':                earliest["title"], 
                'name':                 earliest["name"], 
                'date':                 earliest["date"].strftime("%c"),
                'other_article_urls':   other_urls,
                'other_article_titles': other_titles,
                'cached':               'false',
                }
    
    newSource = Source(source_quote=            pageinfo['quote'], 
                        source_url=             pageinfo['url'], 
                        source_title=           pageinfo["title"], 
                        source_name=            pageinfo['name'], 
                        source_date=            earliest['date'],
                        other_article_urls=     pageinfo['other_article_urls'],
                        other_article_titles=   pageinfo['other_article_titles'],
                        )
    newSource.save()
    newRequest = Request(user=u, request_date=earliest["date"], request_source=newSource)
    newRequest.save()

    pageinfo_text = json.dumps(pageinfo)       
    return HttpResponse(pageinfo_text, content_type='application/json')

    # except Exception as e:
    #     # http://stackoverflow.com/questions/9823936/python-how-do-i-know-what-type-of-exception-occured
    #     print str(e)
    #     
    #     print "FAIL"
    #     print e
    #     return HttpResponse(str(e))

# def googleTop(quote, metadata, u):
#     service = build("customsearch", "v1", developerKey="AIzaSyABOiui8c_-sFGJSSXCk6tbBThZT2NI4Pc")
# 
#     # site_types=["newsarticle", "webpage", "blogposting", "article"]
#     
#     NUM_KEYWORDS_TO_USE = 0
#     NUM_ENTITIES_TO_USE = 0
#     
#     metadata_query = ' '.join(metadata.keywords[:NUM_KEYWORDS_TO_USE]) + ' ' + ' '.join(metadata.entities[:NUM_ENTITIES_TO_USE])
# 
#     try:
#         req = service.cse().list(q = metadata_query, cx='006173695502366383915:cqpxathvhhm', exactTerms=quote)
#         res = req.execute()
#         tot = res['queries']['request'][0]['totalResults']
#         
#         if int(tot) == 0:
#             print "NO EXACT MATCHES FOUND - RELAXING EXACT TERMS"
#             res = service.cse().list(q = quote + ' ' + metadata_query, cx='006173695502366383915:cqpxathvhhm').execute()
#             tot = res['queries']['request'][0]['totalResults']
#             
#             if int(tot) == 0:
#                 print "NO MATCHES FOUND WITH KEYWORDS - SEARCHING QUOTE ONLY"
#                 res = service.cse().list(q = quote, cx='006173695502366383915:cqpxathvhhm').execute()
#                 
#         
#         first = res["items"][0]
#         pagemap = first['pagemap']
#         date_published_est = datetime.now().replace(tzinfo=None)
#         source_name = ' '
#         
#         if pagemap["metatags"][0]:
#             meta = pagemap["metatags"][0]
#             if "og:site_name" in meta.keys(): 
#                 source_name = meta["og:site_name"]
#         
# 
#         date_published_est = findDate(pagemap)
# 
#         # This creates an array of tuples containing (article_title, url) for each source
#         other_urls = [item['link'] for item in res['items'][1:max(1, len(res['items']))]]
#         other_titles = [item['title'] for item in res['items'][1:max(1, len(res['items']))]]
#         
#         pageinfo = {
#                     'quote':                quote, 
#                     'url':                  first["link"], 
#                     'title':                first["title"], 
#                     'name':                 source_name, 
#                     'date':                 date_published_est.strftime('%c'),
#                     'other_article_urls':   other_urls,
#                     'other_article_titles': other_titles,
#                     'cached':               'false',
#                     }
#         
#         newSource = Source(source_quote=            pageinfo['quote'], 
#                             source_url=             pageinfo['url'], 
#                             source_title=           pageinfo["title"], 
#                             source_name=            pageinfo['name'], 
#                             source_date=            date_published_est,
#                             other_article_urls=     pageinfo['other_article_urls'],
#                             other_article_titles=   pageinfo['other_article_titles'],
#                             )
#         newSource.save()
#         newRequest = Request(user=u, request_date=date_published_est, request_source=newSource)
#         newRequest.save()
# 
#         pageinfo_text = json.dumps(pageinfo)
#         
#         return HttpResponse(pageinfo_text, content_type='application/json')
#     except Exception as e:
#         # http://stackoverflow.com/questions/9823936/python-how-do-i-know-what-type-of-exception-occured
#         print str(e)
#         
#         print "FAIL"
#         print e
#         return HttpResponse(str(e))

# deprecated
# def googleFirst(text, u):
#     #metatags related to dates:
#     datekeys = {'article:published_time','Pubdate', 'ptime', 'utime', 'displaydate', 'dat', 'date', 'datetime', 'datePublished', 'datepublished', 'dc.date', 'og:pubdate', 'pubdate', 'datecreated', 'pud', 'pdate'}
# 
#     low = date(1970, 01, 01) # lower bound for date search
#     today = date.today()
#     high = low + (today - low)/2 # begin with midpoint between lower bound and today
#     day = timedelta(days=1) # one-day increment
#     first = {}
#     mindate = today # earliest date mentioned in metatags of search results
# 
#     # binary search
#     for i in range(0, 15): # temporarily limit the number of searches for each quote
# 
#         # end loop if range has been maximally narrowed
#         if low >= high: break
# 
#         #get JSON of results from google with appropriate max date
#         url = "https://www.googleapis.com/customsearch/v1?q=" + text + "&cx=006173695502366383915%3Acqpxathvhhm&exactTerms=" + text + "&sort=date%3Ar%3A%3A" + high.strftime('%Y%m%d') + "&key=AIzaSyABOiui8c_-sFGJSSXCk6tbBThZT2NI4Pc"
#         res = json.loads((urllib.urlopen(url)).read())
#         rescount = int(res["searchInformation"]["totalResults"]) #number of results
# 
#         # for debugging:
#         print rescount
#         print 'low: ' + str(low) + ' high: ' + str(high)
# 
#         # if upper bound date is too early, make upper bound the earliest date of a hit already encountered
#         if rescount < 1:
#             low = high + day
#             high = low + (mindate - low)/2
# 
#         elif rescount == 1:
#             first = res["items"][0]
#             break
# 
#         # for multiple hits and non-maximally narrowed range, find earliest hit
#         else:
#             for entry in res["items"]:
#                 #search for date in two common locations
#                 if "pagemap" in entry:
#                     if entry["pagemap"]["metatags"]:
#                         meta = entry["pagemap"]["metatags"]
#                         for key in datekeys:
#                             if key in meta[0]:
#                                 try:
#                                     currdate = (parse_datetime(meta[0][key])).date()
#                                     print currdate # for debugging purposes
# 
#                                     #update earliest date & earliest hit
#                                     if currdate < mindate:
#                                         mindate = currdate
#                                         first = entry
# 
#                                 # catch error for unintelligible datestamp
#                                 except ValueError: print ('error at ' + key + ' in metatags, parsing ' + meta[0][key])
# 
#                     if "newsarticle" in entry["pagemap"]:
#                         article = entry["pagemap"]["newsarticle"]
#                         for key in datekeys:
#                             if key in article[0]:
#                                 try:
#                                     currdate = (parse_datetime(article[0][key])).date()
#                                     print currdate
#                                     if currdate < mindate:
#                                         mindate = currdate
#                                         first = entry
# 
#                                 # catch error for unintelligible datestamp
#                                 except ValueError: print ('error at ' + key + ' in newsarticle, parsing ' + article[0][key])
# 
#                     print mindate # for debugging purposes
#                 else: print 'no pagemap'
# 
#             # for next search, reduce upper bound by binary method or earliest date
#             mid = low + (high - low)/2
#             high = mid - day if mid <= mindate else mindate - day
# 
#             #for debugging purposes:
#             print mid <= mindate
# 
#     print 'earliest entry: '
# 
#     # TODO - Also return top hits
#     pageinfo = {
#                 'quote':    text, 
#                 'title':    first["title"], 
#                 'url':      first["link"], 
#                 'source':   ' ', 
#                 'date':     mindate.strftime('%c'),
#                 'cached':   'false'
#                 }
# 
#     #create source object and put in db
#     newSource = Source(source_quote=text, 
#                         source_url=first["link"], 
#                         source_title=first["title"], 
#                         source_name=' ', 
#                         source_date=mindate)
#     newSource.save()
# 
#     #create request and put in db
#     newRequest = Request(user=u, request_date=date.today(), request_source=newSource)
#     newRequest.save()
# 
#     pageinfo = json.dumps(pageinfo)
#     return HttpResponse(pageinfo, content_type='application/json')

# temp binary search
# def googleEarliest(request, quote):
#     # service = build("customsearch", "v1", developerKey="AIzaSyABOiui8c_-sFGJSSXCk6tbBThZT2NI4Pc")
# 
#     day = timedelta(days=1) # one-day increment
#     low = date(1970, 01, 01) # lower bound for date search
#     today = date.today()
#     mindate = date.today()
#     high = low + (today - low)/2 # begin with midpoint between lower bound and today
#     
#     first = {}
# 
#     # binary search
#     for i in range(0, 8): # temporarily limit the number of searches for each quote
#         
#         # end loop if range has been maximally narrowed
#         if low >= high: break
# 
#         # get JSON of results from google with appropriate max date
#         url = "https://www.googleapis.com/customsearch/v1?q=" + quote + "&cx=006173695502366383915%3Acqpxathvhhm&exactTerms=" + quote + "&sort=date%3Ar%3A%3A" + high.strftime('%Y%m%d') + "&key=AIzaSyABOiui8c_-sFGJSSXCk6tbBThZT2NI4Pc"
#         res = json.loads((urllib.urlopen(url)).read())
#         rescount = int(res["searchInformation"]["totalResults"]) #number of results
#         
#         print "ittr: ", i, "rescount: ", rescount, 'low: ' + str(low) + ' high: ' + str(high) # for debugging
# 
#         if not rescount:
#             print "no results", 
#             low = high + day
#             high = low + (mindate - low)/2
# 
#         elif rescount == 1:
#             print "one result",
#             first = res["items"][0]
#             break
# 
#         # for multiple hits and non-maximally narrowed range, find earliest hit
#         else:
#             for i, pagemap in enumerate(res["items"]):
#                 currdate = findDate(pagemap["pagemap"]).date()
#                 print "pagemap num:", i, "currdate:", currdate, "mindate", mindate
# 
#                 if currdate < mindate:
#                     mindate = currdate
#                     first = pagemap
# 
#             # for next search, reduce upper bound by binary method or earliest date
#             mid = low + (high - low)/2
#             high = mid - day if mid <= mindate else mindate - day
# 
#     source_name = 'default'
#     if first["pagemap"]["metatags"][0]:
#         meta = first["pagemap"]["metatags"][0]
#         if "og:site_name" in meta.keys(): 
#             source_name = meta["og:site_name"]   
# 
#     pageinfo = {
#                 'quote':    quote, 
#                 'title':    first["title"], 
#                 'url':      first["link"], 
#                 'name':   source_name, 
#                 'date':     mindate.strftime('%c'),
#                 'cached':   'n'
#                 }
# 
# 
#     pageinfo = json.dumps(pageinfo)
#     return HttpResponse(pageinfo, content_type='application/json')
