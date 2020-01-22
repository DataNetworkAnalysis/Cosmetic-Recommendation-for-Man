'''
1. 자음,모음,특수문자 제거 (온점, 쉼표 포함)
2. 띄어쓰기 교정
3. 단어 수정
4. 형태소분석기로 명사 and 형용사 추출 
5. Fasttext embedding

- 사전 추가
'''

from chatspace import ChatSpace
from gensim.models import FastText
from konlpy.tag import Kkma 
import json

import re
import pandas as pd 
import numpy as np

class GlowpickPreprocessing(object):
    def __init__(self, embed_size=100):
        self.embed_size = embed_size
        self.kkma = Kkma()

    def fit(self, x: list, wordfix_path=None, posfix_path=None):
        '''
        args:
        - x: texts 
        - wordfix_path: replace word directory path
        - posfix_path: filtering pos directory path
        return:
        - texts: preprocessed texts
        '''
        # stopword
        texts = list(map(self.stopword, x))
        print('[{0:15s}]: complete stopword'.format('PREPROCESSING'))

        # spacefix
        texts = self.spacefix(texts)
        print('[{0:15s}]: complete spacefix'.format('PREPROCESSING'))

        # wordfixclrea
        if wordfix_path:
            texts = self.wordfix(texts, wordfix_path)
            print('[{0:15s}]: complete wordfix'.format('PREPROCESSING'))

        # posfix
        if posfix_path:
            texts = self.posfix(texts, posfix_path)
            print('[{0:15s}]: complete posfix'.format('PREPROCESSING'))

        return texts

    def stopword(self, x):
        pattern1 = '([ㄱ-ㅎㅏ-ㅣ]+)'
        pattern2 = '[^\w\s,.]'
        pattern3 = '[\d]'
        repl = ''
        x = re.sub(pattern=pattern1, repl=repl, string=x)
        x = re.sub(pattern=pattern2, repl=repl, string=x)
        x = re.sub(pattern=pattern3, repl=repl, string=x)
        return x

    def spacefix(self, x):
        spacer = ChatSpace()
        x = spacer.space(x, batch_size=64)
        x = pd.Series(x).str.split(' ').tolist()

        return x
        
    def wordfix(self, x, path):
        # replace old to new
        def word_replace(x, word_dict):
            for k, v in word_dict.items():
                if k in x:
                    x = x.replace(k, v)
            return x

        # load word dictionary
        word_dict = json.load(open(path,'r'))
        # replace word
        x = pd.Series(x).apply(lambda x: ' '.join(x))
        x = x.apply(lambda sent: word_replace(sent, word_dict))
        x = x.str.split(' ').tolist()

        return x

    def posfix(self, x, path):
        # pos filtering
        def pos_filtering(x, pos, in_pos, stopwords, words):
            remove_value = []
            for k, v in x:
                if len(k) == 1:
                    remove_value.append((k,v))
                elif (v in pos) & (k in stopwords):
                    remove_value.append((k,v))
                elif (v in in_pos) &(k not in words):
                    remove_value.append((k,v))
                elif (v not in pos) & (v not in in_pos):
                    remove_value.append((k,v))
                    
            for v in remove_value:
                x.remove(v)
            
            try:
                return list(np.array(x)[:,0])
            except: # NT : No Token
                return ['NT']

        # load pos dictionary
        pos_dict = json.load(open(path,'r'))
        x = pd.Series(x).apply(lambda x: ' '.join(x))
        x = x.map(self.kkma.pos)
        x = x.apply(lambda pos_lst: pos_filtering(pos_lst, pos_dict['pos'], pos_dict['in_pos'], pos_dict['stop_words'], pos_dict['words']))

        return x.tolist()

    def embedding(self, x, size=100, window=5, min_count=5):
        model = FastText(size=self.embed_size, window=5, min_count=5, sentences=x, seed=223)
        
        return model

    def sent2vec(self, x, model):
        sent_vec = np.zeros((len(x), self.embed_size))
        for i in range(len(x)):
            try:
                sent_vec[i] = model.wv[x[i]].sum(axis=0)
            except:
                continue

        return sent_vec 
        

class Filtering(object):
    def __init__(self, show_features):
        # features 
        self.features = show_features

    def fit(self, data, s_text):
        '''
        args:
        - data: reviews data
        - s_text: preprocessed text

        return:
        - data: filtering data
        '''
        data = self.prod_filter(data, s_text)
        data = self.nb_review_filter(data)
        data = self.rate_filter(data)
        data = self.cat_filter(data, s_text)
        
        return data

    def cat_filter(self, data, s_text):
        '''
        args:
        - data: reviews data
        - s_text: preprocessed text

        return:
        - data: filtering data
        '''
        # check category
        cat_lst = data.category.unique()
        f = set(s_text[0]) & set(cat_lst)
        if len(f) > 0:
            data = data = data[data.category.isin(f)]
            print('[{0:15s}] category (data shape: {1:})'.format('FILTERING',data.shape))
        
        # sorting
        data = data[['dist','rate_x'] + self.features].sort_values(by=['rate_x','dist'])
        data = data[self.features].drop_duplicates()

        return data


    def prod_filter(self, data, s_text):
        '''
        args:
        - data: reviews data
        - s_text: preprocessed text

        return:
        - data: filtering data
        '''
        s_dict = {
                #헤어/바디 항목
                'hair_body_dict':{
            #     '바디워시':['워시','바디 워시','비어 원샷 클렌저 포맨','맨즈 시트러스 민트 3 IN 1'],
            #     '샴푸':['방 덴시피크 옴므','두쉐르 베제딸 뿌르옴므','또니끄 비비휘앙 뿌르옴므','뱅 떼에스 뿌르옴므','뱅 트레땅 알라 프로폴리스 뿌르옴므'],
                '샤워젤':['샤워','샤워 젤'],
                '스프레이':['퍼퓸건','미스트','라스트 샷'],
            #     '로션':['크림','핸드크림','핸드','맨올로지 101 에너자이징 바디 에멀젼'],
                '데오드란트':['데오도란트','맨 블랙 앤 화이트 롤 온','매너 키트','데오도런트'],
                '오일':['맨 퓨어-포먼스 컴포지션']
                },

                #헤어스타일링 항목 
                'hairstyle_dict':{
                '왁스':['무빙러버','젤','하드','헤어잼','크래프트 클레이 리모델러블 매트 텍스처라이저','알앤비','포맨 오리지널 슈퍼 매트','버번 바닐라 & 텐저린 헤어 텍스처라이저','맨 퓨어-포먼스 그루밍 클레이'],
            #     '컬':['볼륨미아 볼륨 무스']
                }
            }

        # intersaction word list to s_dict
        inter_word = []
        for cat, dic in s_dict.items():
            for k, v in dic.items():
                if k in s_text[0]:
                    inter_word = v
                    continue
                for i in v:
                    if i in s_text[0]:
                        inter_word = v

        # filtering
        if len(inter_word) > 0:
            inter_idx = []
            for i, p in enumerate(data['product']):
                for c in inter_word:
                    if c in p:
                        inter_idx.append(i)
            data = data.iloc[inter_idx]
            print('[{0:15s}] product name (data shape: {1:})'.format('FILTERING',data.shape))

        return data

    def nb_review_filter(self, data):
        '''
        args:
        - data: reviews data

        return:
        - data: filtering data
        '''
        def repl(x):
            pattern = '[^\d]'
            return re.sub(pattern, '', x)

        data.nb_reviews = data.nb_reviews.map(repl).astype(int)
        nb_reviews_med = data.nb_reviews.describe().loc['50%']

        data = data[data.nb_reviews >= nb_reviews_med]
        print('[{0:15s}] number of reviews (data shape: {1:})'.format('FILTERING',data.shape) )

        return data


    def rate_filter(self, data):
        rate_dict = {
            'best':0,
            'good':1,
            'soso':2,
            'bad':3,
            'worst':4
        }
        data.rate_x = data.rate_x.map(rate_dict)

        data = data[data.rate_x.isin([0,1])]
        print('[{0:15s}] rating (data shape: {1:})'.format('FILTERING',data.shape)) 

        return data


def l2norm(embed_matrix):
    norm = np.sqrt(np.power(embed_matrix,2).sum(axis=1, keepdims=True))
    embed_matrix = embed_matrix / norm
    return embed_matrix 