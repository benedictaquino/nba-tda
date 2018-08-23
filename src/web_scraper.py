from selenium import webdriver
import selenium.webdriver.chrome.options as c
import selenium.webdriver.firefox.options as f
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException


def scrape_player(year):
    '''
    This function downloads a CSV file from Basketball-Reference.com for a given
    season.

    PARAMETERS
    ----------
    year: {int}

    RETURNS
    -------
    None
    '''
    # Get URL by year
    url = 'https://www.basketball-reference.com/leagues/NBA_{}_per_minute.html'.format(year)
    
    # Pass in Chrome options
    chrome_options = c.Options()  
    # FIXME: figure out how to get selenium to run Chrome headless 
    # Set headless - Trying to run it in headless seems to break things
    # chrome_options.add_argument("--headless")  
    # Set window size
    # chrome_options.add_argument("--window-size=1920,1080")
    # Set chrome to not load images
    chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images":2})


    driver = webdriver.Chrome(chrome_options=chrome_options)

    driver.get(url)
    
    # Try/Except - times out if the button has not loaded in 20 seconds
    timeout=20

    try:
        WebDriverWait(driver, timeout).until(EC.visibility_of_element_located\
                                            ((By.CSS_SELECTOR,
                                            'div.section_heading_text span[href="javascript:void(0)"]')))
        button1 = driver.find_element_by_css_selector\
                ('div.section_heading_text span[href="javascript:void(0)"]')
        button2 = driver.find_element_by_css_selector\
                ('[tip="Export table as <br>suitable for use with excel"]')
        button1.click()
        button2.click()
        csv = driver.find_element_by_id('csv_per_minute_stats').text
        driver.close()
        with open('data/players{}{}.csv'.format(year-1,str(year)[-2:]), 'w+') as f:
            f.write(csv)
        print("Success!")
        
    except TimeoutException:
        print("Timed out waiting for page to load")
        driver.close()


def scrape_players(start_year, end_year):
    '''
    This function downloads a CSV file from Basketball-Reference.com for a given
    range of seasons.

    PARAMETERS
    ----------
    year: {int}

    RETURNS
    -------
    None
    '''
    for year in range(start_year, end_year+1):
        print("Scraping for the {}-{} season".format(year-1,str(year)[-2:]))
        scrape_player(year)

