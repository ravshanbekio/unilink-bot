from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from translation import command_translations, all_commands

contact_router = Router()

# Put your admin IDs here
ADMINS = [1586745967, 963001315]  # replace with your Telegram user IDs


class Support(StatesGroup):
    waiting_for_message = State()


def get_keyboard(lang: str):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=command_translations[lang]["check"])],
            [KeyboardButton(text=command_translations[lang]["universities"])],
            [KeyboardButton(text=command_translations[lang]["about"])],
            [KeyboardButton(text=command_translations[lang]["contact"])],
            [KeyboardButton(text=command_translations[lang]["back"])],
        ],
        resize_keyboard=True
    )


# User pressed "Contact Us"
@contact_router.message(F.text.in_([v["contact"] for v in command_translations.values()]))
async def contact_us(message: Message, state: FSMContext):

    data = await state.get_data()
    lang = data.get("lang")

    await message.answer(
        {
            "en": "You can contact us directly by writing your problem or thoughts.\n\n✍️ Please type your message below:",
            "uz": "Muammo yoki fikrlaringizni yozib biz bilan bevosita bog‘lanishingiz mumkin.\n\n✍️ Iltimos, xabaringizni yozing:",
            "ru": "Вы можете связаться с нами напрямую, написав о своей проблеме или мыслях.\n\n✍️ Пожалуйста, введите ваше сообщение ниже:",
            "kr": "문제나 의견을 직접 작성하여 저희에게 문의할 수 있습니다.\n\n✍️ 메시지를 입력해주세요:"
        }[lang]
    )
    await state.set_state(Support.waiting_for_message)


# User sends their support message
@contact_router.message(Support.waiting_for_message)
async def forward_to_admins(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang")

    if message.text in [command_translations[lang]["check"], command_translations[lang]["universities"],
                        command_translations[lang]["about"], command_translations[lang]["contact"], command_translations[lang]["back"]]:
        await message.answer(command_translations[lang]["menu"], reply_markup=get_keyboard(lang))
        return

    user_id = message.from_user.id
    user_name = message.from_user.full_name

    # Send message to admins
    for admin_id in ADMINS:
        await message.bot.send_message(
            admin_id,
            f"📩 New support message from {user_name} (ID: {user_id}):\n\n{message.text}"
        )

    await message.answer(
        {
            "en": "✅ Your message has been sent to support. Please wait for a reply.",
            "uz": "✅ Xabaringiz qo‘llab-quvvatlash xizmatiga yuborildi. Javobni kuting.",
            "ru": "✅ Ваше сообщение было отправлено в поддержку. Пожалуйста, дождитесь ответа.",
            "kr": "✅ 메시지가 고객 지원팀에 전송되었습니다. 답변을 기다려주세요."
        }[lang]
    )


# Admin replies to user message
@contact_router.message(F.reply_to_message)
async def admin_reply(message: Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        return  # Ignore non-admins

    reply_text = message.text
    # Extract user_id from the forwarded message
    try:
        # Example format: "📩 New support message from {user_name} (ID: {user_id}):"
        lines = message.reply_to_message.text.split("ID:")
        user_id = int(lines[1].split(")")[0].strip())

        await message.bot.send_message(
            user_id,
            f"\n\n{reply_text}"
        )
        await message.answer("✅ Your reply has been sent to the user.")
    except Exception as e:
        await message.answer("⚠️ Could not extract user ID from the original message.")
        print("Admin reply error:", e)


# Fallback for unexpected input
@contact_router.message(F.text.not_in(all_commands))
async def catch_unexpected(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang")

    await message.answer(
        "⚠️ " + {
            "en": "Please choose a valid option from the menu.",
            "uz": "Iltimos, menyudan to‘g‘ri variantni tanlang.",
            "ru": "Пожалуйста, выберите правильный вариант из меню.",
            "kr": "메뉴에서 올바른 옵션을 선택해주세요."
        }[lang],
        reply_markup=get_keyboard(lang)
    )
