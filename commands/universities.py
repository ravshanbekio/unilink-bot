from aiogram import Router, F
import aiohttp
import math
import tempfile
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery  
from aiogram.fsm.context import FSMContext

from commands.apply import escape_md
from utils import get_universities
from translation import command_translations, text_translations, all_commands

universities_router = Router()

# Example data
universities = get_universities(page=1, perPage=10)

async def download_and_send_photo(url: str, message, caption, kb):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
                    f.write(await resp.read())
                    file = FSInputFile(f.name)
                    await message.answer_photo(
                        photo=file,
                        caption=caption,
                        parse_mode="MarkdownV2",
                        reply_markup=kb
                    )

# Generate main menu keyboard
def main_menu_kb(lang: str):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=command_translations[lang]["universities"])],
            [KeyboardButton(text=command_translations[lang]["check"])],
            [KeyboardButton(text=command_translations[lang]["about"])],
            [KeyboardButton(text=command_translations[lang]["contact"])]
        ],
        resize_keyboard=True
    )

# Back button keyboard
def back_kb(lang: str):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=command_translations[lang]["back"])]],
        resize_keyboard=True
    )

# Universities list keyboard
def universities_kb(lang: str, next_page: int, page: int = 1):
    universities = get_universities(page=page, perPage=10)
    
    keyboard = [
            *[[KeyboardButton(text=u[f"name_{lang}"])] for u in universities["response"]["data"]],
        ]
    
    if next_page > 1:
        keyboard.append(
            [KeyboardButton(text=command_translations[lang]["next"])]
        )
        
    keyboard.append(
        [KeyboardButton(text=command_translations[lang]["back"])]
    )
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )

# See universities command
@universities_router.message(F.text.in_(
    [v["universities"] for v in command_translations.values()] +
    [v["next"] for v in command_translations.values()]
))
async def show_universities(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang")

    pageExists = data.get("page")
    if pageExists is not None:
        pageExists += 1
    
    pageExists = 1
        
    universities = get_universities(page=1, perPage=10)
    page = math.ceil(universities["total"] / 10)
    
    await state.update_data(page=pageExists)
    await state.update_data(current_menu="uni_list")
    await message.answer(
        text_translations[lang]["select_uni"],
        parse_mode="MarkdownV2",
        reply_markup=universities_kb(lang=lang, next_page=page, page=pageExists)
    )

# --- BACK handler (inline button) ---
@universities_router.callback_query(F.data.startswith("back_to_list"))
async def back_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang")

    kb = universities_kb(lang)
    await callback.message.answer(command_translations[lang]["choose_again"], reply_markup=kb)
    await callback.answer()

# Handle university selection ONLY if it matches a real university
@universities_router.message(F.text.not_in(all_commands))
async def university_details(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang")

    page = data.get("page")
    print(page)
    universities = get_universities(page=1, perPage=10)
    uni = next(
        (u for u in universities.get("data", []) if u[f"name_{lang}"] == message.text),
        None
    )

    if not uni:
        return  # Ignore if not a valid university

    # Store selected university
    await state.update_data(selected_uni=uni["univer_id"])

    # Inline keyboard (Details + Back)
    apply_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=text_translations[lang]["details"],
                    url=f"{text_translations[lang]}{uni['univer_id']}"
                )
            ],
            [
                InlineKeyboardButton(
                    text=command_translations[lang]["back"], 
                    callback_data="back_to_list"
                )
            ]
        ]
    )

    # Send university details
    await download_and_send_photo(
        uni["images"][0]["image_url"],
        message,
        f"*{escape_md(uni[f'name_{lang}'])}*",
        apply_kb
    )
