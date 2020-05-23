# -*- coding: utf-8 -*-
import scrapy
from nlp_scraping.items import NlpScrapingItem
from bs4 import BeautifulSoup

class LivedoorNewsSpider(scrapy.Spider):
    name = 'livedoor_news'
    allowed_domains = ['news.livedoor.com']
    start_urls = ['https://news.livedoor.com/']
    user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"

    def parse(self, response):
        for category_link in response.css('.contentInner .navInner .parent a::attr(href)').extract():
            # 下の階層へのリンクを辿る
            yield response.follow(category_link, callback=self.parse_by_category)

    def parse_by_category(self, response):

        for post_link in response.css('.mainBody .articleList a::attr(href)').extract():
            # 下の階層へのリンクを辿る
            yield response.follow(post_link, callback=self.parse_by_post)                
            
        older_post_link = response.css('ul.pager li.next a::attr(href)').extract_first()
        if older_post_link is None:
            # リンクが取得できなかった場合は最後のページなので処理を終了
            return
        else:
            # 次のページをのリクエストを実行する
            yield response.follow(older_post_link, callback=self.parse_by_category)

    def parse_by_post(self, response):
        title = response.css('.topicsTtl a::text').extract_first()
        date = response.css('time.topicsTime::text').extract_first()

        article_more_link = response.css('.articleMore a::attr(href)').extract_first()

        if article_more_link is None:
            # リンクが取得できなかった場合は処理を終了
            return
        else:
            # 次のページをのリクエストを実行する
            yield response.follow(article_more_link, callback=self.parse_by_article_more, 
                                        cb_kwargs={'date': date, 'title': title, 'url': article_more_link})

    def parse_by_article_more(self, response, title, date, url, text=None, tags=None, keywords=None):

        bs = BeautifulSoup(response.text, 'lxml')

        if text is None:
            text, tags, keywords = self._extract_text(bs)
        else:
            text_tmp, tags, keywords = self._extract_text(bs)
            text = text + text_tmp

        article_part_link = response.css('.page li.next a::attr(href)').extract_first()
        if article_part_link is None:
            # リンクが取得できなかった場合は最後のページなので処理を終了
            yield NlpScrapingItem(
                published_date = date,
                title = title,
                text = ''.join(text),
                url = url,
                tags = tags,
                keywords = keywords,
            )
        else:
            # 次のページをのリクエストを実行する
            yield response.follow(article_part_link, callback=self.parse_by_category, 
                                    cb_kwargs={'date': date, 'title': title,'url': url, 'text': text, 'tags': tags, 'keywords': keywords})

    def _extract_text(self, bs):
        article_body = bs.find(class_="articleBody")
        tags = [span.find("a").get_text().replace("\n", "") for span in bs.find(class_="breadcrumbs").find_all("span") if span.find("a")]
        keywords = [li.get_text() for li in bs.find(class_="articleHeadKeyword").find_all("li")]
        texts = article_body.find("span").find_all("p")
        # 記事本文のフォーマットに合わせて条件分岐
        if texts:
            article = "".join([p.get_text().replace("\u3000", "") for p in texts])
            return article, tags, keywords
        else:
            article = article_body.find("span")
            if article.find("script"):
                article.find("script").extract()
            article = article.get_text()
            return article.strip().replace("\u3000", ""), tags, keywords

