# -*- coding: utf-8 -*-
"""
Created on Mon Mar 13 21:57:38 2017

@author: Mohan Rao (mohanraobc@gmail.com)
"""
#this code was developed on Spyder with in Anaconda using Python 3.6.0

#Defining a function to scrap the Amazon review page for a particular product 
#The urls for the products are downloaded and stored in an excel sheet before hand
#this list has the urls for all the required products but only page 1 of the reviews

#initializing the required libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import re, sys
# Setting up proxy for successfull connection with web site
# function to list all the url of the first page of the reviews for each product (read from Excel file)
# Make sure to change the path to the location where the input excel file is placed 
# before calling this function
def remove_emoji(string):
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)

def getUrls():
    xl = pd.ExcelFile("URL_1-50_DE.xlsx")
    df = xl.parse("Sheet1")
    urllist = df['URL'].tolist()
    return urllist

# function to get the soup object from the input URL

#url = "http://www.amazon.de/Philips-Luftbefeuchter-Babies-HU4801-01/product-reviews/B00N3X06CS/ref=cm_cr_pr_btm_link_1?ie=UTF8&sortBy=recent&pageNumber=1"

def getsoup(url):
    response = requests.get(url, headers={'User-Agent':'Mozilla/5.0'})
    Status_Code = response.status_code
    print(url)
    print(Status_Code)
    
    if Status_Code == 200:
      soup = BeautifulSoup(response.content, features="lxml")
    else:
      soup = getsoup(url)
    return soup  

# function to get the last page number of reviews for a particular product

def getLastPageNumber(soup):
    pageNumber = []
    review_number = int(soup.find("div", {"data-hook": "cr-filter-info-review-rating-count"}).text.strip().replace(',', '').split()[-3])
    if review_number <=10:
        lastPage = 1
    else:
        lastPage = review_number // 200
    return lastPage

# Function to create a list of URLs for all the review pages for a product

def geturllist(url, lastPage):
    urllistPages = []
    if url.endswith('pageNumber=1'):
      url = url[:-1]
    for i in range(1,lastPage+1):
      urllistPages.append (url + str(i))
    return urllistPages


#Defining a function to extract all the required elements from a product review page
  

 #extracting the titles of the reviews
def getReviews(soup, url):   
    n_ = 0
    title_sec = soup.find_all(attrs={"data-hook": "review-title", "class": "a-size-base a-link-normal review-title a-color-base review-title-content a-text-bold"})
    title = []
    for s in title_sec:
        temp = remove_emoji(s.text)
        title.append(temp.replace('\n', ''))
    n_ = len(title)
        
 #extracting the author names of the reviews
 
    author_sec = soup.find_all(attrs = {"class": "a-profile-name"})
    author = []
    for r in author_sec:
        author.append(r.text)
    while(1):
        if len(author) > n_:
            author.pop(0)
        else:
            break

 #extracting the raw text of the reviews        

    Review_text_sec = soup.find_all(attrs={"data-hook": "review-body", "class": "a-size-base review-text review-text-content"})
    text = []
    for t in Review_text_sec:
        temp = remove_emoji(t.text)
        text.append(temp.replace('\n', ''))

 #extracting the rating of the reviews  

    Rating = soup.find_all(attrs={"data-hook": "review-star-rating"})    
    rate = []
    for d in Rating:
        rate.append(d.text)

 #extracting the date of the reviews 

    Date_sec = soup.find_all(attrs={"data-hook": "review-date"})    
    date = []
    for d in Date_sec:
      date.append(d.text) 

 #extracting the review was helpful info of the reviews 

    help_sec = soup.find_all(attrs={"data-hook": "helpful-vote-statement"})    
    help1 = []
    for d in help_sec:
         help1.append(d.text.replace('\n          ', '')) 
    while(1):
        if len(help1) < n_:
            help1.append('')
        else:
            break
        
 # Adding the url of the first page of the review for reference  
    url1 = []
    url1 = [url] * len(date)

# Creating a dataFrame out of all the required elements of the review page
    
    collate = {'Date': date, 'URL': url1, 'Review_Title': title, 'Author': author, 'Rating': rate, 'Review_text': text, 'Review_helpful': help1}          
    collate_df = pd.DataFrame.from_dict(collate)
    return collate_df                     




#Sequencing and calling the functions to complete the task

if __name__ == '__main__':
    
    urllist = getUrls()
    df2 = []
    y = 1
    for url in urllist:            
        soup = getsoup(url)
        lastPage = getLastPageNumber(soup)
        #lastPage = 3
        urllistPages = geturllist(url, lastPage)
        x = 1
        for url in urllistPages:
            soup = getsoup(url)
            df1 = getReviews(soup, url)         
            if x == 1:
                df3 = []
                df3 = df1
            else:                        
                df2 = df3
                result = df2.append(df1, ignore_index=True)
                df3 = result
            x += 1
            print(df3['Review_Title'])
        df3.to_csv("Amazon_reviews" + str(y) + ".csv")
        y += 1
    
