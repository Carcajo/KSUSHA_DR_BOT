import asyncio
import logging
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

TOKEN = "8744964208:AAGzxouce3_8KvwLl9g4kS-uF0xNHhvPEr4"
REWARD = 50

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

# --- ДАННЫЕ КВЕСТА ---
QUEST_STEPS = [
    {
        "question": "📍 Задание 1: Место, где мы впервые встретились. Поезжай туда, сделай фото и напиши название этого места в описании!",
        "key": "клуб",
    },
    {
        "question": "📍 Задание 2: Место, где мы с тобой фотографировались первый раз и снимали видосики. Жду фото и название места, которое там рядом (это не банк)!",
        "key": "цирк",
    },
    {
        "question": "📍 Задание 3: В этом магазине ты НЕ купила то самое зеленое платье. Сфоткай витрину и напиши название ПОЛНОСТЬЮ!",
        "key": "sky",
    },
    {
        "question": "📍 Здесь ты любишь покупать булочки, хоть и нечасто, но говоришь, что тут самые вкусные. Жду фото и название заведения!",
        "key": "тьери",
    }
]


# Состояния для бота
class QuestStates(StatesGroup):
    intro = State()
    quest = State()


bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
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
async def cmd_start(message: Message, state: FSMContext):
    # Обнуляем данные пользователя при старте
    await state.update_data(current_quest=0, balance=0)
    await state.set_state(QuestStates.intro)

    step_index = 0
    photo_path = f"images/{STEPS[step_index]['photo']}"
    await message.answer_photo(
        photo=FSInputFile(photo_path),
        caption=STEPS[step_index]["text"],
        reply_markup=get_keyboard(step_index)
    )


@router.callback_query(F.data.startswith("step_"), QuestStates.intro)
async def handle_steps(callback: CallbackQuery, state: FSMContext):
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
        await callback.message.answer('Круто, что ты всё такая же классная, как и была. С днем рождения тебя!')

        video_path = "video.mp4"
        try:
            await callback.message.answer_video(
                video=FSInputFile(video_path),
                caption="С днем рождения! ❤️"
            )
        except Exception:
            pass

        # Начинаем квест
        await asyncio.sleep(2)  # Небольшая пауза для эффекта
        await callback.message.answer(
            "Но это еще не всё! Я подготовил для тебя квест. За каждое пройденное место ты получишь +50 руб. на подарок и часть секретного QR-кода. Погнали?")

        await state.set_state(QuestStates.quest)
        await send_next_quest(callback.message, state)


async def send_next_quest(message: Message, state: FSMContext):
    """Отправляет текущее задание квеста."""
    data = await state.get_data()
    q_idx = data.get("current_quest", 0)

    if q_idx < len(QUEST_STEPS):
        question_text = QUEST_STEPS[q_idx]["question"]
        await message.answer(question_text)
    else:
        # Полное завершение квеста
        balance = data.get("balance", 0)
        await message.answer(
            f"🎉 УРА! Ты прошла весь квест!\n💰 Твой итоговый баланс: {balance} руб.\n\nТеперь соедини все 4 части QR-кода, которые я прислал, отсканируй его и узнаешь, где забрать главный подарок!\nС днём Рождения❤️❤️❤️!")


@router.message(QuestStates.quest, F.photo)
async def handle_quest_answer(message: Message, state: FSMContext):
    """Проверка фото и названия места."""
    data = await state.get_data()
    q_idx = data.get("current_quest", 0)
    balance = data.get("balance", 0)

    current_quest = QUEST_STEPS[q_idx]

    # Проверяем, есть ли в описании к фото ключевое слово
    user_answer = message.caption.lower() if message.caption else ""

    if current_quest["key"] in user_answer:
        # Правильно!
        new_balance = balance + REWARD
        new_q_idx = q_idx + 1
        await state.update_data(current_quest=new_q_idx, balance=new_balance)

        # Отправляем часть QR-кода
        qr_path = f"images/qr_{new_q_idx}.jpg"
        await message.answer_photo(
            photo=FSInputFile(qr_path),
            caption=f"✅ Верно! Это {current_quest['key'].capitalize()}.\n💵 Тебе начислено {REWARD} руб.\n🎁 Вот часть {new_q_idx} твоего QR-кода!"
        )

        # Ждем немного и шлем следующее задание
        await asyncio.sleep(1)
        await send_next_quest(message, state)
    else:
        await message.answer(
            "Хм, кажется это не то место или ты забыла написать название в описании к фото. Попробуй еще раз!")


@router.message(QuestStates.quest)
async def remind_about_photo(message: Message):
    """Если прислала просто текст без фото."""
    await message.answer(
        "Чтобы я засчитал ответ, пришли именно **фотографию** места и напиши его название в подписи к фото!")


async def main():
    dp.include_router(router)
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")