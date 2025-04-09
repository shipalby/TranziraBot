import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
from collections import defaultdict
import datetime

# Получаем токен из переменной окружения
API_TOKEN = os.getenv('BOT_TOKEN')

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Словарь для хранения расходов участников
expenses = defaultdict(lambda: defaultdict(float))

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    welcome_message = (
        "✨ Добро пожаловать, Даник бог трат и Арина богиня экономки! ✨\n"
        "Ты на связи с моим супер-ботом, который поможет тебе отслеживать все твои расходы и сбережения! 💸\n"
        "Будь готов к новым приключениям в мире финансов! 📈\n\n"
        "Что ты хочешь сделать?\n"
        "/help - Узнать, как я могу помочь 💁‍♂️\n"
        "/report - Получить отчет по расходам 📊\n"
        "/top_spender - Узнать, кто потратил больше всех 💰"
    )
    await message.reply(welcome_message)

# Обработчик команды /help
@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    await message.reply(
        "Вот что я могу:\n"
        "/report - Получить отчёт по всем расходам 📊\n"
        "/top_spender - Узнать, кто потратил больше всего 💰\n"
        "Просто отправляй свои расходы в формате: 'Категория сумма' 📝\n"
        "Пример: 'Еда 15.5'\n"
        "Если тратишь больше 20 евро в день, я скажу тебе: 'Э, полегче, транжира!' 😂"
    )

# Обработчик входящих сообщений с расходами
@dp.message_handler(lambda message: len(message.text.split()) == 2)
async def handle_expenses(message: types.Message):
    try:
        category, amount = message.text.split()
        amount = float(amount)
        user_id = message.from_user.id

        # Добавляем расход в словарь
        expenses[user_id][category] += amount

        # Проверка на большие траты
        if amount > 20:
            await message.reply(f"Э, полегче, транжира! 😜 Ты потратил {amount} евро на '{category}' сегодня. Я тут пытаюсь сэкономить деньги! 😅")
        else:
            await message.reply(f"Зарегистрировал твой расход: {category} - {amount} евро 🛍️")

    except ValueError:
        await message.reply("Неправильный формат! Используй формат: 'Категория сумма' 📝")

# Обработчик команды /report
@dp.message_handler(commands=['report'])
async def report(message: types.Message):
    user_id = message.from_user.id
    if expenses[user_id]:
        total_spent = sum(expenses[user_id].values())
        report_message = "Вот твой отчет о расходах за месяц 🧾:\n"
        for category, amount in expenses[user_id].items():
            report_message += f"{category}: {amount} евро\n"
        report_message += f"\nОбщая сумма расходов: {total_spent} евро 💸"
        await message.reply(report_message, parse_mode=ParseMode.MARKDOWN)
    else:
        await message.reply("Ты еще не добавил никаких расходов. Добавь их с помощью команды /help 📝")

# Обработчик команды /top_spender
@dp.message_handler(commands=['top_spender'])
async def top_spender(message: types.Message):
    if not expenses:
        await message.reply("Еще нет данных о расходах. Начни записывать расходы первым! 📝")
        return

    top_spender_user = max(expenses, key=lambda user: sum(expenses[user].values()), default=None)

    if top_spender_user is not None:
        total_spent = sum(expenses[top_spender_user].values())
        await message.reply(f"Топ-транжира этого месяца - пользователь с ID {top_spender_user}! 💸 Он потратил {total_spent} евро на различные категории. Ты слишком щедр! 😱")
    else:
        await message.reply("Не удалось найти данных о тратах.")

# Функция для ежедневного отчета
async def daily_report():
    for user_id, user_expenses in expenses.items():
        total_spent = sum(user_expenses.values())
        if total_spent > 20:
            await bot.send_message(
                user_id,
                f"Эй, {user_id}, ты потратил больше 20 евро сегодня! 💸 Полегче, транжира! 😜"
            )

# Запуск бота
if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
