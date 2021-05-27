import requests as rq
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


STEAM_URL = "https://store.steampowered.com"
CATEGORY_PARENT_BLOCK_SELECTOR = "body > div.responsive_page_frame.with_header > div.responsive_page_content > div.responsive_page_template_content > div.home_page_body_ctn > div.home_page_content > div.home_page_gutter > div:nth-child(2)"
CATEGORY_CHILD_CLASS = "gutter_item"

def getCategoriList(steamURL = STEAM_URL):
    try:
        #메인 페이지 요청
        response = rq.get(STEAM_URL)
        if response.status_code != 200:
            return None
        
        parser = BeautifulSoup(response.content, "lxml")
        
        #카테고리 링크가 속해있는 부모 블록
        parentDivBlcok = parser.select_one(CATEGORY_PARENT_BLOCK_SELECTOR)
        
        #부모 블록 아래의 클래스만 검색함
        childCategoryList = parentDivBlcok.find_all("a", class_ = CATEGORY_CHILD_CLASS)
        
        #(카테고리 이름, 카테고리 링크)와 같읕 튜플형이 포함된 리스트를 만듬
        categoriList = [(child.text.strip(), child.attrs["href"]) for child in childCategoryList]
        return categoriList
        
        
    except Exception as e:
        logging.error(e)
        return None
    

class SteamCrawler:
    CATEGORY_ITEM_PAGE_BLOCK_ID = "NewReleases_links"
    CATEGORY_ITEM_PAGE_BUTTON_CLASS = "paged_items_paging_pagelink"
    NEW_RELEASE_URL_FORMAT = "#p={}&tab=NewReleases"
    ITEM_PARENT_DIV_BLOCK_ID = "NewReleasesRows"
    ITEM_CHILD_CLASS = "tab_item"
    
    def __init__(self, targetCategoryURL, hide = False):
        options = webdriver.ChromeOptions()
        
        #헤드리스 옵션 사용 여부
        if hide:
            options.add_argument("headless")

        #창의 크기
        options.add_argument("--window-size=920,580")
        #하드웨어 가속 사용 여부
        options.add_argument("disable-gpu")
        #요청 헤더
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36")
        #사용 언어
        options.add_argument("lang=ko_KR")
        #드라이버 생성
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options = options)
        
        #타겟 URL저장
        self.targetCategoryURL = targetCategoryURL
        
    def __del__(self):
        #자신의 창만 닫음
        self.driver.close()
        
    #함수들 정리할것
    def findTag(self, tag, parentObj = None, timeOut = 10):
        return WebDriverWait(self.driver if parentObj is None else parentObj, timeOut).until(lambda d : d.find_elements_by_tag_name(tag))
    
    def findClass(self, class_, parentObj = None, timeOut = 5):
        return WebDriverWait(self.driver if parentObj is None else parentObj, timeOut).until(lambda d : d.find_elements_by_class_name(class_))
    
    def findID(self, id_, parentObj = None, timeOut = 5):
        return WebDriverWait(self.driver if parentObj is None else parentObj, timeOut).until(lambda d : d.find_element_by_id(id_))
    
    def findSelector(self, selector, parentObj = None, timeOut = 5):
        return WebDriverWait(self.driver if parentObj is None else parentObj, timeOut).until(lambda d : d.find_elements_by_css_selector(selector))
        
    def getCategoryPageCount(self):
        try:
            preURL = self.driver.current_url
            if self.driver.current_url != self.targetCategoryURL:
                self.driver.get(self.targetCategoryURL)
                
            parentBlock = self.findID(self.CATEGORY_ITEM_PAGE_BLOCK_ID)
            print(parentBlock)
            childPageButtons = self.findTag("a", parentBlock)
            
            if self.driver.current_url != preURL:
                self.driver.get(preURL)
            
            return int(childPageButtons[-1].text)
            
        except Exception as e:
            logging.error(e)
            return None
            
    def getPageItem(self, targetURL):
        try:
            self.driver.get(targetURL)
            parent = self.findID(self.ITEM_PARENT_DIV_BLOCK_ID)
            childList = self.findClass(self.ITEM_CHILD_CLASS, parent)
            [print(child.text) for child in childList]
            
        except Exception as e:
            logging.error(e)
            return None
        
        
        
    def getCategoryItems(self):
        try:
            self.driver.get(self.targetCategoryURL)
            pageCount = self.getCategoryPageCount()
            
            import time
            for x in range(pageCount):
                targetURL = self.targetCategoryURL + self.NEW_RELEASE_URL_FORMAT.format(x)
                self.getPageItem(targetURL)
            
        except Exception as e:
            logging.error(e)
            return None
    
if __name__ == "__main__":
    catList = getCategoriList()
    driver = SteamCrawler(catList[0][1])
    ret = driver.getCategoryItems()
    