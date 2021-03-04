from django.shortcuts import render

# Create your views here.
#!pip install scikit-surprise

import pandas as pd # raw dataset
from surprise import SVD, accuracy # SVD model, 평가
from surprise import Reader, Dataset # SVD model의 dataset
import surprise

#filepath = '../travel/static/placerating.csv'
#user_id = 1
results =[]

# def Cal_Svd(filepath, user_id):
#     # 1. raw dataset
#     rating = pd.read_csv(filepath)
def Cal_Svd(rating, user_id):
#     rating['userId'].value_counts()
#     rating['placeId'].value_counts()
    print(rating.head())
    del rating['treviewno']
    # 관광 vs 미관광
#     tab = pd.crosstab(rating['userId'], rating['placeId'])
    #print(tab)
    
    # rating
    # 두 개의 집단변수를 가지고 나머지 rating을 그룹화
    rating_g = rating.groupby(['treviewid', 'tourid'])
    tab = rating_g.sum().unstack() # 행렬구조로 변환
    print(tab)
    #print(tab.info())
    #사용자 2이 가지 않은 곳, 1,15, 39....
    
    # 2. rating 데이터셋 생성
    reader = Reader(rating_scale= (1, 5)) # 평점 범위
    data = Dataset.load_from_df(df=rating, reader=reader)
    # rating이라는 데이터프레임은 reader(1~5)의 평점 범위를 가진다.
    #print(data)
    
    # 3. train/test set
    train = data.build_full_trainset() # 훈련셋
    test = train.build_testset() # 검정셋
    
    # 4. model 생성
    #help(SVD)
    model = SVD(n_factors=100, n_epochs=20, random_state=123)
    model.fit(train) # model 생성
    
    
    # 5. user_id 입력
    #user_id = 1 # 추천대상자
    item_ids = range(0, 2058) # placeId 범위
    actual_rating = 0 # 평점
    
    predict_result = []
    
    for item_id in item_ids :
        if not actual_rating in tab:
            actual_rating = 0
            predict_result.append(model.predict(user_id, item_id, actual_rating))
    ddff = pd.DataFrame(predict_result)
    #print(ddff)
   
    # 유저 1 추천 여행지 상위 5개
    result = ddff.sort_values(by='est', ascending=False)[:5]
    #print(result)
    results.append(result)
    
    return result
# 
# if __name__ == '__main__':
#     Cal_Svd(filepath, user_id)
#     print(results[0])
    #print(type(results[0]))     #dataframe     
    #print(results[0]['iid'])        # placeId