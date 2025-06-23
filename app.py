import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from dotenv import load_dotenv

from modules import settings
from modules.filters import TextEqualsFilter
from modules.states import RegistrationState
from modules.functions import get_request, post_request, patch_request
from modules.keyboards import Buttons, InlineButtons

load_dotenv()

buttons = Buttons()
inline_buttons = InlineButtons()

TOKEN = getenv("BOT_TOKEN")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def check_is_subscribed(chat_id, user_id) -> bool:
    try:
        status = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        return status.status != "left"
    except Exception as e:
        logger.error(e)
        return False


# Registration starts


@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    user_data = {
        "id": str(message.from_user.id),
        "username": (
            message.from_user.username
            if message.from_user.username
            else str(message.from_user.id)
        ),
        "first_name": message.from_user.first_name,
        "last_name": message.from_user.last_name if message.from_user.last_name else "",
        "language_code": message.from_user.language_code,
    }
    post_request(settings.USERS_API_URL, user_data)

    subscription_statuses = {True: {}, False: {}}
    for channel_id, (channel_name, channel_link) in settings.CHANNELS_IDs.items():
        status = await check_is_subscribed(channel_id, message.from_user.id)
        subscription_statuses[status].update({channel_id: (channel_name, channel_link)})

    if subscription_statuses.get(False):
        unjoined_channels_inline_buttons = inline_buttons.get_join_channel_buttons(
            subscription_statuses.get(False)
        )
        await message.answer(
            "Birinchi ushbu kanallarga ulanib oling so'ng a'zo bo'ldim tugmasini bosing",
            reply_markup=unjoined_channels_inline_buttons,
        )
        return

    await message.answer(
        text=f"Assalomu alaykum! Ro'yxatdan o'tish uchun ism familiyangizni to'liq yozing",
        reply_markup=buttons.REMOVE_KEYBOARD,
    )

    await state.set_state(RegistrationState.name)


@dp.callback_query(F.data == "joined")
async def ive_joined(callback: CallbackQuery, state: FSMContext) -> None:
    subscription_statuses = {True: {}, False: {}}
    for channel_id, (channel_name, channel_link) in settings.CHANNELS_IDs.items():
        status = await check_is_subscribed(
            channel_id, callback.message.from_user.id
        )
        subscription_statuses[status].update(
            {channel_id: (channel_name, channel_link)}
        )

    if subscription_statuses.get(False):
        unjoined_channels_inline_buttons = inline_buttons.get_join_channel_buttons(
            subscription_statuses.get(False)
        )
        await callback.message.delete()
        await asyncio.sleep(0.5)
        await callback.message.answer(
            "Birinchi ushbu kanallarga ulanib oling so'ng a'zo bo'ldim tugmasini bosing",
            reply_markup=unjoined_channels_inline_buttons,
        )
        return

    await callback.message.answer(
        text=f"Assalomu alaykum! Ro'yxatdan o'tish uchun ism familiyangizni to'liq yozing",
        reply_markup=buttons.REMOVE_KEYBOARD,
    )

    await state.set_state(RegistrationState.name)


@dp.message(RegistrationState.name)
async def start_name_state_handler(message: Message, state: FSMContext) -> None:
    name = message.text
    patch_request(
        settings.USERS_API_URL + f"{message.from_user.id}/", {"name": name}
    )
    await message.answer(
        text="Telefon raqamingizni ushbu tugma orqali yuboring",
        reply_markup=buttons.PHONE_NUMBER_KEYBOARD(resize=True),
    )

    await state.set_state(RegistrationState.phone)


@dp.message(RegistrationState.phone)
async def phone_name_state_handler(message: Message, state: FSMContext) -> None:
    if not message.contact:
        await message.answer(
            text="Iltimos quyidagi tugmani bosib, telefon raqamingizni yuboring",
            reply_markup=buttons.PHONE_NUMBER_KEYBOARD(resize=False),
        )
        await state.set_state(RegistrationState.phone)
        return

    patch_request(
        settings.USERS_API_URL + f"{message.from_user.id}/",
        {"phone": message.contact.phone_number},
    )
    await message.answer(
        text="Ingliz tili darajangizni belgilang",
        reply_markup=buttons.ENGLISH_LEVEL(resize=True),
    )

    await state.set_state(RegistrationState.english_level)


@dp.message(RegistrationState.english_level)
async def english_level_state_handler(message: Message, state: FSMContext) -> None:
    english_level = message.text
    if english_level not in settings.ENGLISH_LEVELS:
        await message.answer(
            text="Iltimos, quyidagi tugmalardan tanlang",
            reply_markup=buttons.ENGLISH_LEVEL(resize=False),
        )
        await state.set_state(RegistrationState.english_level)
        return

    patch_request(
        settings.USERS_API_URL + f"{message.from_user.id}/",
        {"english_level": english_level},
    )
    await message.answer(
        text="Yoshingizni kiriting",
        reply_markup=buttons.AGE(resize=True),
    )

    await state.set_state(RegistrationState.age)


@dp.message(RegistrationState.age)
async def age_state_handler(message: Message, state: FSMContext) -> None:
    age = message.text
    if age not in settings.AGE:
        await message.answer(
            text="Iltimos, quyidagi tugmalardan tanlang",
            reply_markup=buttons.AGE(resize=False),
        )
        await state.set_state(RegistrationState.age)
        return

    patch_request(
        settings.USERS_API_URL + f"{message.from_user.id}/", {"age": age}
    )

    msg = await message.answer(
        text="Ajoyib!",
        reply_markup=buttons.REMOVE_KEYBOARD,
    )

    await asyncio.sleep(0.5)

    await message.answer(
        text="Viloyat/Respublika ingizni tanlang",
        reply_markup=inline_buttons.get_regions_inline_keyboard(),
    )

    await asyncio.sleep(0.5)

    await msg.delete()

    await message.answer(
        text="Tabriklaymiz botimizdan ro'yxatdan o'tdingiz\nDebate ga ticket olish uchun '📝 Debate ga ro'yxatdan o'tish' tugmasini bosing",
        reply_markup=buttons.MAIN_KEYBOARD,
    )

    await state.clear()


# @dp.callback_query(F.data.startswith("region:"))
# async def region_callback_handler(callback: CallbackQuery, state: FSMContext) -> None:
#     _, region_id, key = callback.data.split(":")
#
#     if key == "get_ticket":
#         await callback.message.edit_text(
#             text="Ushbu tumanlarda debate larimiz bo'ladi",
#             reply_markup=inline_buttons.get_districts_inline_keyboard(
#                 region_id=region_id,
#                 key="get_ticket",
#             ),
#         )
#         return
#
#     patch_request(
#         settings.USERS_API_URL + f"{callback.message.chat.id}/", {"region": region_id}
#     )
#
#     await callback.message.edit_text(
#         text="Tuman/Shahar ingizni tanlang",
#         reply_markup=inline_buttons.get_districts_inline_keyboard(
#             region_id=region_id
#         ),
#     )
#
#     await state.set_state(RegistrationState.district)


# @dp.callback_query(F.data.startswith("district:"))
# async def district_callback_handler(callback: CallbackQuery, state: FSMContext) -> None:
#     _, district_id, key = callback.data.split(":")
#
#     if key == "get_ticket":
#         response = get_request(
#             url=settings.DEBATES_API_URL,
#             params={"district": district_id, "is_passed": False},
#         )
#         json_response = response.json()
#         debate_id = json_response.get("results")[0].get("id")
#
#         response = post_request(url=settings.TICKETS_API_URL, data={"debate": debate_id, "user": callback.message.chat.id})
#         json_response_ticket = response.json()
#         ticket_qr_code_path = json_response_ticket.get("qr_code")
#
#         district_response = get_request(
#             url=settings.DISTRICTS_API_URL+f"{district_id}/",
#         )
#
#         district_response_json = district_response.json()
#
#         try:
#             await callback.message.answer_photo(
#                 photo=f"https://api.ibratdebate.uz/media/{ticket_qr_code_path}",
#                 caption=f"Bu sizning ticketingiz uni debate ga borganingizda kirish uchun ishlatasiz\nDebate da ko'rishguncha!\nUshbu guruhga ulanib oling! - {district_response_json.get('telegram_group_link')}"
#             )
#         except Exception:
#             await callback.message.answer(
#                 text=f"Siz ro'yxatdan o'tdingiz debate da kutamiz\nUshbu guruhga ulanib oling! - {district_response_json.get('telegram_group_link')}"
#             )
#         return
#
#     patch_request(
#         settings.USERS_API_URL + f"{callback.message.chat.id}/",
#         {"district": district_id},
#     )
#
#     await callback.message.delete()
#
#     await callback.message.answer(
#         text="Tabriklaymiz botimizdan ro'yxatdan o'tdingiz\nDebate ga ticket olish uchun '📝 Debate ga ro'yxatdan o'tish' tugmasini bosing",
#         reply_markup=buttons.MAIN_KEYBOARD,
#     )
#
#     await state.clear()


# Registration ends


@dp.message(TextEqualsFilter("👀 Kelasi debatlar"))
async def coming_debates(message: Message, state: FSMContext) -> None:
    response = get_request(settings.DEBATES_API_URL)
    json_response = response.json()
    debates = json_response.get("results", [])
    response_text = "Bu yerda bizda tez kunda bo'ladigan debate larimizning ro'yxati:\n\n"

    for key, debate in enumerate(debates, start=1):
        region_name = debate["region"]["name"]
        district_name = debate["district"]["name"]
        response_text += f"{key}. {region_name} - {district_name}\n"

    await message.answer(
        text=response_text,
        reply_markup=buttons.MAIN_KEYBOARD,
    )


@dp.message(TextEqualsFilter("📝 Debate ga ro'yxatdan o'tish"))
async def get_ticket(message: Message, state: FSMContext) -> None:
    await message.answer(
        text="Debat bo'ladigan Viloyat/Respublika ingizni tanlang",
        reply_markup=inline_buttons.get_regions_inline_keyboard(key="get_ticket"),
    )


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
