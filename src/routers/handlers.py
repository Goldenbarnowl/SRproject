import asyncio

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from datetime import datetime, timedelta

from config import bot, users_data_repo
from src.keyboards.keyboards import user_keyboard_button, alarm_keyboard_maker, menu_keyboard_maker, \
    faq_keyboard_maker, faq_answers, faqs
from src.states.states import User

router = Router()

@router.message(CommandStart())
async def start(message: Message, state : FSMContext):
    chat_id = message.chat.id
    try:
        response = users_data_repo.get_user_by_chat_id(chat_id)
        if not response.data:
            users_data_repo.insert_field(chat_id)
    except:
        pass
    await bot.send_animation(
        chat_id=chat_id,
        animation=FSInputFile("bot_gif.mp4")
    )
    await asyncio.sleep(5)
    await bot.send_message(
        chat_id=chat_id,
        text='👋Привет! Я — Айк, твой личный помощник по сну. \nЯ здесь, чтобы помочь тебе улучшить качество отдыха и сделать твои ночи более эффективными.'
    )
    await asyncio.sleep(2)
    await bot.send_message(
        chat_id=message.chat.id,
        text=f'<b>💬Рекомендации по сну:</b> Я анализирую твои привычки, время засыпания, продолжительность сна и другие факторы, чтобы давать персонализированные советы. Например, подскажу, когда лучше ложиться спать, как создать идеальную атмосферу для отдыха или как бороться с бессонницей.\n'
             f'\n<b>📋Сбор статистики по утрам:</b> Каждое утро я буду спрашивать о твоём самочувствии, качестве сна и энергии. На основе этих данных я делаю отчёты, чтобы ты мог отслеживать прогресс. Со временем ты увидишь, что влияет на твой сон — стресс, кофе вечером или спорт.',
        parse_mode="HTML"
    )
    await asyncio.sleep(2)
    await bot.send_message(
        chat_id=chat_id,
        text=f'✅В итоге, со мной ты сможешь спать лучше, просыпаться бодрым и повысить продуктивность днём. Давай начнём?\n'
             f'\nДля начала <b>введи время</b>, в которое хочешь вставать по утрам <b>\n(в формате ЧЧ:ММ)</b>',
        parse_mode="HTML"
    )
    await state.set_state(User.wait_time)

@router.message(User.wait_time, F.text.regexp(r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"))
async def set_alarm(message: Message, state: FSMContext):
    time_str = message.text
    dt = datetime.strptime(time_str, "%H:%M")
    new_dt = dt - timedelta(hours=8)
    users_data_repo.update_field(message.chat.id, {"time_sleep":dt.strftime("%H:%M"), "time_wake_up": new_dt.strftime("%H:%M")})
    await bot.send_message(
        chat_id=message.chat.id,
        text=f'Ага, я понял. Для здорового сна необходимо 8 часов, а значит тебе желательно ложиться в {new_dt.strftime("%H:%M")}, но если не получается, можешь выбрать другое время и сам следовать режиму!\n'
             f'Не забывай про рекомендации, они весьма полезны, ты можешь вызвать их список с помощью кнопки внизу, или написав "Рекомендации💬"!',
        reply_markup=menu_keyboard_maker()
    )
    await state.set_state(User.menu)

@router.message(User.wait_time)
async def not_correct_time(message: Message, state: FSMContext):
    await bot.send_message(
        chat_id=message.chat.id,
        text='Неверно указано время! Напиши мне время в формате ЧЧ:ММ, например 22:00'
    )

@router.message(F.text == user_keyboard_button["recomend"])
async def recom(message: Message):
    await bot.send_message(
        chat_id=message.chat.id,
        text=f'Boт список рекомендаций\n(нажми чтобы читать):',
        reply_markup=faq_keyboard_maker()
    )

@router.callback_query(User.menu, F.data.in_(faqs.keys()))
async def answers(callback_query: CallbackQuery, state: FSMContext):
    await bot.send_message(
        chat_id=callback_query.from_user.id,
        text=faq_answers[callback_query.data]
    )


@router.message(F.text == user_keyboard_button["new_alarm"])
async def new_alarm(message: Message, state: FSMContext):
    await bot.send_message(
        chat_id=message.chat.id,
        text="Во сколько ты хочешь вставать по утрам? (в формате ЧЧ:ММ)"
    )
    await state.set_state(User.wait_time)


