from django.urls import path
from . import views

urlpatterns = [
    path(
        'delete/<str:exercise_id>/',
        views.exercise_delete,
        name='exercise_delete'
    ),
    # You can add more exercise-specific routes here
]
