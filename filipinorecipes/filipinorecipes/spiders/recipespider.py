import scrapy
import pandas as pd
from sqlalchemy import create_engine
from postgresconfig import USERNAME, PASSWORD, HOST, PORT, DATABASE


class RecipespiderSpider(scrapy.Spider):
    name = "recipespider"
    allowed_domains = ["panlasangpinoy.com"]
    start_urls = ["https://panlasangpinoy.com/recipes/"]

    def parse(self, response):
        data = []
        processed_categories = set()

        for detail in response.css("details.sub-menu-toggle"):
            category = detail.css("summary.menu-item-title span::text").get()

            if category in processed_categories:
                continue  # Skip if already processed
            processed_categories.add(category)  # Mark this category as processed

            subcategories = detail.css("ul.sub-menu li.menu-item a.menu-item-title")

            for subcategory in subcategories:
                subcategory_name = subcategory.css("span::text").get()  # Extract the subcategory name
                link = subcategory.css("::attr(href)").get()  # Get the href attribute
                
                data.append({
                    "Category": category,
                    "Subcategory": subcategory_name,
                    "Link": link
                })

                if link:
                    yield scrapy.Request(response.urljoin(link), callback=self.parse_subcategory, meta={'category': category, 'subcategory': subcategory_name})
                
        df = pd.DataFrame(data)
        # df.to_csv("categories_and_subcategories.csv", index=False)
        print(df)

        connection_string = f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
        engine = create_engine(connection_string)
        df.to_sql("recipe_categories", engine, if_exists="replace", index=False)


    def parse_subcategory(self, response):
        category = response.meta['category']
        subcategory = response.meta['subcategory']

        pass