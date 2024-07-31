import openai
#import os
import re
from django.conf import settings
from transformers import MBartForConditionalGeneration, MBart50Tokenizer
from sentence_transformers import SentenceTransformer, util
#from openai import OpenAI
#from django.contrib import messages

# Перевірка наявності OpenAI API ключа
api_key = settings.OPENAI_API_KEY
if not api_key:
    raise Exception('OpenAI API Key not found')

# Встановлення OpenAI API ключа
openai.api_key = api_key

def get_completion(prompt, num_questions=5):
    try:
        # Виклик OpenAI API для отримання відповіді
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[
                {"role": "system", "content": "You are a helpful assistant who understands Ukrainian. Generate multiple-choice questions in Ukrainian based on the provided text."},
#                {"role": "user", "content": f"Generate {num_questions} multiple-choice questions and answers in Ukrainian based on the following text: {prompt}. Number the questions with a number followed by a period and a space (e.g., '1. '). Number the answer choices with uppercase Latin letters followed by a parenthesis and a space (e.g., 'A) '). Mark the correct answer with an asterisk (*) directly (without spaces) before the letter of the correct choice (e.g., '*C) '). After each question, before the answer choices, please include a relevant literary source (book name with author preffered) related to the questions, highlighted with [[ and ]] symbols. The source preffered, but does not necessarily have to be from Google Books."}
                {"role": "user", "content": f"Generate {num_questions} multiple-choice questions and answers in Ukrainian based on the following text: {prompt}. Number the questions with a number followed by a period and a space (e.g., '1. '). After each question, before the answer choices, include a relevant literary source (book name with author) related to the question, highlighted with [[ and ]] symbols (e.g., '[[Book: ... author: ...]]'). Number the answer choices with uppercase Latin letters followed by a parenthesis and a space (e.g., 'A) '). Mark the correct answer with an asterisk (*) directly (without spaces) before the letter of the correct choice (e.g., '*C) '). For example: '1. Quest 1? [[Book: Book1 author: Author1]] A) Var 1 *B) Var 2' "}
            ]


        )
        # Отримання контенту з відповіді
        completion = response['choices'][0]['message']['content']
        return completion
    except Exception as e:
        # Обробка помилок
        raise Exception(f"Error in OpenAI API call: {e}")


def generate_questions(prompt, num_questions=5):
    response = get_completion(prompt, num_questions)
    print(f"Response: {response} ")

    #response = r"1. Які властивості мають логарифми? A) Вони можуть бути додавані B) Вони можуть бути множені C) Вони можуть бути віднімані *D) Всі відповіді вірні 2. Що таке логарифм? A) Математична область *B) Функція C) Рівняння D) Степень числа 3. Що позначає lg в математиці? A) Лінійна геометрія *B) Логарифм за підставою 10 C) Логічний гейт D) Логарифмічний графік 4. Яку операцію з числовими значеннями виконує логарифмування? A) Повністю додавання *B) Перетворення множення на додавання C) Квадратичні корені D) Ділення чисел 5. Для чого використовують логарифмічні таблиці в математиці? A) Для підсумовування чисел B) Для множення чисел C) Для побудови графіків *D) Для спрощення обчислень"
    #response = r"1. Що таке React? [[Книга: Вступ до React автор: Макс Фрай]] A) JavaScript бібліотека *B) CSS фреймворк C) Backend платформа D) HTML стандарт 2. Яке з наведених понять НЕ є ключовими у React? [[Книга: Введення в React автор: Джон Доу]] A) Virtual DOM B) Компоненти *C) Шаблонізатор D) Стейт 3. Що передбачає концепція рекомендаційних компонентів у React? [[Книга: Розробка веб-додатків на React автор: Олексій Михайленко]] A) Забороняє використання компонентів B) Рекомендує використання компонентів *C) Завжди вимагає вкладеності компонентів D) Не має спеціальних вимог 4. Яка із наведених функцій складає основу життєвого циклу компонентів React? [[Книга: React: швидкий старт автор: Віктор Петрік]] A) render B) mount *C) constructor D) setState 5. Який з методів React використовується для оновлення стану компонента? [[Книга: Поглиблене вивчення React автор: Ліза Сімпсон]] A) applyState B) updateState *C) setState D) modifyState"

    questions = parse_questions(response)
    print(questions)

    return questions


def parse_questions(text):
    questions = []
    # Патерни для знаходження питань та відповідей
    question_pattern = re.compile(r"(\d+\..*?\?)", re.DOTALL)
    #answer_pattern = re.compile(r"([A-D]\)\s\*?.*?)(?=[A-D]\)|$)", re.DOTALL)
    answer_pattern = re.compile(r"(\*?[A-D]\)\s\*?.*?)(?=\*?[A-D]\)|$)", re.DOTALL)
    book_pattern = re.compile(r"\[\[(.*?)\]\]")

    question_matches = question_pattern.split(text)
    book_matches = book_pattern.split(text)

    for i in range(1, len(question_matches), 2):
        question_text = question_matches[i].strip()
        #book_match = book_pattern.search(question_matches[i - 1])
        #book = book_match.group(1) if book_match else None
        book = book_matches[i].strip()
        answer_block = question_matches[i + 1].strip()
        answer_block = book_pattern.sub('', answer_block).strip()
        #answer_block = book_matches[i + 1].strip()
        print(f"question_text: {question_text}")
        print(f"book: {book}")
        print(f"answer_block: {answer_block}")

        answers = []
        matches = answer_pattern.findall(answer_block)
        for match in matches:
            #print(f"match: ={match}=")
            is_correct = match[0] == '*'  # Перевірка на наявність зірочки перед літерою
            answer_text = match[4:].strip() if is_correct else match[3:].strip()
            answers.append({'text': answer_text, 'is_correct': is_correct})
            print(f"answer text: ={answer_text}= is_correct: {is_correct}")

        #questions.append({'question_text': question_text, 'answers': answers})
        questions.append({'question_text': question_text, 'answers': answers, 'book': book})
    return questions


def text_summary(text, src_lang="uk_UA", tgt_lang="uk_UA"):
    model_name = "facebook/mbart-large-50-many-to-many-mmt"
    tokenizer = MBart50Tokenizer.from_pretrained(model_name)
    model = MBartForConditionalGeneration.from_pretrained(model_name)

    tokenizer.src_lang = src_lang
    encoded_input = tokenizer(text, return_tensors="pt", max_length=1024, truncation=True)
    generated_tokens = model.generate(
        **encoded_input,
        forced_bos_token_id=tokenizer.lang_code_to_id[tgt_lang],
        max_length=200,  # Максимальна довжина резюме
        min_length=40,   # Мінімальна довжина резюме
        length_penalty=2.0,
        num_beams=4,     # Кількість променів для пошуку
        early_stopping=True,
        no_repeat_ngram_size=3  # Запобігання повторення фраз
    )

    summary = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
    
    # Обрізати до двох речень
    sentences = re.split(r'(?<=\.)\s', summary)
    summary = ' '.join(sentences[:2])
    
    # Додаємо крапку, якщо її немає в кінці
    if not summary.endswith('.'):
        summary += '.'
    
    return summary


# Ініціалізація моделі для обчислення семантичної подібності
similarity_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def check_similarity(task_text, student_response, threshold=0.75):
    # Отримання векторних уявлень для тексту завдання та відповіді студента
    task_embedding = similarity_model.encode(task_text, convert_to_tensor=True)
    response_embedding = similarity_model.encode(student_response, convert_to_tensor=True)
    
    # Обчислення косинусної подібності між текстами
    similarity_score = util.pytorch_cos_sim(task_embedding, response_embedding).item()
    
    # Повернення результату порівняння з пороговим значенням
    return similarity_score >= threshold

#def text_summary(text, maxlength=None):
#    summary = Summary("mrm8488/bert2bert_shared-uk-finetuned-uk-wiki")
#    result = summary(text)
#    return result


#def parse_questions(text):
#    questions = []
#    question_pattern = re.compile(r"Q:(.*?)A:", re.DOTALL)
#    answer_pattern = re.compile(r"A:(.*?)(?=\nQ:|\Z)", re.DOTALL)

#    question_matches = question_pattern.findall(text)
#    answer_matches = answer_pattern.findall(text)

#    for question, answer_block in zip(question_matches, answer_matches):
#        question_text = question.strip()
#        answers = [{'text': ans.strip().split(' ')[1], 'is_correct': ans.startswith('*')} for ans in answer_block.strip().split('\n') if ans]
#        questions.append({'question_text': question_text, 'answers': answers})
    
#    return questions