#bot.py
import telebot
from config import BOT_TOKEN, DEVELOPER_ID
from utils import search_movie

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🎬 Send me a movie name!")

@bot.message_handler(func=lambda msg: True)
def handle_message(message):
    movie_name = message.text
    
    data = search_movie(movie_name)

    if data.get("Response") == "False":
        bot.reply_to(message, "❌ Movie not found")
        return

    msg = f"""

🎬 {data['Title']} ({data['Year']})

⭐ IMDb: {data['imdbRating']}
🎭 Genre: {data['Genre']}
🎬 Director: {data['Director']}
👥 Cast: {data['Actors']}

📝 {data['Plot']}
"""

    bot.reply_to(message, msg)


# @bot.message_handler(commands=['broadcast'])
# def broadcast(message):
#     if message.from_user.id != DEVELOPER_ID:
#         return

#     text = message.text.replace('/broadcast ', '')

#     for user in user_db:
#         try:
#             bot.send_message(user, text)
#         except:
#             pass

bot.polling()