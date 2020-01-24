"""
1. l2norm 변환
2. kmeans_arms 그림 그리기
3. 2D scatter 그리기
4. wordcloud
"""

import pickle
import re
import numpy as np
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

from preprocessing import l2norm

import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

class Clustering:
    def __init__(self, embed_matrix, words, random_state=24):
        self.seed = random_state
        self.k = None

        self.pca = PCA(n_components=2, random_state=self.seed)

        self.embed_matrix = l2norm(embed_matrix)
        # remove (.) and join elements
        words = [re.sub('[^\w\s]','',' '.join(w_lst)) for w_lst in words]
        self.words_df = pd.DataFrame(words, columns=['content'])
    
    def fit(self, k, savedir=None, **kwargs):
        '''
        # kmeans
        '''
        figsize = (10,10) if 'figsize' not in kwargs.keys() else kwargs['figsize']
        labelsize = 10 if 'labelsize' not in kwargs.keys() else kwargs['labelsize']
        titlesize = 10 if 'titlesize' not in kwargs.keys() else kwargs['titlesize']

        self.k = k
        
        # k-means clustering
        kmeans = KMeans(n_clusters=k, random_state=self.seed).fit(self.embed_matrix)
        outputs = kmeans.predict(self.embed_matrix)
        self.words_df['labels'] = outputs

        # dimension reduction
        pca_df = pd.DataFrame(self.pca.fit_transform(self.embed_matrix))

        # scatter 2D plot
        pca_df['labels'] = outputs
        pca_df.columns = ['PC1','PC2','labels']
        pca_df['labels'] = pca_df.labels.astype(str)

        plt.figure(figsize=figsize)

        for i in range(self.k):
            sns.scatterplot(x='PC1', y='PC2', data=pca_df[pca_df.labels == str(i)], label=f'cluster {i}', alpha=0.3)
        plt.legend(prop={'size':labelsize})
        plt.title(f'K-means Cluster Analysis Results (k={k})', size=titlesize)
        plt.xlabel('PC1',size=labelsize)
        plt.ylabel('PC2',size=labelsize)

        # save plot
        if savedir:
            plt.tight_layout()
            plt.savefig(f'{savedir}/pca_scatter.png', dpi=100)

    def clustering_arms(self, savedir=None, **kwargs):
        '''
        clustering_arms
        '''

        color = 'purple' if 'color' not in kwargs.keys() else kwargs['color']
        labelsize = 10 if 'labelsize' not in kwargs.keys() else kwargs['labelsize']
        titlesize = 10 if 'titlesize' not in kwargs.keys() else kwargs['titlesize']
        
        iner_li = []
        for i in range(1,10):
            kmeans = KMeans(n_clusters=i, random_state=self.seed).fit(self.embed_matrix)
            iner_li.append(kmeans.inertia_)
        
        plt.plot(np.arange(1,10), iner_li, marker='D', linewidth=2, color=color)
        plt.title('Elbow Methods For Optimal k', size=titlesize)
        plt.xlabel('K', size=labelsize)
        plt.ylabel('Inertia', size=labelsize)

        # save plot
        if savedir:
            plt.tight_layout()
            plt.savefig('../images/arms.png', dpi=100)

    def wordcloud(self, min_count=0, font_path='C:/Windows/Fonts/malgun.ttf', savedir=None, **kwargs):
        '''
        min_count : 워드클라우드에 나타낼 최소 단어수
        '''
        figsize = (10,10) if 'figsize' not in kwargs.keys() else kwargs['figsize']
        titlesize = 10 if 'titlesize' not in kwargs.keys() else kwargs['titlesize']
        row = 2 if 'row' not in kwargs.keys() else kwargs['row']

        f, ax = plt.subplots(row,self.k//row, figsize=figsize)
        for i in range(self.k):
            
            words_df_i = self.words_df[self.words_df.labels==i]
            words_lst_i = ' '.join(words_df_i.content.tolist())
            wordcloud = WordCloud(min_word_length=min_count, font_path=font_path , background_color='white').generate(words_lst_i)
            ax[i//(self.k//row),i%(self.k//row)].imshow(wordcloud)
            ax[i//(self.k//row),i%(self.k//row)].axis('off')
            ax[i//(self.k//row),i%(self.k//row)].set_title(f'Cluster {i}', size=titlesize)
            
        # save plot
        if savedir:
            plt.tight_layout()
            plt.savefig(f'../images/class(k={self.k}).png',dpi=100)
