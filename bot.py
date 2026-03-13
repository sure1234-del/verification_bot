import json
import os
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8680097194:AAF7_crZONNEZ7WhjmGg4nZq4HOaJ3rXVsk"
ADMIN_ID = 7209486623

BACKUP_CHANNEL = "https://t.me/uoscli"

DB_FILE = "users.json"

waiting_message = {}

def load_users():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE,"r") as f:
        return json.load(f)

def save_users(data):
    with open(DB_FILE,"w") as f:
        json.dump(data,f,indent=4)

users = load_users()

# ---------- START ----------

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):

    button = KeyboardButton("Verify Phone 📱",request_contact=True)

    keyboard = [
        [button],
        ["Join Backup Channel 📢"],
        ["My Courses 📚","Available Courses 🧭"],
        ["Contact Professor 🎓"]
    ]

    markup = ReplyKeyboardMarkup(keyboard,resize_keyboard=True)

    await update.message.reply_text(
        "👋 Welcome to Course Verification System\n\n"
        "📌 Steps to access courses:\n"
        "1️⃣ Join backup channel\n"
        "2️⃣ Verify phone number\n"
        "3️⃣ Wait for approval\n\n"
        "Your learning journey begins here 🚀",
        reply_markup=markup
    )

# ---------- PHONE VERIFY ----------

async def contact_handler(update:Update,context:ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user
    phone = update.message.contact.phone_number

    if not phone.startswith("+91") and not phone.startswith("91"):
        await update.message.reply_text("❌ Only Indian numbers allowed")
        return

    users[str(user.id)] = {
        "name":user.first_name,
        "username":user.username,
        "phone":phone,
        "verified":False,
        "courses":[]
    }

    save_users(users)

    msg = f"""
📩 NEW VERIFICATION REQUEST

👤 Name: {user.first_name}
🔗 Username: @{user.username}
🆔 ID: {user.id}
📱 Phone: {phone}

Approve:
/approve {user.id}
"""

    await context.bot.send_message(ADMIN_ID,msg)

    await update.message.reply_text(
        "✅ Phone received.\nVerification pending from Professor 🎓"
    )

# ---------- MENU ----------

async def menu(update:Update,context:ContextTypes.DEFAULT_TYPE):

    text = update.message.text
    user = update.message.from_user.id

    if text=="Join Backup Channel 📢":
        await update.message.reply_text(
            f"📢 Join mandatory backup channel first:\n{BACKUP_CHANNEL}"
        )

    elif text=="Available Courses 🧭":
        await update.message.reply_text(
            f"📚 Available Courses\n\nJoin info channel:\n{BACKUP_CHANNEL}"
        )

    elif text=="My Courses 📚":

        uid=str(user)

        if uid not in users:
            await update.message.reply_text("❌ No course found")
            return

        courses = users[uid]["courses"]

        if not courses:
            await update.message.reply_text("📭 No course assigned yet")
            return

        text="🎓 Your Courses:\n\n"

        for c in courses:
            text+=f"📘 {c}\n"

        await update.message.reply_text(text)

    elif text=="Contact Professor 🎓":

        waiting_message[user]=True

        await update.message.reply_text(
            "✉️ Drop a message here 👇\nProfessor will reply soon."
        )

    else:

        if user in waiting_message:

            await context.bot.send_message(
                ADMIN_ID,
                f"📩 Message for Professor\n\nUser ID:{user}\n\n{update.message.text}"
            )

            await update.message.reply_text(
                "✅ Message delivered to Professor 🎓"
            )

            waiting_message.pop(user)

# ---------- APPROVE ----------

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.from_user.id != ADMIN_ID:
        return

    if len(context.args) == 0:
        await update.message.reply_text("Usage: /approve USER_ID")
        return

    user_id = context.args[0]

    if user_id not in users:
        await update.message.reply_text("User not found")
        return

    users[user_id]["verified"] = True

    save_users(users)

    await context.bot.send_message(
        chat_id=int(user_id),
        text="🎉 Verification Approved\nProfessor will send your course link shortly."
    )

    await update.message.reply_text("✅ User approved successfully")

# ---------- SEND LINK ----------

async def sendlink(update:Update,context:ContextTypes.DEFAULT_TYPE):

    if update.message.from_user.id!=ADMIN_ID:
        return

    user=context.args[0]
    link=context.args[1]

    await context.bot.send_message(
        int(user),
        f"🎓 Course Access Link:\n{link}"
    )

# ---------- ADD COURSE ----------

async def addcourse(update:Update,context:ContextTypes.DEFAULT_TYPE):

    if update.message.from_user.id!=ADMIN_ID:
        return

    user=context.args[0]
    course=" ".join(context.args[1:])

    users[user]["courses"].append(course)

    save_users(users)

    await update.message.reply_text("✅ Course added")

# ---------- USERS ----------

async def users_list(update:Update,context:ContextTypes.DEFAULT_TYPE):

    if update.message.from_user.id!=ADMIN_ID:
        return

    text="👥 Students\n\n"

    for uid in users:
        text+=f"{users[uid]['name']} | {users[uid]['phone']}\n"

    await update.message.reply_text(text)

# ---------- STATS ----------

async def stats(update:Update,context:ContextTypes.DEFAULT_TYPE):

    if update.message.from_user.id!=ADMIN_ID:
        return

    total=len(users)

    verified=0

    for u in users:
        if users[u]["verified"]:
            verified+=1

    await update.message.reply_text(
        f"📊 Stats\n\nUsers:{total}\nVerified:{verified}"
    )

# ---------- BROADCAST ----------

async def broadcast(update:Update,context:ContextTypes.DEFAULT_TYPE):

    if update.message.from_user.id!=ADMIN_ID:
        return

    text=" ".join(context.args)

    for uid in users:
        try:
            await context.bot.send_message(uid,text)
        except:
            pass

# ---------- ADMIN PANEL ----------

async def panel(update:Update,context:ContextTypes.DEFAULT_TYPE):

    if update.message.from_user.id!=ADMIN_ID:
        return

    await update.message.reply_text(
"""
🎓 Professor Panel

/approve USER_ID
/sendlink USER_ID LINK
/addcourse USER_ID COURSE

/users
/stats
/broadcast MESSAGE
/reject USER_ID
/remove USER_ID
/reply USER_ID MESSAGE
"""
)

# ---------- APP ----------

app=ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start",start))
app.add_handler(CommandHandler("approve",approve))
app.add_handler(CommandHandler("sendlink",sendlink))
app.add_handler(CommandHandler("addcourse",addcourse))
app.add_handler(CommandHandler("users",users_list))
app.add_handler(CommandHandler("stats",stats))
app.add_handler(CommandHandler("broadcast",broadcast))
app.add_handler(CommandHandler("panel",panel))

app.add_handler(MessageHandler(filters.CONTACT,contact_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,menu))

print("BOT RUNNING...")

app.run_polling()