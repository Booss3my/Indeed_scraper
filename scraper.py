from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
from operator import itemgetter
import argparse


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
}


def extract(age: int, start: int, subject: str) -> BeautifulSoup:
    """
    Extracts job offers from Indeed based on the given parameters.

    Args:
        age (int): Age of offers in days.
        start (int): Starting page for the offers.
        subject (str): Subject of the job offers.

    Returns:
        BeautifulSoup: Parsed HTML content of the job offers page.
    """
    tmp = subject.split()
    job = "%20".join(tmp)
    url = f'https://fr.indeed.com/emplois?q={job}&jt=internship&fromage={age}&start={start}&vjk=18772eed35c54440'

    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup


def transform(soup: BeautifulSoup, offerlist: list):
    """
    Transforms the parsed HTML content into a list of job offer dictionaries.

    Args:
        soup (BeautifulSoup): Parsed HTML content.
        offerlist (list): List to store the job offer dictionaries.
    """
    divs = soup.find('div', {'class': re.compile('.*jobcards.*')})
    title_items = divs.find_all("div", class_="heading4 color-text-primary singleLineTitle tapItem-gutter")
    comp_items = divs.find_all("span", class_="companyName")
    date_items = divs.find_all("span", class_="date")
    location_items = divs.find_all("div", class_="companyLocation")
    link_items = divs.find_all("a", {'class': re.compile('.*job.*')})

    for i in range(len(title_items)):
        title = title_items[i].find_all('span')[-1].text
        company = comp_items[i].text
        freshness = [c.strip() for c in date_items[i] if c.name is None and c.strip() != ''][0]
        location = location_items[i].text
        pre = "https://fr.indeed.com"
        link = link_items[i]['href']
        if ".com" not in link:
            link = pre + link

        offer = {
            'title': title,
            'company': company,
            'freshness': freshness,
            'location': location,
            'link': link
        }
        offerlist.append(offer)


def sort(offerlist: list) -> list:
    """
    Sorts the list of job offer dictionaries based on freshness.

    Args:
        offerlist (list): List of job offer dictionaries.

    Returns:
        list: Sorted list of job offer dictionaries.
    """
    tmp = [d['freshness'] for d in offerlist]
    for i, date in enumerate(tmp):
        if ("Publiée à l'instant" in date) or ("Aujourd'hui" in date):
            date = 0
        else:
            start_idx = date.find('y a ') + 4
            end_idx = date.find(' jour')
            date = int(date[start_idx:end_idx])

    enumerate_object = enumerate(tmp)
    sorted_pairs = sorted(enumerate_object, key=itemgetter(1))

    sorted_offerlist = [offerlist[index] for index, _ in sorted_pairs]

    return sorted_offerlist


def main(max_date: int, subjects: list, pages: int):
    """
    Main function to extract, transform, sort, and save job offers.

    Args:
        max_date (int): Age of offers in days.
        subjects (list): List of subjects for job offers.
        pages (int): Number of pages to scrape per subject.
    """
    offerlist = []
    for subject in subjects:
        for i in range(0, pages * 10, 10):
            soup = extract(max_date, i, subject)
            transform(soup, offerlist)

    offerlist = sort(offerlist)

    df = pd.DataFrame(offerlist)
    print(df.head())
    df.to_excel('offers.xlsx')  # or to_csv


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Indeed Job Scraper")
    parser.add_argument("--max_date", type=int, default=7, help="Age of offers in days")
    parser.add_argument("--subjects", nargs="+", default=["data science", "data analysis"], help="List of subjects for job offers")
    parser.add_argument("--pages", type=int, default=4, help="Number of pages to scrape per subject")
    args = parser.parse_args()

    main(args.max_date, args.subjects, args.pages)
