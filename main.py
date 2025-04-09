import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import logging
from collections import defaultdict
from datetime import datetime

API_TOKEN = os.getenv("BOT_TOKEN")  # Токен из переменных окружения
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Словарь для хранения расходов пользователей
user_expenses = defaultdict(lambda: defaultdict(float))  # user_expenses[user_id][category] = total_amount

# Команда /start для приветствия
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет, Даник Бог Трат и Арина Богиня Экономки! 👑💰\n"
        "Я помогу отслеживать твои расходы и поддерживать бюджет в порядке!\n"
        "Ты можешь отправить мне расходы в формате: 'Категория сумма' (например: 'Еда 20').\n"
        "Используй /report для отчета и /top_spender для получения самого транжирного покупателя!\n"
        "Поехали! 🚀"
    )

# Команда /report для отображения общей суммы
@dp.message_handler(commands=['report'])
async def cmd_report(message: types.Message):
    user_id = message.from_user.id
    total_spent = sum(user_expenses[user_id].values())  # Общая сумма расходов
    if total_spent == 0:
        await message.answer("📊 Ты ещё не сделал ни одного расхода. Начни тратить! 😉")
    else:
        report = "💸 Твои расходы:\n"
        for category, amount in user_expenses[user_id].items():
            report += f"• {category}: {amount:.2f} €\n"
        report += f"🔹 Общая сумма расходов: {total_spent:.2f} €"
        await message.answer(report)

# Команда /top_spender для вывода самого большого тратила
@dp.message_handler(commands=['top_spender'])
async def cmd_top_spender(message: types.Message):
    top_user = max(user_expenses, key=lambda user: sum(user_expenses[user].values()), default=None)
    if top_user is None:
        await message.answer("🚨 Пока нет данных для подсчета самого транжирного покупателя!")
    else:
        top_amount = sum(user_expenses[top_user].values())
        await message.answer(f"🏆 Самый транжирный покупатель: {top_user} с расходами: {top_amount:.2f} €")

# Обработчик сообщений для добавления расходов
@dp.message_handler()
async def handle_expense(message: types.Message):
    try:
        user_id = message.from_user.id
        text = message.text.strip()

        # Ищем последний пробел, чтобы разделить категорию и сумму
        if text.count(' ') < 1:
            await message.answer("❌ Формат неправильный. Используй: 'Категория сумма'. Например: 'Еда 20'.")
            return

        # Разделяем на категорию и сумму, оставляя категорию целой даже если она состоит из нескольких слов
        *category_parts, amount_str = text.rsplit(' ', 1)
        category = ' '.join(category_parts)
        amount = float(amount_str)

        if amount <= 0:
            await message.answer("❌ Сумма должна быть положительной!")
            return
        
        user_expenses[user_id][category] += amount  # Суммируем расходы по одной категории для пользователя

        # Проверка, если траты больше 20 евро в день
        if amount > 20:
            await message.answer("💸 Э, полегче, транжира! Я тут пытаюсь сэкономить деньги! 😅")

        # Похвала за экономию (если трат меньше всех)
        min_spender = min(user_expenses, key=lambda user: sum(user_expenses[user].values()))
        if user_id == min_spender:
            await message.answer(f"🎉 Ты король экономии, {message.from_user.first_name}!")
        
        await message.answer(f"✅ Расход добавлен: {category} - {amount:.2f} €")

    except ValueError:
        await message.answer("❌ Ошибка! Введите корректные данные: 'Категория сумма'. Например: 'Еда 20'.")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
