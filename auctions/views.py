from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from .models import Auction, Bid
from .forms import AuctionCreateForm, BidForm
from users.views import session_login_required
from users.models import User
import secrets


def auction_list(request):
    user_id = request.session.get('user_id')
    all_auctions = Auction.objects.filter(is_closed=False).order_by('-created_at')

    user_auctions = None
    other_auctions = all_auctions

    if user_id:
        try:
            user = User.objects.get(id=user_id)
            user_auctions = all_auctions.filter(seller=user)
            other_auctions = all_auctions.exclude(seller=user)
        except User.DoesNotExist:
            # Handle case where user_id in session is invalid
            pass

    context = {
        'user_auctions': user_auctions,
        'other_auctions': other_auctions,
    }
    return render(request, 'auctions/list.html', context)


@session_login_required
def auction_create(request):
    if request.method == 'POST':
        form = AuctionCreateForm(request.POST, request.FILES)
        if form.is_valid():
            user = User.objects.get(id=request.session.get('user_id'))
            auction = form.save(seller=user)
            return redirect('auctions:detail', auction_id=auction.id)
    else:
        form = AuctionCreateForm()
    return render(request, 'auctions/create.html', {'form': form})


def auction_detail(request, auction_id):
    auction = get_object_or_404(Auction.objects.prefetch_related('bid_set__bidder'), pk=auction_id)
    bid_form = BidForm()
    bids = auction.bid_set.all().order_by('-created_at')
    user_id = request.session.get('user_id')
    is_seller = str(user_id) == str(getattr(auction.seller, 'id', ''))
    return render(request, 'auctions/detail.html', {
        'auction': auction,
        'bids': bids,
        'bid_form': bid_form,
        'is_seller': is_seller,
    })


@session_login_required
def place_bid(request, auction_id):
    auction = get_object_or_404(Auction, pk=auction_id)
    if auction.is_expired():
        return JsonResponse({'success': False, 'error': 'Auction expired'}, status=400)
    form = BidForm(request.POST)
    if form.is_valid():
        amount = form.cleaned_data['amount']
        # compute the minimum valid price at this instant
        min_valid = auction.current_price if auction.current_price is not None else auction.starting_price
        if amount <= min_valid:
            return JsonResponse({'success': False, 'error': 'Bid must be higher than current price'}, status=400)

        bidder = User.objects.get(id=request.session.get('user_id'))

        # attempt an atomic update: set current_price to amount only if it still equals min_valid
        updated = Auction.objects.filter(pk=auction.pk, current_price=min_valid, is_closed=False).update(current_price=amount)
        if not updated:
            # someone else updated the auction price concurrently
            return JsonResponse({'success': False, 'error': 'Another bid was placed just now. Please refresh and try again.'}, status=409)

        # now persist the bid record
        bid = Bid(auction=auction, bidder=bidder, amount=amount, created_at=timezone.now())
        bid.save()
        return JsonResponse({
            'success': True,
            'bid': {
                'bidder_name': bidder.fullName,
                'amount': amount,
                'created_at': timezone.localtime(bid.created_at).strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@session_login_required
def choose_bidder(request, auction_id):
    auction = get_object_or_404(Auction, pk=auction_id)
    user_id = request.session.get('user_id')
    if str(user_id) != str(getattr(auction.seller, 'id', '')):
        return JsonResponse({'success': False, 'error': 'Not allowed'}, status=403)
    if request.method == 'POST':
        chosen_bid_id = request.POST.get('bid_id')
        if chosen_bid_id:
            bid = get_object_or_404(Bid, pk=chosen_bid_id)
            auction.chosen_bid = bid
            auction.is_closed = True
            auction.save()
            return JsonResponse({'success': True})
        # accept highest bid
        highest = auction.highest_bid()
        if highest:
            auction.chosen_bid = highest
            auction.is_closed = True
            auction.save()
            return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)
