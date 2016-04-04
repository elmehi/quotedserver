from googleapiclient.discovery import build
import pprint

def search(searchString):
  # Build a service object for interacting with the API. Visit
  # the Google APIs Console <http://code.google.com/apis/console>
  # to get an API key for your own application.
  service = build("customsearch", "v1",
            developerKey="AIzaSyABOiui8c_-sFGJSSXCk6tbBThZT2NI4Pc")
  res = service.cse().list(
      q = searchString,
      cx='006173695502366383915:cqpxathvhhm',
    ).execute()
  pprint.pprint(res)


def main():
    search('dog')


if __name__ == '__main__':
  main()
