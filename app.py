import time
import random
import logging
import requests
import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ==========================================
# Data Generation Helpers
# ==========================================
def fetch_random_identity():
    """Fetches a realistic fake identity from the RandomUser API."""
    try:
        response = requests.get("https://randomuser.me/api/?nat=in", timeout=10)
        response.raise_for_status()
        data = response.json()['results'][0]

        first_name = data['name']['first']
        last_name = data['name']['last']

        random_num = random.randint(100, 9999)
        custom_email = f"{first_name.lower()}.{last_name.lower()}{random_num}@gmail.com"

        return {
            "full_name": f"{first_name} {last_name}",
            "email": custom_email,
            "age": str(data['dob']['age'])
        }
    except Exception as e:
        random_id = random.randint(1000, 9999)
        return {
            "full_name": f"Test User {random_id}",
            "email": f"test.user{random_id}@gmail.com",
            "age": str(random.randint(18, 25))
        }

def fetch_random_feedback():
    """Dynamically generates unique, generalized feedback locally to avoid API rate limits."""
    openers = ["", "Honestly, ", "In my experience, ", "From what I can tell, ", "Overall, ", "To be honest, ", "As a first-time user, "]
    observations = [
        "the platform is very smooth and responsive",
        "the user interface is quite intuitive",
        "navigation is a breeze",
        "the core features work flawlessly",
        "the design is clean and modern",
        "it was incredibly easy to figure out",
        "the layout makes a lot of sense",
        "the application process felt very seamless"
    ]
    conclusions = [
        "Great job!", 
        "Keep up the good work.", 
        "I wouldn't really change a thing right now.", 
        "Looking forward to using it more.", 
        "No major complaints from my end.", 
        "It serves its purpose perfectly.",
        "A dark mode would be nice, but otherwise it's great.",
        "Everything seems to be working exactly as intended."
    ]
    
    opener = random.choice(openers)
    observation = random.choice(observations)
    conclusion = random.choice(conclusions)
    
    final_feedback = f"{opener}{observation}. {conclusion}"
    return final_feedback[0].upper() + final_feedback[1:]

# ==========================================
# The Universal Bot
# ==========================================
class UniversalGoogleFormBot:
    def __init__(self, form_url, headless=True):
        self.form_url = form_url
        self.options = webdriver.ChromeOptions()
        
        # Cloud & Headless configurations
        if headless:
            self.options.add_argument('--headless=new')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage') # CRITICAL FOR DOCKER/RENDER
        self.options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        self.options.add_argument("--log-level=3")
        
        # UNCOMMENT the line below if deploying to Render via Docker!
        self.options.binary_location = '/usr/bin/chromium'

        self.driver = webdriver.Chrome(options=self.options)
        self.wait = WebDriverWait(self.driver, 10)

    def _random_delay(self, min_seconds=0.7, max_seconds=2.2):
        time.sleep(random.uniform(min_seconds, max_seconds))

    def _human_type(self, element, text):
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.03, 0.15))

    def _js_click(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(random.uniform(0.3, 0.6))
        self.driver.execute_script("arguments[0].click();", element)

    def open_form(self):
        self.driver.get(self.form_url)
        self._random_delay(2, 4)

    def process_text_inputs(self, identity):
        inputs = self.driver.find_elements(By.XPATH, '//input[@type="text" or @type="email" or @type="url" or @type="number"]')
        for idx, field in enumerate(inputs):
            try:
                if not field.is_displayed(): continue
                label = (field.get_attribute("aria-label") or "").lower()

                labelledby_ids = field.get_attribute("aria-labelledby")
                if labelledby_ids:
                    try:
                        for l_id in labelledby_ids.split():
                            label_element = self.driver.find_element(By.ID, l_id)
                            label += " " + label_element.text.lower()
                    except Exception:
                        pass

                field_type = field.get_attribute("type")

                if "name" in label: text_to_enter = identity["full_name"]
                elif "email" in label or field_type == "email": text_to_enter = identity["email"]
                elif "age" in label or "years" in label: text_to_enter = identity["age"]
                elif "phone" in label or "mobile" in label or "contact" in label: text_to_enter = str(random.randint(9000000000, 9999999999))
                else: text_to_enter = f"N/A"

                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", field)
                field.clear()
                self._human_type(field, text_to_enter)
                self._random_delay(0.3, 0.8)
            except Exception:
                pass

    def process_textareas(self):
        textareas = self.driver.find_elements(By.XPATH, '//textarea')
        for idx, field in enumerate(textareas):
            try:
                if not field.is_displayed(): continue
                text_to_enter = fetch_random_feedback()
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", field)
                field.clear()
                self._human_type(field, text_to_enter)
                self._random_delay(0.3, 0.8)
            except Exception:
                pass

    def process_radio_groups(self):
        radiogroups = self.driver.find_elements(By.XPATH, '//div[@role="radiogroup"]')
        for idx, group in enumerate(radiogroups):
            try:
                radios = group.find_elements(By.XPATH, './/div[@role="radio"]')
                if radios:
                    choice = random.choice(radios)
                    self._js_click(choice)
                    self._random_delay(0.3, 0.7)
            except Exception:
                pass

    def process_checkboxes(self):
        checkboxes = self.driver.find_elements(By.XPATH, '//div[@role="checkbox"] | //div[@role="switch"]')
        for idx, box in enumerate(checkboxes):
            try:
                if not box.is_displayed(): continue
                label = (box.get_attribute("aria-label") or "").lower()
                if "copy" in label or "receipt" in label or "send me" in label:
                    continue
                if random.random() < 0.3:
                    if box.get_attribute('aria-checked') == 'false':
                        self._js_click(box)
                        self._random_delay(0.2, 0.6)
            except Exception:
                pass

    def process_dropdowns(self):
        dropdowns = self.driver.find_elements(By.XPATH, '//div[@role="listbox"]')
        for idx, dropdown in enumerate(dropdowns):
            try:
                if not dropdown.is_displayed(): continue
                self._js_click(dropdown)
                self._random_delay(1.0, 1.8)
                options = self.driver.find_elements(By.XPATH, '//div[@role="option" and @aria-selected="false" and not(contains(@style, "display: none"))]')
                valid_options = [opt for opt in options if opt.text and opt.text != "Choose"]
                if valid_options:
                    choice = random.choice(valid_options)
                    self._js_click(choice)
                else:
                    self.driver.execute_script("document.body.click();")
                self._random_delay(0.6, 1.2)
            except Exception:
                pass

    def fill_current_page(self, identity):
        self.process_text_inputs(identity)
        self.process_textareas()
        self.process_radio_groups()
        self.process_checkboxes()
        self.process_dropdowns()

    def navigate_and_submit(self, identity):
        max_pages = 10
        current_page = 1
        while current_page <= max_pages:
            self.fill_current_page(identity)
            submit_xpath = '//div[@role="button"]//span[contains(text(), "Submit")]'
            submit_btns = self.driver.find_elements(By.XPATH, submit_xpath)

            if submit_btns and submit_btns[0].is_displayed():
                self._js_click(submit_btns[0])
                self._random_delay(2, 4)
                if self.driver.find_elements(By.XPATH, '//div[contains(text(), "recorded") or contains(text(), "Submit another response")]'):
                    return True
                else:
                    return False

            next_xpath = '//div[@role="button"]//span[contains(text(), "Next")]'
            next_btns = self.driver.find_elements(By.XPATH, next_xpath)

            if next_btns and next_btns[0].is_displayed():
                self._js_click(next_btns[0])
                self._random_delay(2.0, 3.5)
                current_page += 1
            else:
                return False
        return False

    def close(self):
        self.driver.quit()


# ==========================================
# Streamlit UI
# ==========================================
def main():
    st.set_page_config(page_title="AutoForm Bot", page_icon="🚀", layout="centered")
    
    st.title("🚀 Universal Form Bot")
    st.markdown("Automate data entry and load-test your Google Forms with realistic, API-generated identities.")
    
    # Pre-flight checklist warning
    with st.expander("⚠️ REQUIRED: Google Form Settings", expanded=False):
        st.markdown("""
        To ensure the bot runs smoothly without being blocked by Google's security (CAPTCHAs or Sign-in walls), 
        your Google Form **Settings** must match the following configuration:
        
        * **Collect email addresses:** Responder input *(Do NOT set to 'Verified')*
        * **Send responders a copy:** Off *(Prevents CAPTCHA triggers)*
        * **Limit to 1 response:** Off *(Prevents Google Sign-in walls)*
        """)

    with st.container(border=True):
        target_url = st.text_input("🔗 Google Form URL", placeholder="https://forms.gle/...")
        
        col1, col2 = st.columns(2)
        with col1:
            num_submissions = st.number_input("🔢 Number of Submissions", min_value=1, max_value=500, value=5)
        with col2:
            st.write("⚙️ Browser Settings")
            run_headless = st.checkbox("Run in Background (Headless)", value=True, help="Keep checked if running on a server/cloud!")
    
    start_btn = st.button("▶️ Start Automation", use_container_width=True, type="primary")
    
    if start_btn:
        if not target_url.startswith("http"):
            st.error("❌ Please enter a valid URL starting with http:// or https://")
            return
            
        progress_bar = st.progress(0)
        status_box = st.empty()
        log_expander = st.expander("Live Execution Logs", expanded=True)
        
        tester = None
        try:
            with st.spinner("Initializing Chrome WebDriver..."):
                tester = UniversalGoogleFormBot(target_url, headless=run_headless)
            
            for i in range(num_submissions):
                status_box.info(f"Processing submission {i+1} of {num_submissions}...")
                
                identity = fetch_random_identity()
                log_expander.write(f"👤 **Generated Persona:** {identity['full_name']} | ✉️ {identity['email']}")
                
                tester.open_form()
                is_success = tester.navigate_and_submit(identity)
                
                if is_success:
                    log_expander.success(f"✅ Submission {i+1} completed successfully.")
                else:
                    log_expander.error(f"❌ Submission {i+1} failed. Form may have strict validation.")
                
                progress_bar.progress((i + 1) / num_submissions)
                
                if i < num_submissions - 1:
                    sleep_time = random.uniform(3.0, 5.0)
                    log_expander.caption(f"Waiting {sleep_time:.1f}s before next run...")
                    time.sleep(sleep_time)
                    
            status_box.success("🎉 All submissions completed!")
            st.balloons()
            
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
        finally:
            if tester:
                tester.close()
                log_expander.caption("Browser instance closed safely.")

if __name__ == "__main__":
    main()
