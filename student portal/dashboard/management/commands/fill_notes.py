# внутрішній_каталог_додатку/management/commands/fill_users.py
#Після цього ви зможете викликати цю команду з терміналу, використовуючи python manage.py fill_db, і вона виконає ваш код

from django.core.management.base import BaseCommand
from django.utils import timezone
from random import randint

from django.contrib.auth.models import User
from dashboard.models import Notes, TeachingAssignments, Schedule, Task, Homework, StudentGroups, StudentGroupLinks, Subjects

class Command(BaseCommand):
    help = 'Заповнення таблиці Notes за допомогою Django ORM'  #python manage.py fill_db --help - виклик допомоги

    def handle(self, *args, **kwargs):
        time = timezone.now().strftime('%X')
        self.stdout.write("It's now %s" % time)


        #беремо всі завдання
        tasks = Task.objects.all()

        for task in tasks:
            #отримуємо перший запис з відфільтрованої таблиці предметів (він там в принципі один має бути)
            subject = Subjects.objects.filter(id = task.subject_id).first()
            #відфільтровуємо студентів по групі завдання
            student_group_links = StudentGroupLinks.objects.filter(group=task.group)
            #щоб отримати об'єкти User
            users_in_group = User.objects.filter(studentgrouplinks__in=student_group_links)
            #перебираэмо записи групи студентів
            for student in users_in_group:
                note = Notes.objects.create(user=student, subject=subject)
                note.title = f'Нотатки для {task.title}'
                note.description = f'Нотатки для {task.title} студента {student.last_name} з предмета {subject.title}'
                note.save()