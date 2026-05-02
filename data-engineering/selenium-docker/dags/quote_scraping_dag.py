from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def scrape_quotes():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://quotes.toscrape.com")

        quotes = driver.find_elements(By.CLASS_NAME, "quote")

        results = []
        print("========== LIST DATA SCRAPE ==========")
        for quote in quotes:
            text = quote.find_element(By.CLASS_NAME, "text").text
            author = quote.find_element(By.CLASS_NAME, "author").text
            results.append((text, author))

        # Log ke Airflow
        for i, (text, author) in enumerate(results, start=1):
            print(f"{i}. {text} — {author}")

    finally:
        driver.quit()


with DAG(
    dag_id="quote_scraping_selenium",
    start_date=datetime(2024, 1, 1),
    schedule=None,          # manual trigger
    catchup=False,
    tags=["selenium", "scraping", "demo"],
) as dag:

    scrape_task = PythonOperator(
        task_id="scrape_quotes",
        python_callable=scrape_quotes,
    )

    scrape_task
