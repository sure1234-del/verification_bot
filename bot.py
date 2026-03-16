import json
import os
from telegram import *
from telegram.ext import *

BOT_TOKEN = "8680097194:AAF7_crZONNEZ7WhjmGg4nZq4HOaJ3rXVsk"
PROFESSOR_ID = 7209486623

BACKUP_CHANNEL = "https://t.me/uoscli"
AVAILABLE_COURSES = "https://t.me/uoscli"

users = {}
courses = {}

if os.path.exists("users.json"):
    with open("users.json") as f:
        users=json.load(f)

if os.path.exists("courses.json"):
    with open("courses.json") as f:
        courses=json.load(f)

def save_users():
    with open("users.json","w") as f:
        json.dump(users,f,indent=4)

def save_courses():
    with open("courses.json","w") as f:
        json.dump(courses,f,indent=4)

# ---------- START ----------

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):

    keyboard = [
        ["📱 Verify Phone"]
    ]

    reply = ReplyKeyboardMarkup(keyboard,resize_keyboard=True)

    await update.message.reply_text(
        "Welcome to Professor Learning System\n\n"
        "First verify your phone.",
        reply_markup=reply
    )

# ---------- PHONE VERIFY ----------

async def verify(update:Update,context:ContextTypes.DEFAULT_TYPE):

    button = KeyboardButton(
        "Share Phone Number",
        request_contact=True
    )

    keyboard = ReplyKeyboardMarkup([[button]],resize_keyboard=True)

    await update.message.reply_text(
        "Share phone number to verify",
        reply_markup=keyboard
    )

# ---------- PHONE RECEIVED ----------

async def phone(update:Update,context:ContextTypes.DEFAULT_TYPE):

    user=update.message.from_user
    phone=update.message.contact.phone_number

    users[str(user.id)] = {
        "name":user.first_name,
        "username":user.username,
        "phone":phone,
        "verified":True,
        "courses":[]
    }

    save_users()

    await context.bot.send_message(
        PROFESSOR_ID,
        f"User Verified\n\n"
        f"Name:{user.first_name}\n"
        f"ID:{user.id}\n"
        f"Phone:{phone}"
    )

    keyboard=[["📢 Join Backup Channel"]]

    await update.message.reply_text(
        "Phone verified\nNow join backup channel",
        reply_markup=ReplyKeyboardMarkup(keyboard,resize_keyboard=True)
    )

# ---------- BACKUP JOIN ----------

async def backup(update:Update,context:ContextTypes.DEFAULT_TYPE):

    keyboard=[
        ["📚 My Courses","📘 Available Courses"],
        ["💳 Payment","🎓 Contact Professor"]
    ]

    await update.message.reply_text(
        f"Join backup channel first\n{BACKUP_CHANNEL}",
        reply_markup=ReplyKeyboardMarkup(keyboard,resize_keyboard=True)
    )

# ---------- MENU ----------

async def menu(update:Update,context:ContextTypes.DEFAULT_TYPE):

    text=update.message.text

    if text=="📱 Verify Phone":
        await verify(update,context)

    elif text=="📢 Join Backup Channel":
        await backup(update,context)

    elif text=="📘 Available Courses":

        await update.message.reply_text(
            f"Available courses\n{AVAILABLE_COURSES}"
        )

    elif text=="📚 My Courses":

        uid=str(update.message.from_user.id)

        if uid not in users:
            await update.message.reply_text("No courses")
            return

        clist=users[uid]["courses"]

        if not clist:
            await update.message.reply_text("No course assigned")
            return

        buttons=[]

        for c in clist:
            if c in courses:
                buttons.append([InlineKeyboardButton(c,url=courses[c])])

        await update.message.reply_text(
            "Your Courses",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif text=="💳 Payment":

        context.user_data["payment"]=True

        await update.message.reply_text(
            "Payment Methods\n\n"
            "Amazon Gift Card\n"
            "PhonePe Gift Card\n\n"
            "Send screenshot / code here"
        )

    elif text=="🎓 Contact Professor":

        context.user_data["contact"]=True

        await update.message.reply_text("Send message")

# ---------- USER MESSAGE ----------

async def user_message(update:Update,context:ContextTypes.DEFAULT_TYPE):

    user=update.message.from_user

    if context.user_data.get("payment"):

        await context.bot.send_message(
            PROFESSOR_ID,
            f"Payment from\n"
            f"{user.first_name}\n"
            f"ID:{user.id}"
        )

        await update.message.copy(PROFESSOR_ID)

        await update.message.reply_text("Payment proof sent")

        context.user_data["payment"]=False

        return

    if context.user_data.get("contact"):

        await context.bot.send_message(
            PROFESSOR_ID,
            f"Message from\n"
            f"{user.first_name}\n"
            f"ID:{user.id}"
        )

        await update.message.copy(PROFESSOR_ID)

        await update.message.reply_text("Message sent")

        context.user_data["contact"]=False

# ---------- PROFESSOR PANEL ----------

async def panel(update:Update,context:ContextTypes.DEFAULT_TYPE):

    if update.message.from_user.id!=PROFESSOR_ID:
        return

    await update.message.reply_text(
        "/setcourse name link\n"
        "/addcourse userid course\n"
        "/sendlink userid link\n"
        "/remove userid\n"
        "/ban userid\n"
        "/users\n"
        "/stats\n"
        "/active\n"
        "/broadcast msg\n"
        "/reply userid msg"
    )

# ---------- SET COURSE ----------

async def setcourse(update:Update,context:ContextTypes.DEFAULT_TYPE):

    if update.message.from_user.id!=PROFESSOR_ID:
        return

    name=context.args[0]
    link=context.args[1]

    courses[name]=link

    save_courses()

    await update.message.reply_text("Course saved")

# ---------- ADD COURSE ----------

async def addcourse(update:Update,context:ContextTypes.DEFAULT_TYPE):

    if update.message.from_user.id!=PROFESSOR_ID:
        return

    uid=context.args[0]
    cname=" ".join(context.args[1:])

    if uid not in users:
        await update.message.reply_text("User not found")
        return

    users[uid]["courses"].append(cname)

    save_users()

    await context.bot.send_message(
        int(uid),
        f"Course Added\n{cname}"
    )

# ---------- USERS ----------

async def users_list(update:Update,context:ContextTypes.DEFAULT_TYPE):

    if update.message.from_user.id!=PROFESSOR_ID:
        return

    text="Users\n\n"

    for u in users:
        text+=f"{u} {users[u]['phone']}\n"

    await update.message.reply_text(text)

# ---------- STATS ----------

async def stats(update:Update,context:ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        f"Total Users:{len(users)}\n"
        f"Total Courses:{len(courses)}"
    )

# ---------- APP ----------

app=ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start",start))
app.add_handler(CommandHandler("panel",panel))
app.add_handler(CommandHandler("setcourse",setcourse))
app.add_handler(CommandHandler("addcourse",addcourse))
app.add_handler(CommandHandler("users",users_list))
app.add_handler(CommandHandler("stats",stats))

app.add_handler(MessageHandler(filters.CONTACT,phone))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,menu))
app.add_handler(MessageHandler(filters.ALL,user_message))

print("BOT RUNNING")

app.run_polling()