import StringIO
from functools import partial
from scrapy.http import Request
from scrapy.spider import BaseSpider
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

class CrawlSpider(CrawlSpider):
    
    name = "spider"
    allowed_domains = ["askul.co.jp", "suzuki.co.jp"]
    start_urls = [
        "http://www.askul.co.jp/",
        "http://www.suzuki.co.jp/",
    ]

    rules = [
        Rule(SgmlLinkExtractor(), follow=True, callback="check_match")
    ]

    crawl_count = 0
    matches = 0

    def check_match(self, response):

        self.__class__.crawl_count += 1

        crawl_count = self.__class__.crawl_count
        if crawl_count % 100 == 0:
                print "Crawled %d pages" % crawl_count


        matchlist = ["3M", "3m", "Sumitomo", "sumitomo", "SUMITOMO"]

        exceptions_after = [ "M", "ML"]

        exceptions_before = [
                "width",
                "height",
                "w: ",
                "h: ",
                "diameter",
                "length"]

        url = response.url

        data = response.body


        for m in matchlist:

                #substrings = find_all_substrings(data, m)

                import re
                substrings = [match.start() for match in re.finditer(re.escape(m), data)]

                # Check entries against the exception list for "allowed" special cases
                for pos in substrings:
                        ok = False
                        for exception in exceptions_after:
                                sample = data[pos:pos+len(exception)]
                                if sample == exception:
                                        #print "Was whitelisted special case:" + sample
                                        ok = True
                                        break

                        for exception in exceptions_before:
                                sample = data[pos - len(exception) + len(m): pos+len(m) ]
                                #print "For %s got sample %s" % (exception, sample)
                                if sample == exception:
                                        #print "Was whitelisted special case:" + sample
                                        ok = True
                                        break
                        if not ok:
                                self.__class__.matches += 1
                                print "Match num: %d" % self.__class__.matches
                                print "URL %s" % url
                                print "Match txt:" + m
                                print "------"

                                with open('/tmp/crawl.txt', 'a') as f:
                                    f.write('url: {0}, text: {1}\n'.format(url, m))


        # return dummy item
        return Item()

    def _requests_to_follow(self, response):

        if getattr(response, "encoding", None) != None:
                # Server does not set encoding for binary files
                # Do not try to follow links in
                # binary data, as this will break Scrapy
                return CrawlSpider._requests_to_follow(self, response)
        else:
            return []