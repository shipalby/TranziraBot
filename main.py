import os
import telegram
from telegram import ParseMode
from datetime import datetime
import pytz

# Замените 'YOUR_TOKEN' на ваш токен, который вы получили от BotFather
TOKEN = 7831191628:AAGxSoY6-MJp2BudjiVQB5ZFn-OPm456uN0
CHAT_ID = 4629695919  # Укажите ID чата или группы

# Создаем экземпляр бота
bot = telegram.Bot(token=TOKEN)

# Функция для подсчета расходов
def calculate_expenses(messages):
    expenses = {}
    for message in messages:
        if message.text:
            text = message.text.strip()
            if text.startswith("Еда") or text.startswith("Транспорт") or text.startswith("Прочее"):
                category, amount = text.split()
                try:
                    amount = float(amount)
                    if category in expenses:
                        expenses[category] += amount
                    else:
                        expenses[category] = amount
                except ValueError:
                    pass  # Пропустить строки с некорректными данными
    return expenses

# Функция для создания отчета
def create_report(expenses):
    report_text = "Отчёт по расходам:\n"
    for category, total in expenses.items():
        report_text += f"{category}: {total} €\n"
    return report_text

# Функция для отправки отчета в чат
def send_report():
    # Получаем последние 100 сообщений в группе (или чате)
    messages = bot.get_chat_history(CHAT_ID, limit=100)
    expenses = calculate_expenses(messages)
    report_text = create_report(expenses)
    bot.send_message(chat_id=CHAT_ID, text=report_text, parse_mode=ParseMode.MARKDOWN)

# Запуск отправки отчета каждый месяц (например, в последний день месяца)
if __name__ == "__main__":
    # Получаем текущую дату
    now = datetime.now(pytz.timezone("Europe/Moscow"))
    
    # Если сегодня последний день месяца, отправляем отчет
    if now.day == 30 or now.day == 31:
        send_report()
