from pyrogram import Client, filters, enums
from helper.database import db
import re
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from plugins.features import features_button


@Client.on_message(filters.private & filters.command('del_dump'))
async def delete_dump(client, message):

    SyD = await message.reply_text("Please Wait ...", reply_to_message_id=message.id)
    dump = await db.get_dump(message.from_user.id)
    if not dump:
        return await SyD.edit("__**😔 ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀɴʏ ᴅᴜᴍᴩ ᴄʜᴀɴɴᴇʟ**__")
    await db.set_dump(message.from_user.id, message.from_user.id)
    await SyD.edit("__**❌️ ᴅᴜᴍᴩ ᴅᴇʟᴇᴛᴇᴅ**__")


@Client.on_message(filters.private & filters.command('see_dump'))
async def see_dump(client, message):

    SyD = await message.reply_text("Please Wait ...", reply_to_message_id=message.id)
    dump = await db.get_dump(message.from_user.id)
    if dump:
        await SyD.edit(f"**ʏᴏᴜʀ ᴅᴜᴍʙ ᴄʜᴀɴɴᴇʟ:-**\n\n`{dump}`")
    else:
        await SyD.edit("__**😔 ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀɴʏ ᴅᴜᴍʙ ᴄʜᴀɴɴᴇʟ**__")

@Client.on_message(filters.private & filters.command('set_dump'))
async def add_dump(client, message):

    if len(message.command) == 1:
        return await message.reply_text("**__Give The Dump Channel_\n\nExᴀᴍᴩʟᴇ:- `/set_dump -100XXXXXXX`**")
    dump = message.text.split(" ", 1)[1]
    SyD = await message.reply_text("Please Wait ...", reply_to_message_id=message.id)
    await db.set_dump(message.from_user.id, dump)
    await SyD.edit("__**✅ ꜱᴀᴠᴇᴅ**__")


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

    dump = await db.get_dump(user_id)


    text = f"Received {len(files)} files in Batch #{batch_no}\n"
    if len(files) > 15:
        for f in files:
            part = f["file_name"]
            episode = next((x for x in part.split() if "ep" in x.lower() or "720" in x or "1080" in x or "480"), "File")
            text += f"- {episode}\n"
    else:
        text += "\n".join(f"- {f['file_name']}" for f in files)

    text += f"\n Current Dump Channel : {dump} \n If You Want To Change Thumbnail, Send Picture Then And Dump Channel By /set_dump ."
    markup = await features_button(message.from_user.id)

    # Add your custom buttons below the feature buttons
    extra_buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Rename As Document", callback_data=f"renme_{batch_no}_d")],
        [InlineKeyboardButton("Rename As Video", callback_data=f"renme_{batch_no}_v")]
    ])

    markup.inline_keyboard.extend(extra_buttons.inline_keyboard)

    await message.reply_text(text, reply_markup=markup)


@Client.on_message(filters.command("process") & filters.private)
async def end_batch(client, message):
    user_id = message.from_user.id
    parts = message.text.split(maxsplit=2)

    if len(parts) != 3:
        return await message.reply_text(
            "**Usage:** `/process <batch_no> <type>`\n\n"
            "Example: `/process 12 document or video or audio`",
            parse_mode=enums.ParseMode.MARKDOWN
        )

    
    batch_no = int(parts[1])
    process_type = parts[2].strip().lower()
    if process_type != "document" or "video" or "audio":
        return await message.reply_text("No valid type found.")

    files_cursor = await db.get_batch_files(user_id, batch_no)
    files = await files_cursor.to_list(length=None)

    if not files:
        return await message.reply_text("No files found in this batch.")

    dump = await db.get_dump(user_id)


    text = f"Received {len(files)} files in Batch #{batch_no}\n"
    if len(files) > 15:
        for f in files:
            part = f["file_name"]
            episode = next((x for x in part.split() if "ep" in x.lower() or "720" in x or "1080" in x), "File")
            text += f"- {episode}\n"
    else:
        text += "\n".join(f"- {f['file_name']}" for f in files)

    text += f"\n Current Dump Channel : {dump} \n If You Want To Change Thumbnail, Send Picture Then And Dump Channel By /set_dump ."
    markup = await features_button(message.from_user.id)

    # Add your custom buttons below the feature buttons
    extra_buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Rename As Document", callback_data=f"renme_{batch_no}_d")],
        [InlineKeyboardButton("Rename As Video", callback_data=f"renme_{batch_no}_v")]
    ])

    markup.inline_keyboard.extend(extra_buttons.inline_keyboard)

    await message.reply_text(text, reply_markup=markup)


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
        message.id,
        media.file_name,
        "document" if message.document else "video"
    )
    await message.reply_text("added")

    
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
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/swap old:new`", parse_mode=enums.ParseMode.MARKDOWN)

    try:
        pair = message.text.split(None, 1)[1]
        old, new = pair.split(":", 1)
        await db.add_swap(message.from_user.id, old, new)
        await message.reply(f"✅ Swap saved!\n`{old}` will be replaced with `{new}`", parse_mode=enums.ParseMode.MARKDOWN)
    except Exception as e:
        await message.reply(f"❌ Failed to save swap.\n\nError: `{e}`", parse_mode=enums.ParseMode.MARKDOWN)
