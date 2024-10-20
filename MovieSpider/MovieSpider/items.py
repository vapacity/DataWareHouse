# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class MovieItem(scrapy.Item):
    ASIN = scrapy.Field()
    Title = scrapy.Field()
    Subtitles = scrapy.Field()
    Language = scrapy.Field()
    Release_year = scrapy.Field()
    Release_date = scrapy.Field()
    Rated = scrapy.Field()
    Run_time = scrapy.Field()
    Description = scrapy.Field()
    Contributors = scrapy.Field()
    Actors = scrapy.Field()
    Directors = scrapy.Field()
    Producers = scrapy.Field()
    Media_Format = scrapy.Field()
    Genres = scrapy.Field()
    Customer_Reviews = scrapy.Field()
    IMDb = scrapy.Field()
    Number_of_discs = scrapy.Field()
    Studio = scrapy.Field()



