from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from helper.database import db


async def features_button(user_id):
    metadata = await db.get_metadata(user_id)

    button = [[
        InlineKeyboardButton(
            'ᴍᴇᴛᴀᴅᴀᴛᴀ', callback_data='filters_metadata'),
        InlineKeyboardButton('✅' if metadata else '❌',
                             callback_data='filters_metadata')
    ]
    ]

    return InlineKeyboardMarkup(button)


@Client.on_callback_query(filters.regex('^filters'))
async def handle_filters(bot: Client, query: CallbackQuery):
    user_id = query.from_user.id
    type = query.data.split('_')[1]
    if type == 'metadata':
        get_meta = await db.get_metadata(user_id)

        if get_meta:
            await db.set_metadata(user_id, False)
            markup = await features_button(user_id)
            await query.message.edit_reply_markup(markup)
        else:
            await db.set_metadata(user_id, True)
            markup = await features_button(user_id)
            await query.message.edit_reply_markup(markup)
