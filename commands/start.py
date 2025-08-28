from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from translation import command_translations

start_router = Router()

# States
class LanguageForm(StatesGroup):
    choosing = State()

# Inline keyboard for language selection
lang_inline_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
    ],
    [
        InlineKeyboardButton(text="🇺🇿 Oʻzbekcha", callback_data="lang_uz"),
        InlineKeyboardButton(text="🇰🇷 한국어", callback_data="lang_kr"),
    ]
])

@start_router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    """
        Start message
    """
    await state.set_state(LanguageForm.choosing)
    await message.answer("🌍 Please select your language:", reply_markup=lang_inline_kb)

# Handle language selection
@start_router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]  # en / ru / uz / kr
    await state.update_data(lang=lang)

    t = command_translations[lang]  # shortcut for current language texts

    text = (
        f"{t['start']}\n\n"
    )

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t["check"])],
            [KeyboardButton(text=t["universities"])],
            [KeyboardButton(text=t["about"])],
            [KeyboardButton(text=t["contact"])],
        ],
        resize_keyboard=True
    )

    await callback.message.answer(text, parse_mode="MarkdownV2", reply_markup=keyboard)