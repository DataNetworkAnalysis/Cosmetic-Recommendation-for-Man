'''
실행 방법 : 아나콘다 프롬프트에서 main.py가 있는 폴더 경로에 아래 명령어 입력
python glowpick.py

데이터 목록 
1. Category
2. Brand_Name
3. Product_Name
4. volume
5. price
6. Sales Rank
7. rate
8. nb_reviews
7. product_number
'''

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import pandas as pd

import os
import time


class GlowPick:
    def __init__(self):
        # url
        self.url = 'https://www.glowpick.com/'

        # self.driver setting
        self.driver = webdriver.Chrome()
        self.li_lst = None

    def run(self):
        # make total dataframe
        total_df = pd.DataFrame()

        # if there's file, load file and concatenate
        if os.path.isfile('../dataset/glowpick_products.csv'):
            df = pd.read_csv('../dataset/glowpick_products.csv')
            total_df = pd.concat([total_df, df], axis=0)
        print('total_df.shape: ',total_df.shape)


        titla_nb = 17 # 크게 17가지 범주
        for cat in range(1,titla_nb+1):      
            # glowpick main page
            self.get_main(cat=cat)

            # get title
            title = self.driver.find_element_by_xpath(f'//*[@id="gp-home"]/section[1]/div[1]/form/fieldset[1]/div/div/ul/li[{cat}]/div[1]/span[1]').text
            print('title: ',title)
            print('len(self.li_lst): ',len(self.li_lst))
            for i in range(len(self.li_lst)):
                self.get_main(cat=cat)

                self.driver.implicitly_wait(5)
                category = self.li_lst[i].text
                print()
                print(f'{i} category: ',category)

                # if category in total df, continue
                if total_df.shape[0] > 0:
                    title_df = total_df[total_df['title'] == title]
                    if ('category' in title_df.columns) and (self.li_lst[i].text in title_df.category.unique()):
                        continue

                # select category
                self.driver.execute_script("arguments[0].click();", self.li_lst[i])
                self.driver.implicitly_wait(5)

                # search click
                element = self.driver.find_element_by_xpath('//*[@id="gp-home"]/section[1]/div[1]/form/div/button').send_keys(Keys.ENTER)
                self.driver.implicitly_wait(5)

                # scroll down
                self.scroll_down()

                # crawling
                df = self.crawling()
                df['category'] = category
                df['title'] = title

                total_df = pd.concat([total_df, df], axis=0)

                total_df.to_csv('../dataset/glowpick_products.csv', index=False)
                print(total_df.tail())

        print()
        print('Complete')

        self.driver.quit()

    def get_main(self, cat=17):
        '''
        args:
        - get_lst : sub category li list
        - cat : category index. default 17: 남자화장품
        '''
        # glowpick main page
        self.driver.get(self.url)
        self.driver.implicitly_wait(5)
        # click category list
        self.driver.find_element_by_xpath('//*[@id="gp-home"]/section[1]/div[1]/form/fieldset[1]/div/button').send_keys(Keys.ENTER)
        time.sleep(1)
    
        self.driver.find_element_by_xpath(f'//*[@id="gp-home"]/section[1]/div[1]/form/fieldset[1]/div/div/ul/li[{cat}]').click()
        self.driver.implicitly_wait(5)
        time.sleep(1)

    
        li_ul = self.driver.find_element_by_xpath(f'//*[@id="gp-home"]/section[1]/div[1]/form/fieldset[1]/div/div/ul/li[{cat}]/div[2]/ul')
        self.li_lst = li_ul.find_elements_by_css_selector('.list-item')

    def scroll_down(self):
        # scoll down 
        ul = self.driver.find_element_by_xpath('//*[@id="gp-list"]/div/section[2]/ul')
        start_height = ul.size['height']

        target = self.driver.find_element_by_link_text('사업자정보 확인')
        start = self.driver.find_element_by_link_text('브랜드')

        loop = True
        actions = ActionChains(self.driver)

        while loop:
            actions.move_to_element(start)
            actions.perform()
            actions.move_to_element(target)
            actions.perform()
            time.sleep(0.5)
            
            # check loop
            ul = self.driver.find_element_by_xpath('//*[@id="gp-list"]/div/section[2]/ul')
            current_height = ul.size['height']
            if start_height == current_height:
                loop = False
            else:
                start_height = current_height
                

    def crawling(self):
        # crawling list 
        brand_lst = []
        product_lst = []
        vol_price_lst = []
        sales_rank_lst = []
        rate_lst = []
        nb_reviews_lst = []
        product_url_lst = []

        divs = self.driver.find_elements_by_xpath('//*[@id="gp-list"]/div/section[2]/ul/li')
        for div in divs:
            lst = div.text.split('\n') # exclude a last element '-' 
            product_url = div.find_element_by_css_selector('div > div > div').get_attribute('data-url')
            product_url_lst.append(product_url)

            print(lst, end=" ")
            print(product_url)

            brand_lst.append(lst[0])
            product_lst.append(lst[1])
            vol_price_lst.append(lst[2])
            rate_lst.append(lst[3])
            nb_reviews_lst.append(lst[4])
            sales_rank_lst.append(lst[5])

        # save dataframe
        df = pd.DataFrame({'brand':brand_lst,
                           'product':product_lst,
                           'vol_price':vol_price_lst,
                           'rate':rate_lst,
                           'nb_reviews':nb_reviews_lst,
                           'sales_rank':sales_rank_lst,
                           'product_url':product_url_lst})

        return df

if __name__ == '__main__':
    gp = GlowPick()
    gp.run()