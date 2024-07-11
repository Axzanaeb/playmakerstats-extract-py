import os
import json
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from odd_calculator import calculate_probabilities, calculate_odds, adjust_for_margin
from match import Match

USERNAME = 'jorgelopes371'
PASSWORD = 'Zerozero666!'


def extract_games(driver, url):
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "fixture_games")))
        fixture_games_div = driver.find_element(By.ID, "fixture_games")
        game_rows = fixture_games_div.find_elements(By.TAG_NAME, 'tr')
        season_year_element = driver.find_element(
            By.XPATH, "//div[@class='text']/a[contains(text(), 'AFP Amarante')]")
        season_year_text = season_year_element.get_attribute('innerText')
        season_year = season_year_text.split()[-1]

        matches = []
        date = None
        for row in game_rows:
            columns = row.find_elements(By.TAG_NAME, "td")
            date = columns[0].get_attribute(
                'innerText').strip().split("/") if not date else date
            team_a = columns[1].get_attribute('innerText').strip()
            team_b = columns[5].get_attribute('innerText').strip()
            result = columns[3].get_attribute('innerText').strip()

            if int(date[1]) < 7:
                match = Match(team_a, team_b, result, f"20{
                              season_year[-2:]}/{date[1]}/{date[0]}")
            else:
                match = Match(team_a, team_b, result, f"20{
                              season_year[:-3]}/{date[1]}/{date[0]}")

            matches.append(match)

        return matches
    except Exception as e:
        print(f"Error extracting games: {e}")
        return []


def group_matches(matches):
    grouped_matches = {}
    for match in matches:
        key = (match.team_a, match.team_b)
        grouped_matches.setdefault(key, []).append(match)
    return grouped_matches


def login(driver):
    driver.get("https://www.playmakerstats.com/login.php")
    try:
        driver.find_element(By.CLASS_NAME, 'username').send_keys(USERNAME)
        driver.find_element(By.NAME, 'login_password').send_keys(PASSWORD)
        driver.find_element(By.NAME, "go").click()
    except Exception as e:
        print("Already logged in, proceeding..")


def accept_cookies(driver):
    driver.get("https://www.playmakerstats.com")
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, '//button[@id="didomi-notice-agree-button"]'))).click()
        print("Accepted cookies, refreshing..")
    except Exception as e:
        print("No cookies to accept, proceeding..")


def extract_seasons(driver):
    url = f"https://www.playmakerstats.com/edition.php?id={178913}"
    driver.get(url)
    seasons = driver.find_element(By.ID, "id_edicao")

    all_seasons = [season.get_attribute(
        'value') for season in seasons.find_elements(By.CSS_SELECTOR, 'option')]

    existing_files = os.listdir('.')

    exported_seasons = set()
    for filename in existing_files:
        if filename.startswith('matches-') and filename.endswith('.json'):
            season = filename[len('matches-'):-len('.json')]
            exported_seasons.add(season)

    new_seasons = [
        season for season in all_seasons if season not in exported_seasons]

    return new_seasons


def extract_matchweeks(driver, url):
    driver.get(url)

    element = driver.find_element(
        By.NAME, "form_edicao").find_element(By.CSS_SELECTOR, 'span')
    matchweeks = driver.execute_script(
        "return arguments[0].innerText;", element)

    return int(matchweeks.strip().replace('Matchweek', ''))


chromedriver_autoinstaller.install()

USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
fase_param = "183897"
url = 'https://www.playmakerstats.com'
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
current_directory = os.path.dirname(os.path.abspath(__file__))
user_data_dir = os.path.join(current_directory, "user-data")
options.add_argument(f"--user-data-dir={user_data_dir}")

driver = webdriver.Chrome(options=options)

accept_cookies(driver)
login(driver)
for season in extract_seasons(driver):
    season_url = f"{url}/edition.php?id={season}"
    total_matcheweeks = extract_matchweeks(driver, season_url)
    matches = []

    for matchweek in range(1, total_matcheweeks + 1):
        matchweek_url = f"{season_url}&jornada_in={matchweek}"
        matches.extend(extract_games(driver, matchweek_url))

    with open(f"matches/matches-{season}.csv", "w", newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["team_a", "team_b", "result", "match_date"])
        for match in matches:
            csv_writer.writerow(
                [match.team_a, match.team_b, match.result, match.match_date])

    print(f'season({season}) extraction completed')


driver.quit()
