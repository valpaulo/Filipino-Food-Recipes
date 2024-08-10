from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from sqlalchemy import create_engine, Column, String, Integer, Float, MetaData, Table
from sqlalchemy.orm import sessionmaker
import requests
import time


service = Service(executable_path="./chromedriver")
driver = webdriver.Chrome(service=service)

driver.get('https://panlasangpinoy.com/recipes/')  # Replace with the actual URL

time.sleep(1000000000)


# recipes = []
# # Locate elements using Selenium
# recipe_elements = driver.find_elements(By.CLASS_NAME, 'recipe-item')  # Adjust the locator

# for element in recipe_elements:
#     title = element.find_element(By.CLASS_NAME, 'recipe-title').text
#     link = element.find_element(By.TAG_NAME, 'a').get_attribute('href')
    
#     # Fetch additional details using the requests library
#     response = requests.get(link)
#     if response.status_code == 200:
#         # Parse the response (using BeautifulSoup, regex, or similar tools)
#         # For simplicity, let's assume the API provides JSON response with necessary details.
#         recipe_details = response.json()
#         recipes.append({
#             'title': title,
#             'ingredients': recipe_details.get('ingredients', ''),
#             'prep_time': recipe_details.get('prep_time', 0),
#             'calories': recipe_details.get('calories', 0.0)
#         })
#     time.sleep(1)  # Delay between requests to avoid overloading the server

driver.quit()

# # PostgreSQL connection string
# DATABASE_URI = 'postgresql+psycopg2://username:password@localhost:5432/mydatabase'

# # Create an engine and metadata
# engine = create_engine(DATABASE_URI)
# metadata = MetaData()

# # Define the recipes table
# recipes_table = Table(
#     'recipes', metadata,
#     Column('id', Integer, primary_key=True),
#     Column('title', String, nullable=False),
#     Column('ingredients', String),
#     Column('prep_time', Integer),
#     Column('calories', Float)
# )

# # Create the table in the database
# metadata.create_all(engine)

# # Create a session
# Session = sessionmaker(bind=engine)
# session = Session()

# # Insert scraped data into the database
# for recipe in recipes:
#     ins = recipes_table.insert().values(
#         title=recipe['title'],
#         ingredients=recipe['ingredients'],
#         prep_time=recipe['prep_time'],
#         calories=recipe['calories']
#     )
#     session.execute(ins)

# # Commit the transaction
# session.commit()

# session.close()
