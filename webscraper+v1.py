import os
import time
import requests
import undetected_chromedriver as uc
import chromedriver_autoinstaller
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from colorama import init, Style

# Initialize Colorama
init()

def rgb_to_ansi(r, g, b):
    return f'\033[38;2;{r};{g};{b}m'

def color_fade(text, start_color, end_color):
    def interpolate(start, end, factor):
        return int(start + (end - start) * factor)

    start_rgb = tuple(int(start_color[i:i+2], 16) for i in (0, 2, 4))
    end_rgb = tuple(int(end_color[i:i+2], 16) for i in (0, 2, 4))

    gradient_text = ""
    for i, char in enumerate(text):
        factor = i / (len(text) - 1)
        color_rgb = tuple(interpolate(start, end, factor) for start, end in zip(start_rgb, end_rgb))
        gradient_text += rgb_to_ansi(*color_rgb) + char
    return gradient_text + Style.RESET_ALL

def set_console_title(title):
    while True:
        for i in range(len(title)):
            os.system(f"title {title[:i+1]}")
            time.sleep(0.1)
        time.sleep(1)
        for i in range(len(title), 0, -1):
            os.system(f"title {title[:i-1]}")
            time.sleep(0.05)
        time.sleep(1)

def setup_chrome_driver():
    # Automatically install the correct version of ChromeDriver
    chromedriver_path = chromedriver_autoinstaller.install()
    
    if not chromedriver_path:
        print("Failed to install ChromeDriver.")
        return None

    # Set up undetected ChromeDriver with the correct version
    options = uc.ChromeOptions()
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-web-security")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.headless = False  # Run in non-headless mode for debugging
    
    try:
        # Initialize Chrome with undetected_chromedriver
        driver = uc.Chrome(options=options, driver_executable_path=chromedriver_path)
        return driver
    except Exception as e:
        print(f"Error setting up ChromeDriver: {e}")
        return None

def main():
    import threading
    title_thread = threading.Thread(target=set_console_title, args=("WebScraper+ By Germanized",), daemon=True)
    title_thread.start()

    url = input(color_fade("Enter the URL of the website you want to copy: ", "00ffff", "0000ff")).strip()
    if not urlparse(url).scheme:
        url = 'http://' + url  # Ensure URL has a scheme

    github_pages = input(color_fade("Would you like this to be GitHub Pages compatible? (Y/N): ", "00ffff", "0000ff")).strip().lower()
    github_pages_compatible = github_pages == 'y'

    manual_visit = input(color_fade("Would you like to manually visit the website? (Y/N): ", "00ffff", "0000ff")).strip().lower() == 'y'
    start_scraping = not manual_visit and input(color_fade("Would you like to start scraping after typing 'scrape' in the cmd? (Y/N): ", "00ffff", "0000ff")).strip().lower() == 'y'

    base_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), urlparse(url).netloc)
    print(color_fade("Opening the website. Type 'scrape' and press Enter to start scraping.", "00ffff", "0000ff"))

    if manual_visit:
        driver = setup_chrome_driver()
        if driver:
            try:
                driver.get(url)
                print(color_fade(f"Website opened. Manually inspect the site. Type 'scrape' and press Enter to start scraping.", "00ffff", "0000ff"))
                while True:
                    command = input(color_fade("> ", "00ffff", "0000ff")).strip().lower()
                    if command == 'scrape':
                        save_content(url, base_directory, github_pages_compatible)
                        break
                    else:
                        print(color_fade("Invalid command. Type 'scrape' to start scraping.", "ff0000", "000000"))
            finally:
                driver.quit()
    else:
        driver = None
        max_retries = 5
        retry_delay = 5  # in seconds
        retry_count = 0

        while retry_count < max_retries:
            try:
                driver = setup_chrome_driver()
                if driver:
                    driver.get(url)
                    print(color_fade("Page loaded. Type 'scrape' to start scraping.", "00ffff", "0000ff"))
                    
                    if start_scraping:
                        while True:
                            command = input(color_fade("> ", "00ffff", "0000ff")).strip().lower()
                            if command == 'scrape':
                                save_content(url, base_directory, github_pages_compatible)
                                break
                            else:
                                print(color_fade("Invalid command. Type 'scrape' to start scraping.", "ff0000", "000000"))
                    break
            except Exception as e:
                if "ERR_SSL_PROTOCOL_ERROR" in str(e):
                    print(f"SSL error occurred: {e}. Retrying in {retry_delay} seconds...")
                else:
                    print(f"Error occurred: {e}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_count += 1
            finally:
                if driver:
                    driver.quit()
        
        if retry_count >= max_retries:
            print(color_fade("Failed to open the website after several attempts.", "ff0000", "000000"))

def fetch_page_source(driver):
    try:
        print("Page loaded. Type 'scrape' and press Enter to start scraping.")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        return driver.page_source
    except Exception as e:
        print(f"Error fetching page source: {e}")
        return None

def save_content(url, directory, github_pages_compatible):
    # Ensure the URL has a scheme
    if not urlparse(url).scheme:
        url = 'http://' + url

    print(color_fade("Fetching content from: ", "00ffff", "0000ff") + url)
    if not os.path.exists(directory):
        os.makedirs(directory)

    driver = None
    page_source = None
    try:
        driver = setup_chrome_driver()
        if driver is None:
            return
        
        driver.get(url)
        page_source = fetch_page_source(driver)
        
        if page_source:
            soup = BeautifulSoup(page_source, 'html.parser')
            if github_pages_compatible:
                save_github_pages_compatible(soup, directory, url)
            else:
                save_html(soup, directory, url)
                save_assets(soup, directory, url)
        else:
            print(color_fade("Failed to retrieve page source.", "ff0000", "000000"))
    finally:
        if driver:
            driver.quit()

def save_github_pages_compatible(soup, directory, url):
    html_content = str(soup)
    js_files = [js.get('src') for js in soup.find_all('script') if js.get('src')]
    css_files = [css.get('href') for css in soup.find_all('link', {'rel': 'stylesheet'}) if css.get('href')]

    # Save HTML as index.html
    with open(os.path.join(directory, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(color_fade(f"Saved GitHub Pages-compatible HTML: {os.path.join(directory, 'index.html')}", "00ffff", "0000ff"))

    # Save JavaScript files
    for js_url in js_files:
        save_asset(urljoin(url, js_url), os.path.join(directory, 'scripts.js'))

    # Save CSS files
    for css_url in css_files:
        save_asset(urljoin(url, css_url), os.path.join(directory, 'styles.css'))

def save_html(soup, directory, url):
    parsed_url = urlparse(url)
    filename = 'index.html' if parsed_url.path == '/' else os.path.basename(parsed_url.path)
    filepath = os.path.join(directory, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print(color_fade(f"Saved HTML: {filepath}", "00ffff", "0000ff"))

def save_assets(soup, directory, base_url):
    tags = soup.find_all(['img', 'link', 'script'])
    for tag in tags:
        url_attr = 'src' if tag.name == 'script' else 'href' if tag.name == 'link' else 'src'
        asset_url = tag.get(url_attr)
        if asset_url:
            asset_url = urljoin(base_url, asset_url)
            save_asset(asset_url, directory)

def save_asset(url, directory):
    parsed_url = urlparse(url)
    asset_path = os.path.join(directory, parsed_url.netloc, parsed_url.path.lstrip('/'))
    asset_dir = os.path.dirname(asset_path)

    if not os.path.exists(asset_dir):
        os.makedirs(asset_dir)

    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(asset_path, 'wb') as f:
                f.write(response.content)
            print(color_fade(f"Saved asset: {asset_path}", "00ffff", "0000ff"))
        else:
            print(color_fade(f"Failed to retrieve asset: {url}", "ff0000", "000000"))
    except requests.exceptions.SSLError as e:
        print(color_fade(f"SSL error while retrieving asset: {url}", "ff0000", "000000"))
    except Exception as e:
        print(color_fade(f"Error while retrieving asset: {url}", "ff0000", "000000"))

def main():
    import threading
    title_thread = threading.Thread(target=set_console_title, args=("WebScraper+ By Germanized",), daemon=True)
    title_thread.start()

    url = input(color_fade("Enter the URL of the website you want to copy: ", "00ffff", "0000ff")).strip()
    if not urlparse(url).scheme:
        url = 'http://' + url  # Ensure URL has a scheme

    github_pages = input(color_fade("Would you like this to be GitHub Pages compatible? (Y/N): ", "00ffff", "0000ff")).strip().lower()
    github_pages_compatible = github_pages == 'y'

    manual_visit = input(color_fade("Would you like to manually visit the website? (Y/N): ", "00ffff", "0000ff")).strip().lower() == 'y'
    start_scraping = not manual_visit and input(color_fade("Would you like to start scraping after typing 'scrape' in the cmd? (Y/N): ", "00ffff", "0000ff")).strip().lower() == 'y'

    base_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), urlparse(url).netloc)
    print(color_fade("Opening the website. Type 'scrape' and press Enter to start scraping.", "00ffff", "0000ff"))

    if manual_visit:
        driver = setup_chrome_driver()
        if driver:
            try:
                driver.get(url)
                print(color_fade(f"Website opened. Manually inspect the site. Type 'scrape' and press Enter to start scraping.", "00ffff", "0000ff"))
                while True:
                    command = input(color_fade("> ", "00ffff", "0000ff")).strip().lower()
                    if command == 'scrape':
                        save_content(url, base_directory, github_pages_compatible)
                        break
                    else:
                        print(color_fade("Invalid command. Type 'scrape' to start scraping.", "ff0000", "000000"))
            finally:
                driver.quit()
    else:
        driver = None
        max_retries = 5
        retry_delay = 5  # in seconds
        retry_count = 0

        while retry_count < max_retries:
            try:
                driver = setup_chrome_driver()
                if driver:
                    driver.get(url)
                    print(color_fade("Page loaded. Type 'scrape' to start scraping.", "00ffff", "0000ff"))
                    
                    if start_scraping:
                        while True:
                            command = input(color_fade("> ", "00ffff", "0000ff")).strip().lower()
                            if command == 'scrape':
                                save_content(url, base_directory, github_pages_compatible)
                                break
                            else:
                                print(color_fade("Invalid command. Type 'scrape' to start scraping.", "ff0000", "000000"))
                    break
            except Exception as e:
                print(f"Error occurred: {e}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_count += 1
            finally:
                if driver:
                    driver.quit()
        
        if retry_count >= max_retries:
            print(color_fade("Failed to open the website after several attempts.", "ff0000", "000000"))

if __name__ == "__main__":
    main()
