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
                    yield response.follow(link, callback=self.parse_subcategory, meta={'category': category, 'subcategory': subcategory_name})

        df = pd.DataFrame(data)
        df.to_csv("categories_and_subcategories.csv", index=False)
        print(df)

        connection_string = f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
        engine = create_engine(connection_string)
        df.to_sql("recipe_categories", engine, if_exists="replace", index=False)


    def parse_subcategory(self, response):
        category = response.meta['category']
        subcategory = response.meta['subcategory']
        recipe_links = response.css("a.entry-title-link::attr(href)").getall()
        recipe_titles = response.css("a.entry-title-link::text").getall()


        # Collect subcategory data
        subcategory_data = []
        for title, link in zip(recipe_titles, recipe_links):
            subcategory_data.append({
                "Category": category,
                "Subcategory": subcategory,
                "Recipe": title,
                "Recipe Link": link
            })

        # Create a DataFrame for subcategory data
        subcategory_df = pd.DataFrame(subcategory_data)

        # Save subcategory data to CSV
        subcategory_df.to_csv(f"recipes_{category}_{subcategory}.csv", index=False)
        print(subcategory_df)

        next_page  = response.css("li.pagination-next a::attr(href)").get()
        
        if next_page:
            yield response.follow(next_page, callback=self.parse_subcategory, meta={'category': category, 'subcategory': subcategory})
        