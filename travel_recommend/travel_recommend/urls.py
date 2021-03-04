"""travel_recommend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from travel import views
import recommend_app
from django.urls.conf import include


urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('', views.IndexFunc, name='home'),
    path('loginform', views.LoginFunction, name = 'loginform'),
    path('login', views.LoginFunc),
    path('logout', views.LogoutFunc),
    path('main', views.UserMainFunc, name='main'),
    path('info', views.InfoMainFunc), 
    path('search', views.SearchFunction),
    path('myrecommend', views.MyRecommendFunction),
    path('cossim', views.CosineFunction),
    path('detail', views.DetailFunction),
    path('signup', views.SignupFunction),
    path('travelcheck', views.TravelCheckFunction),
    path('signup2', views.SignupFunction2),
    path('cal_svd',  include('recommend_app.urls')),
    path('cal_knn', include('recommend_app.urls')),
    path('nearajax', views.NearFunc),
    path('mypage', views.MyPageFunc),
    path('mypartreview', views.MypartFunction),
    path('updaterating', views.UpdaterateFunction),
    path('deletereview', views.DeleteFunction),
    path('myinfo',views.MyInfoFunction),
    path('myqna', views.MyQnaFunction),
    path('pwdcheck', views.PwdCheckFunction), 
    path('updateinfo', views.UpInfoFunction),
    path('searchname', views.SearchnameFunction),
    path('insertreview', views.InsertReviewFunction),
    #path('startajax', views.CossimFunc),

]
