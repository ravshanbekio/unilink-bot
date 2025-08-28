from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from translation import text_translations, command_translations

apply_router = Router()

# Escape MarkdownV2 special characters
def escape_md(text: str) -> str:
    special_chars = r"_*[]()~`>#+-=|{}.!"
    for ch in special_chars:
        text = text.replace(ch, f"\\{ch}")
    return text

# Dynamic back button
def get_back_button(lang: str):
    return f"🔙 {text_translations[lang]['back']}"

@apply_router.message(F.text.in_(["⬅ Back", "⬅ Orqaga","⬅ Назад","⬅ 뒤로"]))
async def go_back(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang") 
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=f"{command_translations[lang]['universities']}")],
            [KeyboardButton(text=f"{command_translations[lang]['check']}")],
            [KeyboardButton(text=f"{command_translations[lang]['contact']}")]
        ],
        resize_keyboard=True
    )
    
    await message.answer(
        escape_md(text_translations[lang]["back_to_menu"]),
        parse_mode="MarkdownV2",
        reply_markup=keyboard
    )
