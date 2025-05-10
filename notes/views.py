from django.http import JsonResponse
from django.shortcuts import render, redirect
from users.forms import UserSignupForm
from .models import Note
from django.utils import timezone
from PyPDF2 import PdfReader


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

    # Extract PDF page count
    pdf_page_count = None
    if note.notesheet and note.notesheet.path:
        try:
            reader = PdfReader(note.notesheet.path)
            pdf_page_count = len(reader.pages)
        except Exception:
            pdf_page_count = None

    # Handle comment submission
    if request.method == "POST" and request.session.get("user_id"):
        comment_text = request.POST.get("comment_text", "").strip()
        if comment_text:
            user_id = request.session["user_id"]
            note.add_comment(user_id, comment_text, timezone.now())
        # After posting, redirect to avoid resubmission
        return redirect(request.path)

    # Attach user fullName to each comment
    from users.models import User
    comments = []
    for comment in note.comments:
        user_id = comment.get("userID")
        try:
            user = User.objects.get(id=user_id)
            comment["fullName"] = user.fullName
        except User.DoesNotExist:
            comment["fullName"] = "کاربر حذف شده"
        comments.append(comment)

    return render(request, "note_sheet/sheet-detail.html", {"note": note, "form": signup_form, "comments": comments, "pdf_page_count": pdf_page_count})