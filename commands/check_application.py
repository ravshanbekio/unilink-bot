from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils import check_application_status
from translation import command_translations, all_commands

check_router = Router()


class CheckStatusForm(StatesGroup):
    application_code = State()


# Generate menu keyboard dynamically
def get_keyboard(lang: str):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=command_translations[lang]["universities"])],
            [KeyboardButton(text=command_translations[lang]["check"])],
            [KeyboardButton(text=command_translations[lang]["contact"])],
            [KeyboardButton(text=command_translations[lang]["about"])],
            [KeyboardButton(text=command_translations[lang]["back"])],
        ],
        resize_keyboard=True
    )


# Helper: escape text for MarkdownV2
def escape_md(text: str) -> str:
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{c}' if c in escape_chars else c for c in text)


# Step 1: Ask for application code
@check_router.message(F.text.in_(
    [v["check"] for v in command_translations.values()]
    ))
async def ask_code(message: Message, state: FSMContext):
    await state.set_state(CheckStatusForm.application_code)

    data = await state.get_data()
    lang = data.get("lang")

    texts = {
        "en": "📧 Please enter your *Application code* to check your application status:",
        "uz": "📧 Ariza holatini tekshirish uchun *Ariza kodingizni* kiriting:",
        "ru": "📧 Пожалуйста, введите ваш *Код заявки*, чтобы проверить статус:",
        "kr": "📧 지원 상태를 확인하려면 *지원 코드*를 입력하세요:"
    }

    text = escape_md(texts[lang])
    await message.answer(text, parse_mode="MarkdownV2")


# Step 2: Show application status
@check_router.message(CheckStatusForm.application_code, F.text.not_in(all_commands))
async def display_status(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang")

    app_data = check_application_status(message.text)

    try:
        text = (
        {
            "en": "📄 Application Details",
            "uz": "📄 Ariza Tafsilotlari",
            "ru": "📄 Детали заявки",
            "kr": "📄 지원서 세부 정보"
        }[lang]
        + "\n\n"
        + f"{command_translations[lang]['check']}: {app_data['application_id']}\n"
        + f"{({'en': 'Code','uz': 'Kod','ru': 'Код','kr': '코드'}[lang])}: {app_data['application_code']}\n"
        + f"{({'en': 'Status','uz': 'Holat','ru': 'Статус','kr': '상태'}[lang])}: {app_data['status']}\n"
        + f"{({'en': 'Name','uz': 'Ism','ru': 'Имя','kr': '이름'}[lang])}: {app_data['applicant']['legal_name']}\n"
        + f"{({'en': 'Email','uz': 'Elektron pochta','ru': 'Эл. почта','kr': '이메일'}[lang])}: {app_data['applicant']['email']}\n"
        + f"{({'en': 'University','uz': 'Universitet','ru': 'Университет','kr': '대학교'}[lang])}: {app_data['university']['name_en']}"
        )

        await message.answer(escape_md(text), parse_mode="MarkdownV2", reply_markup=get_keyboard(lang))

    except Exception:
        await message.answer(
            {
                "en": "⚠️ Application not found. Please check your code.",
                "uz": "⚠️ Ariza topilmadi. Kodni tekshiring.",
                "ru": "⚠️ Заявка не найдена. Проверьте код.",
                "kr": "⚠️ 지원서를 찾을 수 없습니다. 코드를 확인하세요."
            }[lang],
            reply_markup=get_keyboard(lang)
        )
