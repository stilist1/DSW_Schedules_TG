# Telegram Schedule Bot

This Telegram bot retrieves and sends daily and weekly schedules from the specified website using Selenium. The bot can handle user interactions through inline commands and replies, making it easy to access schedules.

## Features

- Fetches today's schedule with a `/schedule` command.
- Fetches the weekly schedule with a `/weekly` command.
- Interactive buttons for selecting the schedule type.
- Headless browser setup with Selenium for web scraping.

## Prerequisites

Before running the bot, ensure you have the following installed:

- Python 3.7 or higher
- Pip (Python package manager)
- A Telegram bot token (create a bot using [BotFather](https://core.telegram.org/bots#botfather))

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your_username/telegram_schedule_bot.git
   cd telegram_schedule_bot
