import time
import json
import telebot
from telebot import types

# বট টোকেন (আপনার বটের টোকেন দিয়ে প্রতিস্থাপন করুন)
BOT_TOKEN = "8223378978:AAGYcylIUyqeST6_GLB9PE643CSNJmpf7hw"

# বট ইনস্ট্যান্স তৈরি করা
bot = telebot.TeleBot(BOT_TOKEN)

# ব্যবহারকারীদের ডেটা সংরক্ষণের জন্য (প্রোডাকশনের জন্য ডেটাবেস ব্যবহার করা ভালো)
user_data = {}

# /start কমান্ড হ্যান্ডলার
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    user_data[user_id] = {'step': 0}
    
    welcome_text = """
    🎉 স্বাগতম! আমি একটি টেলিগ্রাম বট।
    
    আপনি নিচের কমান্ডগুলি ব্যবহার করতে পারেন:
    /start - বট শুরু করুন
    /help - সাহায্য পান
    /about - বট সম্পর্কে জানুন
    """
    
    bot.reply_to(message, welcome_text)

# /help কমান্ড হ্যান্ডলার
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
    🤖 সাহায্য:
    
    এই বটটি একটি উদাহরণ। আপনি নিম্নলিখিত কাজগুলি করতে পারেন:
    
    1. টেক্সট মেসেজ পাঠান - বটটি উত্তর দেবে
    2. /start কমান্ড দিয়ে শুরু করুন
    3. /about কমান্ড দিয়ে তথ্য পান
    
    আপনি কোন বিষয়ে সাহায্য চান?
    """
    
    bot.reply_to(message, help_text)

# /about কমান্ড হ্যান্ডলার
@bot.message_handler(commands=['about'])
def send_about(message):
    about_text = """
    ℹ️ বট সম্পর্কে:
    
    এই বটটি Python programming language 
    এবং pyTelegramBotAPI লাইব্রেরি ব্যবহার করে তৈরি করা হয়েছে।
    
    ডেভেলপার: আপনার নাম
    সংস্করণ: 1.0.0
    """
    
    bot.reply_to(message, about_text)

# টেক্সট মেসেজ হ্যান্ডলার
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    user_id = message.from_user.id
    user_message = message.text
    
    # যদি ব্যবহারকারীর ডেটা না থাকে তবে তা যোগ করুন
    if user_id not in user_data:
        user_data[user_id] = {'step': 0}
    
    # সাধারণ উত্তর
    response = f"আপনি লিখেছেন: {user_message}\n\nআমি একটি সাধারণ বট, আরও উন্নত করার প্রয়োজন আছে!"
    
    bot.reply_to(message, response)

# বট চালানো
if __name__ == "__main__":
    print("বট চালু হচ্ছে...")
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"ত্রুটি 발생: {e}")
            time.sleep(15)
