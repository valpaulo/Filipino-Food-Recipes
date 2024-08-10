import scrapy


class RecipespiderSpider(scrapy.Spider):
    name = "recipespider"
    allowed_domains = ["panlasangpinoy.com"]
    start_urls = ["https://panlasangpinoy.com/recipes/"]

    def parse(self, response):
        pass
