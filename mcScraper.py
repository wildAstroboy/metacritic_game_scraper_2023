# As of September 12, 2023, Metacritic has redesigned their website so this script no longer works.
# Based on Metacritic Game Scraper by Julius Johnson
# https://github.com/JuliusJohnson/Metacritic_Game_Scrapper_2020/

import pandas as pd
import time, requests
from bs4 import BeautifulSoup
import pprint

# MetaCritic Dictionary Structure
mc_dict = {'name':[], 'date':[], 'platform':[], 'metascore':[], 'userscore':[]}

# Uses Firefox to navigates the metacritic results pages based of off page number and year
def webPage(pageNumber,year):
    url = 'https://www.metacritic.com/browse/games/score/metascore/year/all/filtered?year_selected='+ str(year) +'&distribution=&sort=desc&view=detailed&page='+ str(pageNumber)
    headers = {'User-agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    #print(response.text)
    return response

# Function to find the number of pages in the results to know how many times to run the scraper function
def numberofPages(response):
    soup = BeautifulSoup(response.text, 'html.parser') # Can optionally use lxml or html5lib to parse the html
    pages = soup('li', {'class':'page last_page'}) # Find the last html element <li class='page last_page'> to find how many pages there are
    pagesFound = pages[0].find('a', {'class':'page_num'}) # Grabbing the page number wrapped in the <a> element
    #print(pagesFound.text)
    return pagesFound.text

# Scraper function to grab the data we want from the webpage
def webScaper(numLoops,content):
    tableNum = 0
    # Need to loop through each section that is separated by ad divs
    while tableNum < numLoops:

        # Getting the Game name
        tableRows = content[tableNum].find_all('tr') # Finding game info which is wrapped in a table row tag <tr>
        # Looping through each <tr> to find <td>
        for tr in tableRows:
            tableData = tr.find_all('td')
            # Looping through each <td> to find <a class:'title'>
            for td in tableData:
                aTag = td.find_all('a',{'class':'title'})
                # Looping through each <a> and grabbing title from <h3>
                for a in aTag:
                    title = a.find('h3')
                    mc_dict['name'].append(title.text)
                    #print(title.text)

        # Getting game release date
        tableRows = content[tableNum].find_all('tr')
        for tr in tableRows:
            tableData = tr.find_all('td')
            # Looping through each <td> to find <div class='clamp-details'>
            for td in tableData:
                div = td.find_all('div',{'class':'clamp-details'})
                # Looping through each <span> to grab the date
                for sp in div:
                    date = sp.find('span',{'class':''})
                    mc_dict['date'].append(date.text)
                    #print(date.text)

        # Getting game platform
        tableRows = content[tableNum].find_all('tr')
        for tr in tableRows:
            tableData = tr.find_all('td')
            # Looping through each <td> to find <div class='platform'>
            for td in tableData:
                div = td.find_all('div', {'class': 'platform'})
                # Looping through the <span> to grab platform
                for sp in div:
                    platform = sp.find('span',{'class':'data'})
                    mc_dict['platform'].append(platform.text.strip())
                    #print(platform.text.strip())

        # Getting Metascore for each game
        # At this point, I hope you understand how we are looping through tags to grab specific data
        tableRows = content[tableNum].find_all('tr')
        for tr in tableRows:
            tableData = tr.find_all('td')
            for td in tableData:
                divTag = td.find_all('div',{'class':'clamp-metascore'})
                for a in divTag:
                    mScore = a.find('div',{'class':'metascore_w'})
                    mc_dict['metascore'].append(mScore.text)
                    #print(mScore.text)

        # Getting Userscore for each game
        tableRows = content[tableNum].find_all('tr')
        for tr in tableRows:
            tableData = tr.find_all('td')
            for td in tableData:
                divTag = td.find_all('div', {'class': 'clamp-userscore'})
                for a in divTag:
                    uScore = a.find('div', {'class': 'metascore_w'})
                    mc_dict['userscore'].append(uScore.text)
                    #print(uScore.text)

        # Next section on page
        tableNum += 1

def init_scraper(pageNumber, year):
    currentPageNum = 0
    # Loop through each page until the last page number is reached
    while currentPageNum < int(pageNumber):
        # Same setup as webPage() and numberofPages() to read html content
        url = 'https://www.metacritic.com/browse/games/score/metascore/year/all/filtered?year_selected=' + str(year) + '&distribution=&sort=desc&view=detailed&page=' + str(currentPageNum)
        headers = {'User-agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.find_all('table')
        #print(content)

        # Game list is separated by ad divs so numLoops is number of sections with game data
        numLoops = len(content)
        # Run scraper with number of sections and html content
        webScaper(numLoops, content)
        currentPageNum += 1
        # Placed after previous code so that printed number matches the page number just parsed
        print("Current page: " + str(currentPageNum))
        pprint.pprint(mc_dict)
        # Sleep so we dont get IP blocked
        time.sleep(6)

# Main function to run
def main():
    # Date range of data you want to gather
    years = list(range(2018,2023))
    for year in years:
        print("Current year: " + str(year))
        # Number of pages for current year
        numPage = numberofPages(webPage(0,year))
        init_scraper(int(numPage), year)
        # Sleep so we dont get IP blocked
        time.sleep(5)

    #print(mc_dict)
    # Put the dictionary into a Data Frame and save it as a csv file
    data = pd.DataFrame.from_dict(mc_dict)
    data.to_csv('rawMetaCriticData_' + str(years[0]) + '_' + str(years[-1]) + '.csv')

main()