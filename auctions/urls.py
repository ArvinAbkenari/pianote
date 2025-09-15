from django.urls import path
from . import views

app_name = 'auctions'

urlpatterns = [
    path('', views.auction_list, name='list'),
    path('create/', views.auction_create, name='create'),
    path('<str:auction_id>/', views.auction_detail, name='detail'),
    path('<str:auction_id>/bid/', views.place_bid, name='place_bid'),
    path('<str:auction_id>/choose/', views.choose_bidder, name='choose_bidder'),
]
