import asyncio
import logging
import sys
from datetime import datetime, timedelta

from aiogram.types import FSInputFile

from config import dp, bot, supabase, users_data_repo
from src.keyboards.keyboards import assessment_keyboard_maker
from src.routers.handlers import router

async def send_message_grade(chat_id):
    await bot.send_message(
        chat_id=chat_id,
        text="Оцените качество с на от 1 до 5:"
    )

# Функция для преобразования 'HH:MM' в datetime (на сегодня или завтра)
def parse_time_to_datetime(time_str: str, now: datetime) -> datetime:
    parsed_time = datetime.strptime(time_str, '%H:%M').time()
    target_datetime = datetime.combine(now.date(), parsed_time)
    if target_datetime < now - timedelta(minutes=1):
        target_datetime += timedelta(days=1)
    return target_datetime

async def wait():
    while True:
        try:
            print(1)  # Для дебага
            # Получаем данные из Supabase (предполагаю синхронный вызов; если блокирует, оберни в asyncio.to_thread)
            response = supabase.table("UserData").select("*").execute().data
            print(response)  # Для дебага

            now = datetime.now()  # Текущее время (обновляем каждый цикл)

            for alarm in response:
                # Проверяем наличие полей
                time_sleep_str = alarm.get("time_sleep")
                if time_sleep_str:
                    # Преобразуем строку в datetime
                    try:
                        time_sleep = parse_time_to_datetime(time_sleep_str, now)
                    except ValueError:
                        logging.error(f"Неверный формат time_sleep '{time_sleep_str}' для chat_id {alarm['chat_id']}")
                        continue


                    # Получаем user_data (если нужно; адаптируй, если time_sleep уже в alarm)
                    alarm_time_resp = users_data_repo.get_user_by_chat_id(alarm["chat_id"])
                    user_data = alarm_time_resp.data if hasattr(alarm_time_resp, 'data') else alarm_time_resp

                    # Теперь сравниваем (с окном в 1 минуту)
                    print(now, "time_sleep--->", time_sleep)
                    if now >= time_sleep and now < time_sleep + timedelta(minutes=1):
                        await bot.send_message(
                            chat_id=alarm["chat_id"],
                            text="Доброе утро, кажется тебе пора вставать!\nНе забывай придерживаться здорового режима сна)"
                        )
                        await bot.send_photo(
                            chat_id=alarm["chat_id"],
                            photo=FSInputFile("photo.jpg"),
                            caption="Пожалуйста, оцените качество сна по шкале от 1 до 5, где 1 это самая низкая оценка, а 5 -- самая высокая",
                            reply_markup=assessment_keyboard_maker()
                        )
            await asyncio.sleep(59)  # Проверяем каждую минуту, чтобы не нагружать CPU
        except:
            pass


async def start():
    dp.include_router(router)
    asyncio.create_task(wait())
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(start())
    asyncio.run(wait())
