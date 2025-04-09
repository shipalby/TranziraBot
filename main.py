import os
import re
import datetime
import asyncio
from collections import defaultdict
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN not set in environment variables")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

expenses = defaultdict(lambda: defaultdict(float))

@dp.message_handler(lambda message: re.match(r"^\w+\s+\d+(\.\d{1,2})?$", message.text))
async def handle_expense(message: Message):
    try:
        category, amount = message.text.strip().split(maxsplit=1)
        amount = float(amount)
        user = message.from_user.full_name
        expenses[user][category] += amount
        await message.reply(f"Добавлено: {category} — {amount:.2f} € от {user}")
    except Exception as e:
        await message.reply("Ошибка при обработке. Убедись, что формат: Категория Сумма (пример: Еда 20)")

async def send_monthly_report():
    while True:
        now = datetime.datetime.now()
        if now.day == 1 and now.hour == 0 and now.minute == 0:
            if not expenses:
                await asyncio.sleep(60)
                continue

            report_text = "📊 Отчёт по расходам за прошлый месяц:\n\n"
            for user, cats in expenses.items():
                total = sum(cats.values())
                report_text += f"👤 *{user}* — всего: *{total:.2f} €*\n"
                for cat, amt in cats.items():
                    report_text += f"  • {cat}: {amt:.2f} €\n"
                report_text += "\n"

            for chat_id in CHAT_IDS:
                try:
                    await bot.send_message(chat_id, report_text, parse_mode="Markdown")
                except Exception as e:
                    print(f"Ошибка отправки в чат {chat_id}: {e}")

            expenses.clear()
            await asyncio.sleep(60)
        await asyncio.sleep(30)

# 👇 Вставь сюда ID чата-группы, куда бот будет отправлять отчёты
CHAT_IDS = [
    -4629695919  # пример ID, замени на свой
]

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(send_monthly_report())
    executor.start_polling(dp, skip_updates=True)
