# -*- coding: utf-8 -*-

"""
Power Point Break — Giveaway Bot
Full System | UTF-8 Safe | GSM Hosting Friendly
"""

import json, random, asyncio, time, re
from datetime import datetime
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)

# ====== BASIC CONFIG ======
BOT_TOKEN = "8370403090:AAHGo3RuBHi-h-8JZNS-n-Ew5Jx7gvHIsDc"
ADMIN = "MinexxProo"     # admin username only (without @)

DATAFILE = "data.json"

# ================================
# LOAD + SAVE DATA
# ================================
def load_data():
    try:
        with open(DATAFILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {
            "giveaway_on": False,
            "winner_limit": 0,
            "winners": [],
            "old_winners": [],
            "force_join": [],
            "history": [],
            "joined": [],
            "auto_mode": False
        }

DATA = load_data()

def save_data():
    with open(DATAFILE, "w", encoding="utf-8") as f:
        json.dump(DATA, f, indent=2, ensure_ascii=False)


# ====== CHECK ADMIN ======
def is_admin(user):
    return (user.username or "").lower() == ADMIN.lower()


# ====== FORCE JOIN CHECK ======
async def check_force_join(user_id, context: ContextTypes.DEFAULT_TYPE):
    if not DATA["force_join"]:
        return True, None

    for ch in DATA["force_join"]:
        try:
            x = await context.bot.get_chat_member(ch, user_id)
            if x.status not in ["member", "administrator", "creator"]:
                return False, ch
        except:
            return False, ch

    return True, None

# ==========================
# START COMMAND
# ==========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uname = f"@{user.username}" if user.username else user.first_name

    if is_admin(user):
        btn = InlineKeyboardMarkup(
            [[InlineKeyboardButton("📜 Show Commands", callback_data="help")]]
        )
        await update.message.reply_text(
            f"👋 Hello Admin {uname}!\n"
            f"Welcome to your Giveaway Bot ✅",
            reply_markup=btn
        )
        return

    # ===== USER VIEW =====
    uid = user.id
    text = (
        f"Hello {uname} 🎉\n"
        f"🆔 User ID: {uid}\n\n"
        "📩 To participate in the giveaway,\n"
        "👉 Please tap button below!\n\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "🚀🌟 Join the Giveaway Now!\n"
        "🎁🏆 Don’t miss your chance to win!\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        "✅ If selected, you will be notified instantly!\n\n"
        f"💬 Need help? @{ADMIN}\n"
        "Good luck 🍀\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )

    btn = InlineKeyboardMarkup(
        [[InlineKeyboardButton("✅ JOIN GIVEAWAY", callback_data="join_gv")]]
    )
    await update.message.reply_text(text, reply_markup=btn)


# ==========================
# SHOW ALL COMMANDS
# ==========================
async def all_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user):
        return await update.message.reply_text("❌ You are not admin.")

    txt = (
        "✅ AVAILABLE COMMANDS\n\n"
        "/start\n"
        "/on - enable giveaway\n"
        "/off - stop giveaway\n"
        "/set - set winner limit\n"
        "/reset - reset current data\n"
        "/verificationlink - set force join channels\n"
        "/setoldwinner - block old winners\n"
        "/alluser - show joined list\n"
        "/allwinnercount - full history\n"
        "/winauto - auto giveaway\n"
        "/countdown - manual countdown\n"
    )

    await update.message.reply_text(txt)


# ==========================
# ENABLE GIVEAWAY → /on
# ==========================
async def enable_giveaway(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user):
        return
    DATA["giveaway_on"] = True
    DATA["joined"] = []
    DATA["winners"] = []
    save_data()

    await update.message.reply_text(
        "✅ Giveaway is now ACTIVE!\n"
        "Now set winner count → /set"
    )


# ==========================
# DISABLE GIVEAWAY → /off
# ==========================
async def disable_giveaway(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user):
        return
    DATA["giveaway_on"] = False
    save_data()
    await update.message.reply_text("✅ Giveaway OFF ❌")
  # ==================================
# SET WINNER LIMIT → /set
# ==================================
async def set_winner_limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user):
        return

    await update.message.reply_text(
        "How many winners?\nExample: `10`",
        parse_mode="Markdown"
    )
    context.user_data["await_winner_limit"] = True


# capture winner limit
async def capture_winner_limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("await_winner_limit"):
        return
    try:
        n = int(update.message.text)
    except:
        return await update.message.reply_text("❌ Invalid number.")

    DATA["winner_limit"] = n
    save_data()
    context.user_data["await_winner_limit"] = False

    await update.message.reply_text(
        f"✅ Winner count set: {n}\n🎉 Giveaway Started!"
    )


# ==================================
# RESET DATA → /reset
# ==================================
async def reset_giveaway(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user):
        return
    DATA["joined"] = []
    DATA["winners"] = []
    DATA["winner_limit"] = 0
    DATA["auto_mode"] = False
    save_data()
    await update.message.reply_text("✅ Current giveaway reset done!")


# ==================================
# FORCE JOIN → /verificationlink
# ==================================
async def verificationlink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user):
        return
    await update.message.reply_text(
        "✅ Send up to 5 channel/group links.\n"
        "Example:\n"
        "@Channel1\n@Channel2\n"
    )
    context.user_data["await_force_join"] = True


# capture verification links
async def capture_verification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("await_force_join"):
        return

    links = update.message.text.split("\n")
    arr = []
    for v in links:
        v = v.strip()
        if v.startswith("@"):
            arr.append(v)

    if len(arr) > 5:
        arr = arr[:5]

    DATA["force_join"] = arr
    save_data()
    context.user_data["await_force_join"] = False

    await update.message.reply_text(
        f"✅ Force join saved!\n\n{arr}"
  )

# ==================================
# SET OLD WINNERS → /setoldwinner
# ==================================
async def set_oldwinner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user):
        return

    await update.message.reply_text(
        "✅ Send old winners (one per line)\n"
        "Format:\n"
        "@name | 12345\n@abc | 98765"
    )
    context.user_data["await_old"] = True


# capture old winners
async def capture_old(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("await_old"):
        return

    lines = update.message.text.split("\n")
    for L in lines:
        if "|" not in L:
            continue
        name, uid = L.split("|", 1)
        uid = uid.strip()
        if uid.isdigit():
            DATA["old_winners"].append(int(uid))

    save_data()
    context.user_data["await_old"] = False
    await update.message.reply_text("✅ Old winners saved!")


# ==================================
# SHOW CURRENT WINNERS → /alluser
# ==================================
async def show_current_winners(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user):
        return

    if not DATA["winners"]:
        return await update.message.reply_text("❌ No winners yet!")

    txt = "🏆 Current Winners:\n\n"
    for i, w in enumerate(DATA["winners"], 1):
        txt += f"{i}) @{w['username']} | {w['user_id']}\n"

    await update.message.reply_text(txt)


# ==================================
# SHOW WINNER HISTORY → /allwinnercount
# ==================================
async def show_winner_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user):
        return

    if not DATA["history"]:
        return await update.message.reply_text("📂 No winner history")

    txt = "📊 Winner History:\n\n"
    for i, w in enumerate(DATA["history"], 1):
        tm = datetime.fromisoformat(w["timestamp"]).strftime("%Y-%m-%d %H:%M")
        txt += f"{i}) @{w['username']} | {w['user_id']} | {tm}\n"

    await update.message.reply_text(txt)


# ==================================
# JOIN GIVEAWAY
# ==================================
async def join_gv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    uid  = user.id
    uname = user.username or ""

    # ✅ Giveaway ON check
    if not DATA["giveaway_on"]:
        return await query.message.reply_text(
            "⛔️ ❌ GIVEAWAY CLOSED ❌ ⛔️\n"
            f"📩 Contact Admin → @{ADMIN}"
        )

    # ✅ Force join check
    ok, ch = await check_force_join(uid, context)
    if not ok:
        btn = InlineKeyboardMarkup(
            [[InlineKeyboardButton("✅ JOIN CHANNEL", url=f"https://t.me/{ch.replace('@','')}")],
             [InlineKeyboardButton("✅ TRY AGAIN", callback_data="join_gv")]]
        )
        return await query.message.reply_text(
            "⚠️ You must join channels first!",
            reply_markup=btn
        )

    # ✅ Old winner check
    if uid in DATA["old_winners"]:
        return await query.message.reply_text(
            "┏━━━━━━━━━━━━━━━━━━━┓\n"
            "🏆 You’ve already won this giveaway!\n"
            "⚖️ Repeat not allowed.\n"
            f"📩 @{ADMIN}\n"
            "┗━━━━━━━━━━━━━━━━━━━┛"
        )

    # ✅ Already participated
    if uid in DATA["joined"]:
        return await query.message.reply_text(
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚠️ You have already participated!\n"
            f"📩 Need help? @{ADMIN}\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        )

    # ✅ Limit full?
    if len(DATA["winners"]) >= DATA["winner_limit"]:
        return await query.message.reply_text(
            "😔 Oops! All winners selected!\n"
            "🎉 Thanks for joining!\n"
            f"📞 @{ADMIN}"
        )

    # ✅ Mark joined
    DATA["joined"].append(uid)

    # ✅ Make winner entry
    winner = {
        "username": uname,
        "user_id": uid,
        "timestamp": datetime.now().isoformat()
    }

    DATA["winners"].append(winner)
    DATA["history"].append(winner)
    save_data()

    # ✅ DM winner
    try:
        await context.bot.send_message(
            chat_id=uid,
            text=(
                "🎉 CONGRATULATIONS! 🎉\n"
                "You WON the Giveaway! 🏆\n\n"
                f"📩 Contact Admin → @{ADMIN}\n"
                "💙 Hosted by: Power Point Break"
            )
        )
    except:
        pass

    # ✅ Notify admin
    try:
        await context.bot.send_message(
            chat_id=f"@{ADMIN}",
            text=f"✅ NEW WINNER → @{uname} | {uid}"
        )
    except:
        pass

    return await query.message.reply_text(
        "🎉 You are SELECTED as WINNER!\nCheck your DM 💌"
  )

# ==========================================
# AUTO GIVEAWAY → /winauto
# ==========================================
async def winauto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user):
        return

    DATA["auto_mode"] = True
    save_data()

    await update.message.reply_text(
        "✅ AUTO-GIVEAWAY MODE ON!\n"
        "➡ Send Winner Count (ex: 20)"
    )
    context.user_data["await_auto_count"] = True


# ==========================================
# CAPTURE AUTO WINNER COUNT
# ==========================================
async def capture_auto_winner_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("await_auto_count"):
        return

    try:
        n = int(update.message.text)
    except:
        return await update.message.reply_text("❌ Invalid number")

    DATA["winner_limit"] = n
    save_data()
    context.user_data["await_auto_count"] = False

    await update.message.reply_text(
        f"✅ Winner Count set → {n}\n"
        "➡ Now send time (ex: 10s / 10m / 1h 10m)"
    )
    context.user_data["await_auto_time"] = True


# ==========================================
# Time string → seconds
# ==========================================
def parse_time(t):
    t = t.lower().strip()
    h = m = s = 0
    if "h" in t:
        h = int(t.split("h")[0].strip())
        t = t.split("h")[1]
    if "m" in t:
        m = int(t.split("m")[0].strip())
        t = t.split("m")[1]
    if "s" in t:
        s = int(t.split("s")[0].strip())
    return h*3600 + m*60 + s


# ==========================================
# PROGRESS BAR
# ==========================================
def bar(p):
    total = 10
    filled = int((p/100) * total)
    return "▰"*filled + "▱"*(total-filled)


# ==========================================
# CAPTURE AUTO TIME + COUNTDOWN
# ==========================================
async def capture_auto_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("await_auto_time"):
        return

    sec = parse_time(update.message.text)
    if sec <= 0:
        return await update.message.reply_text("❌ Invalid time format")

    context.user_data["await_auto_time"] = False

    await update.message.reply_text("✅ Countdown started…")

    total = sec
    msg = await update.message.reply_text("⏳ …")

    while sec > 0:
        percent = (sec / total) * 100
        try:
            await msg.edit_text(
                f"⏳ Time Left: {sec}s\n"
                f"{bar(percent)}\n\n"
                "⏰ Time is running! Hurry up! ⚡"
            )
        except:
            pass

        await asyncio.sleep(1)
        sec -= 1

    await msg.edit_text(
        "⏳ Countdown Ended!\n"
        "🎉 Winners Will Be Announced Soon!"
    )

    await auto_pick(update, context)


# ==========================================
# AUTO PICK WINNERS
# ==========================================
async def auto_pick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid_list = DATA["joined"]
    old = DATA["old_winners"]
    limit = DATA["winner_limit"]

    # valid users
    valid = [x for x in uid_list if x not in old]

    if not valid:
        return await update.message.reply_text("❌ No valid participants!")

    if len(valid) <= limit:
        picked = valid
    else:
        picked = random.sample(valid, limit)

    winner_list = []
    for uid in picked:
        try:
            user = await context.bot.get_chat(uid)
            row = {
                "username": user.username or "",
                "user_id": uid,
                "timestamp": datetime.now().isoformat()
            }
            DATA["winners"].append(row)
            DATA["history"].append(row)
            winner_list.append(row)

            # DM winner
            try:
                await context.bot.send_message(
                    chat_id=uid,
                    text=(
                        "🎉 CONGRATULATIONS! 🎉\n"
                        "You WON the Giveaway! 🏆\n\n"
                        f"📩 Contact Admin → @{ADMIN}"
                    )
                )
            except:
                pass
        except:
            pass

    save_data()

    txt = "🏆 AUTO WINNERS:\n\n"
    for i, w in enumerate(winner_list, 1):
        txt += f"{i}) @{w['username']} | {w['user_id']}\n"

    btn = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ APPROVE", callback_data="auto_ok"),
            InlineKeyboardButton("❌ REJECT", callback_data="auto_no")
        ]
    ])

    await update.message.reply_text(txt, reply_markup=btn)

# ==========================================
# ✅ AUTO — APPROVE / REJECT
# ==========================================
async def auto_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user  = query.from_user

    if not is_admin(user):
        return await query.answer("❌ Not Allowed")

    txt = (
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🏆 Power Point Break — Giveaway Winners\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    for i, w in enumerate(DATA["winners"], 1):
        txt += f"{i}) @{w['username']} | {w['user_id']}\n"

    txt += (
        "\n🎉 Congratulations to all!\n"
        f"📞 Contact Admin: @{ADMIN}\n"
        "🎙 Hosted by: Power Point Break"
    )

    await query.message.reply_text(txt)
    await query.answer("✅ Winners posted")


async def auto_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user):
        return await query.answer("❌ Not Allowed")

    DATA["winners"] = []
    save_data()
    await query.message.reply_text("❌ Auto Giveaway Cancelled")
    await query.answer("Cancelled")



# ==========================================
# ✅ MANUAL COUNTDOWN → /countdown
# ==========================================
async def countdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user):
        return

    await update.message.reply_text(
        "📩 Send countdown Post Content\n"
        "(Example: Giveaway starts soon!)"
    )
    context.user_data["await_cd_message"] = True


async def capture_cd_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("await_cd_message"):
        return

    DATA["countdown_content"] = update.message.text
    save_data()
    context.user_data["await_cd_message"] = False

    await update.message.reply_text(
        "✅ Message Saved!\nNow send Time (10s / 10m / 1h 10m)"
    )
    context.user_data["await_cd_time"] = True


async def capture_cd_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("await_cd_time"):
        return

    sec = parse_time(update.message.text)
    if sec <= 0:
        return await update.message.reply_text("❌ Invalid time")

    context.user_data["await_cd_time"] = False

    msg = await update.message.reply_text("⏳ Countdown starting…")
    total = sec

    while sec > 0:
        percent = (sec / total) * 100
        b = bar(percent)

        m = sec // 60
        s = sec % 60
        t = f"{m:02d}:{s:02d}"

        try:
            await msg.edit_text(
                f"{DATA['countdown_content']}\n\n"
                f"⏳ Time Left: {t}\n"
                f"{b}\n\n"
                "⏰ Time is running! Hurry up! ⚡"
            )
        except:
            pass

        await asyncio.sleep(1)
        sec -= 1

    await msg.edit_text(
        "⏳ Countdown has ended!\n"
        "🎉 Stay ready — Winners will be announced very soon!\n\n"
        "🎙 Hosted by: Power Point Break"
    )



# ==========================================
# ✅ MASTER TEXT CAPTURE
# ==========================================
async def master_text_capture(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if context.user_data.get("await_winner_limit"):
        return await capture_winner_limit(update, context)

    if context.user_data.get("await_force_join"):
        return await capture_verification(update, context)

    if context.user_data.get("await_old"):
        return await capture_old(update, context)

    if context.user_data.get("await_auto_count"):
        return await capture_auto_winner_count(update, context)

    if context.user_data.get("await_auto_time"):
        return await capture_auto_time(update, context)

    if context.user_data.get("await_cd_message"):
        return await capture_cd_message(update, context)

    if context.user_data.get("await_cd_time"):
        return await capture_cd_time(update, context)

    return  # ignore



# ==========================================
# ✅ CALLBACK ROUTER
# ==========================================
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data

    if data == "join_gv":
        return await join_gv(update, context)

    if data == "auto_ok":
        return await auto_approve(update, context)

    if data == "auto_no":
        return await auto_reject(update, context)

    if data == "help":
        return await all_commands(update, context)



# ==========================================
# ✅ HANDLERS + RUN BOT
# ==========================================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("on", enable_giveaway))
    app.add_handler(CommandHandler("off", disable_giveaway))
    app.add_handler(CommandHandler("set", set_winner_limit))
    app.add_handler(CommandHandler("reset", reset_giveaway))
    app.add_handler(CommandHandler("verificationlink", verificationlink))
    app.add_handler(CommandHandler("setoldwinner", set_oldwinner))
    app.add_handler(CommandHandler("alluser", show_current_winners))
    app.add_handler(CommandHandler("allwinnercount", show_winner_history))
    app.add_handler(CommandHandler("winauto", winauto))
    app.add_handler(CommandHandler("countdown", countdown))
    app.add_handler(CommandHandler("allcd", all_commands))

    # ✅ MASTER TEXT CAPTURE
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, master_text_capture))

    # Callback Buttons
    app.add_handler(CallbackQueryHandler(callback_handler))

    print("✅ BOT RUNNING…")
    app.run_polling()


if __name__ == "__main__":
    main()
