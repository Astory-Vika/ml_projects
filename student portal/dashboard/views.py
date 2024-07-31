from django.utils import timezone
from django.forms import ModelForm
from django.http import HttpResponse
from django.shortcuts import get_list_or_404, render, redirect
from django.shortcuts import get_object_or_404
from .forms import *
from plotly.offline import plot
import plotly.express as px
import pandas as pd
import re
import requests
from youtubesearchpython import VideosSearch
import wikipedia
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views import generic
from .models import Answer, Notes, Staffs, Task, TeachingAssignments, TestQuestion, Todo, StudentGroupLinks, Schedule, Subjects, Homework, StudentGroups, User
from .utils import generate_questions
from .utils import text_summary
from .utils import check_similarity
import numpy as np



def logoutUser(request):
    logout(request)
    #messages.info(request,"Ви завершили роботу як користувач!")
    return redirect('login')

@login_required
def home(request):

    username = request.user.username

    # Спроба знайти співробітника і його роль
    staff = Staffs.objects.filter(user=request.user).first()
    role = staff.role if staff else 'guest'  # Присвоєння ролі "guest", якщо співробітник не знайдений

    subjects_details = []

    if role == 'student':
        # Пошук групи, до якої призначено студента
        student_group_link = StudentGroupLinks.objects.filter(user=request.user).first()
        if student_group_link:
            # Отримання призначень для групи студента
            assignments = TeachingAssignments.objects.filter(group=student_group_link.group)
            subjects_details = [{
                'subject_id': assignment.subject.id,
                'subject_title': assignment.subject.title,
                'teacher_last_name': assignment.teacher.last_name,
                'teacher_first_name': assignment.teacher.first_name
            } for assignment in assignments]
        else:
            error = 'You are not assigned to any group'
    elif role == 'teacher':
        # Отримання призначень для викладача
        assignments = TeachingAssignments.objects.filter(teacher=request.user)
        subjects_details = [{
            'subject_id': assignment.subject.id,
            'subject_title': assignment.subject.title,
            'group_title': assignment.group.title
        } for assignment in assignments]

    context = {
        'title': f'Головна сторінка сайту - Користувач: {username}, Роль: {role}',
        'role': role,  # Важливо передати роль у контекст
        'subjects_details': subjects_details,
    }

    return render(request, 'dashboard/home.html', context)


def register(request):
    if request.method == "POST":
        u_form = UserRegisterForm(request.POST)

        if u_form.is_valid():
            u_form.save()

            username = u_form.cleaned_data.get('username')
            messages.success(request, f'Акаунт створено для {username}!')
            return redirect('login')
        else:
            messages.error(request, ('Будь ласка, виправте помилки.'))

    else:
        u_form = UserRegisterForm()
    return render(request, 'dashboard/register.html', {'u_form': u_form})



@login_required
def schedule(request):
    user = request.user

    try:
        staff = Staffs.objects.get(user=user)
        role = staff.role
    except Staffs.DoesNotExist:
        return redirect('home')  # Redirect home if no staff info found

    context = {
        'user': user,
        'role': role,
    }

    if role == 'student':
        try:
            student_group_link = StudentGroupLinks.objects.get(user=user)
            assignments = TeachingAssignments.objects.filter(group=student_group_link.group)
            schedules = Schedule.objects.filter(teaching_assignments__in=assignments).order_by('day_of_week', 'class_num')
            context['schedules'] = schedules
            return render(request, 'dashboard/schedule.html', context)
        except StudentGroupLinks.DoesNotExist:
            context['error'] = 'Групи не призначено'
            return render(request, 'dashboard/error.html', context)

    elif role == 'teacher':
        try:
            schedules = Schedule.objects.filter(teaching_assignments__teacher=user).order_by('day_of_week', 'class_num')
            context['schedules'] = schedules
            return render(request, 'dashboard/schedule.html', context)
        except:
            context['error'] = 'Навчальних завдань не знайдено.'
            return render(request, 'dashboard/error.html', context)

    
    
    
@login_required
def subject_detail(request, subject_id):
    staff = Staffs.objects.filter(user=request.user).first()
    role = staff.role if staff else 'guest'  # Присвоєння ролі "guest", якщо співробітник не знайдений
    
    teaching_assignments = get_list_or_404(TeachingAssignments, subject_id=subject_id)
    tasks = Task.objects.filter(subject_id=subject_id)
    context = {
        'teaching_assignments': teaching_assignments,
        'role': role,  # Передаємо роль у контекст
        'tasks': tasks
    }

    if role == 'student':
        user_homeworks = Homework.objects.filter(user=request.user, task__subject_id=subject_id)

        # Завдання, які були подані та завершені
        completed_homeworks = user_homeworks.filter(is_submitted=True, is_finished=True)
        completed_tasks_ids = completed_homeworks.values_list('task_id', flat=True)

        # Завдання, які ще не виконані
        unfinished_tasks = tasks.exclude(id__in=completed_tasks_ids)
        
        context.update({
            'tasks': unfinished_tasks,  # Призначені, але ще не виконані завдання
            'homeworks': completed_homeworks,  # Виконані завдання
        })
    
    elif role == 'teacher':
        # Для викладачів відображаємо всі завдання з можливістю перегляду деталей по кожному
        for task in tasks:
            # Отримуємо список студентів, які виконали та не виконали завдання
            submissions = Homework.objects.filter(task=task)
            completed = submissions.filter(is_submitted=True)
            not_completed = submissions.filter(is_submitted=False)

            task.completed_submissions = completed
            task.not_completed_submissions = not_completed
        
        context.update({
            'tasks': tasks,  # Відображаємо всі завдання
        })

    return render(request, 'dashboard/subject_detail.html', context)

@login_required
def submit_homework(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        form = HomeworkForm(request.POST)
        if form.is_valid():
            homework = form.save(commit=False)
            homework.user = request.user
            homework.task = task
            homework.is_submitted = True
            homework.submission_date = timezone.now()  # Correct usage of timezone.now()
            homework.save()
            return redirect('home')  # Redirect to an appropriate view after submission
    else:
        form = HomeworkForm()
    return render(request, 'dashboard/submit_homework.html', {'form': form, 'task': task})


@login_required
def grade_homework(request, submission_id):
    submission = get_object_or_404(Homework, id=submission_id)
    if request.method == 'POST':
        form = GradeForm(request.POST, instance=submission)
        if form.is_valid():
            form.save()
            return redirect('view_submissions', task_id=submission.task.id)
    else:
        form = GradeForm(instance=submission)

    context = {
        'form': form,
        'submission': submission
    }
    return render(request, 'dashboard/grade_homework.html', context)




@login_required
def view_submissions(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    submissions = Homework.objects.filter(task=task).select_related('user')
    
    if request.method == 'POST':
        homework_id = request.POST.get('homework_id')
        homework = get_object_or_404(Homework, id=homework_id)
        
        # Виклик функції узагальнення тексту
        homework.summary = text_summary(homework.description)
        homework.save()
        messages.success(request, 'Аналіз завдання виконано успішно!')
        
    # Перевірка відповідності тематиці завдання
    for submission in submissions:
        submission.is_relevant = check_similarity(task.title, submission.description)
        
    # Prepare DataFrame for Plotly
    grades = [submission.grade for submission in submissions if submission.grade is not None]
    df = pd.DataFrame(grades, columns=['Grades'])

    # Aggregate data to count occurrences of each grade
    grade_counts = df['Grades'].value_counts().reset_index()
    grade_counts.columns = ['Grade', 'Count']

    # Generate the Plotly figure
    fig = px.bar(grade_counts, x='Grade', y='Count', title='Успішність студентів по завданню ' + task.title,
                 labels={'Grade': 'Оцінки', 'Count': 'Кількість студентів'})
    fig.update_xaxes(type='category')  # Ensures the x-axis is treated as categories
    fig.update_layout(
        xaxis_title="Оцінки",
        yaxis_title="Кількість студентів",
        xaxis={'categoryorder': 'total descending'}  # Sorts the bars by count
    )
    chart = fig.to_html(full_html=False, include_plotlyjs='cdn')

    context = {
        'task': task,
        'submissions': submissions,
        'chart': chart,
    }
    return render(request, 'dashboard/view_submissions.html', context)



def generate_questions_and_store(homework, num_questions=5):
    #questions_data = generate_questions(homework.description, num_questions)
    questions_data = generate_questions(homework.title, num_questions)
    for q in questions_data:
        print(q)
        question = TestQuestion.objects.create(homework=homework, question_text=q['question_text'])
        question.save()
        for a in q['answers']:
            print(a)
            if a['is_correct']:
                fb = 'Правильна відповідь'
            else:
                fb = 'Неправильна відповідь. Спробуйте почитати: [[' + q['book'] + ']]'
            ans = Answer.objects.create(question=question, answer_text=a['text'], is_correct=a['is_correct'], feedback=fb)
            ans.save()

@login_required
def test_view(request, homework_id):
    homework = get_object_or_404(Homework, pk=homework_id)
    questions = homework.questions.all()  # Fetching all questions related to the homework

    messages.info(request, "Робота з тестом")

    if request.method == 'POST':
        messages.info(request, "Отримуємо результати тесту")
        return redirect('test_result', homework_id=homework_id)
    if not homework.questions.exists():
        messages.info(request, "Генеруємо тест!!!")

        #messages.info(request, 'Це повідомлення буде очищено')
        #storage = messages.get_messages(request)
        #storage.used = True  # Очистити повідомлення

        generate_questions_and_store(homework)
    return render(request, 'dashboard/test_view.html', {
        'homework': homework,
        'questions': questions  # Passing questions explicitly to the template
    })

@login_required
def test_result(request, homework_id):
    homework = get_object_or_404(Homework, pk=homework_id)
    feedback = []
    if request.method == 'POST':
        for question in homework.questions.all():
            user_answer = request.POST.get(f'answer_{question.id}')
            print(user_answer)
            correct_answer = question.answers.filter(is_correct=True).first()
            u_answer = question.answers.filter(id=user_answer).first()
            if correct_answer:
                if str(correct_answer.id) == user_answer:
                               # for question_id, question_text, answer_status, feedback_text in feedback
                    feedback.append((question.id, question.question_text, 'Правильна відповідь', correct_answer.feedback, '', '')) #'Правильна відповідь')) #correct_answer.feedback))
                else:
                    # Регулярний вираз для витягнення тексту між [[ і ]]
                    book_pattern = re.compile(r'\[\[(.*?)\]\]')

                    # Витягаємо текст книги
                    book_match = book_pattern.search(u_answer.feedback)
                    book_text = book_match.group(1) if book_match else None
                    # Приклад посилання на книгу (ви можете використовувати відповідний URL)
                    #book_url = 'https://example.com/learning-react'
                    # Створення URL-адреси для книги з параметром text
                    book_url = 'https://www.google.com/search?&q=' + book_text if book_text else None

                    feedback.append((question.id, question.question_text, 'Неправильна відповідь', u_answer.feedback, book_text, book_url)) #'Спробуйте ще раз.'))
            else:
                feedback.append((question.id, question.question_text, 'Немає правильної відповіді', 'Це питання не має правильної відповіді у базі даних.', '', ''))
                
    return render(request, 'dashboard/test_result.html', {'homework': homework, 'feedback': feedback})



@login_required
def profile(request):
    print(request.user.username)
    homeworks = Homework.objects.filter(is_finished=False, user=request.user)
    todos = Todo.objects.filter(is_finished=False, user=request.user)
    if len(homeworks) == 0:
        homeworks_done = True
    else:
        homeworks_done = False
    if len(todos) == 0:
        todos_done = True
    else:
        todos_done = False
    context = {
    #    'user': request.user,
        'homeworks': zip(homeworks, range(1, len(homeworks)+1)),
        'todos': zip(todos, range(1, len(todos)+1)),
        'homeworks_done': homeworks_done,
        'todos_done': todos_done,
    }
    print(homeworks)
    return render(request, 'dashboard/profile.html', context)
    #return render(request, 'dashboard/profile.html')

@login_required
def delete_note(request, pk=None):
    Notes.objects.get(id=pk).delete()
    return redirect('notes')

@login_required
def notes(request):
  if request.method == "POST":
        form = NotesForm(request.POST)
        print('NotesForm')
        if form.is_valid():
            subject_id = request.POST['subject']
            subject_instance = get_object_or_404(Subjects, id=subject_id)

            notes = Notes(
                user=request.user,
                subject=subject_instance,
                title=request.POST['title'],
                description=request.POST['description']
            )
            print('notes.save()')
            notes.save()
            messages.success(request, f'Нотатки для {request.user.username} додано!')
           # return render(request, 'dashboard/notes.html', {'form': form})
            return redirect('notes')
  else:
    form = NotesForm()


  username = request.user.username

  # Спроба знайти співробітника і його роль
  staff = Staffs.objects.filter(user=request.user).first()
  role = staff.role if staff else 'guest'  # Присвоєння ролі "guest", якщо співробітник не знайдений

  subjects_details = []

  if role == 'student':
        # Пошук групи, до якої призначено студента
        student_group_link = StudentGroupLinks.objects.filter(user=request.user).first()
        if student_group_link:
            # Отримання призначень для групи студента
            assignments = TeachingAssignments.objects.filter(group=student_group_link.group)
            subjects_details = [{
                'subject_id': assignment.subject.id,
                'subject_title': assignment.subject.title,
                'teacher_last_name': assignment.teacher.last_name,
                'teacher_first_name': assignment.teacher.first_name
            } for assignment in assignments]
        else:
            error = 'You are not assigned to any group'
  elif role == 'teacher':
        # Отримання призначень для викладача
        assignments = TeachingAssignments.objects.filter(teacher=request.user)
        subjects_details = [{
            'subject_id': assignment.subject.id,
            'subject_title': assignment.subject.title,
            'group_title': assignment.group.title
        } for assignment in assignments]

    #context = {
    #    'title': f'Головна сторінка сайту - Користувач: {username}, Роль: {role}',
    #    'role': role,  # Важливо передати роль у контекст
    #    'subjects_details': subjects_details,
    #}


    #if request.method == "POST":
    #    form = NotesForm(request.POST)
    #    if form.is_valid():
    #        notes = Notes(
    #            user=request.user,
    #            title=request.POST['title'],
    #            description=request.POST['description']
    #        )
    #        notes.save()
    #        messages.success(request, f'Notes Added from {request.user.username}!')
    #else:
    #    form = NotesForm()
    #notes = Notes.objects.filter(user=request.user)

    # Фильтрация заметок по пользователю и предмету
  notes = []
  if subjects_details:
        for subject in subjects_details:
            #print(subject)
            subject_notes = Notes.objects.filter(user=request.user, subject_id=subject['subject_id'])
            #print(subject_notes)
            notes.extend(subject_notes)

    #context = {'form': form, 'notes': notes}
  context = {'form': form, 'subjects': subjects_details, 'notes': notes}
    #print(context)
  return render(request, 'dashboard/notes.html', context)


@login_required
def homework(request):
    if request.method == "POST":
        form = HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            #homeworks = Homework(user=request.user, subject=request.POST['subject'], title=request.POST['title'], description=request.POST['description'], due=request.POST['due'], is_finished=finished)
            #homeworks.save()
            messages.success(
                request, f'Homework Added from {request.user.username}!')
    else:
        form = HomeworkForm()
    homeworks = Homework.objects.filter(user=request.user)
    if len(homeworks) == 0:
        homeworks_done = True
    else:
        homeworks_done = False
    homeworks = zip(homeworks, range(1, len(homeworks)+1))
    context = {'form': form, 'homeworks': homeworks,
               'homeworks_done': homeworks_done}
    return render(request, 'dashboard/homework.html', context)


@login_required
def todo(request):
    if request.method == "POST":
        form = TodoForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            todos = Todo(
                user=request.user, title=request.POST['title'], is_finished=finished)
            todos.save()
            messages.success(
                request, f'Завдання додано для {request.user.username}!')
    else:
        form = TodoForm()
    todos = Todo.objects.filter(user=request.user)

    if len(todos) == 0:
        todos_done = True
    else:
        todos_done = False
    todos = zip(todos, range(1, len(todos)+1))
    context = {'form': form, 'todos': todos, 'todos_done': todos_done}
    return render(request, 'dashboard/todo.html', context)


def dictionary(request):
    if request.method == "POST":
        text = request.POST['text']
        form = DashboardForm(request.POST)

        url = "https://twinword-word-graph-dictionary.p.rapidapi.com/definition/"
        querystring = {"entry": text}
        headers = {
            "X-RapidAPI-Key": "6396b763cbmshfa58cad16096420p17b87cjsnb5486c406bfa",
            "X-RapidAPI-Host": "twinword-word-graph-dictionary.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)
        
        if response.status_code == 200:
            answer = response.json()
            try:
                definition = answer['meaning']['noun']
                context = {
                    'form': form,
                    'input': text,
                    'definition': definition,
                }
            except KeyError as e:
                messages.error(request, f"Error processing the word: {str(e)}")
                context = {
                    'form': form,
                    'input': '',
                }
        else:
            messages.error(request, f"API Error {response.status_code}: {response.text}")
            context = {
                'form': form,
                'input': '',
            }
        return render(request, 'dashboard/dictionary.html', context)
    else:
        form = DashboardForm()
    return render(request, 'dashboard/dictionary.html', {'form': form})

def wiki(request):
    if request.method == "POST":
        text = request.POST['text']
        form = DashboardForm(request.POST)
        search = wikipedia.page(text)
        context = {
            'form': form,
            'title': search.title,
            'link': search.url,
            'details': search.summary,
        }
        return render(request, 'dashboard/wiki.html', context)
    else:
        form = DashboardForm()
    return render(request, 'dashboard/wiki.html', {'form': form})



def youtube(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        videos = VideosSearch(text, limit=6)
        result_list = []
        print(videos.result())
        for i in videos.result()['result']:
            result_dict = {
                'input': text,
                'title': i['title'],
                'duration': i['duration'],
                'thumbnail': i['thumbnails'][0]['url'],
                'channel': i['channel']['name'],
                'link': i['link'],
                'views': i['viewCount']['short'],
                'published': i['publishedTime'],
            }
            desc = ''

            # Проверка на None перед итерацией
            if i.get('descriptionSnippet') is not None:
                for j in i['descriptionSnippet']:
                    desc += j['text']
            else:
                desc = 'Немає доступного опису'

            #for j in i['descriptionSnippet']:
            #    desc += j['text']
            result_dict['description'] = desc
            result_list.append(result_dict)
        return render(request, 'dashboard/youtube.html', {'form': form, 'results': result_list})
    else:
        form = DashboardForm()
    return render(request, 'dashboard/youtube.html', {'form': form})


def conversion(request):
    if request.method == "POST":
        form = ConversionForm(request.POST)
        if request.POST['measurement'] == 'length':
            measurement_form = ConversionLengthForm()
            context = {'form': form, 'm_form': measurement_form, 'input': True}
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input = request.POST['input']
                answer = ''
                if input and int(input) >= 0:
                    if first == 'yard' and second == 'foot':
                        answer = f'{input} yard = {int(input)*3} foot'
                    if first == 'foot' and second == 'yard':
                        answer = f'{input} foot = {int(input)/3} yard'
                context = {'form': form, 'm_form': measurement_form,
                           'input': True, 'answer': answer}

        if request.POST['measurement'] == 'mass':
            measurement_form = ConversionMassForm()
            context = {'form': form, 'm_form': measurement_form, 'input': True}
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input = request.POST['input']
                answer = ''
                if input and int(input) >= 0:
                    if first == 'pound' and second == 'kilogram':
                        answer = f'{input} pound = {int(input)*0.453592} kilogram'
                    if first == 'kilogram' and second == 'pound':
                        answer = f'{input} kilogram = {int(input)*2.20462} pound'
                context = {'form': form, 'm_form': measurement_form,
                           'input': True, 'answer': answer}

    else:
        form = ConversionForm()
        context = {'form': form, 'input': False}
    return render(request, 'dashboard/conversion.html', context)


def books(request):
    if request.method == "POST":
        text = request.POST['text']
        print(text)
        form = DashboardForm(request.POST)

        url = f'https://www.googleapis.com/books/v1/volumes?q="{text}"'
        #print(url)
        #url = "https://www.googleapis.com/books/v1/volumes?q="+text - треба додати " навколо тексту
        r = requests.get(url)
        #print(r)
        answer = r.json()
        #print(answer)
        result_list = []
        #for i in range(10):
        for i in range(min(10, len(answer['items']))):
            result_dict = {
                'title': answer['items'][i]['volumeInfo']['title'],
                'subtitle': answer['items'][i]['volumeInfo'].get('subtitle'),
                'description': answer['items'][i]['volumeInfo'].get('description'),
                'count': answer['items'][i]['volumeInfo'].get('pageCount'),
                'categories': answer['items'][i]['volumeInfo'].get('categories'),
                'rating': answer['items'][i]['volumeInfo'].get('averageRating'),
                'thumbnail': answer['items'][i]['volumeInfo'].get('imageLinks').get('thumbnail'),
                'preview': answer['items'][i]['volumeInfo'].get('previewLink')
            }
            result_list.append(result_dict)

        context = {
            'form': form,
            'results': result_list,
        }
        return render(request, 'dashboard/books.html', context)
    elif request.method == "GET":
        if 'text' in request.GET:
            text = request.GET.get('text')
            # Тут можна продовжити обробку параметра text
            # text = request.GET['text']
            print(text)
            form = DashboardForm(request.GET)
            url = f'https://www.googleapis.com/books/v1/volumes?q="{text}"'
            print(url)
            r = requests.get(url)
            print(r)
            answer = r.json()
            print(answer)
            result_list = []
            if not answer['items']:
                print("Список items порожній.")
            else:
                for i in range(min(10, len(answer['items']))):
                    result_dict = {
                        'title': answer['items'][i]['volumeInfo']['title'],
                        'subtitle': answer['items'][i]['volumeInfo'].get('subtitle'),
                        'description': answer['items'][i]['volumeInfo'].get('description'),
                        'count': answer['items'][i]['volumeInfo'].get('pageCount'),
                        'categories': answer['items'][i]['volumeInfo'].get('categories'),
                        'rating': answer['items'][i]['volumeInfo'].get('averageRating'),
                        'thumbnail': answer['items'][i]['volumeInfo'].get('imageLinks').get('thumbnail'),
                        'preview': answer['items'][i]['volumeInfo'].get('previewLink')
                    }
                    result_list.append(result_dict)

            context = {
                'form': form,
                'results': result_list,
            }
            return render(request, 'dashboard/books.html', context)

        else:
           # Виконати дії, якщо параметр text не був переданий у GET-запиті
           text = None
           form = DashboardForm()
           return render(request, 'dashboard/books.html', {'form': form})
    else:
        form = DashboardForm()
    return render(request, 'dashboard/books.html', {'form': form})


def delete_todo(request, pk=None):
    Todo.objects.get(id=pk).delete()
    if 'profile' in request.META['HTTP_REFERER']:
        return redirect('profile')
    return redirect('todo')


def update_todo(request, pk=None):
    todo = Todo.objects.get(id=pk)
    if todo.is_finished == True:
        todo.is_finished = False
    else:
        todo.is_finished = True
    todo.save()
    if 'profile' in request.META['HTTP_REFERER']:
        return redirect('profile')
    return redirect('todo')


class NotesDetailView(generic.DetailView):
    model = Notes
