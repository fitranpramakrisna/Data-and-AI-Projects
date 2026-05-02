from seleniumbase import Driver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json
import undetected_chromedriver as uc
import pyautogui
import random
import time
import pandas as pd
from selenium.common.exceptions import WebDriverException

# ======================
# LIST AFFILIATION ID
# ======================
list_affiliation_id = ['60069377','60069380','60069382']

# ======================
# SUBJECT AREA MAPPING
# ======================
SUBJECT_MAPPING = {
    "MEDI": "Medicine",
    "ENGI": "Engineering",
    "PHYS": "Physics and Astronomy",
    "COMP": "Computer Science",
    "SOCI": "Social Science",
    "ENVI": "Environmental Science",
    "MATE": "Material Science",
    "BUSI": "Business, Management and Accounting",
    "EART": "Earth and Planetary Sciences",
    "ENER": "Energy",
    "BIOC": "Biochemistry, Genetics and Molecular Biology",
    "PHAR": "Pharmacology, Toxicology and Pharmaceutics",
    "DECI": "Decision Sciences",
    "AGRI": "Agricultural and Biological Sciences",
    "MATH": "Mathematics",
    "NURS": "Nursing",
    "ECON": "Economics, Econometrics and Finance",
    "CHEM": "Chemistry",
    "ARTS": "Arts and Humanities",
    "DENT": "Dentistry",
    "CENG": "Chemical Engineering",
    "IMMU": "Immunology and Microbiology",
    "MULT": "Multidisciplinary",
    "PSYC": "Psychology",
    "HEAL": "Health Professions",
    "NEUR": "Neuroscience",
    "VETE": "Veterinary"
}

# ======================
# CHROME SETUP
# ======================
options = uc.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = uc.Chrome(options=options, version_main=142)

url = "https://www.scopus.com/signin.uri?origin=&zone=TopNavBar"
driver.get(url)
time.sleep(1)
driver.get(url)

# ======================
# FUNGSI GERAKAN MANUSIAWI
# ======================
def human_like_move(x_target, y_target):
    x_start, y_start = pyautogui.position()
    steps = random.randint(10, 25)
    for i in range(steps):
        x = x_start + (x_target - x_start) * i / steps + random.randint(-2, 2)
        y = y_start + (y_target - y_start) * i / steps + random.randint(-2, 2)
        pyautogui.moveTo(x, y, duration=random.uniform(0.01, 0.05))
    pyautogui.moveTo(x_target, y_target, duration=random.uniform(0.1, 0.2))

def page_passed():
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "bdd-email"))
        )
        return True
    except TimeoutException:
        return False

checkbox_x, checkbox_y = 541, 386
max_tries = 5

for attempt in range(max_tries):
    print(f"Percobaan ke-{attempt+1}")
    time.sleep(random.uniform(2.5, 4.5))
    human_like_move(checkbox_x, checkbox_y)
    time.sleep(random.uniform(0.5, 1.0))
    pyautogui.click()
    time.sleep(random.uniform(5, 8))
    
    if page_passed():
        print("Berhasil lewat halaman CAPTCHA")
        break
else:
    print("Gagal melewati CAPTCHA setelah beberapa percobaan.")

try:
    cookies_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'))
    )
    driver.execute_script("arguments[0].click();", cookies_button)
    print("Cookies berhasil di-accept.")
except Exception as e:
    print("Gagal klik cookies:", e)

# ======================
# LOGIN
# ======================
email_txt = '//*[@id="bdd-email"]'
password_txt = '//*[@id="bdd-password"]'
cookies_btn = '//*[@id="onetrust-accept-btn-handler"]'
next_btn = '//*[@id="bdd-elsPrimaryBtn"]'
login_btn = '//*[@id="bdd-elsPrimaryBtn"]'

email = 'your_scopus_email'
password = 'your scopus_password'

def try_fill_password_and_click(driver, password_txt, password, login_btn, cookies_btn, next_btn, retries=5):
    attempt = 0
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, cookies_btn))
    )
    element.click()

    while attempt < retries:
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, email_txt))
            )
            element.send_keys(email)
            time.sleep(2)

            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, next_btn))
            )
            button.click()
            time.sleep(2)

            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, password_txt))
            )
            element.send_keys(password)
            time.sleep(2)

            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, login_btn))
            )
            button.click()

            print("Password berhasil diisi dan tombol diklik")
            break
        except:
            attempt += 1
            print(f"Percobaan {attempt} gagal, mencoba lagi...")
            time.sleep(2)

try_fill_password_and_click(driver, password_txt, password, login_btn, cookies_btn, next_btn)

# ======================
# FUNGSI UMUM FETCH API
# ======================
def fetch_scopus_api(url):
    try:
        driver.get("https://www.scopus.com/")
        time.sleep(1)

        driver.get(url)
        time.sleep(1)

        data = driver.execute_script("return JSON.parse(document.body.innerText);")
        return data

    except WebDriverException as e:
        print(f"Fetch error: {e}")
        return None

# ======================
# SCRAPING LOOP
# ======================
data_results = []
data_subject_area = []
data_org_collaborators = []

scopus_com_org_id = 1

for id_scopus in list_affiliation_id:
    print(f"Mengambil data untuk ID: {id_scopus} ...")

    api_org = f"https://www.scopus.com/gateway/organisation-profile-api/organizations/{id_scopus}"
    api_subject = f"https://www.scopus.com/gateway/organisation-profile-api/organizations/{id_scopus}/documents/subject-area"
    api_org_collabotors = f"https://www.scopus.com/gateway/organisation-profile-api/organizations/{id_scopus}/collaborators"

    result = None

    for attempt in range(3):
        try:
            result = fetch_scopus_api(api_org)
            time.sleep(2)

            result_subject_area = fetch_scopus_api(api_subject)
            time.sleep(2)
            
            result_org_collaborators = fetch_scopus_api(api_org_collabotors)
            time.sleep(2)

            if result is None:
                print(f"Gagal fetch {id_scopus} (percobaan {attempt+1})")
                continue

            break
        except Exception as e:
            print(f"Error mengambil data {id_scopus}: {e} (percobaan {attempt+1})")
            time.sleep(3)

    if result is None:
        print(f"Gagal total mengambil data ID {id_scopus}, dilewati.")
        continue

    if (
        result.get("preferredName") is None
        and result.get("id") is None
        and result.get("metrics", {}).get("documentsCount", 0) == 0
        and result.get("metrics", {}).get("authorsCount", 0) == 0
    ):
        print(f"ID Scopus {id_scopus} tidak ditemukan, dilewati.")
        continue

    org_url = "https://www.scopus.com/pages/organization/"+id_scopus

    data_results.append({
        "ScopusComOrgID": scopus_com_org_id,
        "OrgID": result.get("id"),
        "OrgName": result.get("preferredName"),
        "OrgURL": org_url,
        "TotalDocs": result["metrics"]["documentsCount"],
        "TotalAuthors": result["metrics"]["authorsCount"]
    })

    scopus_com_org_totaldocs_id = 1

    subject_areas = result_subject_area.get("documentsBySubjectAreaCount", [])

    for item_subject_area in subject_areas:
        code = item_subject_area.get("code")
        doc_count = item_subject_area.get("documentsCount")
        subject_name = SUBJECT_MAPPING.get(code, f"Unknown ({code})")

        data_subject_area.append({
            "ScopusComOrgTotalDocsID": scopus_com_org_totaldocs_id,
            "ScopusComOrgID": scopus_com_org_id,
            "SubjectAreas": subject_name,
            "TotalDocs": doc_count
        })
        scopus_com_org_totaldocs_id += 1
    
    
    org_collaborators = result_org_collaborators.get("collaborators", [])
    scopus_com_org_collaborators = 1
    
    for item_org_collaborators in org_collaborators:
        source_name = item_org_collaborators.get("name")
        doc_count = item_org_collaborators.get("mutualDocumentsCount")

        data_org_collaborators.append({
            "ScopusComOrgSourcesID": scopus_com_org_collaborators,
            "ScopusComOrgID": scopus_com_org_id,
            "SourceName": source_name,
            "TotalDocs": doc_count
        })
        scopus_com_org_collaborators += 1
    
    scopus_com_org_id += 1     # (Sesuai permintaan: ID tetap naik di sini)

    print(f"{result['preferredName']} | Docs: {result['metrics']['documentsCount']} | Authors: {result['metrics']['authorsCount']}")

# ======================
# SAVE JSON
# ======================
with open("ScopusComOrg.json", "w", encoding="utf-8") as f:
    json.dump(data_results, f, indent=4, ensure_ascii=False)

with open("ScopusComOrgSubjectAreas.json", "w", encoding="utf-8") as f:
    json.dump(data_subject_area, f, indent=4, ensure_ascii=False)
    
with open("ScopusComOrgSources.json", "w", encoding="utf-8") as f:
    json.dump(data_org_collaborators, f, indent=4, ensure_ascii=False)

print("File JSON berhasil dibuat.")

driver.quit()
print("Selesai. Semua proses sudah dijalankan.")
