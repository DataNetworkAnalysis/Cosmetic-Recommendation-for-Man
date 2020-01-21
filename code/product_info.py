from selenium import webdriver

import pandas as pd
import time
import os

# load product file
product = pd.read_csv('../dataset/glowpick_products.csv')

# urls
product_urls = product.product_url.unique()
url = 'https://www.glowpick.com'

# driver
driver = webdriver.Chrome()

# information dataframe
info_df = pd.DataFrame()

# if there's file, load file and concatenate
if os.path.isfile('../dataset/glowpick_info.csv'):
    df = pd.read_csv('../dataset/glowpick_info.csv')
    info_df = pd.concat([info_df, df], axis=0)
print('out info_df.shape: ',info_df.shape)

# crawling information of product
for p_url in product_urls:    
    print('='*100)
    print('in info_df.shape: ',info_df.shape)
    print('product url: ',p_url)
    driver.get(url + p_url)
    driver.implicitly_wait(5)

    # if category in total df, continue
    if info_df.shape[0] > 0:
        if p_url in info_df.product_url.unique():
            continue

    # name
    name = driver.find_element_by_xpath('//*[@id="gp-product-detail"]/div/ul[1]/li[2]/div/section[1]/h1/span').text
    print('product: ',name)

    # description
    describe = driver.find_element_by_css_selector('.product-detail__description-box.product-detail__tr > td > div').text
    print('describe: ',describe)

    # tags
    tags = driver.find_element_by_css_selector('.product-detail__tag-list.product-detail__tr > td > p') 
    spans = tags.find_elements_by_tag_name('span')

    t_lst = []
    for span in spans:
        t_lst.append(span.text)
    tags = '/'.join(t_lst)
    print('tags: ',tags)


    # make dataframe
    df = pd.DataFrame({'product_url':[p_url],
                    'description':[describe],
                    'tag':[tags]})

    info_df = pd.concat([info_df, df], axis=0)

    info_df.to_csv('../dataset/glowpick_info.csv', index=False)

    print()

