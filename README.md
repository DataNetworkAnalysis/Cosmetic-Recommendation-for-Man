# 올리브영 남성고객 제품 추천

- Member: 조하늘, 김진우, 이재헌, 허재혁  
- Status: Doing  
- Tag: Project  

## Why

1년의 올리브영 아르바이트 기간 동안, 같은 성별인 여성 고객들에게는 비교적 쉽게 추천할 수 있었으나, **남성 고객들에게 제품 추천은 매우 어렵고 생소했음**.
실제로 알바를 하며 이러한 어려움을 겪은 경우가 많았고, 이를 해결해보고자 올리브영 남성제품에 대한 분석을 결정

## Purpose

1. 남성 고객의 **나이대별**로 어떤 제품을 추천할지 분석
2. 같은 용도의 제품들은 **브랜드별로 어떤 차이가 존재하는지** 분석
3. 분석한 것을 그래프로 **시각화**해보기

이후 새로운 내용에 대해 추가될 예정

## Data

1. 전국 올리브영 매장의 모든 품목이 담겨있는 올리브영 공식 홈페이지의 **남성** **제품** 관련 데이터 이용
2. 글로우픽 데이터를 사용하여 **남성** **제품** 관련 리뷰 데이터 이용

## How to Run
Data Crawling
```
# OliveYoung Data
python olive_young.py

# Glowpick Data
python glowpick.py
python reviews.py
```


## Reference

[올리브영 공식 온라인몰](http://www.oliveyoung.co.kr/store/main/main.do)
[글로우픽](https://www.glowpick.com/)
