# WebScraper+ V1 By Germanized

WebScraper+ is a Python script designed for scraping and saving website content. It supports GitHub Pages compatibility and provides options for both manual and automated scraping.

## Features

- **Automatic ChromeDriver Installation**: Ensures the correct version of ChromeDriver is installed using `chromedriver-autoinstaller`.
- **Non-Headless Mode**: Runs Chrome in non-headless mode to facilitate debugging.
- **Console Title Animation**: Dynamically changes the console title in a typing effect.
- **Color Gradient Console Output**: Displays text with a gradient color effect using `colorama`.
- **Retry Mechanism**: Automatically retries loading the page if errors occur.
- **Manual and Automated Scraping**: Allows both manual inspection and automatic scraping.
- **GitHub Pages Compatibility**: Option to save content in a format compatible with GitHub Pages.

## Requirements

- Python 3.x
- `requests`
- `undetected_chromedriver`
- `chromedriver-autoinstaller`
- `beautifulsoup4`
- `colorama`
- `selenium`

To install the required packages, use the following command in your terminal:
pip install requests undetected_chromedriver chromedriver-autoinstaller beautifulsoup4 colorama selenium


## Usage

1. **Run the Script**: Execute the script using your Python interpreter.

2. **Input URL**: When prompted, enter the URL of the website you wish to scrape. The script will automatically add the `http://` scheme if it's missing.

3. **GitHub Pages Compatibility**: Indicate whether you want the saved content to be compatible with GitHub Pages.

4. **Manual Visit Option**: Choose if you want to manually visit the website. If selected, the script will open the website in Chrome, and you can type `scrape` in the console to start scraping.

5. **Automatic Scraping**: If you opt for automatic scraping, type `scrape` in the console when prompted after the page is loaded.

6. **Retries**: The script includes a retry mechanism to handle errors like SSL protocol issues. It will attempt to reload the page a specified number of times if an error occurs.

## Functions

- **`rgb_to_ansi(r, g, b)`**: Converts RGB values to ANSI escape codes for color output.
- **`color_fade(text, start_color, end_color)`**: Applies a color gradient to the text.
- **`set_console_title(title)`**: Sets and animates the console title.
- **`setup_chrome_driver()`**: Configures and returns a ChromeDriver instance.
- **`fetch_page_source(driver)`**: Retrieves the page source from the current URL.
- **`save_content(url, directory, github_pages_compatible)`**: Saves the website content to the specified directory, with GitHub Pages compatibility if chosen.
- **`save_github_pages_compatible(soup, directory, url)`**: Saves HTML, JavaScript, and CSS files for GitHub Pages compatibility.
- **`save_html(soup, directory, url)`**: Saves the HTML content to the specified directory.
- **`save_assets(soup, directory, base_url)`**: Downloads and saves assets such as images, scripts, and stylesheets.
- **`save_asset(url, directory)`**: Downloads and saves an individual asset from the given URL.

For detailed usage and to run the script, refer to the provided example and instructions above.

# Webscraper+ V2 attach version

WebScraper+ is a Python-based web scraping tool designed to interact with a Chrome browser using Selenium. It supports fetching and saving website content, including JavaScript and CSS files, with compatibility options for GitHub Pages.

## Features

- **Dynamic Console Title**: Animates the console title to show the current status.
- **Color Gradient Output**: Uses a gradient color effect for console text.
- **ChromeDriver Setup**: Connects to a manually started Chrome instance with remote debugging enabled.
- **Tab Tracking**: Monitors and updates information about open Chrome tabs.
- **Retry Mechanism**: Automatically retries fetching content in case of errors.
- **GitHub Pages Compatibility**: Optionally formats content for GitHub Pages.

## Requirements

- Python 3.x
- `requests`
- `beautifulsoup4`
- `selenium`
- `pygetwindow`
- `colorama`

To install the required packages, run:

pip install requests beautifulsoup4 selenium pygetwindow colorama


## Usage

1. **Start Chrome with Debugging**: Open Chrome manually with the following command:

    ```
    chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chrome_dev_profile"
    ```

2. **Run the Script**: Execute the script using your Python interpreter.

3. **Monitor Tabs**: The script will monitor and list open tabs in Chrome, showing their URLs and titles. 

4. **Select a Tab**: Choose a tab by number to scrape its content.

5. **Save Content**: The script will save the page content to a directory, with options for GitHub Pages compatibility.

## Functions

- **`rgb_to_ansi(r, g, b)`**: Converts RGB values to ANSI escape codes for color output.
- **`color_fade(text, start_color, end_color)`**: Applies a gradient color effect to the text.
- **`set_console_title(title)`**: Animates the console title with a typing effect.
- **`setup_driver(remote_debugging_port=9222)`**: Configures and returns a ChromeDriver instance.
- **`update_tabs(driver)`**: Monitors and updates information about open Chrome tabs.
- **`fetch_with_retries(url, retries=3, delay=5)`**: Fetches the content of a URL with retry on errors.
- **`fetch_page_source(driver)`**: Fetches the page source of the current tab.
- **`save_content(url, directory, github_pages_compatible, driver)`**: Saves the webpage content to the specified directory.
- **`save_github_pages_compatible(soup, directory, url)`**: Saves HTML, JavaScript, and CSS files for GitHub Pages compatibility.
- **`save_html(soup, directory, url)`**: Saves the HTML content to the directory.
- **`save_assets(soup, directory, url)`**: Saves JavaScript and CSS files from the page.

## Example Usage

1. **Open Chrome with Debugging**: Use the command provided above to start Chrome with remote debugging.

2. **Run the Script**: Execute the script in your Python environment. 

3. **Follow Prompts**: Enter the tab number you wish to scrape and specify whether to save the content in a GitHub Pages-compatible format.

## Notes

- Ensure that Chrome is running with remote debugging enabled before starting the script.
- The script uses a retry mechanism for fetching content to handle potential SSL or network errors.

For more detailed instructions or issues, refer to the script's comments or contact the author.


