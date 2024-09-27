import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler

TOKEN = '7586896886:AAEENBS4O5BlsHG4wEgRfSKLudbcXO003TE'

info_ru = "Добро пожаловать в Web Academy TJ! Пожалуйста, выберите язык."
info_tj = "Хуш омадед ба Web Academy TJ! Лутфан, забони худро интихоб кунед."

about_info = {
    'ru': "Web Academy TJ предлагает курсы по программированию и развитию навыков в различных областях. Мы готовы помочь вам достичь ваших целей!",
    'tj': "Web Academy TJ курсҳои барномасозӣ ва рушди малакаҳоро дар соҳаҳои гуногун пешниҳод мекунад. Мо омодаем ба шумо дар расидан ба ҳадафҳои худ кӯмак кунем!"
}

courses_info = {
    'python': {
        'ru': "Курс по Python охватывает основы программирования, включая синтаксис, структуры данных и основы ООП.",
        'tj': "Курси Python асосҳои барномасозӣ, аз ҷумла синтаксис, сохторҳои маълумот ва асосҳои ООП-ро дар бар мегирад."
    },
    'ios': {
        'ru': "Курс по iOS разработке включает в себя создание приложений для платформы iOS, изучение Swift и Xcode.",
        'tj': "Курси рушди iOS таҳияи барномаҳо барои платформаи iOS-ро дар бар мегирад, омӯзиши Swift ва Xcode."
    },
    'android': {
        'ru': "Курс по Android разработке охватывает создание приложений для платформы Android, изучение Kotlin и Android Studio.",
        'tj': "Курси рушди Android таҳияи барномаҳо барои платформаи Android-ро дар бар мегирад, омӯзиши Kotlin ва Android Studio."
    }
}

contact_info = {
    'ru': "Наш номер телефона: +992 005716565",
    'tj': "Рақами телефони мо: +992 005716565"
}

# Параметры для пагинации
COURSES_PER_PAGE = 2  # Количество курсов на одной странице

def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, language TEXT)''')
    conn.commit()
    conn.close()

def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Русский", callback_data='ru'), InlineKeyboardButton("Тоҷикӣ", callback_data='tj')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    photo_path = 'photo_2024-09-22_22-09-10.jpg'

    try:
        with open(photo_path, 'rb') as photo:
            message = update.message.reply_photo(photo=photo, caption=info_ru, reply_markup=reply_markup)
            context.user_data['message_id'] = message.message_id
            context.user_data['state'] = 'language'
    except FileNotFoundError:
        update.message.reply_text("Изображение не найдено. Пожалуйста, проверьте путь к файлу.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_language = query.data
    user_id = query.from_user.id

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO users (user_id, language) VALUES (?, ?)', (user_id, user_language))
    conn.commit()
    conn.close()

    if user_language in ['ru', 'tj']:
        context.user_data['language'] = user_language
        show_main_menu(query, context)

    elif user_language == 'back':
        previous_state = context.user_data.get('previous_state')
        if previous_state:
            show_menu(previous_state, query, context)

    elif user_language.startswith('page_'):
        page_number = int(user_language.split('_')[1])
        show_courses(query, context, page_number)

    elif user_language == 'courses':
        context.user_data['previous_state'] = context.user_data['state']
        show_courses(query, context)

    elif user_language == 'contact':
        context.user_data['previous_state'] = context.user_data['state']
        show_contact(query, context)

    elif user_language == 'about':
        context.user_data['previous_state'] = context.user_data['state']
        show_about(query, context)

    elif user_language == 'phone':
        show_phone_number(query, context)

    elif user_language in courses_info:
        course_info = courses_info[user_language][context.user_data['language']]
        context.bot.edit_message_caption(
            chat_id=query.message.chat_id,
            message_id=context.user_data['message_id'],
            caption=course_info,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data='back')]])
        )
        context.user_data['state'] = f"{user_language}_info"

def show_menu(state: str, query: Update, context: CallbackContext):
    if state == 'main_menu':
        show_main_menu(query, context)
    elif state == 'courses':
        show_courses(query, context)
    elif state == 'contact':
        show_contact(query, context)
    elif state == 'about':
        show_about(query, context)

def show_main_menu(query: Update, context: CallbackContext):
    user_language = context.user_data.get('language', 'ru')
    courses_btn = "Курсы" if user_language == 'ru' else "Курсҳо"
    contact_btn = "Контакт" if user_language == 'ru' else "Контакт"
    about_btn = "О нас" if user_language == 'ru' else "Дар бораи мо"

    keyboard = [
        [InlineKeyboardButton(courses_btn, callback_data='courses')],
        [InlineKeyboardButton(contact_btn, callback_data='contact')],
        [InlineKeyboardButton(about_btn, callback_data='about')],
    ]

    current_caption = info_ru if user_language == 'ru' else info_tj
    current_reply_markup = InlineKeyboardMarkup(keyboard)

    photo_path = 'photo_2024-09-22_22-09-10.jpg'  # Вернуть исходное изображение

    try:
        with open(photo_path, 'rb') as photo:
            # Меняем изображение на исходное при возврате в главное меню
            context.bot.edit_message_media(
                chat_id=query.message.chat_id,
                message_id=context.user_data['message_id'],
                media=InputMediaPhoto(photo, caption=current_caption),
                reply_markup=current_reply_markup
            )
    except FileNotFoundError:
        query.message.reply_text("Исходное изображение не найдено.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

    context.user_data['state'] = 'main_menu'


def show_courses(query: Update, context: CallbackContext, page: int = 0):
    user_language = context.user_data.get('language', 'ru')
    course_keys = list(courses_info.keys())
    total_courses = len(course_keys)
    total_pages = (total_courses + COURSES_PER_PAGE - 1) // COURSES_PER_PAGE  # Округляем вверх

    # Получаем курсы для текущей страницы
    start_index = page * COURSES_PER_PAGE
    end_index = start_index + COURSES_PER_PAGE
    current_courses = course_keys[start_index:end_index]

    # Формируем текст для текущей страницы
    courses_text = "Выберите курс:\n" if user_language == 'ru' else "Курсро интихоб кунед:\n"
    for course in current_courses:
        courses_text += f"- {course}\n"

    # Кнопки для навигации
    keyboard = []
    for course in current_courses:
        keyboard.append([InlineKeyboardButton(course.capitalize(), callback_data=course)])

    # Кнопки пагинации
    if page > 0:
        keyboard.append([InlineKeyboardButton("Назад", callback_data=f'page_{page - 1}')])
    if page < total_pages - 1:
        keyboard.append([InlineKeyboardButton("Далее", callback_data=f'page_{page + 1}')])

    # Меняем изображение на 'photo_kurs.jpg' при нажатии на кнопку "Курсы"
    photo_path = 'photo_kurs.jpg'
    try:
        with open(photo_path, 'rb') as photo:
            # Используем InputMediaPhoto для изменения изображения и текста одновременно
            context.bot.edit_message_media(
                chat_id=query.message.chat_id,
                message_id=context.user_data['message_id'],
                media=InputMediaPhoto(photo, caption=courses_text),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except FileNotFoundError:
        query.message.reply_text("Изображение не найдено. Пожалуйста, проверьте путь к файлу.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

    context.user_data['state'] = 'courses'

def show_contact(query: Update, context: CallbackContext) -> None:
    user_language = context.user_data.get('language', 'ru')
    contact_keyboard = [
        [InlineKeyboardButton("Телеграм", url="https://t.me/username")],
        [InlineKeyboardButton("Инстаграм", url="https://instagram.com/username")],
        [InlineKeyboardButton("Телефон", callback_data='phone')],
        [InlineKeyboardButton("Назад", callback_data='back')]
    ]

    context.bot.edit_message_caption(
        chat_id=query.message.chat_id,
        message_id=context.user_data['message_id'],
        caption=contact_info[user_language],
        reply_markup=InlineKeyboardMarkup(contact_keyboard)
    )

    context.user_data['state'] = 'contact'

def show_about(query: Update, context: CallbackContext) -> None:
    user_language = context.user_data.get('language', 'ru')
    context.bot.edit_message_caption(
        chat_id=query.message.chat_id,
        message_id=context.user_data['message_id'],
        caption=about_info[user_language],
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data='back')]])
    )
    context.user_data['state'] = 'about'

def show_phone_number(query: Update, context: CallbackContext):
    user_language = context.user_data.get('language', 'ru')
    context.bot.edit_message_caption(
        chat_id=query.message.chat_id,
        message_id=context.user_data['message_id'],
        caption=contact_info[user_language],
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data='back')]])
    )

def main() -> None:
    updater = Updater(TOKEN)

    init_db()

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
