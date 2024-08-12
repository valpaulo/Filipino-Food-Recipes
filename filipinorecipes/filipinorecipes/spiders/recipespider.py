import scrapy
import pandas as pd
from sqlalchemy import create_engine
from postgresconfig import USERNAME, PASSWORD, HOST, PORT, DATABASE


class RecipespiderSpider(scrapy.Spider):
    name = "recipespider"
    allowed_domains = ["panlasangpinoy.com"]
    start_urls = ["https://panlasangpinoy.com/recipes/"]

    def __init__(self, *args, **kwargs):
        super(RecipespiderSpider, self).__init__(*args, **kwargs)
        self.data_batch = []  # Temporary storage for batch processing
        self.batch_size = 1000  # Adjust batch size based on your system capabilities
        self.csv_file = "all_recipes.csv"

        # Initialize the CSV file with headers
        with open(self.csv_file, "w") as f:
            f.write("Category,Subcategory,Recipe,Recipe Link\n")

        # Initialize the connection to the database
        connection_string = f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
        self.engine = create_engine(connection_string)

    def parse(self, response):
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

                if link:
                    yield response.follow(link, callback=self.parse_subcategory, meta={'category': category, 'subcategory': subcategory_name})

    def parse_subcategory(self, response):
        category = response.meta['category']
        subcategory = response.meta['subcategory']
        recipe_links = response.css("a.entry-title-link::attr(href)").getall()
        recipe_titles = response.css("a.entry-title-link::text").getall()

        for title, link in zip(recipe_titles, recipe_links):
            self.data_batch.append({
                "Category": category,
                "Subcategory": subcategory,
                "Recipe": title,
                "Recipe Link": link
            })

        # Save data in batches to reduce memory usage
        if len(self.data_batch) >= self.batch_size:
            self.save_data_batch()

        # Handle pagination for the subcategory page
        next_page = response.css("li.pagination-next a::attr(href)").get()
        
        if next_page:
            yield response.follow(next_page, callback=self.parse_subcategory, meta={'category': category, 'subcategory': subcategory})
        else:
            # If it's the last page, ensure remaining data is saved
            self.save_data_batch()

    def save_data_batch(self):
        if not self.data_batch:
            return  # No data to save

        # Convert batch data to DataFrame
        df = pd.DataFrame(self.data_batch)

        # Append data to CSV
        df.to_csv(self.csv_file, mode="a", header=False, index=False)

        # Save data to PostgreSQL
        df.to_sql("all_recipe_details", self.engine, if_exists="append", index=False)

        # Clear the batch
        self.data_batch.clear()

    def close(self, reason):
        # Save any remaining data when the spider closes
        if self.data_batch:
            self.save_data_batch()
