# -*- coding: utf-8 -*-
import re
from scrapy import Spider, Request
from scrapy_splash import SplashRequest
from urllib import parse

# splash lua script
script = """
function main(splash, args)
  splash:go(args.url)
  splash:wait(args.wait)
  splash:runjs("foo = function(){ var f = document.getElementById('g_iframe'); return f.contentDocument.getElementsByTagName('body')[0].innerHTML; }")
  local result = splash:evaljs("foo()")
  return result
end
"""


class NcmSpider(Spider):
    name = 'ncm'
    allowed_domains = ['163.com']
    start_urls = 'https://music.163.com/#/discover/toplist'

    # start request
    def start_requests(self):
        yield SplashRequest(url=self.start_urls, callback=self.parse, endpoint='execute',
                            args={'lua_source': script, 'wait': 3})

    def parse(self, response):
        pattern = re.compile('<a.*?href="(.*?)".*?class="s-fc0">(.*?)</a>')
        toplist = pattern.findall(str(response.text))
        for index in range(0, toplist.__len__()):
            url = toplist[index][0]
            yield SplashRequest(url=parse.urljoin(self.start_urls, url), callback=self.toplist_detail,
                                endpoint='execute',
                                args={'lua_source': script, 'wait': 3}, meta={"title": toplist[index][1]})

    def toplist_detail(self, response):
        pattern_song = re.compile('<a.*?href="(/song.*?)".*?>(.*?)</a>')
        songlist = pattern_song.findall(str(response.text))
        for sl in songlist:
            print("%s---%s---%s" % (response.meta.get("title"), sl[1], sl[0]))
