# -*- coding: utf-8 -*-
"""
Github: https://github.com/young1205/Bing-Image-Scrapper
"""
#Import libraries
import os
from BingImageScrapper import BingImageScraper
from patch import webdriver_executable

if __name__ == "__main__":
    #Define file path
    webdriver_path = os.path.normpath(os.path.join(os.getcwd(), 'webdriver', webdriver_executable()))
    image_path = os.path.normpath(os.path.join(os.getcwd(), 'photos'))

    #Website used for scraping: 
    search_site = 'bing'

    #Add new search key into array ["cat","t-shirt","apple","orange","pear","fish"]
    search_keys= ['pug']

    #Parameters
    number_of_images = 20
    headless = False
    min_resolution=(0,0)
    max_resolution=(9999,9999)

    #Main program
    for search_key in search_keys:
        image_scrapper = BingImageScraper(webdriver_path,image_path,search_key,number_of_images,headless,min_resolution,max_resolution)
        
        image_urls = image_scrapper.find_image_urls()
        print("image",image_urls)
        image_scrapper.save_images(image_urls)
    
    #Release resources    
    del image_scrapper