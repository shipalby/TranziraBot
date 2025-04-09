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
user_expenses = defaultdict(list)  # user_expenses[user_id] = [(category, amount, date)]

# Команда /start для приветствия
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет, Даник Бог Трат и Арина Богиня Экономки! 👑💰\n"
        "Я помогу отслеживать твои расходы и поддерживать бюджет в порядке!\n"
        "Ты можешь отправить мне расходы в формате: 'Категория сумма' (например: 'Еда 20').\n"
        "Используй /report для отчета, /top_spender для самого транжирного покупателя и /delete_expenses для удаления расходов!\n"
        "Поехали! 🚀"
    )

# Команда /report для отображения общей суммы
@dp.message_handler(commands=['report'])
async def cmd_report(message: types.Message):
    user_id = message.from_user.id
    if not user_expenses[user_id]:
        await message.answer("📊 Ты ещё не сделал ни одного расхода. Начни тратить! 😉")
    else:
        report = "💸 Твои расходы:\n"
        total_spent = 0
        for category, amount, _ in user_expenses[user_id]:
            report += f"• {category}: {amount:.2f} €\n"
            total_spent += amount
        report += f"🔹 Общая сумма расходов: {total_spent:.2f} €"
        await message.answer(report)

# Команда /top_spender для вывода самого большого тратила
@dp.message_handler(commands=['top_spender'])
async def cmd_top_spender(message: types.Message):
    top_user = max(user_expenses, key=lambda user: sum(amount for _, amount, _ in user_expenses[user]), default=None)
    if top_user is None:
        await message.answer("🚨 Пока нет данных для подсчета самого транжирного покупателя!")
    else:
        top_amount = sum(amount for _, amount, _ in user_expenses[top_user])
        await message.answer(f"🏆 Самый транжирный покупатель: {top_user} с расходами: {top_amount:.2f} €")

# Команда /delete_expenses для удаления расходов
@dp.message_handler(commands=['delete_expenses'])
async def cmd_delete_expenses(message: types.Message):
    user_id = message.from_user.id
    if not user_expenses[user_id]:
        await message.answer("❌ У тебя нет расходов для удаления.")
        return
    
    await message.answer(
        "Выбери, что ты хочешь удалить:\n"
        "1️⃣ Последний расход\n"
        "2️⃣ Последние 3 расхода\n"
        "3️⃣ Все расходы за сегодня"
    )

    # Ожидаем выбора пользователя
    await dp.bot.register_message_handler(delete_expense_handler, lambda msg: msg.from_user.id == message.from_user.id)

async def delete_expense_handler(message: types.Message):
    user_id = message.from_user.id
    choice = message.text.strip()

    if choice == '1️⃣ Последний расход':
        if user_expenses[user_id]:
            deleted_expense = user_expenses[user_id].pop()
            await message.answer(f"✅ Удален последний расход: {deleted_expense[0]} - {deleted_expense[1]:.2f} €")
        else:
            await message.answer("❌ У тебя нет расходов для удаления.")
    elif choice == '2️⃣ Последние 3 расхода':
        if len(user_expenses[user_id]) >= 3:
            deleted_expenses = user_expenses[user_id][-3:]
            user_expenses[user_id] = user_expenses[user_id][:-3]
            deleted_report = "\n".join([f"• {cat} - {amt:.2f} €" for cat, amt, _ in deleted_expenses])
            await message.answer(f"✅ Удалены последние 3 расхода:\n{deleted_report}")
        else:
            await message.answer("❌ У тебя меньше 3 расходов для удаления.")
    elif choice == '3️⃣ Все расходы за сегодня':
        today = datetime.today().date()
        expenses_to_delete = [expense for expense in user_expenses[user_id] if expense[2].date() == today]
        if expenses_to_delete:
            user_expenses[user_id] = [expense for expense in user_expenses[user_id] if expense[2].date() != today]
            deleted_report = "\n".join([f"• {cat} - {amt:.2f} €" for cat, amt, _ in expenses_to_delete])
            await message.answer(f"✅ Удалены все расходы за сегодня:\n{deleted_report}")
        else:
            await message.answer("❌ У тебя нет расходов за сегодня для удаления.")
    else:
        await message.answer("❌ Неверный выбор. Пожалуйста, выбери 1, 2 или 3.")

# Обработчик сообщений для добавления расходов
@dp.message_handler()
async def handle_expense(message: types.Message):
    try:
        user_id = message.from_user.id
        text = message.text.strip()

        if text.count(' ') < 1:
            await message.answer("❌ Формат неправильный. Используй: 'Категория сумма'. Например: 'Еда 20'.")
            return

        *category_parts, amount_str = text.rsplit(' ', 1)
        category = ' '.join(category_parts)
        amount = float(amount_str)

        if amount <= 0:
            await message.answer("❌ Сумма должна быть положительной!")
            return

        user_expenses[user_id].append((category, amount, datetime.now()))  # Добавляем расход с датой

        response_message = f"✅ Расход добавлен: {category} - {amount:.2f} €\n"
        
        # Если сумма больше 20, добавляем предупреждение
        if amount > 20:
            response_message += "💸 Э, полегче, транжира! Я тут пытаюсь сэкономить деньги! 😅"
        
        # Похвала за экономию
        min_spender = min(user_expenses, key=lambda user: sum(amount for _, amount, _ in user_expenses[user]))
        if user_id == min_spender:
            response_message += f"🎉 Ты король экономии, {message.from_user.first_name}!"

        # Отправляем сообщение в одном
        await message.answer(response_message)

    except ValueError:
        await message.answer("❌ Ошибка! Введите корректные данные: 'Категория сумма'. Например: 'Еда 20'.")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
