import logging
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)  # убираю логи
logging.getLogger("telegram.ext").setLevel(logging.WARNING)  # убираю логи

# настройка в-драйвера для безголового режима
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# функция /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["Today", "Week"],  # Кнопки
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Q Вибери кнопку для отримання розкладу: ",
                                   reply_markup=reply_markup)

# Функция для получения расписания на один день
async def get_schedule(day_offset: int) -> str:
    target_date = datetime.now() + timedelta(days=day_offset)

    driver.get("https://harmonogramy.dsw.edu.pl/Plany/PlanyGrup/14423")

    # Жду загрузки нужного элемента
    parent_element = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, "gridViewPlanyGrup_DXGroupRowExp0"))
    )

    children = parent_element.find_elements(By.XPATH, "//*[starts-with(@id, 'gridViewPlanyGrup_DXDataRow')]")
    DisplayText = f"**Расписание на {target_date.strftime('%A, %d %B %Y')}**:\n"

    for child in children:
        try:
            time_from_element = child.find_element(By.XPATH, "./td[2][@class='dxgv']").get_attribute("innerText")
            time_to_element = child.find_element(By.XPATH, "./td[3][@class='dxgv']").get_attribute("innerText")
            subject_element = child.find_element(By.XPATH, "./td[5]//a[@class='planLink']").get_attribute("innerText")
            location_element = child.find_element(By.XPATH, "./td[8]//a[@class='planLink']").get_attribute("innerText")
            form_element = child.find_element(By.XPATH, "./td[6][@class='dxgv']").get_attribute("innerText")

            form_element_translated = " - Лекція" if form_element == "Wyk" else " - Цвіченіе" if form_element == "Cw" else " - шось не понятне"

            DisplayText += f"**{subject_element}**{form_element_translated}\n"
            DisplayText += f"**Час занять:** {time_from_element}-{time_to_element}\n"
            DisplayText += f"**Будівля + Зал:** {location_element}\n\n"
        except Exception as e:
            logging.error(f"Error processing child: {e}")

    return DisplayText

# Функция получения расписания на сегодня
async def schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        schedule_text = await get_schedule(0)  # 0 - для текущего дня
        await context.bot.send_message(chat_id=update.effective_chat.id, text=schedule_text, parse_mode='Markdown')
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Ошибка при получении расписания.")
        logging.error(f"Error in schedule function: {e}")

# Функция получения расписания на неделю
async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        all_schedules = ""
        for day_offset in range(7):  # Цикл для 7 дней
            daily_schedule = await get_schedule(day_offset)
            all_schedules += daily_schedule + "\n\n"

        await context.bot.send_message(chat_id=update.effective_chat.id, text=all_schedules, parse_mode='Markdown')
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Ошибка при получении расписания на неделю.")
        logging.error(f"Error in weekly function: {e}")

# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    logging.info(f"Received message: {user_message}")  # логируем полученное сообщение

    if user_message.lower() == "today":
        await schedule(update, context)
    elif user_message.lower() == "week":
        await weekly(update, context)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Будь ласка, виберіть одну з опцій.")

# Основной блок запуска бота
if __name__ == '__main__':
    application = ApplicationBuilder().token('TG_API_BOT)SuDa').build()
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    application.add_handler(CommandHandler('schedule', schedule))
    application.add_handler(CommandHandler('weekly', weekly))  # обработчик команды /weekly
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))  # обработчик текстовых сообщений

    application.run_polling()
