from bs4 import BeautifulSoup
import requests, re
import pandas as pd

def extract(age,start, subject):

    #age fo offer in days
    #start page starts at which offer
    #subject (ex: data science)
    
    tmp = subject.split()
    job = "%20".join(tmp)
    headers ={'Users-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'}
    url = f'https://fr.indeed.com/emplois?q={job}&jt=internship&fromage={age}&start={start}&vjk=18772eed35c54440'
    r = requests.get(url,headers)
    soup = BeautifulSoup(r.content,'html.parser')
    return soup


def transform(soup,offerlist):
    divs= soup.find("div", class_="mosaic-provider-jobcards")
    title_items = divs.find_all("div",class_="heading4 color-text-primary singleLineTitle tapItem-gutter")
    comp_items =  divs.find_all("span", class_="companyName")
    date_items =  divs.find_all("span", class_="date")
    location_items = divs.find_all("div", class_="companyLocation")
    link_items = divs.find_all("a",{'class' : re.compile('.*job.*')})

    for i in range(len(title_items)):
        title = title_items[i].find_all('span')[-1].text
        company = comp_items[i].text
        freshness = [c.strip() for c in date_items[i] if c.name is None and c.strip() != ''][0]
        location = location_items[i].text
        pre = "https://fr.indeed.com"
        link = link_items[i]['href']
        if ".com" not in link:
            link = pre + link

        offer ={'title':title,
                'company':company,
                'freshness':freshness,
                'location':location,
                'link':link
                } 
        offerlist.append(offer)
    return


############### parameters
max_date= 7 #7 day old offers 
subjects =["data science","data analysis"]
pages = 5
########################""""

offerlist=[]
for subject in subjects:
    for i in range (0,pages*10,10):
        soup = extract (max_date,i,subject)
        transform(soup,offerlist)

df = pd.DataFrame(offerlist)
print(df.head())
df.to_excel('offers.xlsx') # or to_csv 


 