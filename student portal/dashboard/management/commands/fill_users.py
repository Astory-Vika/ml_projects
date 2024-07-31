# внутрішній_каталог_додатку/management/commands/fill_users.py
#Після цього ви зможете викликати цю команду з терміналу, використовуючи python manage.py fill_db, і вона виконає ваш код

from django.core.management.base import BaseCommand
from django.utils import timezone

from django.contrib.auth.models import User
from dashboard.models import Staffs

# Дані адміністраторів
admin_data = [
    {'last_name': 'Іваненко', 'first_name': 'Іван', 'middle_name': 'Іванович', 'username': 'admin1', 'password': 'pass123', 'role': 'admin'},
    {'last_name': 'Петренко', 'first_name': 'Петро', 'middle_name': 'Петрович', 'username': 'admin2', 'password': 'pass123', 'role': 'admin'},
# Дані викладачів
    {'last_name': 'Сидоренко', 'first_name': 'Сидір', 'middle_name': 'Сидорович', 'username': 'teacher1', 'password': 'pass123', 'role': 'teacher'},
    {'last_name': 'Михайленко', 'first_name': 'Михайло', 'middle_name': 'Михайлович', 'username': 'teacher2', 'password': 'pass123', 'role': 'teacher'},
    {'last_name': 'Коваленко', 'first_name': 'Катерина', 'middle_name': 'Василівна', 'username': 'teacher3', 'password': 'pass123', 'role': 'teacher'},
    {'last_name': 'Бондаренко', 'first_name': 'Богдан', 'middle_name': 'Богданович', 'username': 'teacher4', 'password': 'pass123', 'role': 'teacher'},
    {'last_name': 'Василенко', 'first_name': 'Василь', 'middle_name': 'Васильович', 'username': 'teacher5', 'password': 'pass123', 'role': 'teacher'},
    {'last_name': 'Олексієнко', 'first_name': 'Олексій', 'middle_name': 'Олексійович', 'username': 'teacher6', 'password': 'pass123', 'role': 'teacher'},
    {'last_name': 'Андрієнко', 'first_name': 'Андрій', 'middle_name': 'Андрійович', 'username': 'teacher7', 'password': 'pass123', 'role': 'teacher'},
    {'last_name': 'Тарасенко', 'first_name': 'Тарас', 'middle_name': 'Тарасович', 'username': 'teacher8', 'password': 'pass123', 'role': 'teacher'},
# Дані студентів
    {'last_name': 'Козак', 'first_name': 'Олег', 'middle_name': 'Олегович', 'username': 'student1', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Гончар', 'first_name': 'Ганна', 'middle_name': 'Григорівна', 'username': 'student2', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Коваленко', 'first_name': 'Олександр', 'middle_name': 'Володимирович', 'username': 'student3', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Савченко', 'first_name': 'Вікторія', 'middle_name': 'Олександрівна', 'username': 'student4', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Бойко', 'first_name': 'Вадим', 'middle_name': 'Юрійович', 'username': 'student5', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Грищенко', 'first_name': 'Ірина', 'middle_name': 'Михайлівна', 'username': 'student6', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Литвиненко', 'first_name': 'Дмитро', 'middle_name': 'Сергійович', 'username': 'student7', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Мельник', 'first_name': 'Анна', 'middle_name': 'Петрівна', 'username': 'student8', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Шевченко', 'first_name': 'Тарас', 'middle_name': 'Григорович', 'username': 'student9', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Кравчук', 'first_name': 'Людмила', 'middle_name': 'Василівна', 'username': 'student10', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Ткаченко', 'first_name': 'Юлія', 'middle_name': 'Вікторівна', 'username': 'student11', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Захарченко', 'first_name': 'Максим', 'middle_name': 'Олегович', 'username': 'student12', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Григоренко', 'first_name': 'Павло', 'middle_name': 'Вікторович', 'username': 'student13', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Сергієнко', 'first_name': 'Сергій', 'middle_name': 'Олександрович', 'username': 'student14', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Денисенко', 'first_name': 'Денис', 'middle_name': 'Олегович', 'username': 'student15', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Олексієнко', 'first_name': 'Олексій', 'middle_name': 'Петрович', 'username': 'student16', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Анатолієнко', 'first_name': 'Анатолій', 'middle_name': 'Іванович', 'username': 'student17', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Юрієнко', 'first_name': 'Юрій', 'middle_name': 'Васильович', 'username': 'student18', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Максименко', 'first_name': 'Максим', 'middle_name': 'Григорович', 'username': 'student19', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Романенко', 'first_name': 'Роман', 'middle_name': 'Дмитрович', 'username': 'student20', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Віталієнко', 'first_name': 'Віталій', 'middle_name': 'Сергійович', 'username': 'student21', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Володимиренко', 'first_name': 'Володимир', 'middle_name': 'Миколайович', 'username': 'student22', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Богданенко', 'first_name': 'Богдан', 'middle_name': 'Ігорович', 'username': 'student23', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Василенко', 'first_name': 'Василь', 'middle_name': 'Андрійович', 'username': 'student24', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Степаненко', 'first_name': 'Степан', 'middle_name': 'Петрович', 'username': 'student25', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Олегенко', 'first_name': 'Олег', 'middle_name': 'Вікторович', 'username': 'student26', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Андрієнко', 'first_name': 'Андрій', 'middle_name': 'Юрійович', 'username': 'student27', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Ігоренко', 'first_name': 'Ігор', 'middle_name': 'Васильович', 'username': 'student28', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Світланенко', 'first_name': 'Світлана', 'middle_name': 'Олексіївна', 'username': 'student29', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Ларисенко', 'first_name': 'Лариса', 'middle_name': 'Іванівна', 'username': 'student30', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Оксаненко', 'first_name': 'Оксана', 'middle_name': 'Петрівна', 'username': 'student31', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Наталієнко', 'first_name': 'Наталія', 'middle_name': 'Вікторівна', 'username': 'student32', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Юліяненко', 'first_name': 'Юлія', 'middle_name': 'Максимівна', 'username': 'student33', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Марієнко', 'first_name': 'Марія', 'middle_name': 'Ігорівна', 'username': 'student34', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Тетяненко', 'first_name': 'Тетяна', 'middle_name': 'Олегівна', 'username': 'student35', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Іриненко', 'first_name': 'Ірина', 'middle_name': 'Василівна', 'username': 'student36', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Антоненко', 'first_name': 'Антон', 'middle_name': 'Сергійович', 'username': 'student37', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Вікторенко', 'first_name': 'Віктор', 'middle_name': 'Іванович', 'username': 'student38', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Петренко', 'first_name': 'Петро', 'middle_name': 'Михайлович', 'username': 'student39', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Михайленко', 'first_name': 'Михайло', 'middle_name': 'Володимирович', 'username': 'student40', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Олененко', 'first_name': 'Олена', 'middle_name': 'Григорівна', 'username': 'student41', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Катериненко', 'first_name': 'Катерина', 'middle_name': 'Юріївна', 'username': 'student42', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Олександренко', 'first_name': 'Олександра', 'middle_name': 'Михайлівна', 'username': 'student43', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Валентиненко', 'first_name': 'Валентина', 'middle_name': 'Петрівна', 'username': 'student44', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Валерієнко', 'first_name': 'Валерій', 'middle_name': 'Олександрович', 'username': 'student45', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Дмитренко', 'first_name': 'Дмитро', 'middle_name': 'Ігорович', 'username': 'student46', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Євгененко', 'first_name': 'Євген', 'middle_name': 'Вікторович', 'username': 'student47', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Іваненко', 'first_name': 'Іван', 'middle_name': 'Петрович', 'username': 'student48', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Кириленко', 'first_name': 'Кирило', 'middle_name': 'Андрійович', 'username': 'student49', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Леоніденко', 'first_name': 'Леонід', 'middle_name': 'Максимович', 'username': 'student50', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Маркіяненко', 'first_name': 'Маркіян', 'middle_name': 'Тарасович', 'username': 'student51', 'password': 'pass123', 'role': 'student'},
    {'last_name': 'Назаренко', 'first_name': 'Назар', 'middle_name': 'Богданович', 'username': 'student52', 'password': 'pass123', 'role': 'student'}
]


class Command(BaseCommand):
    help = 'Заповнення таблиці Users за допомогою Django ORM'  #python manage.py fill_db --help - виклик допомоги

    def handle(self, *args, **kwargs):
        time = timezone.now().strftime('%X')
        self.stdout.write("It's now %s" % time)

# Додавання адміністраторів
        for data in admin_data:
            user = User.objects.create_user(data['username'], password=data['password'])
            user.last_name = data['last_name']
            user.first_name = data['first_name']
            user.save()

            staff = Staffs(
                user=user,
                middle_name=data['middle_name'],
                role=data['role']
            )
            staff.save()