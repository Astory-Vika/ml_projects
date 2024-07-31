from django.urls import path
from django.contrib import admin
from . import views
from django.views.generic import TemplateView
from .views import subject_detail

urlpatterns = [
    # views.home => views.py - def home(request):
    path('', views.home, name='home'),

    #from student
#    path('admin', admin.site.urls),
    path('profile', views.profile, name='profile'),
    path('schedule/', views.schedule, name='schedule'),
    path('subject-detail/<int:subject_id>/', subject_detail, name='subject_detail'),
    path('submit_homework/<int:task_id>/', views.submit_homework, name='submit_homework'),
    path('homework/<int:homework_id>/test/', views.test_view, name='test_view'),
    path('homework/<int:homework_id>/test/result/', views.test_result, name='test_result'),
    path('submissions/<int:task_id>/', views.view_submissions, name='view_submissions'),
    path('grade/<int:submission_id>/', views.grade_homework, name='grade_homework'),
    path('submissions/chart/<int:task_id>/', views.view_submissions, name='view_submissions'),

    path('notes', views.notes, name='notes'),
    path('homework', views.homework, name='homework'),
    path('conversion', views.conversion, name='conversion'),
    path('todo', views.todo, name='todo'),
    path('wiki', views.wiki, name='wiki'),
    path('youtube', views.youtube, name='youtube'),
    path('dictionary', views.dictionary, name='dictionary'),
    path('books', views.books, name='books'),

    path('notes_detail/<int:pk>',
         views.NotesDetailView.as_view(), name="notes_detail"),
    path('delete_note/<int:pk>', views.delete_note, name='delete-note'),
    path('delete_todo/<int:pk>', views.delete_todo, name='delete-todo'),
    path('update_todo/<int:pk>', views.update_todo, name='update-todo'),

]
