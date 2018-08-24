import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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

    OUTPUT
    ------
    {csv}
    '''
    # Get URL by year
    url = 'https://www.basketball-reference.com/leagues/NBA_{}_totals.html'.format(year)
    
    # Pass in Chrome options
    chrome_options = Options()  
    # FIXME: figure out how to get selenium to run Chrome headless 
    # Set headless - Trying to run it in headless seems to break things
    # chrome_options.add_argument("--headless")  
    # Set window size
    # chrome_options.add_argument("--window-size=1920,1080")
    # Set chrome to not load images
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    # chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images":2})


    driver = webdriver.Chrome(chrome_options=chrome_options)

    driver.get(url)
    
    # Try/Except
    timeout = 20

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
        csv = driver.find_element_by_id('csv_totals_stats').text
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
    start_year: {int}

    end_year: {int}

    RETURNS
    -------
    None

    OUTPUT
    ------
    {csv}
    '''
    for year in range(start_year, end_year+1):
        print("Scraping for the {}-{} season".format(year-1,str(year)[-2:]))
        scrape_player(year)


def load_data(filename):
    '''
    This function loads the data from a csv file into a DataFrame and cleans it

    PARAMETERS
    ----------
    filename: {str}

    RETURNS
    -------
    players_df: {pandas.DataFrame}
    '''
    players_df = pd.read_csv(filename)
    # the Rk column is meaningless, so we drop it
    players_df.drop(columns='Rk', inplace=True)
    # Fill missing shot percentage values with 0.0
    players_df.fillna(0.0, inplace=True)

    # Separate name from player id and set the id as the index
    player_id = pd.DataFrame(players_df['Player']\
                .apply(lambda x: x.split('\\')).tolist(),
                columns=['Player', 'id'])

    players_df['Player'] = player_id['Player']
    players_df['id'] = player_id['id']

    # If a player played for multiple teams, only keep his aggregated stats
    tm_total = players_df[players_df['Tm'] == 'TOT']['id'].unique()

    drop_list = []

    for player in tm_total:
        drop_list.extend(players_df[(players_df['id'] == player)\
                        &(players_df['Tm'] != 'TOT')].index)
        
    players_df.drop(drop_list, inplace=True)

    # Set index to player id
    players_df.set_index('id', inplace=True)

    return players_df

def make_dummies(players_df):
    '''
    This function loads the data from a csv file into a DataFrame and cleans it

    PARAMETERS
    ----------
    players_df: {pandas.DataFrame}

    RETURNS
    -------
    players_df: {pandas.DataFrame}
    '''
    # Create dummy variables for position    
    players_df = pd.get_dummies(players_df, columns=['Pos']) 

    # For multiple positions, set individual position indicators on and drop
    # multi-position columns
    positions = ['Pos_C', 'Pos_PF', 'Pos_PG', 'Pos_SG', 'Pos_SF']
    multi_pos = []

    for col in players_df.columns[29:]:
        if col not in positions:
            multi_pos.append(col)

    for pos in multi_pos:
        positions = pos.split('_')[1].split('-')

        for i in range(len(positions)):
            positions[i] = 'Pos_' + positions[i]
            
        for position in positions:
            players_df[position] += players_df[pos]

    players_df.drop(columns=multi_pos, inplace=True)

    return players_df


if __name__ == "__main__":
    scrape_players(1985,2018)
