import asyncio
import logging
import os
from pathlib import Path
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# --- НАСТРОЙКИ ПУТЕЙ ---
BASE_DIR = Path(__file__).resolve().parent
IMAGES_DIR = BASE_DIR / "images"

# Берем токен из переменных (на Railway назови её BOT_TOKEN) или используем твой
TOKEN = os.getenv("BOT_TOKEN", "8744964208:AAGzxouce3_8KvwLl9g4kS-uF0xNHhvPEr4")
REWARD = 50

STEPS = [
    {
        "photo": "img7.jpg",
        "text": "Привет, красотка! С днем рождения! 🎉 У тебя сегодня особенный день, и я подготовил для тебя кое-что интересное. Начнем?",
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

QUEST_STEPS = [
    {
        "question": "📍 Задание 1: Место, где мы впервые встретились. Поезжай туда, сделай фото и напиши название этого места в описании!",
        "key": "клуб"},
    {
        "question": "📍 Задание 2: Место, где мы с тобой фотографировались первый раз и снимали видосики. Жду фото и название места, которое там рядом (это не банк)!",
        "key": "цирк"},
    {
        "question": "📍 Задание 3: В этом магазине ты НЕ купила то самое зеленое платье. Сфоткай витрину и напиши название ПОЛНОСТЬЮ!",
        "key": "sky"},
    {
        "question": "📍 Здесь ты любишь покупать булочки, хоть и нечасто, но говоришь, что тут самые вкусные. Жду фото и название заведения!",
        "key": "тьери"}
]


class QuestStates(StatesGroup):
    intro = State()
    quest = State()


bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()


def get_keyboard(step_index: int):
    buttons_text = STEPS[step_index]["buttons"]
    keyboard = [[InlineKeyboardButton(text=t, callback_data=f"step_{step_index + 1}") for t in buttons_text]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def safely_send_photo(message: Message, photo_name: str, caption: str, reply_markup=None):
    """Вспомогательная функция для безопасной отправки фото."""
    photo_path = IMAGES_DIR / photo_name
    if photo_path.exists():
        return await message.answer_photo(photo=FSInputFile(photo_path), caption=caption, reply_markup=reply_markup)
    else:
        logging.error(f"Файл не найден: {photo_path}")
        return await message.answer(f"📸 (Картинка {photo_name} не найдена)\n\n{caption}", reply_markup=reply_markup)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.update_data(current_quest=0, balance=0)
    await state.set_state(QuestStates.intro)
    await safely_send_photo(message, STEPS[0]["photo"], STEPS[0]["text"], get_keyboard(0))


@router.callback_query(F.data.startswith("step_"), QuestStates.intro)
async def handle_steps(callback: CallbackQuery, state: FSMContext):
    next_step = int(callback.data.split("_")[1])
    await callback.message.edit_reply_markup(reply_markup=None)

    if next_step < len(STEPS):
        await safely_send_photo(callback.message, STEPS[next_step]["photo"], STEPS[next_step]["text"],
                                get_keyboard(next_step))
    else:
        await callback.message.answer('Круто, что ты всё такая же классная, как и была. С днем рождения тебя!')

        video_path = BASE_DIR / "video.mp4"
        if video_path.exists():
            try:
                await callback.message.answer_video(video=FSInputFile(video_path), caption="С днем рождения! ❤️")
            except Exception as e:
                logging.error(f"Ошибка видео: {e}")

        await asyncio.sleep(2)
        await callback.message.answer(
            "Но это еще не всё! Я подготовил для тебя квест. За каждое пройденное место ты получишь +50 руб. на подарок и часть секретного QR-кода. Погнали?")
        await state.set_state(QuestStates.quest)
        await send_next_quest(callback.message, state)
    await callback.answer()


async def send_next_quest(message: Message, state: FSMContext):
    data = await state.get_data()
    q_idx = data.get("current_quest", 0)
    if q_idx < len(QUEST_STEPS):
        await message.answer(QUEST_STEPS[q_idx]["question"])
    else:
        balance = data.get("balance", 0)
        await message.answer(
            f"🎉 УРА! Ты прошла весь квест!\n💰 Твой итоговый баланс: {balance} руб.\n\nТеперь соедини все 4 части QR-кода, отсканируй его и узнаешь, где забрать главный подарок!\nС днём Рождения❤️❤️❤️!")


@router.message(QuestStates.quest, F.photo)
async def handle_quest_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    q_idx = data.get("current_quest", 0)
    balance = data.get("balance", 0)
    current_quest = QUEST_STEPS[q_idx]

    user_answer = message.caption.lower() if message.caption else ""

    if current_quest["key"] in user_answer:
        new_balance = balance + REWARD
        new_q_idx = q_idx + 1
        await state.update_data(current_quest=new_q_idx, balance=new_balance)

        qr_name = f"qr_{new_q_idx}.jpg"
        await safely_send_photo(message, qr_name,
                                f"✅ Верно! Это {current_quest['key'].capitalize()}.\n💵 Тебе начислено {REWARD} руб.\n🎁 Вот часть {new_q_idx} твоего QR-кода!")

        await asyncio.sleep(1)
        await send_next_quest(message, state)
    else:
        await message.answer(
            "Хм, кажется это не то место или ты забыла написать название в описании к фото. Попробуй еще раз!")


@router.message(QuestStates.quest)
async def remind_about_photo(message: Message):
    await message.answer(
        "Чтобы я засчитал ответ, пришли именно **фотографию** места и напиши его название в подписи к фото!")


async def main():
    dp.include_router(router)
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот выключен")