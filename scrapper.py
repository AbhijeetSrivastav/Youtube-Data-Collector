# Imports

from bs4 import BeautifulSoup as bs

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import re
import json as json


class Scrapper:
    def __init__(self, channel_link):
        self.channel_link = channel_link

        self.base_url = self.channel_link + '/videos'

        self.titles = []
        self.videos_urls = []
        self.views = []
        self.thumbnails_urls = []
        self.likes = []

        self.comments = []
        self.commentors = []
        self.commented_on = []

    def scrapMainPageData(self):
        """Scraps Title, Video link, Views for top 50 videos"""
        try:
            # setting up driver and soup
            driver = webdriver.Chrome()
            driver.get(self.base_url)
            content = driver.page_source.encode('utf-8').strip()
            soup = bs(content, 'lxml')
        except Exception as e:
            raise Exception(e)

        # Scrapping raw data for title, views and video links
        title_raw = soup.find_all('a', id='video-title')
        views__raw = soup.find_all('span', class_='style-scope ytd-grid-video-renderer')
        video_link_raw = soup.find_all('a', id='video-title')

        # Parsing and saving title, vies, video link to respective lists
        for title in title_raw:
            self.titles.append(title.text)

        for view in views__raw:
            self.views.append(view.text)

        for video_link in video_link_raw:
            link = 'https://www.youtube.com/' + video_link.get('href')
            self.videos_urls.append(link)

    def scrapThumbnailLink(self):
        """Generates thumbnail links for each video"""
        for video_url in self.videos_urls:
            try:
                thumbnail_url = 'https://i.ytimg.com/vi/' + video_url.rsplit('=')[1] + '/maxresdefault.jpg'
                self.thumbnails_urls.append(thumbnail_url)
            except IndexError:
                thumbnail_url = 'https://i.ytimg.com/vi/' + video_url.rsplit('shorts/')[1] + '/maxresdefault.jpg'
                self.thumbnails_urls.append(thumbnail_url)

    def scrapLikes(self):
        """Scraps number of likes for each video"""
        try:
            # setting up soup
            driver = webdriver.Chrome()
        except Exception as e:
            raise Exception(e)

        result = {}

        for video_url in self.videos_urls:
            driver.get(video_url)
            html = driver.page_source
            soup = bs(html, 'html.parser')

            data = re.search(r"var ytInitialData = ({.*?});", soup.prettify()).group(1)
            try:
                data_json = json.loads(data)
                videoPrimaryInfoRenderer = \
                    data_json['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0][
                        'videoPrimaryInfoRenderer']
                videoSecondaryInfoRenderer = \
                    data_json['contents']['twoColumnWatchNextResults']['results']['results']['contents'][1][
                        'videoSecondaryInfoRenderer']

                # number of likes
                likes_label = \
                    videoPrimaryInfoRenderer['videoActions']['menuRenderer']['topLevelButtons'][0][
                        'toggleButtonRenderer'][
                        'defaultText']['accessibility']['accessibilityData']['label']  # "No likes" or "###,### likes"
                likes_str = likes_label.split(' ')[0].replace(',', '')

                if likes_str == 'No':
                    like = '0'
                else:
                    like = likes_str

                self.likes.append(like)
            except Exception:
                like = '0'
                self.likes.append(like)

    def scrapCommentData(self):
        """Scraps comments, commentor name, comment post time for each video"""
        try:
            # seeting up driver
            driver = webdriver.Chrome()
            wait_driver = WebDriverWait(driver, 10)
        except Exception as e:
            raise Exception(e)

        for video_url in self.videos_urls:
            driver.get(video_url)

            for i in range(13):
                wait_driver.until(EC.visibility_of_element_located((By.TAG_NAME, "body"))).send_keys(Keys.END)
                time.sleep(5)

            try:
                for comment in wait_driver.until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#content-text"))):
                    self.comments.append(comment.text.replace('\n', ''))
            except Exception:
                pass

            try:
                for commentor in wait_driver.until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#author-text"))):
                    self.commentors.append(commentor.text.capitalize())
            except Exception:
                pass

            try:
                for posted_on in wait_driver.until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#header-author"))):
                    self.commented_on.append(posted_on.text.split('\n', 1)[1])

            except Exception:
                pass
