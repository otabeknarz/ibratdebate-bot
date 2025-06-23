from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from . import settings
from .functions import get_request


class Buttons:
    REMOVE_KEYBOARD = ReplyKeyboardRemove()

    MAIN_KEYBOARD = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Debate ga ro'yxatdan o'tish")],
        ],
        resize_keyboard=True,
    )

    PHONE_NUMBER_KEYBOARD = lambda self, resize: ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="📞 Telefon raqamimni jo'natish", request_contact=True
                )
            ]
        ],
        resize_keyboard=resize,
    )

    ENGLISH_LEVEL = lambda self, resize: ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=english_level)
                for english_level in settings.ENGLISH_LEVELS
            ],
        ],
        resize_keyboard=resize,
    )

    AGE = lambda self, resize: ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="<16"), KeyboardButton(text="16-18")],
            [KeyboardButton(text="19-24"), KeyboardButton(text=">24")],
        ],
        resize_keyboard=resize,
    )


class InlineButtons:
    @staticmethod
    def get_regions_inline_keyboard(key: str = None):
        params = None
        if key == "get_ticket":
            params = {"debates__is_passed": False}

        response = get_request(settings.REGIONS_API_URL, params=params)
        json_regions = response.json()
        regions = []
        last_id = None
        for json_region in json_regions.get("results"):
            if last_id != json_region.get("id"):
                regions.append(json_region)
                last_id = json_region.get("id")

        regions = [regions[i : i + 3] for i in range(0, len(regions), 3)]

        inline_buttons = [
            [
                InlineKeyboardButton(
                    text=region.get("name"),
                    callback_data=f"region:{region.get('id')}:{key}",
                )
                for region in triple_regions
            ]
            for triple_regions in regions
        ]

        return InlineKeyboardMarkup(inline_keyboard=inline_buttons)

    @staticmethod
    def get_districts_inline_keyboard(region_id: str, key: str = None):
        params = {"region": region_id}
        if key == "get_ticket":
            params["debates__is_passed"] = False

        response = get_request(
            settings.DISTRICTS_API_URL, params=params
        )
        json_districts = response.json()
        districts = json_districts.get("results")
        districts = [districts[i : i + 3] for i in range(0, len(districts), 3)]

        inline_buttons = [
            [
                InlineKeyboardButton(
                    text=district.get("name"),
                    callback_data=f"district:{district.get('id')}:{key}",
                )
                for district in triple_districts
            ]
            for triple_districts in districts
        ]

        return InlineKeyboardMarkup(inline_keyboard=inline_buttons)

    @staticmethod
    def get_join_channel_buttons(channels: dict) -> InlineKeyboardMarkup:
        inline_buttons = [
            [InlineKeyboardButton(text=channel_name, url=channel_link)]
            for channel_id, (channel_name, channel_link) in channels.items()
        ]
        inline_buttons.append(
            [
                InlineKeyboardButton(
                    text="Ibrat Debate Instagram", url="https://instagram.com/ibrat.debate"
                )
            ]
        )
        inline_buttons.append(
            [
                InlineKeyboardButton(
                    text="✅ A'zo bo'ldim", callback_data="joined"
                )
            ]
        )
        return InlineKeyboardMarkup(inline_keyboard=inline_buttons)

