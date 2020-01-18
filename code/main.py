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
parser.add_argument('--savedir',type=str,default='../saved_file', help='directory path to save model and preprocessed file')
# evaluation
parser.add_argument('--search',type=str,help='text to search')
parser.add_argument('--modelname',type=str,help='embedding model name')
parser.add_argument('--pre_filename',type=str,help='preprocessed filename')
args = parser.parse_args()


# check savedir
if not os.path.isdir(args.savedir):
    os.mkdir(args.savedir)

# Load data
data = pd.read_csv(args.filepath)
# train
GP = GlowpickPreprocessing()
if args.train:    
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
    model = FastText.load(f'{args.savedir}/{args.modelname}')
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
    with open(f'{args.savedir}/{args.pre_filename}','rb') as f:
        sent_vec = pickle.load(f)

    dist_arr = np.zeros((sent_vec.shape[0]))
    for i, sent in enumerate(sent_vec):
        dist = cosine(sent, test_sent_vec[0])
        dist_arr[i] = dist

    
    data['dist'] = dist_arr
    data.to_csv('../dataset/review_dist.csv')
