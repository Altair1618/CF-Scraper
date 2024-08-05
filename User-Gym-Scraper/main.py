from bs4 import BeautifulSoup
from enum import Enum
from typing import Set
import random
import requests
import time


class GymConfig(Enum):
    SOLO = 1
    TEAM = 2
    ALL = 3


# Constants
CODEFORCES_URL: str = f'https://codeforces.com/'


# Configs
USER: str = 'Altr14'
GYM_CONFIG: GymConfig = GymConfig.ALL


# Set of Gym URLs
url: Set[str] = set()


def get_submission_url(user: str, page: int) -> str:
    if page == 1:
        return f'{CODEFORCES_URL}submissions/{user}'
    return f'{CODEFORCES_URL}submissions/{user}/page/{page}'


def is_gym_submission(tds: list) -> bool:
    problem_anchor = tds[3].find('a')
    
    # Check if the submission is a gym submission
    if not problem_anchor['href'].startswith('/gym'):
        return False
    
    # Check if the submission is virtual participation
    sup = tds[2].find('sup')
    if not sup or not sup['title'] == 'Virtual participant':
        return False
    
    # Check if the submission is a team submission or not and filter depending on the configuration
    submitter_href = tds[2].find_all('a')[0]['href']
    
    if GYM_CONFIG == GymConfig.SOLO and submitter_href.startswith('/team'):
        return False
    
    if GYM_CONFIG == GymConfig.TEAM and submitter_href.startswith('/profile'):
        return False

    return True


def main():
    initial_url: str = get_submission_url(USER, 1)

    # Get the first page
    response = requests.get(initial_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Get Max Page
    max_page = int(soup.find_all('div', class_='pagination')[1].find_all('span')[-1].text)
    
    # Iterate over all pages
    for page in range(1, max_page + 1):
        print(f"Scraping page {page} of {max_page}")

        # Add delay to avoid getting kicked
        time.sleep(random.uniform(1, 3))

        response = requests.get(get_submission_url(USER, page))
        soup = BeautifulSoup(response.text, 'html.parser')

        table = soup.find('table', class_='status-frame-datatable')
        submissions = table.find_all('tr')[1:]
        
        for submission in submissions:
            tds = submission.find_all('td')

            if is_gym_submission(tds):
                problem_anchor = tds[3].find('a')
                
                # Remove all url after and including /problem
                gym_url = problem_anchor['href'].split('/problem')[0][1:]

                # print(f'{CODEFORCES_URL}{gym_url}')
                url.add(f'{CODEFORCES_URL}{gym_url}')


    # Write the url to a file
    output_file_name = f'result/{USER}'

    if GYM_CONFIG == GymConfig.SOLO:
        output_file_name += '_solo'
    elif GYM_CONFIG == GymConfig.TEAM:
        output_file_name += '_team'
    else:
        output_file_name += '_all'

    output_file_name += '.txt'

    with open(output_file_name, 'w') as f:
        for u in url:
            f.write(f'{u}\n')


if __name__ == '__main__':
    main()
