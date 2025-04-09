
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

expenses = {}

def start(update, context):
    update.message.reply_text("Привет! Я твой бот для учёта расходов. Напиши 'Еда 20', чтобы зарегистрировать расход.")

def track_expense(update, context):
    message = update.message.text
    user = update.message.from_user.username

    try:
        category, amount = message.split()
        amount = float(amount)

        if user not in expenses:
            expenses[user] = {}

        if category not in expenses[user]:
            expenses[user][category] = 0

        expenses[user][category] += amount
        update.message.reply_text(f"Добавлен расход: {category} - {amount} от {user}")
    except ValueError:
        update.message.reply_text("Неверный формат. Пример: 'Еда 20'")

def report(update, context):
    report_text = "Отчёт по расходам:
"
    for user, categories in expenses.items():
        report_text += f"
{user}:
"
        for category, amount in categories.items():
            report_text += f"{category}: {amount} евро
"
    update.message.reply_text(report_text)

def main():
    token = 'YOUR_BOT_TOKEN'
    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('report', report))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, track_expense))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
