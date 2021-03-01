# -*- coding: utf-8 -*-
"""
Created on Sun Feb 28 12:30:30 2021

@author: Szymon
"""

from bs4 import BeautifulSoup
import pandas as pd
import time
import requests
import numpy as np
import random
import sys
def is_digit(s):
    return any(i.isdigit() for i in s)


frontier = [f'https://www.gumtree.pl/s-mieszkania-i-domy-do-wynajecia/\
            warszawa/page-{n}/v1c9008l3200008p{n}' for n in range(30)]
data = {'title': [], 'link': [], 'price': [],'date added': [],'district': [],
        'city': [], 'property type': [], 'owner': [], 'Number of rooms': [],
        'Number of baths': [], 'Parking': [],'m2': [] }

for url in frontier:
    time.sleep(1)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser') 
    titles = [flat.next_element for flat in soup.find_all("a",
              class_ = "href-link tile-title-text")]
    links = ["https://www.gumtree.pl" + link.get('href') for link in
             soup.find_all("a", class_ = "href-link tile-title-text")]
    prices = [ ''.join( char for char in price.text if char.isdigit()) 
               if is_digit(price.text) else '' for price in 
               soup.find_all("span", class_ =  "price-text")
             ]
    
    
    for url in links:
        time.sleep(1)
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')

        m2 = [price.find("span", class_ = "value").text 
              for price in soup.find_all("div", class_ = "attribute")
              if price.next_element.text == "Wielkość (m2)"]
        if not m2: m2 = ['']
        
        localisation = [ loc.text for loc in soup.find_all("div", 
                        class_ = "location")] 
        try:
            if localisation:
                del localisation[0]
                localisation = localisation[0].split(', ')
            else:
                localisation = ['', '']
        except IndexError:
            print(url)
            sys.exit()
           
       
        
        date = [date.find("span", class_ = "value").text for date in 
                soup.find_all("div", class_="attribute")
                if date.next_element.text == "Data dodania"]
        if not date: date = ['']
        
        estate = [typ.find("span", class_ = "value").text for typ in
                soup.find_all("div", class_ = "attribute")
                if typ.next_element.text == "Rodzaj nieruchomości"]
        if not estate: estate = ['']
        
        owner = [own.find("span", class_ = "value").text for own in
                 soup.find_all("div", class_ = "attribute")
                 if own.next_element.text == "Do wynajęcia przez"]
        if not owner: owner = ['']
        
        rooms = [room.find("span", class_ = "value").text for room in
                 soup.find_all("div", class_ = "attribute")
                 if room.next_element.text == "Liczba pokoi"]
        if not rooms: rooms = ['']
        
        bath = [bath.find("span", class_ = "value").text for bath in
                soup.find_all("div", class_ = "attribute")
                if bath.next_element.text == "liczba łazienek"]
        if not bath: bath = ['']
            
        parking = [park.find("span", class_ = "value").text for park in
                  soup.find_all("div", class_ = "attribute")
                  if park.next_element.text == "Parking"] 
        if not parking: parking = ['']
        
        data['date added'].extend(date)
        data['district'].extend([localisation[0]])
        data['city'].extend([localisation[1]])
        data['property type'].extend(estate)
        data['owner'].extend(owner)
        data['Number of rooms'].extend(rooms)
        data['Number of baths'].extend(bath)
        data['Parking'].extend(parking)
        data['m2'].extend(m2)
    
    data['title'].extend(titles)
    data['link'].extend(links)
    data['price'].extend(prices)


    
df = pd.DataFrame(data).drop_duplicates()
df['price_for_m2'] = [ round(float(a)/int(b),2) if b != '' and a != '' else '' 
                       for a,b in zip(df['price'], df['m2']) ]
df['date added'] = pd.to_datetime(df['date added'])
df = df.replace(r'^\s*$', np.nan, regex=True)
df = df.astype({"price": float, "m2": float})
df.to_csv('./gumtree_mieszkania_warszawa.csv', sep=';',index=False, encoding = 'utf-8')


