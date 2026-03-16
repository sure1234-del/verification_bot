import json
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler

BOT_TOKEN = "8680097194:AAF7_crZONNEZ7WhjmGg4nZq4HOaJ3rXVsk"
PROFESSOR_ID = 7209486623

AVAILABLE_COURSE_GROUP = "https://t.me/uoscli"
BACKUP_CHANNEL = "https://t.me/uoscli"

# ---------- DATABASE ----------

def load_json(file):
    if not os.path.exists(file):
        return {}
    with open(file,'r') as f:
        return json.load(f)

def save_json(file,data):
    with open(file,'w') as f:
        json.dump(data,f,indent=4)

users = load_json("users.json")
courses = load_json("courses.json")

# ---------- LOG SYSTEM ----------

def log_event(text):
    logs = []
    if os.path.exists("logs.json"):
        with open("logs.json","r") as f:
            logs=json.load(f)

    logs.append({
        "time":str(datetime.now()),
        "event":text
    })

    with open("logs.json","w") as f:
        json.dump(logs,f,indent=4)

# ---------- START ----------

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):

    keyboard=[
        [InlineKeyboardButton("📱 Verify Phone",callback_data="verify")],
        [InlineKeyboardButton("📚 My Courses",callback_data="mycourses")],
        [InlineKeyboardButton("📘 Available Courses",url=AVAILABLE_COURSE_GROUP)],
        [InlineKeyboardButton("📢 Join Backup Channel",url=BACKUP_CHANNEL)],
        [InlineKeyboardButton("💳 Payment",callback_data="payment")],
        [InlineKeyboardButton("🎓 Contact Professor",callback_data="contact")]
    ]

    await update.message.reply_text(
        "🎓 Welcome to Professor Learning System\n\n"
        "Please complete verification to access courses.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------- VERIFY ----------

async def verify(update:Update,context:ContextTypes.DEFAULT_TYPE):

    query=update.callback_query
    await query.answer()

    user=query.from_user

    users[str(user.id)]={
        "name":user.first_name,
        "username":user.username,
        "courses":[],
        "verified":True
    }

    save_json("users.json",users)

    log_event(f"User verified {user.id}")

    await query.message.reply_text("✅ Verification completed")

# ---------- MY COURSES ----------

async def mycourses(update:Update,context:ContextTypes.DEFAULT_TYPE):

    query=update.callback_query
    await query.answer()

    uid=str(query.from_user.id)

    if uid not in users:
        await query.message.reply_text("No courses found")
        return

    course_list=users[uid]["courses"]

    if not course_list:
        await query.message.reply_text("No courses assigned")
        return

    keyboard=[]

    for c in course_list:

        if c in courses:

            keyboard.append(
                [InlineKeyboardButton(c,url=courses[c])]
            )

    await query.message.reply_text(
        "📚 Your Courses",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------- PAYMENT ----------

async def payment(update:Update,context:ContextTypes.DEFAULT_TYPE):

    query=update.callback_query
    await query.answer()

    await query.message.reply_text(
        "💳 Payment Method\n\n"
        "Amazon Pay Gift Card\n"
        "PhonePe Gift Card\n\n"
        "After purchase send screenshot/code here."
    )

# ---------- CONTACT PROFESSOR ----------

async def contact(update:Update,context:ContextTypes.DEFAULT_TYPE):

    query=update.callback_query
    await query.answer()

    await query.message.reply_text(
        "✉️ Drop a message here👇"
    )

    context.user_data["contact"]=True

# ---------- USER MESSAGE ----------

async def user_message(update:Update,context:ContextTypes.DEFAULT_TYPE):

    user=update.message.from_user

    if context.user_data.get("contact"):

        await context.bot.forward_message(
            chat_id=PROFESSOR_ID,
            from_chat_id=update.message.chat_id,
            message_id=update.message.message_id
        )                                                                                                                                                    	                                                                                                                                     	await update.message.reply_text("Message sent to Professor")

        context.user_data["contact"]=False

# ---------- PROFESSOR PANEL ----------

async def panel(update:Update,context:ContextTypes.DEFAULT_TYPE):

    if update.message.from_user.id!=PROFESSOR_ID:
        return

    await update.message.reply_text(
        "🎓 Professor Panel\n\n"
        "/setcourse name link\n"
        "/addcourse user course\n"
        "/users\n"
        "/stats\n"
        "/remove user"
    )

# ---------- SET COURSE ----------

async def setcourse(update:Update,context:ContextTypes.DEFAULT_TYPE):

    if update.message.from_user.id!=PROFESSOR_ID:
        return

    name=context.args[0]
    link=context.args[1]

    courses[name]=link

    save_json("courses.json",courses)

    await update.message.reply_text("Course saved")

# ---------- ADD COURSE ----------

async def addcourse(update:Update,context:ContextTypes.DEFAULT_TYPE):

    if update.message.from_user.id!=PROFESSOR_ID:
        return

    user=context.args[0]
    course=" ".join(context.args[1:])

    if user not in users:
        await update.message.reply_text("User not found")
        return

    users[user]["courses"].append(course)

    save_json("users.json",users)

    await update.message.reply_text("Course assigned")

# ---------- USERS ----------

async def list_users(update:Update,context:ContextTypes.DEFAULT_TYPE):

    if update.message.from_user.id!=PROFESSOR_ID:
        return

    text="Users\n\n"

    for u in users:
        text+=f"{u} {users[u]['name']}\n"

    await update.message.reply_text(text)

# ---------- STATS ----------

async def stats(update:Update,context:ContextTypes.DEFAULT_TYPE):

    if update.message.from_user.id!=PROFESSOR_ID:
        return

    total=len(users)

    await update.message.reply_text(
        f"Bot Stats\nUsers:{total}\nCourses:{len(courses)}"
    )

# ---------- REMOVE USER ----------

async def remove(update:Update,context:ContextTypes.DEFAULT_TYPE):

    if update.message.from_user.id!=PROFESSOR_ID:
        return

    user=context.args[0]

    if user in users:
        users.pop(user)

    save_json("users.json",users)

    await update.message.reply_text("User removed")

# ---------- APP ----------

app=ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start",start))
app.add_handler(CommandHandler("panel",panel))
app.add_handler(CommandHandler("setcourse",setcourse))
app.add_handler(CommandHandler("addcourse",addcourse))
app.add_handler(CommandHandler("users",list_users))
app.add_handler(CommandHandler("stats",stats))
app.add_handler(CommandHandler("remove",remove))

app.add_handler(CallbackQueryHandler(verify,pattern="verify"))
app.add_handler(CallbackQueryHandler(mycourses,pattern="mycourses"))
app.add_handler(CallbackQueryHandler(payment,pattern="payment"))
app.add_handler(CallbackQueryHandler(contact,pattern="contact"))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,user_message))

print("BOT RUNNING")

app.run_polling()