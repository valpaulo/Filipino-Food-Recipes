# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FilipinorecipesItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class RecipesItem(scrapy.Item):
    category = scrapy.Field()
    subcategory = scrapy.Field()
    link = scrapy.Field()
    recipe = scrapy.Field()
    