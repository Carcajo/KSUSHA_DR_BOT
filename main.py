import asyncio
import logging
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.filters import CommandStart

# --- НАСТРОЙКИ ---
TOKEN = "8744964208:AAGzxouce3_8KvwLl9g4kS-uF0xNHhvPEr4"

# Список всех шагов. Ты можешь менять тексты и кнопки прямо здесь.
# 'photo' - имя файла в папке images
# 'text' - подпись к фото
# 'buttons' - список названий кнопок (можно любое количество)
STEPS = [
    {
        "photo": "img7.jpg",
        "text": "Привет, красотка! С днем рождения! 🎉 У тебя сегодня особенный день, и я подготовила для тебя кое-что интересное. Начнем?",
        "buttons": ["Да!", "Конечно", "Поехали"]
    },
    {
        "photo": "img3.jpg",
        "text": "Отлично! Скажи, ты по-прежнему отличница?",
        "buttons": ["Да", "Нет", "Почти"]
    },
    {
        "photo": "img2.jpg",
        "text": "А ты все еще любишь фоткаться в разных местах?",
        "buttons": ["На все 100%", "Немного", "Определенно"]
    },
    {
        "photo": "img6.jpg",
        "text": "Так и знала) А мальчики уже дарят настоящие цветы?",
        "buttons": ["Да", "Парень дарит)", "Нет"]
    },
    {
        "photo": "img5.jpg",
        "text": "Наверное ты и сейчас любишь платья мерять и одежду подбирать себе?)",
        "buttons": ["Естественно", "Конечно", "Обожаю"]
    },
    {
        "photo": "img4.jpg",
        "text": "Не удивлена) А ты уже стала чьим-то подарком?)))",
        "buttons": ["Да-а-а!", "Уже да", "Мне повезло"]
    },
    {
        "photo": "img8.jpg",
        "text": "Последний вопрос перед финалом: Ты все еще милашка?",
        "buttons": ["Да", "Смотря для кого", "Вредная я)"]
    }
]

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()


def get_keyboard(step_index: int):
    """Создает клавиатуру для конкретного шага."""
    buttons_text = STEPS[step_index]["buttons"]
    keyboard = []

    row = []
    for text in buttons_text:
        row.append(InlineKeyboardButton(text=text, callback_data=f"step_{step_index + 1}"))

    keyboard.append(row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


@router.message(CommandStart())
async def cmd_start(message: Message):
    step_index = 0
    photo_path = f"images/{STEPS[step_index]['photo']}"

    await message.answer_photo(
        photo=FSInputFile(photo_path),
        caption=STEPS[step_index]["text"],
        reply_markup=get_keyboard(step_index)
    )


@router.callback_query(F.data.startswith("step_"))
async def handle_steps(callback: CallbackQuery):
    """Обработка всех переходов по кнопкам."""
    next_step = int(callback.data.split("_")[1])

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()

    if next_step < len(STEPS):
        photo_path = f"images/{STEPS[next_step]['photo']}"
        await callback.message.answer_photo(
            photo=FSInputFile(photo_path),
            caption=STEPS[next_step]["text"],
            reply_markup=get_keyboard(next_step)
        )
    else:
        await callback.message.answer('Круто, что ты всё такая же классная, как и была. С днем рождения тебя. Напиши Максиму (@Carcajo), спроси, "Что будем делать дальше?"')

        video_path = "video.mp4"
        try:
            await callback.message.answer_video(
                video=FSInputFile(video_path),
                caption="С днем рождения! ❤️"
            )
        except Exception as e:
            await callback.message.answer(
                f"Ошибка при отправке видео: {e}\nПроверь, что файл video.mp4 лежит в папке с ботом.")


async def main():
    dp.include_router(router)
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")