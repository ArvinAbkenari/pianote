from django.http import JsonResponse
from django.shortcuts import render
from users.forms import UserSignupForm, UserSigninForm
from .models import Note


# Create your views here.
def notes_view(request):
    signup_form = UserSignupForm()
    notes = Note.objects.filter(deleteFlag=False)
    return render(request, "notes/sheets.html",{"form": signup_form , "notes": notes})


def ajax_search(request):
    query = request.GET.get("q", "")
    results = []

    if query:
        from django.db.models import Q
        notes = Note.objects.filter(
            Q(name__icontains=query)
        )
        results = [{"name": note.name} for note in notes]

    return JsonResponse({"results": results})




def note_detail_view(request, note_id):
    signup_form = UserSignupForm()
    try:
        note = Note.objects.get(id=note_id, deleteFlag=False)
    except Note.DoesNotExist:
        return render(request, "404.html", status=404)

    return render(request, "note_sheet/sheet-detail.html", {"note": note,"form": signup_form})