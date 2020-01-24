'''
실행 방법 : 아나콘다 프롬프트에서 main.py가 있는 폴더 경로에 아래 명령어 입력
python reviews.py

데이터 목록 
1. User_id
2. Age
3. Skin_type
4. Sex
5. Date
6. Rate
7. Content

'''

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

import pandas as pd 
import time
import os


class GlowPickReview:
    def __init__(self):
        try:
            # load dataframe
            df = pd.read_csv('../dataset/glowpick_products.csv')
            # except for zero review
            df = df[df.nb_reviews!='(0)']
            # product url list
            self.prod_url_lst = df.product_url.unique().tolist()
        except:
            print('glowpick_product is missing. You have to run glowpick.py at first')

        # url
        self.url = 'https://www.glowpick.com'
        # driver setting
        self.driver = webdriver.Chrome()
    
    def run(self):
        # make total dataframe
        total_df = pd.DataFrame()

        if os.path.isfile('../dataset/glowpick_reviews.csv'):
            df = pd.read_csv('../dataset/glowpick_reviews.csv')
            total_df = pd.concat([total_df, df], axis=0)
        print('total_df.shape: ',total_df.shape)

        for prod_url in self.prod_url_lst:
            print('total_df.shape: ',total_df.shape)
            if total_df.shape[0] > 0:
                if prod_url in total_df.product_url.unique():
                    continue
            
            try:
                self.driver.get(self.url + prod_url)
                self.driver.implicitly_wait(5)
            except:
                continue

            self.scroll_down()

            print()
            print(prod_url)
            df = self.crawling()
            df['product_url'] = prod_url

            total_df = pd.concat([total_df, df], axis=0)
        
            total_df.to_csv('../dataset/glowpick_reviews.csv',index=False)

        self.driver.quit()

    def scroll_down(self):
        # scoll down 
        ul = self.driver.find_element_by_xpath('//*[@id="gp-product-detail"]/div/ul[2]/li[5]/section/ul')
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
            ul = self.driver.find_element_by_xpath('//*[@id="gp-product-detail"]/div/ul[2]/li[5]/section/ul')
            current_height = ul.size['height']
            if start_height == current_height:
                loop = False
            else:
                start_height = current_height
                # print('current height: ',current_height)

    def crawling(self):
        user_id_lst = []
        age_skin_type_lst = []
        sex_lst = []
        date_lst = []
        rate_lst = []
        content_lst = []

        divs = self.driver.find_elements_by_xpath('//*[@id="gp-product-detail"]/div/ul[2]/li[5]/section/ul/li')

        for div in divs:
            lst = div.text.split('\n')
            sex = div.find_element_by_css_selector('span.txt > span').get_attribute('class').split(' ')[-1].split('-')[2]
            rate = div.find_element_by_css_selector('span.label > span').get_attribute('class').split(' ')[-1].split('-')[1]

            print(f'{lst[0]}/{lst[1]}/{lst[2]}/{lst[3]}/{sex}/{rate}')

            date_lst.append(lst[0])
            user_id_lst.append(lst[1])
            age_skin_type_lst.append(lst[2])
            content_lst.append(' '.join(lst[3:]))
            sex_lst.append(sex)
            rate_lst.append(rate)
        
            

        df = pd.DataFrame({'date':date_lst,
                           'user_id':user_id_lst,
                           'sex':sex_lst,
                           'age_skin_type':age_skin_type_lst,
                           'rate':rate_lst,
                           'content':content_lst})
        return df


if __name__ == '__main__':
    GPR = GlowPickReview()
    GPR.run()