# внутрішній_каталог_додатку/management/commands/fill_users.py
#Після цього ви зможете викликати цю команду з терміналу, використовуючи python manage.py fill_db, і вона виконає ваш код

from django.core.management.base import BaseCommand
from django.utils import timezone
from random import randint, choice

from django.contrib.auth.models import User
from dashboard.models import Task, Homework, StudentGroups, StudentGroupLinks, Subjects

class Command(BaseCommand):
    help = 'Заповнення таблиці Homework за допомогою Django ORM'  #python manage.py fill_db --help - виклик допомоги

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
                hwork = Homework.objects.create(user=student, task=task)

                hwork.is_submitted = True;
                hwork.submission_date = timezone.now() + timezone.timedelta(days=randint(1, 10))
                hwork.title = task.title[:100]
                hwork.description = task.description

                hwork.is_finished = choice([True, False]);
                if hwork.is_finished:
                    hwork.finishdate = timezone.now() + timezone.timedelta(days=randint(10, 20))
                    hwork.grade = randint(1, 5)
                    hwork.gradedescription = f'Коментар для оцінки "{hwork.grade}" студента {student.last_name} з предмета {subject.title} '

                hwork.save()
                # Виводимо повідомлення про успішне розподілення
                #self.stdout.write(self.style.SUCCESS(f"Студент {student.username} task {task.title} submission_date {hwork.submission_date} "
                #                                     f"grade {hwork.grade} gradedescr {hwork.gradedescription}"))

