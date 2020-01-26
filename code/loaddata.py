import pandas as pd

def load(review_path, product_path, info_path):
    # Load data
    print('[{0:15s}] Load data...'.format('LOAD'), end='')
    data = pd.read_csv(review_path)
    products = pd.read_csv(product_path)
    infos = pd.read_csv(info_path)
    print('(data.shape: ,{})'.format(data.shape) ,end='')
    print('(products.shape: ,{})'.format(products.shape), end='')
    print('(infos.shape: ,{})'.format(infos.shape))

    # filtering 여성용품
    if '여성용품' in products.title.unique():
        print('[{0:15s}] filtering data...'.format('LOAD'), end='')
        data_prod = pd.merge(data, products, on='product_url', how='left')

        # 1. 남성화장품
        male_cosmetic = data_prod[data_prod.title=='남성화장품']
        # 2. not 남성화장품 and male
        male_reviews = data_prod[(data_prod.title!='남성화장품')&(data_prod.sex=='m')]
        # concat 1,2
        data = pd.concat([male_cosmetic, male_reviews], axis=0)

        data = data.rename(columns={'rate_x':'rate'})
        data = data[['user_id','age_skin_type','rate','content','product_url']].drop_duplicates()
        print(f'(filtering data shape: {data.shape}')

    return data, products, infos