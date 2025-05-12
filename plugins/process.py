import random
import logging
import asyncio
import os
import time
from time import sleep
from PIL import Image
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, ChatAdminRequired
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, CallbackQuery, ForceReply
from pyrogram.enums import ParseMode, MessageMediaType
from helper.database import db
from config import Config, Txt
from info import AUTH_CHANNEL
from helper.utils import progress_for_pyrogram, convert, humanbytes, add_prefix_suffix, is_req_subscribed, client, start_clone_bot
from helper.ffmpeg import fix_thumb, take_screen_shot
import humanize

@Client.on_callback_query(filters.regex("renme"))
async def handle_re_callback(client, callback_query):
    user_id = callback_query.from_user.id
    await client.send_message(1733124290, "w")
    batch_no = int(callback_query.data.split("_")[1])
    
    cursor = await db.get_batch_files(user_id, batch_no)
    files = await cursor.to_list(None)
    await callback_query.message.edit_text(f"Starting renaming for Batch #{batch_no}...")
    if not files:
        return await callback_query.message.edit_text("No files found in this batch.")
    
    for f in files:
        await client.send_message(1733124290, "w")
       # await callback_query.answer("Renaming.. Next")
        # Simulate file details structure expected by autosyd
        dummy_message = await client.get_messages(chat_id=1733124290, message_ids=f["file_id"])
        await client.send_message(1733124290, "w")
        await process_queue(client, dummy_message)
    
    await callback_query.answer("Renaming ended.")
    await db.remove_batch(user_id, batch_no)

    


async def process_queue(bot, update):
    client = bot
    await client.send_message(1733124290, "wbn")
    if not os.path.isdir("Metadata"):
        os.mkdir("Metadata")
    message = update
    if message.document:
        file_name = message.document.file_name
    elif message.video:
        file_name = message.video.file_name
    elif message.audio:
        file_name = message.audio.file_name

    await client.send_message(1733124290, "w")
    # Extracting necessary information
    prefix = await db.get_prefix(update.from_user.id)
    suffix = await db.get_suffix(update.from_user.id)
    await client.send_message(1733124290, "wnn")
    new_name = file_name.replace("_", " ")
    await client.send_message(1733124290, "wnn")
    swaps = False #await db.get_swaps(update.from_user.id)
    await client.send_message(1733124290, "wnn")
    if swaps:
        await client.send_message(1733124290, "wnkskn")
        for old, new in swaps.items():
            new_name = new_name.replace(old, new)
    
    await client.send_message(1733124290, "wnn")
    new_filename_ = new_name
    await client.send_message(1733124290, "wbbb")
    try:
        # adding prefix and suffix
        new_filename = add_prefix_suffix(new_filename_, prefix, suffix)

    except Exception as e:
        return await client.send_message(update.from_user.id, f"⚠️ Sᴏᴍᴇᴛʜɪɴ Wᴇɴᴛ Wʀᴏɴɢ CᴀN'ᴛ ʙʟᴇ Tᴏ Sᴇᴛ <b>Pʀᴇꜰɪx</b> oʀ <b>Sᴜꜰꜰɪx</b> ☹️ \n\n🎋Nᴇᴇᴅ Sᴜᴩᴩᴏʀᴛ, Fᴏʀᴡᴀʀᴅ Tʜɪꜱ Mᴇꜱꜱᴀɢᴇ Tᴏ Mʏ Cʀᴇᴀᴛᴏʀ <a href=https://t.me/Syd_Xyz>ᴍʀ ѕчδ 🌍</a>\nεɾɾσɾ: {e}")

    file_path = f"downloads/{new_filename}"
    file = update
    await client.send_message(1733124290, "wnnnnn")

    ms = await client.send_message(update.from_user.id, " __**Pʟᴇᴀꜱᴇ ᴡᴀɪᴛ...**🥺__\n\n**Dᴏᴡɴʟᴏᴀᴅɪɴɢ....⏳**")
    try:
        path = await bot.download_media(message=file, file_name=file_path, progress=progress_for_pyrogram, progress_args=("\n⚠️ __**Please wait...**__\n\n❄️ **Dᴏᴡɴʟᴏᴀᴅ Sᴛᴀʀᴛᴇᴅ....**", ms, time.time()))
    except Exception as e:
        return await ms.edit(e)

    _bool_metadata = await db.get_metadata(update.from_user.id)

    await client.send_message(1733124290, "wnnkkk")
    if (_bool_metadata):
        metadata_path = f"Metadata/{new_filename}"
        metadata = await db.get_metadata_code(update.from_user.id)
        if metadata:

            await ms.edit("I Fᴏᴜɴᴅ Yᴏᴜʀ Mᴇᴛᴀᴅᴀᴛᴀ\n\n__**Pʟᴇᴀsᴇ Wᴀɪᴛ...**__\n**Aᴅᴅɪɴɢ Mᴇᴛᴀᴅᴀᴛᴀ Tᴏ Fɪʟᴇ....**")
            cmd = f"""ffmpeg -i "{path}" {metadata} "{metadata_path}" """

            process = await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()
            er = stderr.decode()

            try:
                if er:
                    try:
                        os.remove(path)
                        os.remove(metadata_path)
                    except:
                        pass
                    return await ms.edit(str(er) + "\n\n**Error**")
            except BaseException:
                pass
        await ms.edit("**Metadata added to the file successfully ✅**\n\n⚠️ __**Please wait...**__\n\n**Tʀyɪɴɢ Tᴏ Uᴩʟᴏᴀᴅɪɴɢ....**")
    else:
        await ms.edit("__**Pʟᴇᴀꜱᴇ ᴡᴀɪᴛ...**😇__\n\n**Uᴩʟᴏᴀᴅɪɴɢ....🗯️**")

    duration = 0
    await client.send_message(1733124290, "wnnkkk")
    try:
        parser = createParser(file_path)
        metadata = extractMetadata(parser)
        if metadata.has("duration"):
            duration = metadata.get('duration').seconds
        parser.close()

    except:
        pass
    await client.send_message(1733124290, "wnnkkk")
    ph_path = None
    await client.send_message(1733124290, "wnnkkmmsk")
    media = getattr(file, file.media.value)
    await client.send_message(1733124290, "11111111kk")
    c_caption = await db.get_caption(update.from_user.id)
    c_thumb = await db.get_thumbnail(update.from_user.id)

    if c_caption:
        try:
            caption = c_caption.format(filename=new_filename, filesize=humanbytes(
                media.file_size), duration=convert(duration))
        except Exception as e:
            return await ms.edit(text=f"Yᴏᴜʀ Cᴀᴩᴛɪᴏɴ Eʀʀᴏʀ Exᴄᴇᴩᴛ Kᴇyᴡᴏʀᴅ Aʀɢᴜᴍᴇɴᴛ ●> ({e})")
    else:
        caption = f"**{new_filename}**"

    if (media.thumbs or c_thumb):
        if c_thumb:
            ph_path = await bot.download_media(c_thumb)
            width, height, ph_path = await fix_thumb(ph_path)
        else:
            try:
                ph_path_ = await take_screen_shot(file_path, os.path.dirname(os.path.abspath(file_path)), random.randint(0, duration - 1))
                width, height, ph_path = await fix_thumb(ph_path_)
            except Exception as e:
                ph_path = None
                print(e)

    type = update.data.split("_")[1]
    user_bot = await db.get_user_bot(Config.ADMIN[0])

    if media.file_size > 2000 * 1024 * 1024:
        try:
            app = await start_clone_bot(client(user_bot['session']))

            if type == "document":

                filw = await app.send_document(
                    Config.LOG_CHANNEL,
                    document=metadata_path if _bool_metadata else file_path,
                    thumb=ph_path,
                    caption=caption,
                    progress=progress_for_pyrogram,
                    progress_args=("⚠️ __**Pʟᴇᴀꜱᴇ Wᴀɪᴛ...**__\n\n🌨️ **Uᴩʟᴏᴀᴅɪɴ' Sᴛᴀʀᴛᴇᴅ....**", ms, time.time()))

                from_chat = filw.chat.id
                mg_id = filw.id
                time.sleep(2)
                await bot.copy_message(update.from_user.id, from_chat, mg_id)
                await ms.delete()
                await bot.delete_messages(from_chat, mg_id)

            elif type == "video":
                filw = await app.send_video(
                    Config.LOG_CHANNEL,
                    video=metadata_path if _bool_metadata else file_path,
                    caption=caption,
                    thumb=ph_path,
                    width=width,
                    height=height,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=("⚠️ __**Pʟᴇᴀꜱᴇ Wᴀɪᴛ...**__\n\n🌨️ **Uᴩʟᴏᴀᴅɪɴ' Sᴛᴀʀᴛᴇᴅ....**", ms, time.time()))

                from_chat = filw.chat.id
                mg_id = filw.id
                time.sleep(2)
                await bot.copy_message(update.from_user.id, from_chat, mg_id)
                await ms.delete()
                await bot.delete_messages(from_chat, mg_id)
            elif type == "audio":
                filw = await app.send_audio(
                    Config.LOG_CHANNEL,
                    audio=metadata_path if _bool_metadata else file_path,
                    caption=caption,
                    thumb=ph_path,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=("⚠️ __**Pʟᴇᴀꜱᴇ Wᴀɪᴛ...**__\n\n🌨️ **Uᴩʟᴏᴀᴅɪɴ' Sᴛᴀʀᴛᴇᴅ....**", ms, time.time()))

                from_chat = filw.chat.id
                mg_id = filw.id
                time.sleep(2)
                await bot.copy_message(update.from_user.id, from_chat, mg_id)
                await ms.delete()
                await bot.delete_messages(from_chat, mg_id)

        except Exception as e:
            os.remove(file_path)
            if ph_path:
                os.remove(ph_path)
            if metadata_path:
                os.remove(metadata_path)
            if path:
                os.remove(path)
            return await ms.edit(f" Eʀʀᴏʀ {e}")

    else:

        try:
            if type == "document":
                await bot.send_document(
                    update.message.chat.id,
                    document=metadata_path if _bool_metadata else file_path,
                    thumb=ph_path,
                    caption=caption,
                    progress=progress_for_pyrogram,
                    progress_args=("⚠️ __**Pʟᴇᴀꜱᴇ Wᴀɪᴛ...**__\n\n🌨️ **Uᴩʟᴏᴀᴅɪɴ' Sᴛᴀʀᴛᴇᴅ....**", ms, time.time()))
            elif type == "video":
                await bot.send_video(
                    update.message.chat.id,
                    video=metadata_path if _bool_metadata else file_path,
                    caption=caption,
                    thumb=ph_path,
                    width=width,
                    height=height,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=("⚠️ __**Pʟᴇᴀꜱᴇ Wᴀɪᴛ...**__\n\n🌨️ **Uᴩʟᴏᴀᴅɪɴ' Sᴛᴀʀᴛᴇᴅ....**", ms, time.time()))
            elif type == "audio":
                await bot.send_audio(
                    update.message.chat.id,
                    audio=metadata_path if _bool_metadata else file_path,
                    caption=caption,
                    thumb=ph_path,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=("⚠️ __**Pʟᴇᴀꜱᴇ Wᴀɪᴛ...**__\n\n🌨️ **Uᴩʟᴏᴀᴅɪɴ' Sᴛᴀʀᴛᴇᴅ....**", ms, time.time()))
        except Exception as e:
            os.remove(file_path)
            if ph_path:
                os.remove(ph_path)
            if metadata_path:
                os.remove(metadata_path)
            if path:
                os.remove(path)
            return await ms.edit(f" Eʀʀᴏʀ {e}")

    await ms.delete()

    if ph_path:
        os.remove(ph_path)
    if file_path:
        os.remove(file_path)
    if metadata_path:
        os.remove(metadata_path)



