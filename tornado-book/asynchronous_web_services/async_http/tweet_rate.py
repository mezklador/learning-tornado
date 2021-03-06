import urllib
import json
import datetime
import time

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web # why this?
import tornado.httpclient

from oauth import oauth

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        # localhost:8000/?q=stuff
        # so here self.get_arugement gives the value of q i.e. 'stuff'
        query = self.get_argument('q')
        # Using tornado's HTTPClient class, an object is instantiated
        # and fetch method is called on that  
        client = tornado.httpclient.HTTPClient()
        # urllib.urlencode formats it to proper url format %xx something like
        # that. and response of client.fetch is stored in response
        #response = client.fetch("http://search.twitter.com/search.json?" + \
        #       urllib.urlencode({"q": query, "result_type": "recent", "rpp": 100}))
        
        url = "https://api.twitter.com/1.1/search/tweets.json?" + urllib.urlencode({"q": query, "result_type": "recent", "count": 100})
        response = client.fetch(url, headers={'Authorization': oauth(url)})
        # the response has header and body. As body contains the results, it 
        # is used. And it is converted to python object from json 
        # using json.loads
        body = json.loads(response.body)
        # result_count = len(body['results'])
        result_count = len(body['statuses'])
        now = datetime.datetime.utcnow()
        #raw_oldest_tweet_at = body['results'][-1]['created_at']
        raw_oldest_tweet_at = body['statuses'][-1]['created_at']
        oldest_tweet_at = datetime.datetime.strptime(raw_oldest_tweet_at,
        #       "%a, %d %b %Y %H:%M:%S +0000")
                "%a %b %d %H:%M:%S +0000 %Y")
        seconds_diff = time.mktime(now.timetuple()) - \
                time.mktime(oldest_tweet_at.timetuple())
        tweets_per_second = float(result_count) / seconds_diff
        self.write("""
<div style="text-align: center">
    <div style="font-size: 72px">%s</div>
    <div style="font-size: 144px">%.02f</div>
    <div style="font-size: 24px">tweets per second</div>
</div>""" % (query, tweets_per_second))

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[(r"/", IndexHandler)])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
