# full_scopus_scraper_with_subject_area.py
import time
import random
import json
import datetime
import pyautogui
import undetected_chromedriver as uc
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# ----------------------------
# CONFIG - ganti sesuai kebutuhan
# ----------------------------
LIST_AFFILIATION_ID = [
    '60069377','60069380','60069382','60069383'
]

# Isi kredensial (lebih baik ambil dari env var untuk keamanan)
EMAIL = "fitran.pramakrisna@binus.edu"
PASSWORD = "9January2000!!"

# Driver options
CHROME_VERSION_MAIN = 103  # sesuaikan jika perlu
USE_HEADLESS = False       # false karena kita butuh pyautogui / interaksi

# Retry / timing config
MAX_CAPTCHA_TRIES = 5
MAX_LOGIN_RETRIES = 5
MAX_API_ATTEMPTS_PER_ID = 3

# ----------------------------
# Mapping kode subject -> nama
# ----------------------------
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

# ----------------------------
# Human-like mouse helper
# ----------------------------
def human_like_move(x_target, y_target):
    x_start, y_start = pyautogui.position()
    steps = random.randint(10, 25)
    for i in range(steps):
        x = x_start + (x_target - x_start) * i / steps + random.randint(-2, 2)
        y = y_start + (y_target - y_start) * i / steps + random.randint(-2, 2)
        pyautogui.moveTo(x, y, duration=random.uniform(0.01, 0.05))
    pyautogui.moveTo(x_target, y_target, duration=random.uniform(0.1, 0.2))

# ----------------------------
# Setup Chrome (undetected)
# ----------------------------
options = uc.ChromeOptions()
if USE_HEADLESS:
    options.add_argument("--headless=new")
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = uc.Chrome(options=options, version_main=CHROME_VERSION_MAIN)

# ----------------------------
# Page check helper
# ----------------------------
def page_passed_check(timeout=5):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, "bdd-email"))
        )
        return True
    except TimeoutException:
        return False

# ----------------------------
# CAPTCHA handling (attempts)
# ----------------------------
def try_pass_captcha(checkbox_x=541, checkbox_y=386, max_tries=MAX_CAPTCHA_TRIES):
    for attempt in range(max_tries):
        print(f"[CAPTCHA] Percobaan ke-{attempt+1} ...")
        time.sleep(random.uniform(2.5, 4.5))
        try:
            human_like_move(checkbox_x, checkbox_y)
            time.sleep(random.uniform(0.5, 1.0))
            pyautogui.click()
            time.sleep(random.uniform(5, 8))
        except Exception as e:
            print("[CAPTCHA] pyautogui error:", e)

        if page_passed_check():
            print("[CAPTCHA] Berhasil lewat halaman CAPTCHA.")
            return True
        else:
            print("[CAPTCHA] Masih terdeteksi CAPTCHA, ulangi.")
    print("[CAPTCHA] Gagal melewati CAPTCHA setelah beberapa percobaan.")
    return False

# ----------------------------
# Login function
# ----------------------------
def login_scopus(email, password):
    try:
        sign_in_url = "https://www.scopus.com/signin.uri?origin=&zone=TopNavBar"
        driver.get(sign_in_url)
        time.sleep(1)
        driver.get(sign_in_url)
        time.sleep(1)

        # Attempt to pass captcha if present
        try_pass_captcha()

        # Try to accept cookies if visible
        try:
            cookies_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'))
            )
            driver.execute_script("arguments[0].click();", cookies_btn)
            print("[LOGIN] Cookies accepted.")
        except Exception:
            print("[LOGIN] Cookies button not found or clickable (continuing).")

        # Fill email -> next -> password -> login
        for attempt in range(MAX_LOGIN_RETRIES):
            try:
                email_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="bdd-email"]'))
                )
                email_input.clear()
                email_input.send_keys(email)
                time.sleep(1.5)

                next_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="bdd-elsPrimaryBtn"]'))
                )
                next_btn.click()
                time.sleep(2)

                password_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="bdd-password"]'))
                )
                password_input.clear()
                password_input.send_keys(password)
                time.sleep(1.5)

                login_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="bdd-elsPrimaryBtn"]'))
                )
                login_btn.click()
                time.sleep(3)

                # verify login by checking presence of some element (TopNav or user menu)
                # If still the sign-in page, retry
                if page_passed_check(timeout=3):
                    # still sign-in inputs => login maybe failed; continue retry
                    print(f"[LOGIN] Masih di halaman sign-in, percobaan {attempt+1} gagal.")
                    time.sleep(2)
                    continue
                print("[LOGIN] Login mungkin berhasil (lanjut).")
                return True
            except (TimeoutException, NoSuchElementException) as e:
                print(f"[LOGIN] Percobaan login {attempt+1} gagal: {e}")
                time.sleep(2)
        print("[LOGIN] Gagal login setelah beberapa percobaan.")
        return False
    except Exception as e:
        print("[LOGIN] Exception saat login:", e)
        return False

# ----------------------------
# API access functions
# ----------------------------
def access_scopus_org_api(affiliation_id, access_reset_after=5):
    try:
        access_count = 0
        url_home = "https://www.scopus.com/"
        while True:
            driver.get(url_home)
            time.sleep(1)
            url = f"https://www.scopus.com/gateway/organisation-profile-api/organizations/{affiliation_id}"
            driver.get(url)
            time.sleep(1)
            try:
                # page body contains raw JSON
                data = driver.execute_script("return JSON.parse(document.body.innerText);")
            except Exception as e:
                print(f"[ORG API] JSON parse error for {affiliation_id}: {e}")
                return None

            access_count += 1
            if access_count >= access_reset_after:
                access_count = 0
            return data
    except WebDriverException as e:
        print(f"[ORG API] WebDriverException for {affiliation_id}: {e}")
        return None

# ----------------------------
# UPDATED: Subject-area API using fetch + credentials include
# ----------------------------
def access_scopus_subject_area_api(affiliation_id):
    try:
        api_url = f"https://www.scopus.com/gateway/organisation-profile-api/organizations/{affiliation_id}/documents/subject-area"

        js = f"""
        return fetch("{api_url}", {{
            method: "GET",
            credentials: "include",
            headers: {{
                "Accept": "application/json, text/plain, */*"
            }}
        }}).then(r => r.json()).catch(e => {{ return {'_fetch_error': String(e) }}} );
        """

        data = driver.execute_script(js)
        if isinstance(data, dict) and data.get("_fetch_error"):
            print(f"[SUBJECT API] Fetch error for {affiliation_id}: {data.get('_fetch_error')}")
            return None

        return data
    except WebDriverException as e:
        print(f"[SUBJECT API] WebDriverException for {affiliation_id}: {e}")
        return None
    except Exception as e:
        print(f"[SUBJECT API] Unexpected error for {affiliation_id}: {e}")
        return None

# ----------------------------
# MAIN: run login, loop, collect and save
# ----------------------------
def main():
    started = datetime.date.today().strftime("%d/%m/%Y")
    # login
    ok = login_scopus(EMAIL, PASSWORD)
    if not ok:
        print("Tidak bisa login. Hentikan program.")
        driver.quit()
        return

    data_results = []
    subject_area_results = []

    scopus_com_org_id = 1
    scopus_com_org_totaldocs_id = 1

    for affiliation_id in LIST_AFFILIATION_ID:
        print(f"--- Mengambil data untuk affiliation_id: {affiliation_id} ---")
        org_result = None
        for attempt in range(MAX_API_ATTEMPTS_PER_ID):
            org_result = access_scopus_org_api(affiliation_id)
            time.sleep(1)
            if org_result is None:
                print(f"[ORG] Gagal fetch {affiliation_id} (attempt {attempt+1})")
                time.sleep(2)
                continue
            break

        if org_result is None:
            print(f"[ORG] Gagal total untuk {affiliation_id}, dilewati.")
            continue

        # Validasi minimal (sesuaikan jika struktur berbeda)
        metrics = org_result.get("metrics", {})
        docs_count = metrics.get("documentsCount", 0)
        authors_count = metrics.get("authorsCount", 0)
        preferred_name = org_result.get("preferredName") or ""
        org_id_value = org_result.get("id") or affiliation_id

        # Skip jika kosong total docs & authors & name (opsional)
        if not preferred_name and docs_count == 0 and authors_count == 0:
            print(f"[ORG] affiliation_id {affiliation_id} kemungkinan tidak ditemukan, dilewati.")
            continue

        org_url = f"https://www.scopus.com/pages/organization/{affiliation_id}"

        # Simpan hasil organisasi
        data_results.append({
            "ScopusComOrgID": scopus_com_org_id,
            "OrgID": org_id_value,
            "OrgName": preferred_name,
            "OrgURL": org_url,
            "TotalDocs": docs_count,
            "TotalAuthors": authors_count,
            "retrieve_date": started
        })

        print(f"[ORG] {preferred_name} | Docs: {docs_count} | Authors: {authors_count}")

        # Ambil subject-area API
        subject_data = None
        for attempt in range(MAX_API_ATTEMPTS_PER_ID):
            subject_data = access_scopus_subject_area_api(affiliation_id)
            time.sleep(1)
            if subject_data is None:
                print(f"[SUBJECT] Gagal fetch subject-area {affiliation_id} (attempt {attempt+1})")
                time.sleep(2)
                continue
            break

        if subject_data and isinstance(subject_data, dict):
            # Perubahan: gunakan key yang benar documentsBySubjectAreaCount (dengan fallback)
            subject_list = subject_data.get("documentsBySubjectAreaCount") or subject_data.get("documentsBySubjectArea") or subject_data.get("subjectAreas") or subject_data.get("subject_area") or []
            if not subject_list:
                print(f"[SUBJECT] documentsBySubjectAreaCount kosong untuk {affiliation_id}.")
            else:
                for item in subject_list:
                    code = item.get("code") or item.get("abbr") or item.get("subjectAreaCode") or None
                    docs = item.get("documentsCount") or item.get("documents") or 0
                    mapped = SUBJECT_MAPPING.get(code, "Unknown") if code else "Unknown"

                    subject_area_results.append({
                        "ScopusComOrgTotalDocsID": scopus_com_org_totaldocs_id,
                        "ScopusComOrgID": scopus_com_org_id,  # foreign key to data_results
                        "SubjectAreas": mapped,
                        "TotalDocs": docs
                    })
                    scopus_com_org_totaldocs_id += 1

        else:
            print(f"[SUBJECT] Tidak dapat mengambil subject-area untuk {affiliation_id}.")

        # increment parent id for next organization
        scopus_com_org_id += 1

        # jeda antar organisasi supaya tidak terlalu agresif
        time.sleep(random.uniform(1.5, 3.5))

    # Jika tidak ada data, berhenti
    if not data_results:
        print("Tidak ada data organisasi yang berhasil diambil. Tutup driver.")
        driver.quit()
        return

    # Simpan ke JSON files
    with open("scopus_results.json", "w", encoding="utf-8") as f:
        json.dump(data_results, f, indent=4, ensure_ascii=False)
    print("File scopus_results.json berhasil dibuat.")

    with open("scopus_subject_area_results.json", "w", encoding="utf-8") as f:
        json.dump(subject_area_results, f, indent=4, ensure_ascii=False)
    print("File scopus_subject_area_results.json berhasil dibuat.")

    # close driver
    driver.quit()
    print("Selesai. Driver ditutup.")

if __name__ == "__main__":
    main()
