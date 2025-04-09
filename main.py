import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
from datetime import datetime
import calendar

# Получаем токен из переменных окружения
API_TOKEN = os.getenv("BOT_TOKEN")

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Словарь для учета расходов
expenses = {}

# Словарь для учета расходов по дням
daily_expenses = {}

# Генерация отчета по расходам
def generate_report():
    report_text = "Отчёт по расходам:\n----------------------------\n"
    total = 0
    for category, amount in expenses.items():
        report_text += f"{category}: {amount} €\n"
        total += amount
    report_text += f"\nОбщая сумма: {total} €"
    return report_text

# Функция для проверки, если расходы на день превышают 20 €
def check_daily_spending(user_id):
    today = datetime.today().strftime('%Y-%m-%d')
    if user_id in daily_expenses:
        daily_total = sum(daily_expenses[user_id].values())
        if daily_total > 20:
            return "Эй, полегче, транжира, я тут пытаюсь сэкономить деньги!"
    return None

# Функция для подсчета минимальных расходов в конце месяца
def congratulate_best_saver():
    min_spender = None
    min_spent = float('inf')

    # Считаем расходы всех пользователей за месяц
    for user_id, daily_data in daily_expenses.items():
        monthly_total = sum(daily_data.values())
        if monthly_total < min_spent:
            min_spent = monthly_total
            min_spender = user_id

    # Если найден победитель, поздравляем его
    if min_spender is not None:
        bot.send_message(min_spender, "Поздравляю! Ты — король экономии! Ты потратил меньше всех в этом месяце!")

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я твой бот для отслеживания расходов.\nИспользуй команду /report, чтобы получить отчет.")

# Обработчик команды /report
@dp.message_handler(commands=['report'])
async def send_report(message: types.Message):
    report_text = generate_report()
    await message.reply(report_text, parse_mode=ParseMode.MARKDOWN)

# Обработчик для получения текстовых сообщений и записи расходов
@dp.message_handler()
async def record_expenses(message: types.Message):
    try:
        # Проверяем, что сообщение подходит по формату "категория сумма"
        text = message.text.split()
        category = text[0]
        amount = float(text[1])
        
        user_id = message.from_user.id
        today = datetime.today().strftime('%Y-%m-%d')

        # Проверяем, если это первый расход за день, создаем запись
        if user_id not in daily_expenses:
            daily_expenses[user_id] = {}

        if category in expenses:
            expenses[category] += amount
        else:
            expenses[category] = amount

        # Добавляем расход в словарь для ежедневных трат
        if today not in daily_expenses[user_id]:
            daily_expenses[user_id][today] = 0
        daily_expenses[user_id][today] += amount
        
        # Проверка превышения лимита по тратам за день
        warning = check_daily_spending(user_id)
        if warning:
            await message.reply(warning)

        await message.reply(f"Добавлено {amount} € в категорию {category}.")
    except Exception as e:
        await message.reply("Ошибка! Пожалуйста, используйте формат: 'Категория Сумма'. Пример: 'Еда 20'.")

# Функция для запуска в конце месяца
async def end_of_month_routine():
    # Проверяем в конце месяца (можно запускать раз в день или с задержкой)
    current_date = datetime.today()
    if current_date.day == calendar.monthrange(current_date.year, current_date.month)[1]:
        congratulate_best_saver()

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
