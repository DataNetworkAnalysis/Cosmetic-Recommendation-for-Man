'''
1. 자음,모음,특수문자 제거 (온점, 쉼표 포함)
2. 띄어쓰기 교정
3. 단어 수정
4. 형태소분석기로 명사 and 형용사 추출 
5. Fasttext embedding

- 사전 추가
'''


import pandas as pd 
from chatspace import ChatSpace
from gensim.models import FastText
from konlpy.tag import Kkma 
from scipy.spatial.distance import cosine

import pickle
import argparse
import re
import numpy as np 

parser = argparse.ArgumentParser()
parser.add_argument('--train',action='store_true', help='train or not')
parser.add_argument('--path',type=str,default='../dataset/glowpick_reviews.csv', help='file path')
parser.add_argument('--search',type=str,help='text to search')
args = parser.parse_args()


class GlowpickPreprocessing(object):
    def __init__(self, embed_size=100):
        self.embed_size = embed_size

    def fit(self, x, use_wordfix=False, use_pos=False):
        '''
        return:
            texts: preprocessed texts
        '''
        # stopword
        texts = list(map(self.stopword, x))
        print('[Log]: complete stopword')

        # spacefix
        texts = self.spacefix(texts)
        print('[Log]: complete spacefix')

        # wordfixclrea
        if use_wordfix:
            texts = self.wordfix(texts)
            print('[Log]: complete wordfix')

        # posfix
        if use_pos:
            texts = self.posfix(texts)

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
        texts = spacer.space(x, batch_size=64)
        texts = pd.Series(texts).str.split(' ').tolist()

        return texts

    def posfix(self, x):
        return x 
        
    def wordfix(self, x):
        
        return x

    def embedding(self, x, size=100, window=5, min_count=5):
        model = FastText(size=self.embed_size, window=5, min_count=5, sentences=x)
        
        return model

    def sent2vec(self, x, model):
        sent_vec = np.zeros((len(x), self.embed_size))
        for i in range(len(x)):
            sent_vec[i] = model.wv[x[i]].sum(axis=0)

        return sent_vec 

# Load data
data = pd.read_csv(args.path)
# train
GP = GlowpickPreprocessing()
kkma = Kkma()
if args.train:    
    # train set
    text = GP.fit(data.content.tolist())
    # embdding model
    model = GP.embedding(text)
    model.save('model.bin') # save

    # save sent text
    text = GP.sent2vec(text, model)
    with open('preprocessed_text.txt','wb') as f:
        pickle.dump(text,f)
else:
    # load embed model
    model = FastText.load('model.bin')
    # test
    test_text = GP.fit([args.search])
    print('test_text: ',test_text)
    test_sent_vec = GP.sent2vec(test_text, model)
    print('test sent vector: ',test_sent_vec)

    print('\n\n')
    for sent in test_text:
        nouns_lst = kkma.nouns(' '.join(sent))
        for word in nouns_lst:
            print('-'*100)
            print(word)
            print('----')
            print(model.wv.most_similar(word))

    # similarity
    with open('preprocessed_text.txt','rb') as f:
        sent_vec = pickle.load(f)

    dist_arr = np.zeros((sent_vec.shape[0]))
    for i, sent in enumerate(sent_vec):
        dist = cosine(sent, test_sent_vec[0])
        dist_arr[i] = dist

    
    data['dist'] = dist_arr
    data.to_csv('../dataset/review_dist.csv')
