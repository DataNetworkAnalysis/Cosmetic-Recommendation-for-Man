"""
1. l2norm 변환
2. kmeans_arms 그림 그리기
3. 2D scatter 그리기
4. wordcloud
"""


import pickle
import numpy as np
import pandas as pd
import seaborn as sns
from preprocessing import l2norm
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from wordcloud import WordCloud
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib
from IPython.display import set_matplotlib_formats
matplotlib.rc('font', family = 'Malgun Gothic')
set_matplotlib_formats('retina')
matplotlib.rc('axes',unicode_minus = False)

class preprocessing_words:
    def __init__(self):
        self.pca = PCA(n_components=2, random_state=42)

    def fit(self, embed_matrix,words,k):
        '''
        k : Number of clusters
        embed_matrix : embedding pile(pickle)
        words : words pile(pickle)
        '''
        embed = self.l2norm(embed_matrix)
        self.clustering_plot(embed,k)
        self.wordcloud(words, k)



    # function

    # l2norm 변환
    def l2norm(self, embed_matrix: pickle):
        norm = np.sqrt(np.power(embed_matrix,2).sum(axis=1, keepdims=True))
        embed_matrix = embed_matrix / norm
        return embed_matrix

    # clustering_arms
    def clustering_arms(self, embed_matrix):
        iner_li = []
        for i in range(1,10):
            kmeans = KMeans(n_clusters = i, random_state = 42).fit(embed_matrix)
            iner_li.append(kmeans.inertia_)
        plt.plot(np.arange(1,10), iner_li)
        plt.savefig('../images/arms.png', dpi = 300)

    # kmeans
    def clustering_plot(self, embed_matrix, k):
        self.df = pd.DataFrame(embed_matrix)
        kmeans = KMeans(n_clusters = k, random_state = 42).fit(embed_matrix)
        outputs = kmeans.predict(embed_matrix)
        self.df['labels'] = outputs
        # scatter 2D plot
        pca_df = pd.DataFrame(self.pca.fit_transform(self.df.drop('labels', axis = 1)))
        pca_df['labels'] = self.df['labels']
        pca_df.columns = ['p1','p2','labels']
        pca_df['labels'] = pca_df.labels.astype(str)
        plt.figure(figsize = (15,15))
        for i in pca_df.labels.unique():
            sns.scatterplot(x = 'p1', y = 'p2', data = pca_df[pca_df.labels == i], label = i, alpha = 0.3)
            plt.legend()
            plt.savefig('../images/pca_scatter.png', dpi = 300)
        return self.df


    def wordcloud(self, words,k,min_count = 0):
        '''
        min_count : 워드클라우드에 나타낼 최소 단어수
        '''
        plt.clf()
        for i in range(k):
            word_li = []
            for idx in self.df.loc[self.df['labels'] == i].index:
                for word in words[idx]:
                    word_li.append(word)
            word_li_count = pd.DataFrame(word_li)[0].value_counts()
            word_dict = dict(word_li_count)
            wordcloud = WordCloud(min_word_length = min_count,font_path = 'C:/Windows/Fonts/malgun.ttf', background_color='white',colormap = "Accent_r", width=1500, height=1000).generate_from_frequencies(word_dict)
            plt.imshow(wordcloud)
            plt.axis('off')
            plt.show()
            plt.clf()  
            wordcloud.to_file('../images/class{0}_k={1}.png'.format(i,k))