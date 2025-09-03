import telebot, random, re, time, requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import os

# ✅ Load Token from .env
load_dotenv()
TOKEN = "8223378978:AAGYcylIUyqeST6_GLB9PE643CSNJmpf7hw"
bot = telebot.TeleBot(TOKEN)

# ✅ Luhn Algorithm
def luhn(card):
    nums = [int(x) for x in card]
    return (sum(nums[-1::-2]) + sum(sum(divmod(2 * x, 10)) for x in nums[-2::-2])) % 10 == 0

# ✅ Generate credit card number
def generate_card(bin_format):
    bin_format = bin_format.lower()
    if len(bin_format) < 16:
        bin_format += "x" * (16 - len(bin_format))
    else:
        bin_format = bin_format[:16]
    while True:
        cc = ''.join(str(random.randint(0, 9)) if x == 'x' else x for x in bin_format)
        if luhn(cc):
            return cc

# ✅ Generate card info block
def generate_output(bin_input, username):
    parts = bin_input.split("|")
    bin_format = parts[0] if len(parts) > 0 else ""
    mm_input = parts[1] if len(parts) > 1 and parts[1] != "xx" else None
    yy_input = parts[2] if len(parts) > 2 and parts[2] != "xxxx" else None
    cvv_input = parts[3] if len(parts) > 3 and parts[3] != "xxx" else None

    bin_clean = re.sub(r"[^\d]", "", bin_format)[:6]

    if not bin_clean.isdigit() or len(bin_clean) < 6:
        return f"❌ Invalid BIN provided.\n\nExample:\n<code>/gen 545231xxxxxxxxxx|03|27|xxx</code>"

    scheme = "MASTERCARD" if bin_clean.startswith("5") else "VISA" if bin_clean.startswith("4") else "UNKNOWN"
    ctype = "DEBIT" if bin_clean.startswith("5") else "CREDIT" if bin_clean.startswith("4") else "UNKNOWN"

    cards = []
    start = time.time()
    for _ in range(10):
        cc = generate_card(bin_format)
        mm = mm_input if mm_input else str(random.randint(1, 12)).zfill(2)
        yy_full = yy_input if yy_input else str(random.randint(2026, 2032))
        yy = yy_full[-2:]
        cvv = cvv_input if cvv_input else str(random.randint(100, 999))
        cards.append(f"<code>{cc}|{mm}|{yy}|{cvv}</code>")
    elapsed = round(time.time() - start, 3)

    card_lines = "\n".join(cards)

    text = f"""<b>───────────────</b>
<b>Info</b> - ↯ {scheme} - {ctype}
<b>───────────────</b>
<b>Bin</b> - ↯ {bin_clean} |<b>Time</b> - ↯ {elapsed}s
<b>Input</b> - ↯ <code>{bin_input}</code>
<b>───────────────</b>
{card_lines}
<b>───────────────</b>
<b>Requested By</b> - ↯ @{username} [Free]
"""
    return text

# ✅ /start
@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = str(message.from_user.id)
    with open("users.txt", "a+") as f:
        f.seek(0)
        if user_id not in f.read().splitlines():
            f.write(user_id + "\n")

    text = (
        "🤖 Bot Status: Active ✅\n\n"
        "📢 For announcements and updates, join us 👉 [here](https://t.me/TrickHubBD)\n\n"
        "💡 Tip: To use 𝒁𝒆𝒓𝒐𝑶𝒏𝑮𝒆𝒏 ∞ in your group, make sure I'm added as admin."
    )
    bot.reply_to(message, text, parse_mode="Markdown")

# ✅ /gen
@bot.message_handler(commands=['gen'])
def gen_handler(message):
    parts = message.text.split(" ", 1)
    if len(parts) < 2:
        return bot.reply_to(message, "⚠️ Example:\n<code>/gen 545231xxxxxxxxxx|03|27|xxx</code>", parse_mode="HTML")

    bin_input = parts[1].strip()
    username = message.from_user.username or "anonymous"
    text = generate_output(bin_input, username)

    btn = InlineKeyboardMarkup()
    btn.add(InlineKeyboardButton("Re-Generate ♻️", callback_data=f"again|{bin_input}"))
    bot.reply_to(message, text, parse_mode="HTML", reply_markup=btn)

@bot.callback_query_handler(func=lambda call: call.data.startswith("again|"))
def again_handler(call):
    bin_input = call.data.split("|", 1)[1]
    username = call.from_user.username or "anonymous"
    text = generate_output(bin_input, username)

    btn = InlineKeyboardMarkup()
    btn.add(InlineKeyboardButton("Re-Generate ♻️", callback_data=f"again|{bin_input}"))

    try:
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=text,
                              parse_mode="HTML",
                              reply_markup=btn)
    except:
        bot.send_message(call.message.chat.id, text, parse_mode="HTML", reply_markup=btn)

# ✅ /ask
@bot.message_handler(commands=['ask'])
def ask_handler(message):
    parts = message.text.split(" ", 1)
    if len(parts) < 2:
        return bot.reply_to(message, "❓ Usage: `/ask your question`", parse_mode="Markdown")

    prompt = parts[1]
    try:
        res = requests.get(f"https://gpt-3-5.apis-bj-devs.workers.dev/?prompt={prompt}")
        if res.status_code == 200:
            data = res.json()
            if data.get("status") and data.get("reply"):
                reply = data["reply"]
                bot.reply_to(message, f"*{reply}*", parse_mode="Markdown")
            else:
                bot.reply_to(message, "❌ Couldn't parse reply from API.", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ GPT API failed to respond.", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: `{e}`", parse_mode="Markdown")

# ✅ /fake
@bot.message_handler(commands=['fake'])
def fake_address_handler(message):
    parts = message.text.split(" ", 1)
    if len(parts) < 2:
        return bot.reply_to(message, "⚠️ Example:\n`/fake us`", parse_mode="Markdown")

    country_code = parts[1].strip().lower()
    supported = [
        "dz","ar","au","bh","bd","be","br","kh","ca","co","dk","eg",
        "fi","fr","de","in","it","jp","kz","my","mx","ma","nz","pa",
        "pk","pe","pl","qa","sa","sg","es","se","ch","th","tr","uk",
        "us"
    ]

    if country_code not in supported:
        return bot.reply_to(message, "❌ This country is not supported or invalid.", parse_mode="Markdown")

    url = f"https://randomuser.me/api/?nat={country_code}"
    try:
        res = requests.get(url).json()
        user = res['results'][0]

        name = f"{user['name']['first']} {user['name']['last']}"
        addr = user['location']
        full_address = f"{addr['street']['number']} {addr['street']['name']}"
        city = addr['city']
        state = addr['state']
        zip_code = addr['postcode']
        country = addr['country']

        msg = f"""📦 *Fake Address Info*

👤 *Name:* `{name}`
🏠 *Address:* `{full_address}`
🏙️ *City:* `{city}`
🗺️ *State:* `{state}`
📮 *ZIP:* `{zip_code}`
🌐 *Country:* `{country.upper()}`"""

        bot.reply_to(message, msg, parse_mode="Markdown")
    except Exception:
        bot.reply_to(message, "❌ Something went wrong. Try again later.", parse_mode="Markdown")

# ✅ /country
@bot.message_handler(commands=['country'])
def country_command(message):
    msg = """🌍 *Supported Countries:*
🇺🇸 United States (US)
🇧🇩 Bangladesh (BD)
🇮🇳 India (IN)
🇬🇧 United Kingdom (UK)
... and more (see code)
"""
    bot.reply_to(message, msg, parse_mode="Markdown")

# ✅ /broadcast (Owner only)
OWNER_ID = 6321618547  # Replace with your Telegram ID

@bot.message_handler(commands=['broadcast'])
def broadcast_handler(message):
    if message.from_user.id != OWNER_ID:
        return bot.reply_to(message, "🚫 You are not authorized.")

    try:
        _, text = message.text.split(" ", 1)
    except:
        return bot.reply_to(message, "⚠️ Usage:\n`/broadcast Your message`", parse_mode="Markdown")

    bot.reply_to(message, "📢 Sending broadcast...")

    try:
        with open("users.txt", "r") as f:
            users = f.read().splitlines()
    except FileNotFoundError:
        return bot.send_message(message.chat.id, "❌ No users found.")

    sent, failed = 0, 0
    for uid in users:
        try:
            bot.send_message(uid, f"📢 *Broadcast:*\n\n{text}", parse_mode="Markdown")
            sent += 1
            time.sleep(0.1)
        except:
            failed += 1
            continue

    bot.send_message(message.chat.id, f"✅ Done.\n🟢 Sent: `{sent}`\n🔴 Failed: `{failed}`", parse_mode="Markdown")

print("🤖 Bot is running...")
bot.polling()
