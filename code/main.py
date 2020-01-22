from scipy.spatial.distance import cosine
from gensim.models import FastText
from konlpy.tag import Kkma 

import pickle
import argparse
import os

import pandas as pd
import numpy as np 
from preprocessing import GlowpickPreprocessing, Filtering
from loaddata import load

import warnings
warnings.filterwarnings('ignore')

parser = argparse.ArgumentParser()
# preprocessing
parser.add_argument('--train',action='store_true', help='train or not')
parser.add_argument('--reviewpath',type=str,default='../dataset/glowpick_reviews.csv', help='reviews path')
parser.add_argument('--productpath',type=str,default='../dataset/glowpick_products.csv', help='products path')
parser.add_argument('--wordpath',type=str,default=None, help='replace word dictionary')
parser.add_argument('--pospath',type=str,default=None, help='filtering pos dictionary')
parser.add_argument('--embed_size',type=int,default=100, help='ebedding vector size')
parser.add_argument('--savedir',type=str,default='../saved_file', help='directory path to save model and preprocessed file')
# evaluation
parser.add_argument('--search',type=str,help='text to search')
args = parser.parse_args()

################################
# check savedir
################################
if not os.path.isdir(args.savedir):
    os.mkdir(args.savedir)


################################
# configuration
################################
# preprocessing
GP = GlowpickPreprocessing()

# save names
modelname = 'new_model'
pre_textname = 'new_pre_text'
pre_embedname = 'new_pre_embed'

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

################################
# train or evaluation
################################
if args.train:    
    print('[{0:.15s}] Train'.format('STATE'))
    # 1. load data
    data, _ = load(args)

    # 2. preprocessing train set
    text = GP.fit(data.content.tolist(), 
                  wordfix_path=args.wordpath,
                  posfix_path=args.pospath)
    
    # 3. embdding model
    model = GP.embedding(text)
    model.save(f'{args.savedir}/{modelname}.bin') # save

    # save preprocessed text
    with open(f'{args.savedir}/{pre_textname}.pickle','wb') as f:
        pickle.dump(text,f)

    # save sentence embedding vector
    embed = GP.sent2vec(text, model)
    with open(f'{args.savedir}/{pre_embedname}.pickle','wb') as f:
        pickle.dump(embed,f)
else:
    print('[{0:15s}] Evaluation'.format('STATE'))
    # configuration
    # - feature selection
    show_features = ['category','brand','nb_reviews','vol_price','product']
    # - molphs analyzer
    kkma = Kkma()
    # - load embed model
    model = FastText.load(f'{args.savedir}/{modelname}.bin')
    # - filtering class
    filtering = Filtering(show_features)
    
    # 1. load data
    data, products = load(args)

    # 2. preprocessing new sentence
    test_text = GP.fit([args.search], args.wordpath, args.pospath)
    print('[{0:15s}] result : {1:}'.format('PREPROCESSING',test_text))
    test_sent_vec = GP.sent2vec(test_text, model)

    # 3. calculration similarity : cosine distance
    sent_vec = pickle.load(open(f'{args.savedir}/{pre_embedname}.pickle','rb'))
    dist_arr = np.zeros((sent_vec.shape[0]))
    for i, sent in enumerate(sent_vec):
        dist = cosine(sent, test_sent_vec[0])
        dist_arr[i] = dist
    data['dist'] = dist_arr
    data = pd.merge(data, products, on='product_url', how='left')

    # 4. featering
    data = filtering.fit(data, test_text)

    # choice top-5
    print()
    for i in range(data.shape[0]):
        for j in data.iloc[i]:
            print('{0:.50s} / '.format(str(j)), end="")
        print('\n')
        if i == 4:
            break
