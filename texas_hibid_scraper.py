# TODO add filter for year of vehicle
# TODO add CSV output file for Excel viewing
import json
import os
import pprint
import re
import sys
import urllib.request
from bs4 import BeautifulSoup as bs

miles = "500"
zipCode = "78414"
searchTerms = ['cars', 'trucks', 'trucks---rvs', 'trailers']
additionalSearch = ""
confirmation = "n"
pageIterator = 1
termIterator = 0
while confirmation != "y":
    zipCode = input("Zip Code: (Default 78414) Press Enter to keep ")
    miles = input("Distance: (Default 500) Press Enter to keep ")
    additionalSearch = input("Add Search Terms, comma separated: \n(Default covers most vehicles and trailers): ")
    if zipCode == "":
        zipCode = "78414"
    if miles == "":
        miles = "500"
    if additionalSearch != "":
        additionalSearch = additionalSearch.split(",")
        for word in additionalSearch:
            searchTerms.append(word)
    print("Searching with zipcode {}, distance {}, and terms {}\n\nDo you wish to continue? (y/n)".format(zipCode,
                                                                                                        miles, searchTerms))
    confirmation = str(input())
if confirmation.lower() == "y":

    while True:
        url = 'https://texas.hibid.com/lots/{}/?status=open&zip={}&miles={}&apage={}&ipp=100'.format(searchTerms[termIterator],
                                                                                                     zipCode, miles, pageIterator)
        opener = urllib.request.build_opener()
        # Add headers so that user-agent is not null and connection is not rejected
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        response = urllib.request.urlopen(url)
        source = response.read()

        soup = bs(source, 'lxml')

        lots = soup.find_all("script", text=lambda text: text and "var lotModels" in text)
        result = []
        for lot in lots:
            result.extend(lot)
        result = result[0][20:-4]
        result = re.sub("[}],\s*[{]", "},\n{\n", result)
        toJSON = json.loads(result)
        listing = {}
        if not toJSON:
            print("-----{}".format(searchTerms[termIterator]).upper(), "category exhausted-----\n")
            termIterator += 1  # Go to next term
            pageIterator = 1  # Reset page count to 1
            if termIterator == len(searchTerms):
                print("Search complete, csv file created in local directory")  # TODO
                break
            continue
        for item in toJSON:
            print("Title: {}  ".format(item['lead']), end="  ")
            print("High Bid: {}".format(item['lotStatus']['highBid']), end="  ")
            print("Time Left: {}\n".format(item['lotStatus']['timeLeft']))
            print("https://texas.hibid.com/lot/{}\n".format(item['eventItemId']))
        pageIterator += 1

