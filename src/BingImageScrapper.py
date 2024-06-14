# -*- coding: utf-8 -*-
"""
Github: https://github.com/young1205/Bing-Image-Scrapper
"""
# import selenium drivers
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

# import helper libraries
import time
import urllib.request
import os
import requests
import io
import re
import json
from PIL import Image

# custom patch libraries
import patch


class BingImageScraper:
    def __init__(
        self,
        webdriver_path,
        image_path,
        search_key="cat",
        number_of_images=1,
        headless=False,
        min_resolution=(0, 0),
        max_resolution=(1920, 1080),
    ):
        # check parameter types
        image_path = os.path.join(image_path, search_key)
        if type(number_of_images) != int:
            print("[Error] Number of images must be integer value.")
            return
        if not os.path.exists(image_path):
            print("[INFO] Image path not found. Creating a new folder.")
            os.makedirs(image_path)
        # check if chromedriver is updated
        while True:
            try:
                # try going to www.Bing.com
                options = Options()
                if headless:
                    options.add_argument("--headless")
                driver = webdriver.Chrome(
                    ChromeDriverManager().install(), chrome_options=options
                )
                driver.set_window_size(1400, 1050)
                driver.get("https://www.Bing.com")
                break
            except:
                # patch chromedriver if not available or outdated
                try:
                    driver
                except NameError:
                    is_patched = patch.download_lastest_chromedriver()
                else:
                    is_patched = patch.download_lastest_chromedriver(
                        driver.capabilities["version"]
                    )
                if not is_patched:
                    exit(
                        "[ERR] Please update the chromedriver.exe in the webdriver folder according to your chrome version:https://chromedriver.chromium.org/downloads"
                    )

        self.driver = driver
        self.search_key = search_key
        self.number_of_images = number_of_images
        self.webdriver_path = webdriver_path
        self.image_path = image_path

        # Only search for small images
        self.url = (
            "https://www.bing.com/images/search?q="
            + self.search_key
            + "=+filterui%3aimagesize-small&first=1"
        )
        self.headless = headless
        self.min_resolution = min_resolution
        self.max_resolution = max_resolution

    def find_image_urls(self):
        """
        This function search and return a list of image urls based on the search key.
        Example:
            Bing_image_scraper = BingImageScraper("webdriver_path","image_path","search_key",number_of_photos)
            image_urls = Bing_image_scraper.find_image_urls()

        """
        print("[INFO] Scraping for image link... Please wait.")
        image_urls = []
        count = 0
        missed_count = 0
        self.driver.get(self.url)
        time.sleep(3)

        class_name = "iusc"
        images = self.driver.find_elements_by_class_name(class_name)

        for image in images:
            if count < self.number_of_images:
                # only download images that starts with http
                json_data = image.get_attribute("m")
                image_data = json.loads(json_data)
                src_link = image_data["murl"]
                print("[INFO] found src_link: ", src_link)
                if not isinstance(src_link, type(None)):
                    if ("http:/" in src_link) and (
                        (".png" in src_link) or (".jpg" in src_link)
                    ):
                        image_urls.append(src_link)
                        count = count + 1
            else:
                break

        print("[INFO] List of image urls:", image_urls)
        return image_urls

    def save_images(self, image_urls):
        # save images into file directory
        """
        This function takes in an array of image urls and save it into the prescribed image path/directory.
        Example:
            Bing_image_scraper = BingImageScraper("webdriver_path","image_path","search_key",number_of_photos)
            image_urls=["https://example_1.jpg","https://example_2.jpg"]
            Bing_image_scraper.save_images(image_urls)

        """
        print("[INFO] Saving Image... Please wait...")
        for indx, image_url in enumerate(image_urls):
            try:
                print("[INFO] Image url:%s" % (image_url))
                search_string = "".join(e for e in self.search_key if e.isalnum())
                image = requests.get(image_url, timeout=5)
                if image.status_code == 200:
                    with Image.open(io.BytesIO(image.content)) as image_from_web:
                        try:
                            # filename = "%s%s.%s"%(search_string,str(indx),image_from_web.format.lower())
                            filename = "%s%s.%s" % (search_string, str(indx), "png")
                            image_path = os.path.join(self.image_path, filename)
                            print("[INFO] %d .Image saved at: %s" % (indx, image_path))
                            image_from_web.save(image_path)
                        except OSError:
                            rgb_im = image_from_web.convert("RGB")
                            rgb_im.save(image_path)
                        image_resolution = image_from_web.size
                        if image_resolution != None:
                            if (
                                image_resolution[0] < self.min_resolution[0]
                                or image_resolution[1] < self.min_resolution[1]
                                or image_resolution[0] > self.max_resolution[0]
                                or image_resolution[1] > self.max_resolution[1]
                            ):
                                image_from_web.close()
                                # print("BingImageScraper Notification: %s did not meet resolution requirements."%(image_url))
                                os.remove(image_path)

                        image_from_web.close()
            except Exception as e:
                print("[ERROR] Failed to be downloaded", e)
                pass
        print(
            "[INFO] Download Completed. Please note that some photos are not downloaded as it is not in the right format (e.g. jpg, jpeg, png)"
        )
