import time
import random
import logging
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configure Logging (Saves to file silently)
logging.basicConfig(filename='universal_form_bot.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


# ==========================================
# API Helper Functions
# ==========================================
def fetch_random_identity():
    """Fetches a realistic fake identity from the RandomUser API."""
    try:
        response = requests.get("https://randomuser.me/api/?nat=in", timeout=10)
        response.raise_for_status()
        data = response.json()['results'][0]

        first_name = data['name']['first']
        last_name = data['name']['last']

        # Force @gmail.com to replace the API's default @example.com
        random_num = random.randint(100, 9999)
        custom_email = f"{first_name.lower()}.{last_name.lower()}{random_num}@gmail.com"

        return {
            "full_name": f"{first_name} {last_name}",
            "email": custom_email,
            "age": str(data['dob']['age'])
        }
    except Exception as e:
        logging.warning(f"Identity API failed: {e}. Using fallback.")
        random_id = random.randint(1000, 9999)
        return {
            "full_name": f"Test User {random_id}",
            "email": f"test.user{random_id}@gmail.com",
            "age": str(random.randint(18, 25))
        }


def fetch_random_feedback():
    """Dynamically generates unique, generalized feedback by combining sentence fragments."""
    import random

    # 1. How the sentence starts
    openers = [
        "",
        "Honestly, ",
        "In my experience, ",
        "From what I can tell, ",
        "Overall, ",
        "To be honest, ",
        "As a first-time user, "
    ]

    # 2. The core observation
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

    # 3. The concluding thought
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

    # Combine one from each list to create a completely unique sentence
    opener = random.choice(openers)
    observation = random.choice(observations)
    conclusion = random.choice(conclusions)

    # Example output: "Overall, the user interface is quite intuitive. Keep up the good work."
    final_feedback = f"{opener}{observation}. {conclusion}"

    # Capitalize the first letter just in case the opener was blank
    final_feedback = final_feedback[0].upper() + final_feedback[1:]

    return final_feedback


# ==========================================
# The Universal Bot
# ==========================================
class UniversalGoogleFormBot:
    def __init__(self, form_url, headless=True):
        self.form_url = form_url
        self.options = webdriver.ChromeOptions()
        if headless:
            self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        # Suppress noisy terminal logs from Selenium
        self.options.add_argument("--log-level=3")

        self.driver = webdriver.Chrome(options=self.options)
        self.wait = WebDriverWait(self.driver, 10)

    def _random_delay(self, min_seconds=0.7, max_seconds=2.2):
        time.sleep(random.uniform(min_seconds, max_seconds))

    def _human_type(self, element, text):
        """Simulates human typing to dodge behavioral CAPTCHAs."""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.03, 0.15))

    def _js_click(self, element):
        """Safely scrolls to and clicks an element using JavaScript."""
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(random.uniform(0.3, 0.6))
        self.driver.execute_script("arguments[0].click();", element)

    def open_form(self):
        self.driver.get(self.form_url)
        self._random_delay(2, 4)

    def process_text_inputs(self, identity):
        inputs = self.driver.find_elements(By.XPATH,
                                           '//input[@type="text" or @type="email" or @type="url" or @type="number"]')
        for idx, field in enumerate(inputs):
            try:
                if not field.is_displayed(): continue

                label = (field.get_attribute("aria-label") or "").lower()

                # Check for hidden labels (fixes the "Name" field issue)
                labelledby_ids = field.get_attribute("aria-labelledby")
                if labelledby_ids:
                    try:
                        for l_id in labelledby_ids.split():
                            label_element = self.driver.find_element(By.ID, l_id)
                            label += " " + label_element.text.lower()
                    except Exception:
                        pass

                field_type = field.get_attribute("type")

                if "name" in label:
                    text_to_enter = identity["full_name"]
                elif "email" in label or field_type == "email":
                    text_to_enter = identity["email"]
                elif "age" in label or "years" in label:
                    text_to_enter = identity["age"]
                elif "phone" in label or "mobile" in label or "contact" in label:
                    text_to_enter = str(random.randint(9000000000, 9999999999))
                else:
                    text_to_enter = f"N/A"

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

                # Dodge the "Send Receipt" trap to prevent CAPTCHAs
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
                options = self.driver.find_elements(By.XPATH,
                                                    '//div[@role="option" and @aria-selected="false" and not(contains(@style, "display: none"))]')
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
                if self.driver.find_elements(By.XPATH,
                                             '//div[contains(text(), "recorded") or contains(text(), "Submit another response")]'):
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
# Execution (CLI Version)
# ==========================================
if __name__ == "__main__":
    print("========================================")
    print("      🚀 CLI UNIVERSAL FORM BOT 🚀      ")
    print("========================================\n")

    # Get inputs directly from the terminal
    TARGET_FORM_URL = ""
    while not TARGET_FORM_URL.startswith("http"):
        TARGET_FORM_URL = input("🔗 Enter Form URL: ").strip()

    NUMBER_OF_SUBMISSIONS = 0
    while NUMBER_OF_SUBMISSIONS <= 0:
        try:
            NUMBER_OF_SUBMISSIONS = int(input("🔢 Number of Submissions: "))
        except ValueError:
            pass

    headless_input = input("👻 Run hidden in background? (y/n) [default: y]: ").strip().lower()
    run_headless = False if headless_input == 'n' else True

    print("\n⚙️  Initializing Chrome WebDriver...")
    tester = UniversalGoogleFormBot(TARGET_FORM_URL, headless=run_headless)

    try:
        print("✅ Ready. Starting sequence...\n")
        for i in range(NUMBER_OF_SUBMISSIONS):
            identity = fetch_random_identity()
            print(f"[{i + 1}/{NUMBER_OF_SUBMISSIONS}] 👤 Persona: {identity['full_name']} | ✉️ {identity['email']}")

            tester.open_form()
            is_success = tester.navigate_and_submit(identity)

            if is_success:
                print(f"   🟢 SUCCESS: Form submitted.")
            else:
                print(f"   🔴 FAILED: Validation or navigation error.")

            if i < NUMBER_OF_SUBMISSIONS - 1:
                sleep_time = random.uniform(3.0, 5.0)
                print(f"   ⏳ Cooldown: Waiting {sleep_time:.1f}s...\n")
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\n🛑 Process interrupted by user.")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
    finally:
        tester.close()
        print("\n🏁 Automation complete. Browser closed.")