from typing import Tuple
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from dashboard.models import Homework, Notes, Todo, Subjects





class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'last_name', 'first_name', 'email',
                  'password1', 'password2']
    username = forms.CharField(max_length=150, label="Введіть логін користувача: ")
    last_name = forms.CharField(max_length=150, label="Прізвище: ")
    first_name = forms.CharField(max_length=150, label="Ім'я: ")


class CustomDateInput(forms.DateInput):
    input_type = 'date'



class DashboardForm(forms.Form):
    text = forms.CharField(max_length=100, label="Ваш запит")
    
class NotesForm(forms.Form):
    class Meta:
        model = Notes
        fields = ['subject', 'title', 'description']

    subject = forms.ModelChoiceField(queryset=Subjects.objects.all(), label="Виберіть предмет: ")
    #subject = forms.ModelChoiceField(queryset=Subjects.objects.none(), label="Виберіть предмет: ")
    title = forms.CharField(max_length=200, label="Введіть найменування: ")
    description = forms.CharField(max_length=200, label="Опис: ")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(NotesForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['subject'].queryset = Subjects.objects.filter(user=user)

class HomeworkResponseForm(forms.ModelForm):
    class Meta:
        model = Homework
        fields = ['title', 'description']  # Додайте сюди інші поля, якщо це потрібно

class HomeworkForm(forms.ModelForm):
    class Meta:
        model = Homework
        fields = ['title', 'description', 'is_finished']
        widgets = {
            'due_date': CustomDateInput()  # Припускаючи, що в моделі є поле due_date
        }



class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo

        fields = ['title', 'is_finished']


class ConversionForm(forms.Form):
    CHOICES = [('length', 'Довжина'),
               ('mass', 'Масса')]

    measurement = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)


class ConversionLengthForm(forms.Form):
    CHOICES = [('yard', 'Ярд'),
               ('foot', 'Фути')]
    input = forms.CharField(required=False,
                            label=False, widget=forms.TextInput(attrs={'type': 'number', 'placeholder': 'Введіть число'}))
    measure1 = forms.CharField(
        label='', widget=forms.Select(choices=CHOICES))
    measure2 = forms.CharField(
        label='', widget=forms.Select(choices=CHOICES))


class ConversionMassForm(forms.Form):
    CHOICES = [('pound', 'Фунт'),
               ('kilogram', 'Кілограм')]
    input = forms.CharField(required=False,
                            label=False, widget=forms.TextInput(attrs={'type': 'number', 'placeholder': 'Введіть число'}))

    measure1 = forms.CharField(
        label='', widget=forms.Select(choices=CHOICES))
    measure2 = forms.CharField(
        label='', widget=forms.Select(choices=CHOICES))
    
class HomeworkForm(forms.ModelForm):
    class Meta:
        model = Homework
        fields = ['description']

class GradeForm(forms.ModelForm):
    class Meta:
        model = Homework
        fields = ['grade', 'gradedescription']
        widgets = {
            'grade': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'gradedescription': forms.Textarea(attrs={'rows': 4, 'cols': 40})
        }