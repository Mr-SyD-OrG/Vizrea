from pyrogram import Client, filters, enums
from helper.database import db
import re
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio




@Client.on_message(filters.command("batch") & filters.private)
async def start_batch(client, message):
    await message.reply_text("Batch #{batch_no} started.\nSend files now. Type /endbatch to finish.")
    user_id = message.from_user.id
    last = await db.batches.find({"user_id": user_id}).sort("batch_no", -1).to_list(1)
    batch_no = last[0]["batch_no"] + 1 if last else 1
    await db.set_active_batch(user_id, batch_no)
    await message.reply_text(f"Batch #{batch_no} started.\nSend files now. Type `endbatch` to finish.")


@Client.on_message(filters.command("endbatch") & filters.private)
async def end_batch(client, message):
    user_id = message.from_user.id
    batch_no = await db.get_active_batch(user_id)
    if not batch_no:
        return await message.reply_text("No active batch.")

    await db.clear_active_batch(user_id)
    files_cursor = await db.get_batch_files(user_id, batch_no)
    files = await files_cursor.to_list(length=None)

    if not files:
        return await message.reply_text("No files found in this batch.")

    text = f"Received {len(files)} files in Batch #{batch_no}\n"
    if len(files) > 15:
        for f in files:
            part = f["file_name"]
            episode = next((x for x in part.split() if "ep" in x.lower() or "720" in x or "1080" in x), "File")
            text += f"- {episode}\n"
    else:
        text += "\n".join(f"- {f['file_name']}" for f in files)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Rename Now", callback_data=f"rename_{batch_no}")],
        [InlineKeyboardButton("Schedule", callback_data=f"schedule_{batch_no}")]
    ])
    await message.reply_text(text, reply_markup=keyboard)


@Client.on_message(filters.private & (filters.document | filters.video))
async def handle_sedia(client, message):
    user_id = message.from_user.id
    batch_no = await db.get_active_batch(user_id)
    if not batch_no:
        return
    media = message.document or message.video
    await db.add_file_to_batch(
        user_id,
        batch_no,
        media.file_id,
        media.file_name,
        "document" if message.document else "video"
    )

    
@Client.on_message(filters.private & filters.command('set_prefix'))
async def add_caption(client, message):

    if len(message.command) == 1:
        return await message.reply_text("**__Give The Prefix__\n\nExᴀᴍᴩʟᴇ:- `/set_prefix @Roofiverse`**")
    prefix = message.text.split(" ", 1)[1]
    SnowDev = await message.reply_text("Please Wait ...", reply_to_message_id=message.id)
    await db.set_prefix(message.from_user.id, prefix)
    await SnowDev.edit("__**✅ ᴘʀᴇꜰɪx ꜱᴀᴠᴇᴅ**__")


@Client.on_message(filters.private & filters.command('del_prefix'))
async def delete_prefix(client, message):

    SnowDev = await message.reply_text("Please Wait ...", reply_to_message_id=message.id)
    prefix = await db.get_prefix(message.from_user.id)
    if not prefix:
        return await SnowDev.edit("__**😔 ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀɴʏ ᴘʀᴇꜰɪx**__")
    await db.set_prefix(message.from_user.id, None)
    await SnowDev.edit("__**❌️ ᴘʀᴇꜰɪx ᴅᴇʟᴇᴛᴇᴅ**__")


@Client.on_message(filters.private & filters.command('see_prefix'))
async def see_caption(client, message):

    SnowDev = await message.reply_text("Please Wait ...", reply_to_message_id=message.id)
    prefix = await db.get_prefix(message.from_user.id)
    if prefix:
        await SnowDev.edit(f"**ʏᴏᴜʀ ᴘʀᴇꜰɪx:-**\n\n`{prefix}`")
    else:
        await SnowDev.edit("__**😔 ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀɴʏ ᴘʀᴇꜰɪx**__")


# SUFFIX
@Client.on_message(filters.private & filters.command('set_suffix'))
async def add_csuffix(client, message):

    if len(message.command) == 1:
        return await message.reply_text("**__Give The Suffix__\n\nExᴀᴍᴩʟᴇ:- `/set_suffix @Roofiverse`**")
    suffix = message.text.split(" ", 1)[1]
    SnowDev = await message.reply_text("Please Wait ...", reply_to_message_id=message.id)
    await db.set_suffix(message.from_user.id, suffix)
    await SnowDev.edit("__**✅ ꜱᴜꜰꜰɪx ꜱᴀᴠᴇᴅ**__")


@Client.on_message(filters.private & filters.command('del_suffix'))
async def delete_suffix(client, message):

    SnowDev = await message.reply_text("Please Wait ...", reply_to_message_id=message.id)
    suffix = await db.get_suffix(message.from_user.id)
    if not suffix:
        return await SnowDev.edit("__**😔 ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀɴʏ ꜱᴜꜰꜰɪx**__")
    await db.set_suffix(message.from_user.id, None)
    await SnowDev.edit("__**❌️ ꜱᴜꜰꜰɪx ᴅᴇʟᴇᴛᴇᴅ**__")


@Client.on_message(filters.private & filters.command('see_suffix'))
async def see_csuffix(client, message):

    SnowDev = await message.reply_text("Please Wait ...", reply_to_message_id=message.id)
    suffix = await db.get_suffix(message.from_user.id)
    if suffix:
        await SnowDev.edit(f"**ʏᴏᴜʀ ꜱᴜꜰꜰɪx:-**\n\n`{suffix}`")
    else:
        await SnowDev.edit("__**😔 ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀɴʏ ꜱᴜꜰꜰɪx**__")

@Client.on_message(filters.private & filters.command('set_rep'))
async def add_rep(client, message):
    if len(message.command) < 3:
        return await message.reply_text("**__Give The Prefix__\n\nExᴀᴍᴩʟᴇ:- `/set_prefix @Roofiverse`**")
    txt = message.text.split(" ", 2)
    Sydd = txt[1]
    Syddd = txt[2] if txt[2] else ''
    SyD = await message.reply_text("Please Wait ...", reply_to_message_id=message.id)
    await db.set_rep(message.from_user.id, Sydd, Syddd)
    await SyD.edit("__**ꜱᴀᴠᴇᴅ !**__")


@Client.on_message(filters.private & filters.command('del_rep'))
async def delete_rep(client, message):
    SyD = await message.reply_text("Please Wait ...", reply_to_message_id=message.id)
    dump = await db.get_rep(message.from_user.id)
    if not dump:
        return await SyD.edit("__**😔 ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀɴʏ ᴘʀᴇꜰɪx**__")
    await db.set_rep(message.from_user.id, None, None)
    await SyD.edit("__**❌️ ᴘʀᴇꜰɪx ᴅᴇʟᴇᴛᴇᴅ**__")

@Client.on_message(filters.private & filters.command('set_topic'))
async def add_topic(client, message):
    if len(message.command) == 1:
        return await message.reply_text("**__Give The ᴅᴜᴍᴩ ᴄʜᴀɴɴᴇʟ ɪᴅ__\n\nExᴀᴍᴩʟᴇ:- `/set_dump -1002042969565`**")
    mrsyd = message.text.split(" ", 1)[1]
   # mrsyd = await client.ask(message.from_user.id, "<b>ꜱᴇɴᴅ ᴍᴇ ᴛʜᴇ ᴛᴏᴩɪᴄ ɪᴅ ᴏʀ ʟɪɴᴋ.\n\n/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪs ᴘʀᴏᴄᴇss.</b>")
    if mrsyd.startswith("https://t.me/"):
        match = re.search(r"/(\d+)$", mrsyd)
        if match:
            topic_id = match.group(1)
            txt = topic_id
        else:
            return await message.reply("<b>⚠ Invalid link provided. Make sure it ends with a numeric topic ID.</b>")
    else:
        txt = mrsyd.split(" ", 1)[0]
    SyD = await message.reply_text("Please Wait ...", reply_to_message_id=message.id)
    await db.set_topic(message.from_user.id, txt)
    await SyD.edit("__**✅ ᴛᴏᴩɪᴄ ꜱᴀᴠᴇᴅ**__")
