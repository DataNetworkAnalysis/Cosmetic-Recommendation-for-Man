# 화알못 남성을 위한 화장품 바이블

- Member: 조하늘, 이재헌, 김진우, 허재혁  
- Status: Doing  
- Tag: Project  

## Why

1년의 올리브영 아르바이트 기간 동안, 같은 성별인 여성 고객들에게는 비교적 쉽게 추천할 수 있었으나, **남성 고객들에게 제품 추천은 매우 어렵고 생소했음**.
실제로 알바를 하며 이러한 어려움을 겪은 경우가 많았고, 이를 해결해보고자 올리브영 남성제품에 대한 분석을 결정

## Purpose

1. 원하는 화장품에 대해 문장을 입력하면 관련 상품들을 추천
2. 추천된 상품들에 대한 정보를 대시보드 형태로 요약하여 제공

## Data

[글로우픽(glowpick)](https://www.glowpick.com/) 데이터를 사용하여 **남성** **제품** 관련 리뷰 데이터 이용


## How to Run
Data Crawling
```
# Glowpick Data
python glowpick.py
python reviews.py
```

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
