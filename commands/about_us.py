from aiogram import Router, types, F
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from translation import command_translations, text_translations

about_router = Router()

@about_router.message(F.text.in_([v["about"] for v in command_translations.values()]))
async def about_us(message: types.Message, state: FSMContext):

    data = await state.get_data()
    lang = data.get("lang")
    
    text = text_translations[lang].get("about_text")

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=command_translations[lang]["check"])],
            [KeyboardButton(text=command_translations[lang]["universities"])],
            [KeyboardButton(text=command_translations[lang]["contact"])],
            [KeyboardButton(text=command_translations[lang]["about"])],
            [KeyboardButton(text=command_translations[lang]["back"])],
        ],
        resize_keyboard=True
    )

    await message.answer(text, parse_mode="MarkdownV2", reply_markup=keyboard)
