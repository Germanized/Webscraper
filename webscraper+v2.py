import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
import pygetwindow as gw
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

def setup_driver(remote_debugging_port=9222):
    options = Options()
    options.add_experimental_option("debuggerAddress", f"localhost:{remote_debugging_port}")
    
    driver = None
    while driver is None:
        try:
            driver = webdriver.Chrome(options=options)
        except WebDriverException:
            print(color_fade("Waiting for Chrome to be opened manually with debugging enabled...", "ff0000", "000000"))
            time.sleep(5)
    
    return driver

def update_tabs(driver):
    known_tabs = {}  # Dictionary to keep track of known tabs
    initial_fetch = True
    index = 1

    while True:
        try:
            tabs = driver.window_handles
            current_tabs = {}
            
            for i, tab in enumerate(tabs):
                driver.switch_to.window(tab)
                title = driver.title
                url = driver.current_url
                identifier = f"{index}. {url} ({title})"
                
                if tab not in known_tabs:
                    if initial_fetch:
                        print(color_fade(identifier, "00ffff", "0000ff"))
                    else:
                        print(color_fade(f"New tab: {identifier}", "00ff00", "0000ff"))
                    index += 1
                
                current_tabs[tab] = (url, title)
            
            # Detect closed tabs
            closed_tabs = set(known_tabs) - set(current_tabs)
            for closed_tab in closed_tabs:
                print(color_fade(f"Tab closed: {known_tabs[closed_tab][0]} ({closed_tab})", "ff0000", "0000ff"))
                del known_tabs[closed_tab]
            
            # Update known tabs with the current state
            known_tabs.update({tab: current_tabs[tab] for tab in current_tabs})
            
            initial_fetch = False  # Only print "Fetching tabs..." initially
            
        except WebDriverException:
            print(color_fade("Lost connection to Chrome. Reconnecting...", "ff0000", "000000"))
            driver = setup_driver()
        time.sleep(5)

def fetch_with_retries(url, retries=3, delay=5):
    for _ in range(retries):
        try:
            response = requests.get(url, verify=False)
            response.raise_for_status()
            return response
        except SSLError as e:
            print(f"SSL error: {e}. Retrying...")
            time.sleep(delay)
    raise Exception("Max retries exceeded")

# Usage
try:
    response = fetch_with_retries(urljoin(url, js_url))
    with open(js_path, 'wb') as f:
        f.write(response.content)
except Exception as e:
    print(f"Failed to fetch content: {e}")

def main():
    import threading
    title_thread = threading.Thread(target=set_console_title, args=("WebScraper+ By Germanized",), daemon=True)
    title_thread.start()

    print(color_fade("Please open Chrome manually with the following command:", "00ffff", "0000ff"))
    print(color_fade(r'chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chrome_dev_profile"', "00ff00", "0000ff"))

    driver = setup_driver()
    if not driver:
        print(color_fade("Failed to connect to the running Chrome instance.", "ff0000", "000000"))
        return

    update_tabs_thread = threading.Thread(target=update_tabs, args=(driver,), daemon=True)
    update_tabs_thread.start()

    print("Fetching tabs, please wait...")
    time.sleep(10)  # Give it some time to fetch the tabs
    
    tabs = driver.window_handles
    tab_options = {}
    
    for i, tab in enumerate(tabs):
        driver.switch_to.window(tab)
        url = driver.current_url
        tab_options[i] = url
        print(color_fade(f"{i + 1}. {url}", "00ffff", "0000ff"))
    
    tab_choice = int(input(color_fade("Select a tab by number: ", "00ffff", "0000ff"))) - 1
    selected_url = tab_options.get(tab_choice)
    
    if selected_url:
        driver.switch_to.window(driver.window_handles[tab_choice])
    else:
        print(color_fade("Invalid tab selection.", "ff0000", "000000"))
        return

    github_pages = input(color_fade("Would you like this to be GitHub Pages compatible? (Y/N): ", "00ffff", "0000ff")).strip().lower()
    github_pages_compatible = github_pages == 'y'

    url = driver.current_url
    base_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), urlparse(url).netloc)
    save_content(url, base_directory, github_pages_compatible, driver)

def fetch_page_source(driver):
    try:
        print("Page loaded. Type 'scrape' and press Enter to start scraping.")
        input()  # Wait for user input to start scraping
        return driver.page_source
    except WebDriverException as e:
        print(f"Error fetching page source: {e}")
        return None

def save_content(url, directory, github_pages_compatible, driver):
    print(color_fade("Fetching content from: ", "00ffff", "0000ff") + url)
    if not os.path.exists(directory):
        os.makedirs(directory)

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

def save_github_pages_compatible(soup, directory, url):
    base_url = urlparse(url)
    html_content = str(soup)
    js_files = [js.get('src') for js in soup.find_all('script') if js.get('src')]
    css_files = [css.get('href') for css in soup.find_all('link', {'rel': 'stylesheet'}) if css.get('href')]

    # Update paths in the HTML content
    for js in soup.find_all('script', src=True):
        js['src'] = os.path.join('scripts', os.path.basename(js['src']))

    for css in soup.find_all('link', href=True, rel='stylesheet'):
        css['href'] = os.path.join('styles', os.path.basename(css['href']))

    # Save updated HTML as index.html
    with open(os.path.join(directory, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print(color_fade(f"Saved GitHub Pages-compatible HTML: {os.path.join(directory, 'index.html')}", "00ffff", "0000ff"))

    # Save JavaScript files
    for js_url in js_files:
        js_filename = os.path.basename(js_url)
        js_path = os.path.join(directory, 'scripts', js_filename)
        os.makedirs(os.path.dirname(js_path), exist_ok=True)
        try:
            response = fetch_with_retries(urljoin(url, js_url))
            with open(js_path, 'wb') as f:
                f.write(response.content)
            print(color_fade(f"Saved JavaScript file: {js_path}", "00ffff", "0000ff"))
        except Exception as e:
            print(color_fade(f"Failed to save JavaScript file: {e}", "ff0000", "0000ff"))

    # Save CSS files
    for css_url in css_files:
        css_filename = os.path.basename(css_url)
        css_path = os.path.join(directory, 'styles', css_filename)
        os.makedirs(os.path.dirname(css_path), exist_ok=True)
        try:
            response = fetch_with_retries(urljoin(url, css_url))
            with open(css_path, 'wb') as f:
                f.write(response.content)
            print(color_fade(f"Saved CSS file: {css_path}", "00ffff", "0000ff"))
        except Exception as e:
            print(color_fade(f"Failed to save CSS file: {e}", "ff0000", "0000ff"))



def save_html(soup, directory, url):
    html_path = os.path.join(directory, 'index.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print(color_fade(f"Saved HTML: {html_path}", "00ffff", "0000ff"))

def save_assets(soup, directory, url):
    base_url = urlparse(url)
    js_files = [js.get('src') for js in soup.find_all('script') if js.get('src')]
    css_files = [css.get('href') for css in soup.find_all('link', {'rel': 'stylesheet'}) if css.get('href')]
    
    # Save JavaScript files
    for js_url in js_files:
        js_filename = os.path.basename(js_url)
        js_path = os.path.join(directory, 'scripts', js_filename)
        os.makedirs(os.path.dirname(js_path), exist_ok=True)
        with open(js_path, 'wb') as f:
            f.write(requests.get(urljoin(url, js_url)).content)
        print(color_fade(f"Saved JavaScript file: {js_path}", "00ffff", "0000ff"))

    # Save CSS files
    for css_url in css_files:
        css_filename = os.path.basename(css_url)
        css_path = os.path.join(directory, 'styles', css_filename)
        os.makedirs(os.path.dirname(css_path), exist_ok=True)
        with open(css_path, 'wb') as f:
            f.write(requests.get(urljoin(url, css_url)).content)
        print(color_fade(f"Saved CSS file: {css_path}", "00ffff", "0000ff"))

if __name__ == "__main__":
    main()
