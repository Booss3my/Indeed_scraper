from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
from operator import itemgetter
import argparse
from zenrows import ZenRowsClient
import os
from dotenv import load_dotenv
from datetime import date,timedelta

today = date.today()
load_dotenv()
# from scrape_proxies import get_healthy_proxies

# print("Looking for healthy free proxies ...")
# healthy_proxies = get_healthy_proxies()
# if len(healthy_proxies)>0:
#     print("Healthy proxies found")



HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Connection": "keep-alive",
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
    job = "+".join(tmp)
    
    url = f'https://fr.indeed.com/jobs?q={job}&fromage={age}&start={start}'
    key = os.environ['antibotbypass_API_KEY']
    client = ZenRowsClient(key)
    response = client.get(url) #replace requests 
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup


def textify(div):
    if div!=None:
        return div.text
    return ""
    


def transform(soup: BeautifulSoup):
    """
    Transforms the parsed HTML content into a list of job offer dictionaries.

    Args:
        soup (BeautifulSoup): Parsed HTML content.
        offerlist (list): List to store the job offer dictionaries.
    """
    offer_list = []
    divs = soup.find_all("div", attrs={"class": re.compile(r"result job")})
    for div in divs:
        title= textify(div.find("span", attrs={"id": re.compile(r"jobTitle")}))
        company = textify(div.find('span', attrs={'data-testid': 'company-name'}))
        location = textify(div.find('div', attrs={'data-testid': 'text-location'}))
        contract = textify(div.find('div', attrs={'data-testid': 'attribute_snippet_testid'}))
        freshness = textify(div.find("span", class_="date"))
        link = textify(div.find("a", {'id':re.compile(r"job")}))       
        offer = {
            'title': title,
            'company': company,
            'freshness': freshness,
            'contract':contract,
            'location': location,
            'link': link
        }
        offer_list.append(offer)

    return pd.DataFrame(offer_list)

def freshness_to_date(freshness) :
    dates = []
    for date in freshness:
        if ("instant" in date) or ("Aujourd'hui" in date) or len(date)==0:
            date = 0
        else:
            print(date)
            date = int(date.split("jour")[0].split("a ")[1].replace(u'\xa0', u''))
        date = today + timedelta(days=-date)
        dates.append(date)
    return dates


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
            df=transform(soup)
            df["date"] = freshness_to_date(df["freshness"])
            offerlist.append(df)

    
    df = pd.concat(offerlist)
    df.sort_values(by=date).to_csv('offers.csv')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Indeed Job Scraper")
    parser.add_argument("--max_date", type=int, default=10, help="Age of offers in days")
    parser.add_argument("--subjects", nargs="+", default=["data science", "data analysis"], help="List of subjects for job offers")
    parser.add_argument("--pages", type=int, default=4, help="Number of pages to scrape per subject")
    args = parser.parse_args()

    main(args.max_date, args.subjects, args.pages)
