import scrapy
import pandas as pd
from sqlalchemy import create_engine
from postgresconfig import USERNAME, PASSWORD, HOST, PORT, DATABASE

class RecipespiderSpiderv2(scrapy.Spider):
    name = "recipespiderv2"
    allowed_domains = ["panlasangpinoy.com"]
    start_urls = ["https://panlasangpinoy.com/categories/recipes/"]

    def __init__(self, *args, **kwargs):
        super(RecipespiderSpiderv2, self).__init__(*args, **kwargs)
        self.data_batch = []  # Temporary storage for batch processing
        self.batch_size = 1000  # Adjust batch size based on your system capabilities
        self.csv_file = "all_recipes_v2.csv"

        # Initialize the connection to the database
        connection_string = f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
        self.engine = create_engine(connection_string)

        # Initialize the CSV file with headers if it doesn't exist
        with open(self.csv_file, "w") as f:
            f.write("Recipe Link,Recipe Name,Course,Cuisine,Keyword,Servings,Author,Ingredient List,Instructions,Calories,Carbohydrates,Protein,Fat,Saturated Fat,Polyunsaturated Fat,Monounsaturated Fat,Trans Fat,Cholesterol,Sodium,Potassium,Fiber,Sugar,Vitamin A,Vitamin C,Calcium,Iron\n")

    def parse(self, response):
        recipe_links = response.css("a.entry-title-link::attr(href)").getall()
        recipe_titles = response.css("a.entry-title-link::text").getall()

        for title, link in zip(recipe_titles, recipe_links):
            yield response.follow(link, callback=self.parse_recipe, meta={'recipe': title})

        next_page = response.css("li.pagination-next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_subcategory(self, response):
        pass



    def parse_recipe(self, response):
        recipe = response.meta['recipe']
        recipe_details = response.css("div.oc-recipe-buttons a.wprm-recipe-print::attr(href)").get()
        yield response.follow(recipe_details, callback=self.parse_recipe_details, meta={'recipe': recipe})

    def parse_recipe_details(self, response):
        link = response.url
        recipe_name = response.css("h2.wprm-recipe-name::text").get()
        course = response.css("span.wprm-recipe-course::text").get()
        cuisine = response.css("span.wprm-recipe-cuisine::text").get()
        keyword = response.css("span.wprm-recipe-keyword::text").get()
        servings = response.css("span.wprm-recipe-servings::text").get()
        author = response.css("span.wprm-recipe-author::text").get()

        ingredients = response.css('ul.wprm-recipe-ingredients li.wprm-recipe-ingredient')
        ingredient_list = []
        for ingredient in ingredients:
            amount = ingredient.css('span.wprm-recipe-ingredient-amount::text').get(default='').strip()
            unit = ingredient.css('span.wprm-recipe-ingredient-unit::text').get(default='').strip()
            name = ingredient.css('span.wprm-recipe-ingredient-name::text').get(default='').strip()
            full_ingredient = f"{amount} {unit} {name}".strip()
            ingredient_list.append(full_ingredient)


        ##### NUTRITION DATA #####
        nutrition_data = {
            "calories": None,
            "carbohydrates": None,
            "protein": None,
            "fat": None,
            "saturated_fat": None,
            "polyunsaturated_fat": None,
            "monounsaturated_fat": None,
            "trans_fat": None,
            "cholesterol": None,
            "sodium": None,
            "potassium": None,
            "fiber": None,
            "sugar": None,
            "vitamin_a": None,
            "vitamin_c": None,
            "calcium": None,
            "iron": None,
        }

        nutrients = response.css("div.wprm-nutrition-label-container span.wprm-nutrition-label-text-nutrition-container")
        for nutrient in nutrients:
            label = nutrient.css("span.wprm-nutrition-label-text-nutrition-label::text").get()
            value = nutrient.css("span.wprm-nutrition-label-text-nutrition-value::text").get()
            unit = nutrient.css("span.wprm-nutrition-label-text-nutrition-unit::text").get()

            if label and value and unit:
                label = label.strip().replace(":", "")
                if "Calories" in label:
                    nutrition_data["calories"] = f"{value.strip()} {unit.strip()}"
                elif "Carbohydrates" in label:
                    nutrition_data["carbohydrates"] = f"{value.strip()} {unit.strip()}"
                elif "Protein" in label:
                    nutrition_data["protein"] = f"{value.strip()} {unit.strip()}"
                elif "Fat" in label:
                    nutrition_data["fat"] = f"{value.strip()} {unit.strip()}"
                elif "Saturated Fat" in label:
                    nutrition_data["saturated_fat"] = f"{value.strip()} {unit.strip()}"
                elif "Polyunsaturated Fat" in label:
                    nutrition_data["polyunsaturated_fat"] = f"{value.strip()} {unit.strip()}"
                elif "Monounsaturated Fat" in label:
                    nutrition_data["monounsaturated_fat"] = f"{value.strip()} {unit.strip()}"
                elif "Trans Fat" in label:
                    nutrition_data["trans_fat"] = f"{value.strip()} {unit.strip()}"
                elif "Cholesterol" in label:
                    nutrition_data["cholesterol"] = f"{value.strip()} {unit.strip()}"
                elif "Sodium" in label:
                    nutrition_data["sodium"] = f"{value.strip()} {unit.strip()}"
                elif "Potassium" in label:
                    nutrition_data["potassium"] = f"{value.strip()} {unit.strip()}"
                elif "Fiber" in label:
                    nutrition_data["fiber"] = f"{value.strip()} {unit.strip()}"
                elif "Sugar" in label:
                    nutrition_data["sugar"] = f"{value.strip()} {unit.strip()}"
                elif "Vitamin A" in label:
                    nutrition_data["vitamin_a"] = f"{value.strip()} {unit.strip()}"
                elif "Vitamin C" in label:
                    nutrition_data["vitamin_c"] = f"{value.strip()} {unit.strip()}"
                elif "Calcium" in label:
                    nutrition_data["calcium"] = f"{value.strip()} {unit.strip()}"
                elif "Iron" in label:
                    nutrition_data["iron"] = f"{value.strip()} {unit.strip()}"
        ##### END NUTRITION DATA #####


        final_data = {
            "recipe_link": link,
            "recipe_name": recipe_name,
            "course": course,
            "cuisine": cuisine,
            "keyword": keyword,
            "servings": servings,
            "author": author,
            "ingredient_list": ingredient_list,
            **nutrition_data  # Unpack nutrition data into the final dict
        }

        # Yield the final data
        yield final_data

        df = pd.DataFrame([final_data])
        df.to_csv(self.csv_file, mode="a", header=False, index=False)
        df.to_sql("all_recipe_details_v2", self.engine, if_exists="append", index=False)

