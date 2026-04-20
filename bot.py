import telebot
from config import BOT_TOKEN
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils import (
    search_movie,
    smart_recommendation
)

bot = telebot.TeleBot(BOT_TOKEN)

# 🔥 USER DATA STORAGE
user_history = {}
last_movie = {}

# ---------------------------
# TRACK USER PREFERENCES
# ---------------------------
def track_user(user_id, genre):
    if user_id not in user_history:
        user_history[user_id] = {}

    if genre not in user_history[user_id]:
        user_history[user_id][genre] = 0

    user_history[user_id][genre] += 1


def get_favorite_genre(user_id):
    if user_id not in user_history:
        return None
    return max(user_history[user_id], key=user_history[user_id].get)


# ---------------------------
# START COMMAND
# ---------------------------
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🎬 Send me a movie name!")


# ---------------------------
# SEARCH MOVIE
# ---------------------------
@bot.message_handler(func=lambda msg: True)
def handle_message(message):
    movie_name = message.text

    data = search_movie(movie_name)

    if data.get("Response") == "False":
        bot.reply_to(message, "❌ Movie not found")
        return

    # 🔥 STORE LAST MOVIE
    last_movie[message.from_user.id] = data['Title']

    genres = data['Genre'].split(", ")

    markup = InlineKeyboardMarkup()
    for genre in genres:
        markup.add(
            InlineKeyboardButton(
                genre,
                callback_data=f"genre:{genre}"
            )
        )

    msg = f"""
🎬 {data['Title']} ({data['Year']})

⭐ IMDb: {data['imdbRating']}
🎭 Genre: {data['Genre']}
🎬 Director: {data['Director']}
👥 Cast: {data['Actors']}

📝 {data['Plot']}
"""

    bot.send_message(message.chat.id, msg, reply_markup=markup)


# ---------------------------
# HANDLE GENRE CLICK
# ---------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("genre:"))
def handle_genre(call):
    bot.answer_callback_query(call.id)

    user_id = call.from_user.id
    genre = call.data.split(":")[1]

    # 🔥 TRACK USER INTEREST
    track_user(user_id, genre)

    movie_name = last_movie.get(user_id)

    if not movie_name:
        bot.send_message(call.message.chat.id, "❌ Search a movie first")
        return

    # 🔥 SMART RECOMMENDATION
    movies = smart_recommendation(user_id, movie_name, genre)

    if not movies:
        bot.send_message(call.message.chat.id, f"❌ No {genre} movies found")
        return

    for m in movies:
        msg = f"""
🎬 {m['title']}
⭐ Rating: {m['rating']}
"""

        bot.send_photo(
            call.message.chat.id,
            m['poster'],
            caption=msg
        )


bot.polling()