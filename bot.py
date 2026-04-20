import telebot
from config import BOT_TOKEN
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import search_movie, smart_recommendation

bot = telebot.TeleBot(BOT_TOKEN)

user_history = {}
last_movie = {}


def track_user(user_id, genre):
    user_history.setdefault(user_id, {})
    user_history[user_id][genre] = user_history[user_id].get(genre, 0) + 1


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🎬 Send me a movie name!")


@bot.message_handler(func=lambda msg: True)
def handle_message(message):
    try:
        data = search_movie(message.text)

        if not data or data.get("Response") == "False":
            bot.reply_to(message, "❌ Movie not found")
            return

        last_movie[message.from_user.id] = data['Title']

        genres = data['Genre'].split(", ")

        markup = InlineKeyboardMarkup()
        for g in genres:
            markup.add(InlineKeyboardButton(g, callback_data=f"genre:{g}"))

        msg = f"""
🎬 {data['Title']} ({data['Year']})
⭐ IMDb: {data['imdbRating']}
🎭 {data['Genre']}
📝 {data['Plot']}
"""

        bot.send_message(message.chat.id, msg, reply_markup=markup)

    except Exception as e:
        print("BOT ERROR:", e)
        bot.reply_to(message, "⚠️ Something went wrong. Try again.")


@bot.callback_query_handler(func=lambda call: call.data.startswith("genre:"))
def handle_genre(call):
    try:
        bot.answer_callback_query(call.id)

        user_id = call.from_user.id
        genre = call.data.split(":")[1]

        track_user(user_id, genre)

        movie = last_movie.get(user_id)

        if not movie:
            bot.send_message(call.message.chat.id, "❌ Search first")
            return

        movies = smart_recommendation(user_id, movie, genre)

        if not movies:
            bot.send_message(call.message.chat.id, "⚠️ No recommendations found")
            return

        for m in movies:
            bot.send_photo(
                call.message.chat.id,
                m['poster'],
                caption=f"🎬 {m['title']}\n⭐ {m['rating']}"
            )

    except Exception as e:
        print("CALLBACK ERROR:", e)
        bot.send_message(call.message.chat.id, "⚠️ Error loading recommendations")


# 🔥 NEVER STOP BOT
bot.polling(non_stop=True, interval=0)