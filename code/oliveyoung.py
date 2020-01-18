'''
실행 방법 : 아나콘다 프롬프트에서 main.py가 있는 폴더 경로에 아래 명령어 입력
python main.py

데이터 목록 [3108 rows x 6 columns]
1. Category
2. Brand_Name
3. Product_Name
4. Price
5. Sales Rank
6. Pre_Discount_Price


크롤링 방법
1. Category 별 판매수량순으로 정렬 후 데이터 수집
2. 가격순위는 이후에 크롤링한 가격으로 체크할 수 있음
'''

import pandas as pd 
import numpy as np
import os 

from selenium import webdriver

# Category List
category_lst = ['스킨케어','바디케어','헤어케어','메이크업','향수/탈취','쉐이빙/잡화'] # 카테고리
category_num = [100000100070001, 100000100070002, 100000100070003, 100000100070004, 100000100070005, 100000100070006]
total_df = pd.DataFrame() # 저장할 dataframe

# Crawling url list
url = 'http://www.oliveyoung.co.kr/store/display/getMCategoryList.do?dispCatNo={}&fltDispCatNo=&prdSort=03&pageIdx={}&rowsPerPage=24&searchTypeSort=btn_thumb&plusButtonFlag=N&isLoginCnt=2&aShowCnt=&bShowCnt=&cShowCnt='

# driver는 실행창 없이 실행
options = webdriver.ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

# Category 개수만큼 반복
for i in range(len(category_lst)):
    # Save columns list
    brand_lst = list() # 브랜드 이름
    name_lst = list() # 제품 이름
    price_lst = list() # 제품 가격
    pre_price_lst = list() # 할인 전 가격

    # First page
    p = 1 
    driver.get(url.format(category_num[i],p))

    # 최대 페이지 수
    num = driver.find_element_by_xpath('/html/body/div[2]/div[4]/div[1]/p/span').text # 총 상품 수
    max_page = int(int(num) / 24) + 1 # 한 페이지에 24개 상품이 있음

    for p in range(1,max_page+1):
        driver.get(url.format(category_num[i],p)) # url 접속

        # Crawling start
        contents = driver.find_element_by_xpath('/html/body/div[2]/div[4]/div[1]')
        product_list = driver.find_elements_by_css_selector('div.prd_info')

        for p_content in product_list:    
            brand = p_content.find_element_by_css_selector('span.tx_brand').text.strip()
            name = p_content.find_element_by_css_selector('p.tx_name').text.strip()

            price = p_content.find_element_by_css_selector('span.tx_cur span.tx_num').text.strip()

            try:
                pre_price = p_content.find_element_by_tag_name('span.tx_org span.tx_num').text.strip()
            except:
                pre_price = 0 # 할인 상품이 아닌경우 할인 전 가격을 0으로 지정
            
            # print list
            print('Category: {} / Brand: {} / Name: {} / Price: {} / Pre-Discount Price: {}'.format(category_lst[i], brand, name, price, pre_price))

            # Add values into list
            brand_lst.append(brand)
            name_lst.append(name)
            price_lst.append(price)
            pre_price_lst.append(pre_price)


    # Make product info dataframe 
    df = pd.DataFrame({'brand_name':brand_lst,
                    'product_name':name_lst,
                    'price':price_lst,
                    'pre_price':pre_price_lst})
    df['category'] = category_lst[i]
    df['sales_rank'] = np.arange(1,df.shape[0]+1)

    # Sort by define colnames
    order_colnames = ['category','brand_name','product_name','price','pre_price','sales_rank']
    df = df[order_colnames]
    total_df = pd.concat([total_df, df], axis=0)

# dataset 파일이 없으면 생성
if not(os.path.isdir('../dataset')):
    os.mkdir('../dataset')

# Save
total_df.to_csv('../dataset/oliveyoung_product_info.csv',index=False)

driver.quit()