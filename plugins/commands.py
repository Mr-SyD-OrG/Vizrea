from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio


@Client.on_message(filters.private & filters.command("batch"))
async def handle_batch(client, message: Message):
    user_id = message.from_user.id

    await message.reply("Batch started. Send your files now.\nSend `end_batch` to finish.", parse_mode="markdown")

    collected_files = []

    while True:
        try:
            msg: Message = await client.ask(
                user_id,
                filters=filters.private & (filters.document | filters.video | filters.text),
                timeout=300  # Optional timeout in seconds
            )
        except asyncio.TimeoutError:
            break

        if msg.text and msg.text.strip().lower() == "end_batch":
            break

        if msg.document or msg.video:
            collected_files.append(msg)

    if not collected_files:
        return await message.reply_text("No files received in this batch.")

    total = len(collected_files)
    text = f"Received {total} files\n"

    if total > 15:
        for msg in collected_files:
            media = msg.document or msg.video
            if media and media.file_name:
                name = media.file_name
                parts = name.replace("_", " ").split()
                info = " / ".join([p for p in parts if "ep" in p.lower() or "1080" in p or "720" in p])
                text += f"- {info or 'Unknown'}\n"
    else:
        for msg in collected_files:
            media = msg.document or msg.video
            if media and media.file_name:
                text += f"- {media.file_name}\n"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Rename Now", callback_data="rename_now")],
        [InlineKeyboardButton("Schedule", callback_data="schedule")]
    ])

    await message.reply_text(text, reply_markup=keyboard)

@Client.on_callback_query()
async def handle_buttons(client, query):
    data = query.data
    if data == "rename_now":
        await query.answer("Rename option selected.")
    elif data == "schedule":
        await query.answer("Schedule option selected.")

