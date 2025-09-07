from django.http import JsonResponse
from django.shortcuts import render, redirect
from users.forms import UserSignupForm
from .models import Note
from django.utils import timezone
from PyPDF2 import PdfReader
from django.core.paginator import Paginator
from pymongo import MongoClient
from users.views import session_login_required
from django.db.models import Q


# Create your views here.
def notes_view(request):
    signup_form = UserSignupForm()
    notes = Note.objects.filter(deleteFlag=False)
    for note in notes:
        if note.notesheet and note.notesheet.path:
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(note.notesheet.path)
                page = doc.load_page(0)
                pix = page.get_pixmap()
                img_bytes = pix.tobytes("png")
                import base64
                note.preview = base64.b64encode(img_bytes).decode('utf-8')
            except Exception:
                note.preview = None
        else:
            note.preview = None
    return render(
        request, "notes/sheets.html", {"form": signup_form, "notes": notes}
    )


def ajax_search(request):
    query = request.GET.get("q", "")
    results = []

    if query:
        notes = Note.objects.filter(
            Q(name__icontains=query)
        )
        results = [
            {"name": note.name, "composer": note.composer, "id": note.id}
            for note in notes
        ]

    return JsonResponse({"results": results})


def note_detail_view(request, note_id):
    signup_form = UserSignupForm()
    try:
        note = Note.objects.get(id=note_id, deleteFlag=False)
        # Only increment views if this is a GET request
        # and not a redirect after POST
        if request.method == "GET" and not request.GET.get("from_action"):
            note.views += 1
            note.save(update_fields=["views"])
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

    if request.method == "POST" and request.session.get("user_id"):
        form_type = request.POST.get("form_type")
        user_id = request.session["user_id"]
        if form_type == "comment":
            comment_text = request.POST.get("comment_text", "").strip()
            if comment_text:
                note.add_comment(user_id, comment_text, timezone.now())
        elif form_type == "voting":
            vote_shape = request.POST.get("vote")
            if vote_shape:
                note.add_like(user_id, vote_shape, timezone.now())
        # Redirect with a query param to prevent view increment
        return redirect(f"{request.path}?from_action=1")

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

    my_vote = None
    if request.session.get("user_id"):
        user_id = str(request.session["user_id"])
        for v in note.voters:
            if str(v.get("userID")) == user_id and not v.get("deleteFlag", False):
                my_vote = v.get("shape")
                break
    return render(
        request,
        "note_sheet/sheet-detail.html",
        {
            "note": note,
            "form": signup_form,
            "comments": comments,
            "pdf_page_count": pdf_page_count,
            "my_vote": my_vote,
        }
    )


@session_login_required
def notes_list(request):
    # Extract MongoDB URI and database name from settings
    mongo_uri = "mongodb://localhost:27017/"
    db_name = "pianote"
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db['notes_note']

    selected_genres = request.GET.getlist('genre')
    selected_levels = request.GET.getlist('level')

    try:
        level_ints = [int(level) for level in selected_levels]
    except ValueError:
        level_ints = []
    query = {}
    if selected_genres:
        query['genre'] = {'$in': selected_genres}
    if level_ints:
        query['level'] = {'$in': level_ints}

    results = list(collection.find(query))
    level_mapping = {
        1: "مبتدی",
        2: "متوسط",
        3: "پیشرفته",
    }
    for note in results:
        note['level_value'] = level_mapping.get(note.get('level'), "unknown")

    # Pagination
    paginator = Paginator(results, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'notes/sheets.html', {
        'notes': page_obj.object_list,
        'page_obj': page_obj,
        'selected_genres': selected_genres,
        'selected_levels': selected_levels,
    })
