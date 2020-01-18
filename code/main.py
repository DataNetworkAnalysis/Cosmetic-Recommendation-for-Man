from scipy.spatial.distance import cosine
from gensim.models import FastText
from konlpy.tag import Kkma 

import pickle
import argparse
import os

import pandas as pd
import numpy as np 
from preprocessing import GlowpickPreprocessing

parser = argparse.ArgumentParser()
# preprocessing
parser.add_argument('--train',action='store_true', help='train or not')
parser.add_argument('--filepath',type=str,default='../dataset/glowpick_reviews.csv', help='file path')
parser.add_argument('--wordpath',type=str,default=None, help='replace word dictionary')
parser.add_argument('--pospath',type=str,default=None, help='filtering pos dictionary')
parser.add_argument('--embed_size',type=int,default=100, help='ebedding vector size')
parser.add_argument('--savedir',type=str,default='../saved_file', help='directory path to save model and preprocessed file')
# evaluation
parser.add_argument('--search',type=str,help='text to search')
args = parser.parse_args()


# check savedir
if not os.path.isdir(args.savedir):
    os.mkdir(args.savedir)

# Load data
data = pd.read_csv(args.filepath)
# train
GP = GlowpickPreprocessing()
# config
modelname = 'model'
pre_textname = 'pre_text'
pre_embedname = 'pre_embed'

if args.wordpath:
    modelname += '_word'
    pre_textname += '_word'
    pre_embedname += '_word'
if args.pospath:
    modelname += '_pos'
    pre_textname += '_pos'
    pre_embedname += '_pos'
if args.embed_size != 100:
    modelname += f'_v{args.embed_size}'
    pre_textname += f'_v{args.embed_size}'
    pre_embedname += f'_v{args.embed_size}'

if args.train:    
    # train set
    text = GP.fit(data.content.tolist(), 
                  wordfix_path=args.wordpath,
                  posfix_path=args.pospath)
    
    # save pre text
    with open(f'{args.savedir}/{pre_textname}.pickle','wb') as f:
        pickle.dump(text,f)

    # embdding model
    model = GP.embedding(text)
    model.save(f'{args.savedir}/{modelname}.bin') # save

    # save sent vec
    embed = GP.sent2vec(text, model)
    with open(f'{args.savedir}/{pre_embedname}.pickle','wb') as f:
        pickle.dump(embed,f)
else:
    # molphs analyzer
    kkma = Kkma()
    # load embed model
    model = FastText.load(f'{args.savedir}/{modelname}.bin')
    # test
    test_text = GP.fit([args.search], args.wordpath, args.pospath)
    print('test_text: ',test_text)
    test_sent_vec = GP.sent2vec(test_text, model)

    # similarity
    with open(f'{args.savedir}/{pre_embedname}.pickle','rb') as f:
        sent_vec = pickle.load(f)

    dist_arr = np.zeros((sent_vec.shape[0]))
    for i, sent in enumerate(sent_vec):
        dist = cosine(sent, test_sent_vec[0])
        dist_arr[i] = dist

    data['dist'] = dist_arr
    products = pd.read_csv('../dataset/glowpick_products.csv')
    data_prod = pd.merge(data, products, on='product_url', how='left')
    rate_dict = {
        'best':0,
        'good':1,
        'soso':2,
        'bad':3,
        'worst':4
    }
    data_prod.rate_x = data_prod.rate_x.map(rate_dict)

    # feature selection
    features = ['product_url','category','brand','vol_price','nb_reviews','sex','age_skin_type','rate_x','product','content']
    show_features = ['category','brand','nb_reviews','vol_price','product']

    # filtering
    s_dict = {
        #메이크업항목
        'makeup_dict':{
        '비비':['BB','파운데이션','듀얼 스틱','원 플루이드 그린','저스트 스킨','모이스처라이저 B'],
        '톤업':['톤 업','톤 매너','아프리카 버드 옴므 올인원 브라이트닝 에센스'],
        '씨씨':['CC','CC크림','리얼컴플렉션 젤 피니셔','포맨 히든스틱'],
        '쿠션':['쿠션크림'],
        '립':['밤','듀얼 스틱'],
        '브로우':['눈썹','마스터 커버스틱','숯 유어셀프'],
        },

        #헤어/바디 항목
        'hair_body_dict':{
        '바디워시':['워시','바디 워시','비어 원샷 클렌저 포맨','맨즈 시트러스 민트 3 IN 1'],
        '샴푸':['방 덴시피크 옴므','두쉐르 베제딸 뿌르옴므','또니끄 비비휘앙 뿌르옴므','뱅 떼에스 뿌르옴므','뱅 트레땅 알라 프로폴리스 뿌르옴므'],
        '샤워젤':['샤워','샤워 젤'],
        '스프레이':['퍼퓸건','미스트','라스트 샷'],
        '로션':['크림','핸드크림','핸드','맨올로지 101 에너자이징 바디 에멀젼'],
        '데오드란트':['데오도란트','맨 블랙 앤 화이트 롤 온','매너 키트','데오도런트'],
        '오일':['맨 퓨어-포먼스 컴포지션']
        },

        #헤어스타일링 항목 
        'hairstyle_dict':{
        '왁스':['무빙러버','젤','하드','헤어잼','크래프트 클레이 리모델러블 매트 텍스처라이저','알앤비','포맨 오리지널 슈퍼 매트','버번 바닐라 & 텐저린 헤어 텍스처라이저','맨 퓨어-포먼스 그루밍 클레이'],
        '컬':['볼륨미아 볼륨 무스']
        }
    }

    # check intersection keyword
    for cat, dic in s_dict.items():
        for k, v in dic.items():
            if k in test_text[0]:
                inter_word = v
                continue
            for i in v:
                if i in test_text[0]:
                    inter_word = v
    
    if len(inter_word)!=0:
        inter_idx = []
        for i, p in enumerate(data_prod['product']):
            for c in inter_word:
                if c in p:
                    inter_idx.append(i)
        data_prod = data_prod.iloc[inter_idx]

    # check category
    cat_lst = products.category.unique()
    f = set(test_text[0]) & set(cat_lst)
    if len(f) > 0:
        temp = data_prod[['dist'] + features]
        temp = temp[temp.category.isin(f)].sort_values(by=['rate_x','dist'])
    else:
        temp = data_prod[['dist'] + features].sort_values(by=['rate_x','dist'])
    temp = temp[show_features].drop_duplicates()
    
    # choice top-5
    for i in range(5):
        for j in temp.iloc[i]:
            print('{0:.50s} / '.format(str(j)), end="")
        print('\n')
