import time
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException

import undetected_chromedriver as uc
uc.Chrome.__del__ = lambda self: None


# ======================
# CONFIG
# ======================
LIST_AFFILIATION_ID = ['60069377'
                       ,'60069380','60069382','60069383','60069381','60070707','60069385','60069392','60069390',
                       '60103610','60069388','60069439','60069397','60103797','60103730','60087601','60105184','60104457',
                       '60069400','60105174']


# ======================
# LOGIN HELPER
# ======================

def try_fill_password_and_click(driver, retries=5):
    email = 'email_account'
    password = 'password_account'
    email_txt = '//*[@id="bdd-email"]'
    password_txt = '//*[@id="bdd-password"]'
    cookies_btn = '//*[@id="onetrust-accept-btn-handler"]'
    next_btn = '//*[@id="bdd-elsPrimaryBtn"]'
    login_btn = '//*[@id="bdd-elsPrimaryBtn"]'
    attempt = 0
    
    # Klik tombol cookies (jika muncul)
    try:
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, cookies_btn))
        )
        element.click()
        print("Cookies accepted")
    except Exception as e:
        print(f"Tombol cookies tidak ditemukan atau gagal diklik: {e}")
    
    while attempt < retries:
        try:
            # Isi email
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, email_txt))
            )
            element.clear()
            element.send_keys(email)
            time.sleep(1)

            # Klik tombol next (atau login step 1)
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, next_btn))
            )
            button.click()
            time.sleep(2)

            # Isi password
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, password_txt))
            )
            element.clear()
            element.send_keys(password)
            time.sleep(1)

            # Klik tombol login
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, login_btn))
            )
            button.click()

            print("Password berhasil diisi dan tombol diklik")
            break
        except Exception as e:
            attempt += 1
            print(f"Percobaan {attempt} gagal, mencoba lagi... Error: {e}")
            time.sleep(2)



# ======================
# API FETCH
# ======================
def fetch_scopus_api(driver, url):
    try:
        driver.get(url)
        time.sleep(1)
        return driver.execute_script(
            "return JSON.parse(document.body.innerText);"
        )
    except WebDriverException as e:
        print(f"Fetch error: {e}")
        return None

# ======================
# MAIN FUNCTION (AIRFLOW CALLS THIS)
# ======================
def run_scraping():
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--headless=new")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")


    driver = uc.Chrome(options=options)
    url = "https://www.scopus.com/signin.uri?origin=&zone=TopNavBar"
    driver.get(url)
    time.sleep(1)
    driver.get(url)
    
    try:
        try_fill_password_and_click(driver)

        all_orgs = []

        for org_id in LIST_AFFILIATION_ID:
            api_url = f"https://www.scopus.com/gateway/organisation-profile-api/organizations/{org_id}"
            result = fetch_scopus_api(driver, api_url)

            if not result:
                continue

            all_orgs.append({
                "orgID": result.get("id"),
                "orgName": result.get("preferredName"),
                "orgURL": f"https://www.scopus.com/pages/organization/{org_id}",
                "totalDocs": result["metrics"]["documentsCount"],
                "totalAuthors": result["metrics"]["authorsCount"]
            })

        df = pd.DataFrame(all_orgs)
        print(df)

    finally:
        driver.quit()
        print("Sudah berhasil scraping")
