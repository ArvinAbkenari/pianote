from django.db import models
from django.utils import timezone
import secrets


def make_objectid_hex():
    # return a 24-char hex string similar to Mongo ObjectId
    return secrets.token_hex(12)


class Auction(models.Model):
    id = models.CharField(max_length=24, primary_key=True, editable=False, default=make_objectid_hex)
    # explicitly reference the custom users.User model by string to avoid mismatches
    seller = models.ForeignKey('users.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='auctions/images/', null=True, blank=True)
    starting_price = models.FloatField()
    current_price = models.FloatField()
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    is_closed = models.BooleanField(default=False)
    chosen_bid = models.ForeignKey('Bid', on_delete=models.SET_NULL, null=True, blank=True, related_name='as_chosen_bid')

    def highest_bid(self):
        return self.bid_set.order_by('-amount').first()

    def is_expired(self):
        return timezone.now() >= self.expires_at or self.is_closed

    def __str__(self):
        return self.title


class Bid(models.Model):
    id = models.CharField(max_length=24, primary_key=True, editable=False, default=make_objectid_hex)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    bidder = models.ForeignKey('users.User', on_delete=models.CASCADE)
    amount = models.FloatField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.bidder} - {self.amount}"
