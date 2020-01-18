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
        print('[Log]: complete stopword')

        # spacefix
        texts = self.spacefix(texts)
        print('[Log]: complete spacefix')

        # wordfixclrea
        if wordfix_path:
            texts = self.wordfix(texts, wordfix_path)
            print('[Log]: complete wordfix')

        # posfix
        if posfix_path:
            texts = self.posfix(texts, posfix_path)
            print('[Log]: complete posfix')

        return texts

    def stopword(self, x):
        pattern1 = '([ㄱ-ㅎㅏ-ㅣ]+)'
        pattern2 = '[^\w\s,.]'
        repl = ''
        x = re.sub(pattern=pattern1, repl=repl, string=x)
        x = re.sub(pattern=pattern2, repl=repl, string=x)
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
            sent_vec[i] = model.wv[x[i]].sum(axis=0)

        return sent_vec 