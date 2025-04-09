import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
import logging
from collections import defaultdict
from datetime import datetime

API_TOKEN = os.getenv("BOT_TOKEN")  # Токен из переменных окружения
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Словарь для хранения расходов пользователей
user_expenses = defaultdict(lambda: defaultdict(int))  # user_expenses[user_id][category] = amount

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
    await message.answer(f"💸 Общая сумма расходов: {total_spent} €")

# Команда /top_spender для вывода самого большого тратила
@dp.message_handler(commands=['top_spender'])
async def cmd_top_spender(message: types.Message):
    top_user = max(user_expenses, key=lambda user: sum(user_expenses[user].values()), default=None)
    if top_user is None:
        await message.answer("🚨 Пока нет данных для подсчета самого транжирного покупателя!")
    else:
        top_amount = sum(user_expenses[top_user].values())
        await message.answer(f"🏆 Самый транжирный покупатель: {top_user} с расходами: {top_amount} €")

# Обработчик сообщений для добавления расходов
@dp.message_handler()
async def handle_expense(message: types.Message):
    try:
        user_id = message.from_user.id
        text = message.text.strip().split()
        if len(text) != 2:
            await message.answer("❌ Формат неправильный. Используй: 'Категория сумма'. Например: 'Еда 20'.")
            return
        
        category = text[0]  # Категория может быть любым текстом
        amount = float(text[1])  # Сумма расхода
        
        if amount <= 0:
            await message.answer("❌ Сумма должна быть положительной!")
            return
        
        user_expenses[user_id][category] += amount  # Добавляем расход для пользователя

        # Проверка, если траты больше 20 евро в день
        if amount > 20:
            await message.answer("💸 Э, полегче, транжира! Я тут пытаюсь сэкономить деньги! 😅")

        # Похвала за экономию (если трат меньше всех)
        min_spender = min(user_expenses, key=lambda user: sum(user_expenses[user].values()))
        if user_id == min_spender:
            await message.answer(f"🎉 Ты король экономии, {message.from_user.first_name}!")
        
        await message.answer(f"✅ Расход добавлен: {category} - {amount} €")

    except ValueError:
        await message.answer("❌ Ошибка! Введите корректные данные: 'Категория сумма'. Например: 'Еда 20'.")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
