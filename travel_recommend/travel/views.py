from django.shortcuts import render, redirect
from django.http.response import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from travel.models import Travel, Tuser, Treview, Tgenre
import MySQLdb
from datetime import datetime, timedelta
from dateutil.parser import parse
from django.db.models import Max
from travel.weather import Weather
from travel.cosine_sim import cosinePlace
import json
import numpy as np
import recommend_app.cal_svd, recommend_app.cal_knn
import pandas as pd
import os
from jamo import h2j, j2hcj
config = {
    'host':'127.0.0.1',
    'user':'root',
    'password':'123',
    'database':'test',
    'port':3306,
    'charset':'utf8',
    'use_unicode':True
}
conn = MySQLdb.connect(**config)
travelall = ""
treviewall = ""
# Create your views here.

def IndexFunc(request):
    global travelall
    global treviewall
    travelall = Travel.objects.all()
    #print(travelall)
    treviewall = Treview.objects.all()
    return render(request, 'index.html')

def LoginFunction(request):
    # DB에 값 넣기
    path = os.getcwd()
    print(path)
    print(travelall)
#     rat = pd.read_excel(path + '/travel_recommend/travel/static/datafile/prating2020.xlsx')
#     place = pd.read_excel(path + '/travel_recommend/travel/static/datafile/국내자료2020.xlsx')
#     genredf = pd.read_excel(path + '/travel_recommend/travel/static/datafile/장르2020.xlsx')
#          
#     gdatas = []
#     for g in range(len(genredf)):
#         Tgenre(
#             genreid = np.round(genredf.iloc[g].genreId,0),
#             genrename = genredf.iloc[g].genrename
#         ).save()
#         gdic = {'genreId':np.round(genredf.iloc[g].genreId,0), 'genreName':genredf.iloc[g].genrename}
#         gdatas.append(gdic)
#     df3 = pd.DataFrame(gdatas)
#     print(df3)
#     pdatas = []
#  
#     for p in range(len(place)):
# #         pdic = {'placeId':np.round(place.iloc[p].placeId,0),'sido':place.iloc[p].sido,'sigungu':place.iloc[p].sigungu,'placeName':place.iloc[p].placename,'count':np.round(place.iloc[p].count,0),'score':np.round(place.iloc[p].score,2),'tscore':np.round(place.iloc[p].tscore,0),'genre':np.round(place.iloc[p].genreId,0)}
# #         print(pdic)
# #         print(Tgenre.objects.get(genreid = np.round(place.iloc[p].genre,0)).genreid)
# #         Travel(
# #             tourId = np.round(place.iloc[p].placeId,0),
# #             city = place.iloc[p].sido,
# #             town = place.iloc[p].sigungu,
# #             tourName = place.iloc[p].placeName,
# #             genre = np.round(place.iloc[p].genre,0)
# #         ).save() 
#         tourid = np.round(place.iloc[p].placeId,0)
#         city = place.iloc[p].sido
#         town = place.iloc[p].sigungu
#         tourname = place.iloc[p].placename
#         cnt = place.iloc[p]['count']
#         print(cnt)
#         score = place.iloc[p].score
#         tscore = place.iloc[p].tscore
#         genre = np.round(place.iloc[p].genreId,0)
#         
#         sql = "insert into travel values({},'{}','{}','{}',{},{},{},{})".format(tourid,city, town, tourname,cnt,score,tscore, genre)
#         sql = "update travel set score = {} where tourId = {}".format(score, tourid)
#         print(tourid,city, town, tourname,cnt,score,tscore, genre)
#         cursor = conn.cursor()
#         cursor.execute(sql)
#         conn.commit()
# #         pdatas.append(pdic)
# #     df2 = pd.DataFrame(pdatas)
# #     print(df2)
#     rdatas = []
#     i = 0
#     for r in range(len(rat)):
#         rdic = {'userId':int(rat.iloc[r].userId),'placeId':int(rat.iloc[r].placeId),'rating':rat.iloc[r].rating}
#         print(rdic)
#         i += 1
# #         Treview(
# #             treview_no = i,
# #             treview_id = np.round(rat.iloc[r].userId,0),
# #             tourid = np.round(rat.iloc[r].placeId,0),
# #             rating = rat.iloc[r].rating
# #         ).save()
#         treviewno = i
#         treviewid = int(rat.iloc[r].userId)
#         tourid = int(rat.iloc[r].placeId)
#         rating = rat.iloc[r].rating
#         print("insert into treview values({},{},{},{})".format(treviewno, treviewid, tourid, rating))
#         sql = "insert into treview values({},{},{},{})".format(treviewno, treviewid, tourid, rating)
#         cursor = conn.cursor()
#         cursor.execute(sql)
#         conn.commit()
#         rdatas.append(rdic)
#     df1 = pd.DataFrame(rdatas)
#     print(df1)

    
    return render(request, 'login.html')

def LoginFunc(request):
    id = request.POST.get('id')
    pwd = request.POST.get('pwd')

    if Tuser.objects.filter(user_id = id).exists() == True:
        tusers = Tuser.objects.filter(user_id = id)
    else:
        ss = '''
            <script> 
                alert('아이디 또는 비밀번호가 일치하지 않습니다');
                history.back();
            </script>
        '''
        return render(request, 'login.html', {'error' : ss})
    
    for user in tusers:
#         print(user.user_pwd)
        if user.user_pwd != pwd:
            ss = '''
            <script> 
                alert('아이디 또는 비밀번호가 일치하지 않습니다');
                history.back();
            </script>
            '''
            return render(request, 'login.html', {'error' : ss})
        
        request.session['user'] = user.user_name
        request.session['user_id'] = user.user_id
#         print(user.user_name)
        return redirect('main') # urls에 name값 할당
        
def LogoutFunc(request):
    #print(request.session.get('user'))
    if request.session.get('user'):
        del(request.session['user'])
        del(request.session['user_id'])
    #print(request.session.get('user')) # 세션 삭제된것 확인
    return redirect('home')


def UserMainFunc(request):
    user_log = request.session.get('user')
    user_id = request.session.get('user_id')
#     userinfo = str(user_log) + "(" + str(user_id) + ")"
    print(type(str(user_id)), str(user_id))
    print(user_log) # 세션 값 = 사용자 이름
    if user_log == None:
        return redirect('loginform')
    travel_part = Travel.objects.all()
#     print(travelall)
#     print(travel_part[0].tourid)
    tid = []
    for tr in travel_part:
        tid.append(tr.tourid)
        print(tr.tourid)
    rno = []
    rid = []
    rate = []
    trid = []
    for i in tid:
        print(i)
        rat = Treview.objects.filter(tourid = i)
#             print(len(rat))
        for r in rat:
#                 print(i)
            rno.append(r.treviewno)
            rid.append(r.treviewid.user_id)
            trid.append(r.tourid.tourid)
            rate.append(r.rating)
    
#         for r in rating:
# #             print(r.tourid)
#             rno.append(r.treview_no)
#             rid.append(r.treview_id)
#             rate.append(r.rating)
    print(len(rno),len(rid),len(trid),len(rate))
    rdic = {'treviewno':rno,'treviewid':rid,'tourid':trid, 'rating':rate}
    rdf1 = pd.DataFrame(rdic)    
    rdf2 = pd.DataFrame(rdic)     
#         print(type(rdf))
    results1 = recommend_app.cal_knn.Cal_Knn(rdf1, user_id)
    results2 = recommend_app.cal_svd.Cal_Svd(rdf2, user_id)
#         print(results)
#         print(results['iid'].values)

    travel = Travel.objects.all()
    tlist1 = results1['iid'].values
    tlist2 = results2['iid'].values        
    
    flist1 = []
    for f in tlist1 :
        for t in travel:
            if t.tourid == f:
                tour = t.tourname
                area = t.city + ' ' + t.town
                genrename = t.genre.genrename
                cnt = t.count
                score = t.score
                tscore = t.tscore
                print(tscore)
                tdic = {'tour':tour,'area':area,'genrename':genrename, 'cnt':cnt, 'score':score,'tscore':tscore}
#             filepath = path + '/travel_recommend/travel/static/datafile/국내여행지.xlsx'    
        #tour = Travel.objects.filter(placeId = f)
        flist1.append(tdic)
    print(flist1)
    
    flist2 = []
    for f in tlist2 :
        for t in travel:
            if t.tourid == f:
                tour = t.tourname
                area = t.city + ' ' + t.town
                genrename = t.genre.genrename
                cnt = t.count
                score = t.score
                tscore = t.tscore
                tdic = {'tour':tour,'area':area,'genrename':genrename, 'cnt':cnt, 'score':score,'tscore':tscore}
#             filepath = path + '/travel_recommend/travel/static/datafile/국내여행지.xlsx'    
        #tour = Travel.objects.filter(placeId = f)
        flist2.append(tdic)
    print(flist2)
    
    #tour = ['여행지1', '여행지2', '여행지3', '여행지4', '여행지5']

    return render(request, 'recommendmain.html', {'tour_knn':flist1, 'tour_svd':flist2, 'user_log' : user_log, 'user_id':user_id})

def InfoMainFunc(request):
    
    user_log = request.session.get('user')
    user_id = request.session.get('user_id')
#     userinfo = str(user_log) + "(" + str(user_id) + ")"
    print(type(str(user_id)), str(user_id))
    print(user_log) # 세션 값 = 사용자 이름
    
    
    travel_part = travelall
    tid = []
    for tr in travel_part:
        tid.append(tr)
    print(len(tid), tid[:10])
    tls = []
    ratels = []
    for i in tid:
#         print(i)
        rat = Treview.objects.filter(tourid = i)
#             print(len(rat))
        sum = 0
        k = 0
        try:
            for r in rat:
                sum += float(r.rating)
                k += 1
            rate = np.round(sum / k,4)
            count = k
            ratels.append(np.round(sum / k,4))
    
        except Exception as e:
#                 print(e)
            rate = sum
            count = k
            ratels.append(sum)
            
        tdic = {'tour':i.tourname, 'area': i.city + ' ' + i.town, 'genrename':i.genre.genrename, 'vote_average':rate, 'vote_count':count}
        tls.append(tdic)
    
    travells = np.array(ratels)
    sort_index = np.argsort(travells)
    trls = []
    for i in np.flip(sort_index):
        print(tls[i])
        trls.append(tls[i])
        
    tdf = pd.DataFrame(trls)
    print(tdf.head())
    
    

    if user_log == None:
        return render(request, 'searchmain.html', {'tour':trls})
    else:
        return render(request, 'searchmain.html', {'tour':trls, 'user_log' : user_log, 'user_id':user_id})

def SearchFunction(request):
    if request.method == 'POST':
        search = request.POST.get('search')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        try:
            user_log = request.session.get('user')
            user_id = request.session.get('user_id')
        except:
            user_log = ''
            user_id = ''
        
        print(user_log) # 세션 값 = 사용자 이름

        if start_date == '':
            start_date = None
            weather = ''
        if end_date == '':
            end_date = None
            weather = ''
            
        wlist = []
        clist = []
        # 날씨 출력    
        try:
            dlist = []
            for i in range((parse(end_date) - parse(start_date)).days + 1):
                d = (parse(start_date) + timedelta(days = i)).date().strftime("%y.%m.%d")
                dlist.append(d)
            print(dlist)
            
            weather = Weather(search)
            
            query = (weather['date'] >= start_date) & (weather['date'] <= end_date)
            
            for i in range(len(weather.loc[query]['weather'].values)):
                
                w = weather.loc[query]['weather'].values[i]
                c = "./static/image/unnamed.png"
                if (w >= 1 and w <= 3) or (w >= 33 and w <= 35):
                    w = '맑음'
                    c = "./static/image/sunny.png"
                elif (w >= 4 and w <= 5) or (w >= 36 and w <= 37):
                    w = '구름 조금'
                    c = "./static/image/sunny_cloudy.png"
                elif (w >= 6 and w <= 8) or (w == 38):
                    w = '흐림'
                    c = "./static/image/cloudy.png"
                elif (w == 11):
                    w = '안개'
                    c = "./static/image/fog.png"
                elif (w == 12 or w == 13):
                    w = '소나기'
                    c = "./static/image/shower.png"
                elif (w >= 14 and w <= 17) or (w == 39):
                    if (w == 15 or w == 16 or w == 41 or w == 42):
                        w = '천둥번개와 비'
                        c = "./static/image/thunder_rain.png"
                    else:
                        w = '한때 비'
                        c = "./static/image/sunny_rain.png"
                elif w == 18 or w <= 40:
                    if (w >= 19 and w <= 21) or (w == 32):
                        w = '강풍'
                        c = "./static/image/windy.png"
                    elif(w == 23 or w == 24 or w == 29 or w == 43 or w == 44):
                        w = '눈'
                        c = "./static/image/snow.png"
                    elif(w == 25):
                        w = '진눈깨비'
                        c = "./static/image/mixedsnow.png"
                    elif(w == 26):
                        w = '얼어붙은 비'
                        c = "./static/image/frozen_rain.png"
                    else:   
                        w = '비'
                        c = "./static/image/rain.png"
                elif w == 30:
                    w = '뜨거움 - 주의'
                    c = "./static/image/hot.png"
                elif w == 31:
                    w = '추움 - 주의'
                    c = "./static/image/cold.png"
                    
                print(w, ' ', c)

                wlist.append(w)
                clist.append(c)
            print(wlist)
            wls = []   
            for i in range(len(dlist)):
                wdic = {'date':dlist[i], 'weather':wlist[i], 'weather_icon':clist[i]}
                wls.append(wdic)
        except Exception as e: 
            print('err : ', e)
            print('===날짜가 없을경우===')
            print(start_date)
            print(end_date)
            wls = []

#         print(user_id)
                
        if search == '':
            travel_part = travelall
        else:
            print(search)
            travel_part = Travel.objects.filter(city__icontains = search)
            if len(travel_part) == 0:
                travel_part = Travel.objects.filter(town__icontains = search)
#         print(rating)
#         filepath = path+'/travel_recommend/travel/static/datafile/placerating.csv'
#         results = recommend_app.cal_knn.Cal_Knn(filepath, user_id)
        tid = []
        for tr in travel_part:
            tid.append(tr.tourid)
        rno = []
        rid = []
        rate = []
        trid = []
        for i in tid:
#             print(i)
            rat = Treview.objects.filter(tourid = i)
#             print(len(rat))
            for r in rat:
#                 print(i)
                rno.append(r.treviewno)
                rid.append(r.treviewid)
                trid.append(r.tourid.tourid)
                rate.append(r.rating)
        
#         for r in rating:
# #             print(r.tourid)
#             rno.append(r.treview_no)
#             rid.append(r.treview_id)
#             rate.append(r.rating)
        print(len(rno),len(rid),len(trid),len(rate))
        rdic = {'treview_no':rno,'treview_id':rid,'tourid':trid, 'rating':rate}
        rdf1 = pd.DataFrame(rdic)    
        rdf2 = pd.DataFrame(rdic)     
#         print(type(rdf))
        
        travel = travelall
        tls = []
        ratels = []
#         count = []
        for t in travel_part:            
            sum = 0
            k = 0
            try:
                for j in rdf1[rdf1['tourid']==t.tourid]['rating'].values:
#                     print(j, ' ', type(sum),  type(float(j)))
                    sum += float(j)
                    k += 1
#                     print(sum, ' ', k, ' ', i)
                rate = np.round(sum / k,4)
                count = k
                ratels.append(np.round(sum / k,4))
            except Exception as e:
#                 print(e)
                rate = sum
                count = k
                ratels.append(sum)
            
            tdic = {'tour':t.tourname, 'area': t.city + ' ' + t.town, 'genrename':t.genre.genrename, 'vote_average':rate, 'vote_count':count}
            tls.append(tdic)
        
        travells = np.array(ratels)
        sort_index = np.argsort(travells)
        trls = []
        for i in np.flip(sort_index):
            print(tls[i])
            trls.append(tls[i])
            
        tdf = pd.DataFrame(trls)
        print(tdf.head())
        
        #tour = ['여행지1', '여행지2', '여행지3', '여행지4', '여행지5']
        if user_log == None:
            context={'travel':search, 'start':start_date, 'end':end_date, 'wls':wls, 'tour':trls}
        else:
            context={'travel':search, 'start':start_date, 'end':end_date, 'wls':wls, 'tour':trls, 'user_log' : user_log, 'user_id':user_id}
        return render(request, 'searchmain.html', context)

def MyRecommendFunction(request):
    if request.method == 'POST':
        search = request.POST.get('search')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        user_log = request.session.get('user')
        user_id = request.session.get('user_id')
        if user_log == None:
            return redirect('loginform')
        
        print(user_log) # 세션 값 = 사용자 이름

        if start_date == '':
            start_date = None
            weather = ''
        if end_date == '':
            end_date = None
            weather = ''
            
        wlist = []
        clist = []
        # 날씨 출력    
        try:
            dlist = []
            for i in range((parse(end_date) - parse(start_date)).days + 1):
                d = (parse(start_date) + timedelta(days = i)).date().strftime("%y.%m.%d")
                dlist.append(d)
            print(dlist)
            
            weather = Weather(search)
            
            query = (weather['date'] >= start_date) & (weather['date'] <= end_date)
            
            for i in range(len(weather.loc[query]['weather'].values)):
                
                w = weather.loc[query]['weather'].values[i]
                c = "./static/image/unnamed.png"
                if (w >= 1 and w <= 3) or (w >= 33 and w <= 35):
                    w = '맑음'
                    c = "./static/image/sunny.png"
                elif (w >= 4 and w <= 5) or (w >= 36 and w <= 37):
                    w = '구름 조금'
                    c = "./static/image/sunny_cloudy.png"
                elif (w >= 6 and w <= 8) or (w == 38):
                    w = '흐림'
                    c = "./static/image/cloudy.png"
                elif (w == 11):
                    w = '안개'
                    c = "./static/image/fog.png"
                elif (w == 12 or w == 13):
                    w = '소나기'
                    c = "./static/image/shower.png"
                elif (w >= 14 and w <= 17) or (w == 39):
                    if (w == 15 or w == 16 or w == 41 or w == 42):
                        w = '천둥번개와 비'
                        c = "./static/image/thunder_rain.png"
                    else:
                        w = '한때 비'
                        c = "./static/image/sunny_rain.png"
                elif w == 18 or w <= 40:
                    if (w >= 19 and w <= 21) or (w == 32):
                        w = '강풍'
                        c = "./static/image/windy.png"
                    elif(w == 23 or w == 24 or w == 29 or w == 43 or w == 44):
                        w = '눈'
                        c = "./static/image/snow.png"
                    elif(w == 25):
                        w = '진눈깨비'
                        c = "./static/image/mixedsnow.png"
                    elif(w == 26):
                        w = '얼어붙은 비'
                        c = "./static/image/frozen_rain.png"
                    else:   
                        w = '비'
                        c = "./static/image/rain.png"
                elif w == 30:
                    w = '뜨거움 - 주의'
                    c = "./static/image/hot.png"
                elif w == 31:
                    w = '추움 - 주의'
                    c = "./static/image/cold.png"
                    
                print(w, ' ', c)

                wlist.append(w)
                clist.append(c)
            print(wlist)
            wls = []   
            for i in range(len(dlist)):
                wdic = {'date':dlist[i], 'weather':wlist[i], 'weather_icon':clist[i]}
                wls.append(wdic)
        except Exception as e: 
            print('err : ', e)
            print('===날짜가 없을경우===')
            print(start_date)
            print(end_date)
            wls = []

        ###
        ### 데이터 분석 받아오는곳
        ###
#         tuser = Tuser.objects.filter(user_name = user_log)
#         for t in tuser:
#             user_id = t.user_id
        print(user_id)
        
#         path = os.getcwd()
#         print(path)
        
        if search == '':
            travel_part = travelall
        else:
            print(search)
            travel_part = Travel.objects.filter(city__icontains = search)
            if len(travel_part) == 0:
                travel_part = Travel.objects.filter(town__icontains = search)
#         print(rating)
#         filepath = path+'/travel_recommend/travel/static/datafile/placerating.csv'
#         results = recommend_app.cal_knn.Cal_Knn(filepath, user_id)
        tid = []
        for tr in travel_part:
            tid.append(tr.tourid)
        rno = []
        rid = []
        rate = []
        trid = []
        for i in tid:
#             print(i)
            rat = Treview.objects.filter(tourid = i)
#             print(len(rat))
            for r in rat:
#                 print(i)
                rno.append(r.treview_no)
                rid.append(r.treview_id)
                trid.append(r.tourid.tourid)
                rate.append(r.rating)
        
#         for r in rating:
# #             print(r.tourid)
#             rno.append(r.treview_no)
#             rid.append(r.treview_id)
#             rate.append(r.rating)
        print(len(rno),len(rid),len(trid),len(rate))
        rdic = {'treview_no':rno,'treview_id':rid,'tourid':trid, 'rating':rate}
        rdf1 = pd.DataFrame(rdic)    
        rdf2 = pd.DataFrame(rdic)     
#         print(type(rdf))
        results1 = recommend_app.cal_knn.Cal_Knn(rdf1, user_id)
        results2 = recommend_app.cal_svd.Cal_Svd(rdf2, user_id)
#         print(results)
#         print(results['iid'].values)
        travel = travelall
        tlist1 = results1['iid'].values
        tlist2 = results2['iid'].values        
        tls = []
        
        flist1 = []
        for f in tlist1 :
            for t in travel:
                if t.tourid == f:
                    tour = t.tourname
                    area = t.city + ' ' + t.town
                    genrename = t.genre.genrename
                    
                    tdic = {'tour':tour,'area':area,'genrename':genrename}
#             filepath = path + '/travel_recommend/travel/static/datafile/국내여행지.xlsx'    
            #tour = Travel.objects.filter(placeId = f)
            flist1.append(tdic)
        print(flist1)
        
        flist2 = []
        for f in tlist2 :
            for t in travel:
                if t.tourid == f:
                    tour = t.tourname
                    area = t.city + ' ' + t.town
                    genrename = t.genre.genrename
                    
                    tdic = {'tour':tour,'area':area,'genrename':genrename}
#             filepath = path + '/travel_recommend/travel/static/datafile/국내여행지.xlsx'    
            #tour = Travel.objects.filter(placeId = f)
            flist2.append(tdic)
        print(flist2)
        
        #tour = ['여행지1', '여행지2', '여행지3', '여행지4', '여행지5']

        context={'travel':search, 'start':start_date, 'end':end_date, 'wls':wls, 'tour_knn':flist1, 'tour_svd':flist2, 'user_log' : user_log, 'user_id':user_id}

        return render(request, 'recommendmain.html', context)


def CosineFunction(request):
    user_log = request.session.get('user')
    user_id = request.session.get('user_id')
            
    tour = request.GET['tour']
    print(tour)
    
    tourinfo = Travel.objects.get(tourname = tour)
    
    
    rate = treviewall
    travel = travelall
    
    rls = []
    for r in rate:
        print(r)
        rls.append({'treview_no':r.treviewno,'treview_id':r.treviewid.user_id,'tourid':r.tourid.tourid, 'rating':r.rating})
    rating = pd.DataFrame(rls)
    print(rating.head())
    tls = []
    for t in travel:
        print(t)
        tls.append({'tourid':t.tourid, 'city':t.city, 'town':t.town, 'tourname':t.tourname, 'genre':t.genre.genrename})
    place = pd.DataFrame(tls)
    print(place.head())
    df = cosinePlace(rating, place, tour,'genre')
    print(len(df), df.iloc[0].tourname)
    datas = []
    for s in range(len(df)):
        dic = {'tour':df.iloc[s].tourname, 'area':df.iloc[s].area, 'genre':df.iloc[s].genre, 'weighted_vote':np.round(df.iloc[s].weighted_vote,3)}
        datas.append(dic)
    print(type(user_log), user_log, user_id)
    if user_log != None:
        context = {'tourinfo':tourinfo, 'tour':datas, 'user_log' : user_log, 'user_id':user_id}
    else: 
        context = {'tourinfo':tourinfo, 'tour':datas}
    return render(request, 'cossim.html',context)

def NearFunc(request):
    area = request.GET['area']
    way = request.GET['way']
    print(area, way)
    city = area.split()[0]
    if len(area.split()) == 3:
        town = area.split()[1] + " " + area.split()[2]
    else:
        town = area.split()[1]
    print(town)
    if way == 'food':
        travel_near = Travel.objects.filter(city = city,town = town, genre__lte = 2).order_by('-tscore')
    elif way == 'place':
        travel_near = Travel.objects.filter(city = city,town = town, genre__gt = 2).order_by('-tscore')
    datas = []
    for tn in travel_near:
        dic = {'tour':tn.tourname, 'area':area, 'genre':tn.genre.genrename, 'cnt':tn.count, 'score':tn.score}
        datas.append(dic)
    return HttpResponse(json.dumps(datas), content_type = "application/json")

def MyPageFunc(request):
    user_log = request.session.get('user')
#     user_log = "홍길동"
    user_id = request.session.get('user_id')
#     user_id = 1
    if user_log == None:
        return redirect('loginform')
    
    user = Tuser.objects.get(user_id = user_id)
                             
    ureview = Treview.objects.filter(treviewid = user_id)
    print(ureview)
    paginator = Paginator(ureview, 20)
    page = request.GET.get('page')
    
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)      # num_pages = 0
    print(data)
    ## 개별 페이지 표시용
    print(paginator.num_pages)
    if data.number > 5 and data.number < paginator.num_pages - 5:
        allpage = range(data.number - 4, data.number + 6)
    elif data.number <= 5:
        allpage = range(0,11)
    else:
        allpage = range(paginator.num_pages - 10, paginator.num_pages + 1)
#     allpage = range(paginator.num_pages + 1)
    print(list(allpage))    
#     return render(request, 'board.html', {'data':data, 'allpage':allpage})
    urls = []
    for ur in ureview:
        urdic = {'tourid':ur.tourid.tourid,'tourname':ur.tourid.tourname,'area':ur.tourid.city + " " + ur.tourid.town, 'rating':ur.rating}
        urls.append(urdic)
    
    context = {'data':data, 'allpage':allpage, 'user':user, 'user_log' : user_log, 'user_id':user_id} 
    return render(request, 'mypage.html', context)   

def MypartFunction(request):
    startword = request.GET['startword']
    user_log = request.session.get('user')
    user_id = request.session.get('user_id')
    
    user = Tuser.objects.get(user_id = user_id)
    ureview2 = Treview.objects.filter(treviewid = user_id)
    print(ureview2)
    ureview=[]
    for i in ureview2:
#         print(j2hcj(h2j(i.tourid.tourname))[0], startword)
        if j2hcj(h2j(i.tourid.tourname))[0] == startword:
            print(j2hcj(h2j(i.tourid.tourname))[0])
            ureview.append(i)
        if startword == "*":    
            if j2hcj(h2j(i.tourid.tourname))[0] not in ['ㄱ','ㄴ','ㄷ','ㄹ','ㅁ','ㅂ','ㅅ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ','ㄲ','ㄸ','ㅆ','ㅉ','ㅃ']:
                print(j2hcj(h2j(i.tourid.tourname)))
                ureview.append(i)
    print(ureview)     
    
#     print(ureview)
    paginator = Paginator(ureview, 20)
    page = request.GET.get('page')
    
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)      # num_pages = 0
    print(data)
    ## 개별 페이지 표시용
    allpage = range(paginator.num_pages + 1)
        
#     return render(request, 'board.html', {'data':data, 'allpage':allpage})
    urls = []
    for ur in ureview:
        urdic = {'tourid':ur.tourid.tourid,'tourname':ur.tourid.tourname,'area':ur.tourid.city + " " + ur.tourid.town, 'rating':ur.rating}
        urls.append(urdic)
    
    context = {'data':data, 'allpage':allpage, 'w':startword, 'user':user, 'user_log' : user_log, 'user_id':user_id} 
    return render(request, 'mypartreview.html', context)

def UpdaterateFunction(request):
    rate = request.GET['rate'] 
    rid = request.GET['rid']  
    user_id = request.session.get('user_id')
    print(rate, rid)
    sql = "update treview set rating = '{}' where tourid = {} and treviewid = {}".format(rate, rid, user_id)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit() 
    
    datas = rate
    return HttpResponse(json.dumps(datas), content_type = "application/json")

def DeleteFunction(request):
    rid = request.GET['rid']  
    user_id = request.session.get('user_id')
    sql = "delete from treview where tourid = {} and treviewid = {}".format(rid, user_id)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    datas = rid
    return HttpResponse(json.dumps(datas), content_type = "application/json")

def MyInfoFunction(request):
    user_log = request.session.get('user')
    user_id = request.session.get('user_id')
    
    user = Tuser.objects.get(user_id = user_id)
                             
    ureview = Treview.objects.filter(treviewid = user_id)
    print(ureview)
    paginator = Paginator(ureview, 20)
    page = request.GET.get('page')
    
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)      # num_pages = 0
    print(data)
    ## 개별 페이지 표시용
    allpage = range(paginator.num_pages + 1)
        
#     return render(request, 'board.html', {'data':data, 'allpage':allpage})
    urls = []
    for ur in ureview:
        urdic = {'tourid':ur.tourid.tourid,'tourname':ur.tourid.tourname,'area':ur.tourid.city + " " + ur.tourid.town, 'rating':ur.rating}
        urls.append(urdic)
    
    context = {'data':data, 'allpage':allpage, 'user':user, 'user_log' : user_log, 'user_id':user_id} 
    return render(request, 'myinfo.html', context)

def MyQnaFunction(request):
    user_log = request.session.get('user')
    user_id = request.session.get('user_id')
    
    user = Tuser.objects.get(user_id = user_id)
                             
    ureview = Treview.objects.filter(treviewid = user_id)
    print(ureview)
    paginator = Paginator(ureview, 20)
    page = request.GET.get('page')
    
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)      # num_pages = 0
    print(data)
    ## 개별 페이지 표시용
    allpage = range(paginator.num_pages + 1)
        
#     return render(request, 'board.html', {'data':data, 'allpage':allpage})
    urls = []
    for ur in ureview:
        urdic = {'tourid':ur.tourid.tourid,'tourname':ur.tourid.tourname,'area':ur.tourid.city + " " + ur.tourid.town, 'rating':ur.rating}
        urls.append(urdic)
    
    context = {'data':data, 'allpage':allpage, 'user':user, 'user_log' : user_log, 'user_id':user_id} 
    return render(request, 'myqna.html', context)

def PwdCheckFunction(request):
    pwd = request.GET['pwd']
    print(pwd)
    user_id = request.session.get('user_id')
    user = Tuser.objects.get(user_id = user_id)
    print(user)
    if user.user_pwd == pwd:
        datas = {'user_id':user.user_id, 'username':user.user_name, 'user_pwd':user.user_pwd}
    
    return HttpResponse(json.dumps(datas), content_type = "application/json")
            
def UpInfoFunction(request):
    pwd = request.GET['pwd']
    newpwd = request.GET['newpwd']
    renewpwd = request.GET['renewpwd']
    name = request.GET['name']
    user_id = request.session.get('user_id')
    print(pwd, name, user_id)
    user = Tuser.objects.get(user_id = user_id)
    print(user)
    if user.user_pwd == pwd:
        if newpwd == renewpwd:
            datas = "성공"
            sql = "update tuser set user_pwd = '{}', user_name = '{}' where user_id = '{}'".format(newpwd, name, user_id)
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
        else:
            datas = "불일치"
    else:
        datas = "비밀번호에러"
 
    return HttpResponse(json.dumps(datas), content_type = "application/json")

def SearchnameFunction(request):
    rname = request.GET['rname']
    print(rname)
    
    tarea = Travel.objects.filter(tourname = rname)
    if len(tarea) == 0:
        tarea = Travel.objects.filter(tourname__icontains = rname)
        key = "noption"
        print(key)
        datas = []
        for n in tarea:
            irum = n.tourname
            datas.append({'irum':irum, 'keys':key})
        if len(tarea) == 0:
            datas = "실패"
        
    else:
        key = "aoption"
        print(key)
        datas = []
        for a in tarea:
            ra = a.city + ' ' + a.town
            datas.append({'rarea':ra, 'keys':key})
        
    return HttpResponse(json.dumps(datas), content_type = "application/json")    

def InsertReviewFunction(request):
    rname = request.GET['rname']
    rarea = request.GET['rarea']
    rrate = request.GET['rrate']
    user_id = request.session.get('user_id')
    city = rarea.split()[0]
    if len(rarea.split()) == 3:
        town = rarea.split()[1] + " " + rarea.split()[2]
    else:
        town = rarea.split()[1]
    travel = Travel.objects.get(tourname = rname, city = city, town = town)
    tid = travel.tourid
    ureview = Treview.objects.filter(treviewid = user_id, tourid = tid)
    if len(ureview) == 0:
        obj = Treview.objects.aggregate(treviewno=Max('treviewno'))
        no = obj['treviewno'] + 1
        sql = "insert into treview values({},'{}',{},'{}')".format(no, user_id, tid, rrate)
        print("in")
    else:
        sql = "update treview set rating = '{}' where tourid = {} and treviewid = '{}'".format(rrate, tid, user_id)
        print("up")
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    datas = "성공"
    return HttpResponse(json.dumps(datas), content_type = "application/json")
    
    
###### 수정 20201224
def DetailFunction(request):

    travel_id = request.GET.get('travel_id')
    travel = Travel.objects.get(tourid = travel_id)
    
    travels =  Travel.objects.filter(city = travel.city)|Travel.objects.filter(town = travel.town)
    # select * from travel where city = ? or town =? limit 5;
    travels = travels[:5]
    
    return render(request, 'detail2.html', {'travel':travel, 'travels':travels})


def SignupFunction(request):
    return render(request, 'signup.html')

def TravelCheckFunction(request):
    rname = request.GET['travel']
    print(rname)
    tarea = Travel.objects.filter(tourname = rname)
    if len(tarea) == 0:
        tarea = Travel.objects.filter(tourname__icontains = rname)
        key = "noption"
        print(key)
        datas = []
        for n in tarea:
            irum = n.tourname
            datas.append({'irum':irum, 'keys':key})
        if len(tarea) == 0:
            datas = "실패"
        print(datas)
    elif len(tarea) == 1:
        for a in tarea:
            ra = a.tourid
        datas = [{'rarea':ra, 'keys':"단일데이터"}]
        
    else:
        key = "aoption"
        print(key)
        datas = []
        for a in tarea:
            ra = a.city + ' ' + a.town
            datas.append({'rarea':ra, 'keys':key})

    return HttpResponse(json.dumps(datas), content_type = "application/json")

def SignupFunction2(request):
    if request.method == 'POST':
        
        name = request.POST.get('name')
        ID = request.POST.get('ID')
        password = request.POST.get('password')
        
        travel1 = request.POST.get('travel1')
        area1 = request.POST.get('area1')
        rating1 = request.POST.get('rating1')
        travel2 = request.POST.get('travel2')
        area2 = request.POST.get('area2')
        rating2 = request.POST.get('rating2')        
        travel3 = request.POST.get('travel3')
        area3 = request.POST.get('area3')
        rating3 = request.POST.get('rating3')        
        print(area1, area2, area3)
        # csv에 신규정보를 

        #유저등록
        if Tuser.objects.filter(user_id = ID).exists() == False:
            Tuser(
                user_id = ID,
                user_name = name,
                user_pwd = password
            ).save()

        else:
            ss = """
            <script> 
                alert('이미 존재하는 아이디입니다.');
                history.back();
            </script>
            """
            return render(request, 'signup.html', {'error' : ss})
             
        #리뷰등록
        try:
            
            InsertReview(ID, area1, rating1)
            InsertReview(ID, area2, rating2)
            InsertReview(ID, area3, rating3)            
            
        except:
            ss = '''
            <script> 
                alert('존재하는 여행지를 입력해주세요.');
                history.back();
            </script>
            '''
            return render(request, 'signup.html', {'error' : ss})
        

    return redirect('home')

def InsertReview(ID, area, rating):
    obj = Treview.objects.aggregate(treviewno=Max('treviewno'))
    no = obj['treviewno'] + 1
    if no is None:
        no = 1
        
#     city = area.split()[0]
#     if len(area.split()) == 3:
#         town = area.split()[1] + " " + area.split()[2]
#     else:
#         town = area.split()[1]
#     travel = Travel.objects.get(tourname = travel, city = city, town = town)
#     tid = travel.tourid
    tid = area
    print(area)
    
#     try :
#         obj = Travel.objects.get(city = travel)
#     except:
#         obj = Travel.objects.get(town = travel)
#     travel = obj.tourid    
    
    sql = "insert into treview values({}, '{}', {}, '{}')".format(no, ID, tid, rating)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
