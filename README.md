# 화알못 남성을 위한 화장품 바이블

- Member: 조하늘, 이재헌, 김진우, 허재혁  
- Status: Doing  
- Tag: Project  

# Why

1년의 올리브영 아르바이트 기간 동안, 같은 성별인 여성 고객들에게는 비교적 쉽게 추천할 수 있었으나, **남성 고객들에게 제품 추천은 매우 어렵고 생소했음**.
실제로 알바를 하며 이러한 어려움을 겪은 경우가 많았고, 이를 해결해보고자 올리브영 남성제품에 대한 분석을 결정

# Purpose

1. 원하는 화장품에 대해 문장을 입력하면 관련 상품들을 추천
2. 추천된 상품들에 대한 정보를 대시보드 형태로 요약하여 제공

# Data

[글로우픽(glowpick)](https://www.glowpick.com/) 데이터를 사용하여 **남성** **제품** 관련 리뷰 데이터 이용

1. glowpick_products

Feature | Type | Description
---|---|---
brand | string | 브랜드명
product | string | 제품명
vol_price | string | 해당 제품의 용량 & 가격
rate | float | 해당 제품의 평점
nb_reviews | string | 해당 제품의 리뷰 수
sales_rank | string | 해당 카테고리의 판매 순위
product_url | string | 해당 제품의 url 
category | string | 카테고리
title | string | 대분류

2. glowpick_reviews

Feature | Type | Description
---|---|---
date | string | 댓글 단 날짜 (수집일 기준)
user_id | string | 유저 ID
sex | string | 성별
age_skin_type | string | 나이 & 피부 유형 (건성/지성/중성/복합성/민감성)
rate | string | 선호도 (best/good/soso/bad/worst)
content | string | 리뷰 내용
product_url | string | 해당 제품의 url

# How to Run

**Data bCrawling**
```bash
$ python glowpick.py
$ python reviews.py
```

**Preprocessing**
```bash
$ bash preprocessing.sh
```

**test**
```bash
$ bash test.sh "검색문장"
```

# Results

## 군집분석(Clustering Analysis)

최적의 k를 구하기위해 1부터 9까지 kmeans를 실행한 후 clustering 결과마다 Inertia 값을 비교하여 그 차이가 줄어드는 지점의 k로 결정한다.

$$Inertia = \sum_{k=1}^K \sum_{i \in C_k} d(x_i, \mu_k)$$

여기서 $K$는 클러스터 수이고 $C_k$는 $k$번째 클러스터에 속하는 데이터의 집합, $\mu_k$는 $k$번째 클러스터의 중심위치, $d$는 $x_i$, $\mu_k$ 두 데이터 사이의 거리(distance) 혹은 비유사도(dissimilarity)로 정의한다.

내용 출처: https://datascienceschool.net/view-notebook/2205ad8f0c5947c08696e8927b466341/

<p align="center">
    <img src="https://github.com/DataNetworkAnalysis/Cosmetic-Man/blob/master/images/arms.png?raw=true">
<p>

적절한 군집수는 6으로 결정했고 각 결과에 대해 시각화하기 위해서 차원축소 방법 중 하나인 주성분분석(Principle Component Analysis)를 사용한다. 임베딩 벡터 차원 수를 시각화할 수 있도록 2차원으로 축소 후 클래스별로 산점도를 그렸다.

군집2의 경우 군집0,3과 유사한 점이 많고 군집 4의 경우 수가 적고 다른 군집과 섞여있었다. 더 정확한 해석을 하기위해 각 군집별 리뷰데이터를 워드클라우드로 확인한다.

<p align="center">
    <img src="https://github.com/DataNetworkAnalysis/Cosmetic-Man/blob/master/images/pca_scatter.png?raw=true">
<p>

각 군집별 특징을 워드클라우드로 보았을 때 우선 군집 4의 경우 NT(No Token)라는 단어가 가장 크고 단어 수가 비교적 적음을 알 수 있다. 이는 전처리 과정에서 형태소 분석시 추출된 단어가 없는 경우 NT(No Token)로 처리했기 때문이다. 군집4는 제외하고 다른 군집들에 대해서 각각 해석하도록한다.

**군집 해석**
- **신사의 품격**(군집 0)
    - 주 키워드는 사용/피부/느낌이며 주로 바르는 화장품과 관련된 내용있었다. 사용감, 즉 촉감에 예민한 사람들을 위한 화장품들이 모여있다. 끈적거림을 싫어하는 사람이라면 이 군집을 화장품을 살펴보도록 하자.
- **가뭄의 단비**(군집 1)
    - 군집 1과 유사해보이지만 촉촉/건조/수분/크림과 같은 키워드가 더 많이 보인다. 리뷰별 상품들을 확인했을 때 주로 피부 유형이 건성인 사람들을 위한 화장품들이 모여있다. 추운 겨울 건조한 피부 때문에 고민이라면 이 군집의 화장품을 보는게 좋다.
- **홀애비탈출키트**(군집 2)
    - 주 키워드는 냄새/향수/아빠/선물 이다. 인상 깊은 리뷰는 "아빠와 남동생이 덕분에 더이상 냄새가 나지않아요" 였다. 지옥철 한가운데에서 유난히 내 주변에만 사람이 한가한편이라면 이 군집에 있는 화장품들을 살펴보는게 좋을듯 하다.
- **미용실가지뫄**(군집 3)
    - 주 키워드는 가격/사용/머리/고정 이다. 남자의 생명은 머리라는 말도 있다. 남자들이 가장 많이 찾는 카테고리를 고르자면 헤어스타일링을 빼놓을 수가 없다. 여름에 비바람이 불고 겨울에 찬바람이 불어도 끄떡없는 헤어제품을 원한다면 이 군집에 있는 제품들을 보자.
- **피부영세시대**(군집5)
    - 이 군집은 피부영세시대라 쓰고 피부young세시대 또는 피부0세시대라고 읽는다. 자극에 예민하거나 피부에 트러블이 많아서 고민이 많다면 다시 아기피부로 돌아가기위해 이 군집의 제품들을 보는것을 추천한다.

<p align="center">
    <img src="https://github.com/DataNetworkAnalysis/Cosmetic-Man/blob/master/images/class(k=6).png?raw=true">
<p>


## 상품 추천(Product Recommendation)

혼자사는 남자들을 위한 향 좋은 화장품을 찾기위해서 **"홀애비 냄새나는 남사친을 위한 향 좋은 제품"** 이라는 문장을 검색해보았다. 주변에 혼자사는 남사친들에게서 이런 생각을 해봤고 선물을 줘야하는 경우가 생겼다면 한 번 쯤 검색해서 괜찮은 제품이 뭐가 있을지 확인해볼 수 있다.

```bash
$ bash test.sh '홀애비 냄새나는 남사친을 위한 향 좋은 제품'
```

주로 향수 관련된 제품들이 많았다. 냄새를 없애는데 가장 좋은 방법인 것 같다. 그러나 가격을 고려했을때 다음에도 또 보고싶은 남사친이 아니라면 선물은 자제하는게 좋을 거 같다.

category	|brand	|nb_reviews|	vol_price	|product	|product_url
---|---|---|---|---|---
향초   	| 양키캔들 (YANKEE CANDLE)	|113	|623g39,000원	|미드나잇 쟈스민	|/product/43548
여성향수	| 안나수이 (ANNA SUI)	 | 193|	30ml62,000원	|라뉘드 보헴 오 드 뚜왈렛	|/product/16708
남성향수	| 샤넬 (CHANEL)	|59   |	50ml114,000원	|블루 드 샤넬 오 드 빠르펭|	/product/16788
남성향수	| 샤넬 (CHANEL)	|89  	|100ml140,000원	|알뤼르 옴므 스포츠 오 드 뚜왈렛 스프레이|	/product/3297
남성향수	| 페라리 (Ferrari)  |	206	|40ml45,000원	|스쿠데리아 블랙 EDT	|/product/3338


추천된 상품들의 리뷰 내용을 살펴봤을때 주로 향수/냄새/느낌/여자/친구/잔향 이 눈에 띈다.

<p align="center">
    <img src="https://github.com/DataNetworkAnalysis/Cosmetic-Man/blob/master/images/rys_wordcloud.jpg?raw=true">
<p>

추천된 목록의 리뷰들에 대해 앞서 분류한 군집들간 비교해보았을때 검색 키워드에 맞게 "홀애비탈출키트" 지수가 가장 높았다. 추천 상품들에 대한 평이 향과 관련된 내용들이라는 것을 알 수 있다.

<p align="center">
    <img src="https://github.com/DataNetworkAnalysis/Cosmetic-Man/blob/master/images/rys_radar.png?raw=true">
<p>
