from django.contrib import admin
from .models import Auction, Bid


@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'starting_price', 'current_price', 'created_at', 'expires_at', 'is_closed')
    search_fields = ('title', 'description', 'seller__fullName')
    list_filter = ('is_closed', 'created_at', 'expires_at')


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('auction', 'bidder', 'amount', 'created_at')
    search_fields = ('auction__title', 'bidder__fullName')
    list_filter = ('created_at',)
