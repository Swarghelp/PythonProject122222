import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    KeyboardButton,
    LabeledPrice,
    PreCheckoutQuery,
    ReplyKeyboardMarkup,
)

# ==================== НАСТРОЙКИ ====================
BOT_TOKEN = "8870818643:AAEPBFxIYqpXnMXbp7azV2wNoBGMdDIstYQ"
ADMIN_ID = 1294437052  # Укажите ваш ID (из @userinfobot)

# Ссылки на изображения
WELCOME_IMAGE = "https://i.postimg.cc/28pJbDbN/7edd5105c61e87c01d2b23a91649e3c4.jpg"
BOT_DEV_IMAGE = "https://i.postimg.cc/28pJbDbN/7edd5105c61e87c01d2b23a91649e3c4.jpg"
PARSER_IMAGE = "https://i.postimg.cc/28pJbDbN/7edd5105c61e87c01d2b23a91649e3c4.jpg"
TEST_STAR_IMAGE = "https://i.postimg.cc/28pJbDbN/7edd5105c61e87c01d2b23a91649e3c4.jpg"

ORDERS_DB = []

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# ==================== СОСТОЯНИЯ (FSM) ====================
class OrderForm(StatesGroup):
    name = State()
    phone = State()
    details = State()


# ==================== КЛАВИАТУРЫ ====================
def main_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📦 Каталог услуг"),
                KeyboardButton(text="📝 Оставить заявку"),
            ],
            [KeyboardButton(text="ℹ️ О нас"), KeyboardButton(text="📞 Контакты")],
        ],
        resize_keyboard=True,
    )


def cancel_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]], resize_keyboard=True
    )


def catalog_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🤖 Разработка бота", callback_data="item_bot"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Парсер данных", callback_data="item_parser"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⭐ Тест-услуга (1 Star)", callback_data="item_star"
                )
            ],
            [
                InlineKeyboardButton(
                    text="➕ Заказать разработку", callback_data="start_order"
                )
            ],
        ]
    )


def buy_star_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💳 Оплатить 1 ⭐", callback_data="pay_star"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад в каталог", callback_data="back_to_catalog"
                )
            ],
        ]
    )


def admin_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📋 Список всех заявок", callback_data="admin_view_orders"
                )
            ]
        ]
    )


# ==================== СБРОС И ОТМЕНА ====================
@dp.message(Command("cancel"))
@dp.message(F.text.lower() == "❌ отмена")
@dp.message(F.text.lower() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нечего отменять.", reply_markup=main_kb())
        return

    await state.clear()
    await message.answer("Заполнение формы отменено.", reply_markup=main_kb())


# ==================== ПАНЕЛЬ АДМИНИСТРАТОРА ====================
@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ У вас нет прав администратора.")
        return

    await message.answer(
        "👑 <b>Панель администратора</b>\n\nВы успешно авторизованы.",
        parse_mode="HTML",
        reply_markup=admin_kb(),
    )


@dp.callback_query(F.data == "admin_view_orders")
async def admin_view_orders(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("У вас нет доступа.", show_alert=True)
        return

    if not ORDERS_DB:
        await callback.message.answer(
            "📋 Список заявок пуст.", reply_markup=admin_kb()
        )
        await callback.answer()
        return

    response = "📋 <b>Список полученных заявок:</b>\n\n"
    for idx, order in enumerate(ORDERS_DB, 1):
        response += (
            f"<b>Заявка #{idx}</b>\n"
            f"👤 Имя: {order['name']}\n"
            f"📞 Контакт: {order['phone']}\n"
            f"💬 Telegram ID: <code>{order['user_id']}</code> (@{order['username']})\n"
            f"📋 Задача: {order['details']}\n"
            f"---------------------------\n"
        )

    await callback.message.answer(
        response, parse_mode="HTML", reply_markup=admin_kb()
    )
    await callback.answer()


# ==================== ОСНОВНЫЕ ХЕНДЛЕРЫ С КАРТИНКАМИ ПОД СООБЩЕНИЕМ ====================
@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()

    # Отправляем ФОТО, а текст пишем в caption (подпись под фото)
    await message.answer_photo(
        photo=WELCOME_IMAGE,
        caption=(
            f"Привет, <b>{message.from_user.first_name}</b>! 👋\n\n"
            f"Добро пожаловать в демо-бот студии разработки.\n"
            f"Выберите интересующий раздел в меню ниже:"
        ),
        parse_mode="HTML",
        reply_markup=main_kb(),
    )


@dp.message(F.text == "📦 Каталог услуг")
async def show_catalog(message: types.Message):
    # Отправляем фото каталога с подписью
    await message.answer_photo(
        photo=BOT_DEV_IMAGE,
        caption="<b>📦 Каталог услуг</b>\n\nВыберите нужную позицию из списка:",
        parse_mode="HTML",
        reply_markup=catalog_kb(),
    )


@dp.callback_query(F.data == "back_to_catalog")
async def back_to_catalog(callback: types.CallbackQuery):
    # Обновляем фото и подпись под ним
    media = InputMediaPhoto(
        media=BOT_DEV_IMAGE,
        caption="<b>📦 Каталог услуг</b>\n\nВыберите нужную позицию из списка:",
        parse_mode="HTML",
    )
    await callback.message.edit_media(media=media, reply_markup=catalog_kb())
    await callback.answer()


@dp.callback_query(F.data.startswith("item_"))
async def process_catalog_click(callback: types.CallbackQuery):
    if callback.data == "item_bot":
        text = (
            "🤖 <b>Разработка Telegram-бота</b>\n\n"
            "Создание ботов любой сложности под ключ (aiogram 3, базы данных, админки).\n\n"
            "⏱ <b>Срок:</b> 1-3 дня\n"
            "💰 <b>Цена:</b> от 2 000 ₽"
        )
        photo = BOT_DEV_IMAGE
        reply_markup = catalog_kb()

    elif callback.data == "item_parser":
        text = (
            "📊 <b>Парсер данных / Скрипты</b>\n\n"
            "Автоматический сбор информации с сайтов, выгрузка в Excel/Telegram/БД.\n\n"
            "⏱ <b>Срок:</b> 1 день\n"
            "💰 <b>Цена:</b> от 1 000 ₽"
        )
        photo = PARSER_IMAGE
        reply_markup = catalog_kb()

    elif callback.data == "item_star":
        text = (
            "⭐ <b>Тестовая цифровая услуга</b>\n\n"
            "Проверка встроенной оплаты через Telegram Stars.\n"
            "Списание происходит моментально прямо внутри мессенджера.\n\n"
            "💰 <b>Стоимость:</b> 1 Telegram Star"
        )
        photo = TEST_STAR_IMAGE
        reply_markup = buy_star_kb()

    # Изменяем картинку и текст под ней прямо в существующем сообщении
    media = InputMediaPhoto(media=photo, caption=text, parse_mode="HTML")
    await callback.message.edit_media(media=media, reply_markup=reply_markup)
    await callback.answer()


# ==================== ОПЛАТА TELEGRAM STARS ====================
@dp.callback_query(F.data == "pay_star")
async def send_star_invoice(callback: types.CallbackQuery):
    prices = [LabeledPrice(label="Тестовая услуга", amount=1)]

    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title="Тестовая покупка",
        description="Покупка тестовой услуги за 1 Telegram Star",
        payload="test_star_payment_payload",
        provider_token="",  # Для Stars token пустой
        currency="XTR",
        prices=prices,
        photo_url=TEST_STAR_IMAGE,  # Картинка в счёте оплаты
    )
    await callback.answer()


@dp.pre_checkout_query()
async def process_pre_checkout_query(
    pre_checkout_query: PreCheckoutQuery,
):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message(F.successful_payment)
async def process_successful_payment(message: types.Message):
    await message.answer(
        "🎉 <b>Спасибо за оплату!</b>\n\n"
        "Ваш платёж за 1 Telegram Star успешно принят.",
        parse_mode="HTML",
        reply_markup=main_kb(),
    )

    admin_text = (
        f"⭐ <b>Новая оплата Stars!</b>\n\n"
        f"👤 Покупатель: {message.from_user.first_name} (@{message.from_user.username})\n"
        f"💬 User ID: <code>{message.from_user.id}</code>\n"
        f"Сумма: 1 Telegram Star"
    )
    try:
        await bot.send_message(
            chat_id=ADMIN_ID, text=admin_text, parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"Не удалось отправить уведомление админу: {e}")


@dp.message(F.text == "ℹ️️ О нас")
async def about_us(message: types.Message):
    await message.answer(
        "Разрабатываем качественные решения для бизнеса и Telegram-каналов."
    )


@dp.message(F.text == "📞 Контакты")
async def contacts(message: types.Message):
    await message.answer("Разработчик: @Dujoa")


# ==================== СБОР ЗАЯВКИ (FSM) ====================
@dp.message(F.text == "📝 Оставить заявку")
@dp.callback_query(F.data == "start_order")
async def start_order(
    event: types.Message | types.CallbackQuery, state: FSMContext
):
    await state.set_state(OrderForm.name)
    text = "Как к вам обращаться?\n\n(Вы можете нажать «❌ Отмена» для выхода)"

    if isinstance(event, types.CallbackQuery):
        await event.message.answer(text, reply_markup=cancel_kb())
        await event.answer()
    else:
        await event.answer(text, reply_markup=cancel_kb())


@dp.message(OrderForm.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(OrderForm.phone)
    await message.answer(
        "Укажите ваш номер телефона или @username для связи:",
        reply_markup=cancel_kb(),
    )


@dp.message(OrderForm.phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(OrderForm.details)
    await message.answer(
        "Опишите коротко вашу задачу:", reply_markup=cancel_kb()
    )


@dp.message(OrderForm.details)
async def process_details(message: types.Message, state: FSMContext):
    await state.update_data(details=message.text)
    data = await state.get_data()

    order_info = {
        "name": data["name"],
        "phone": data["phone"],
        "details": data["details"],
        "user_id": message.from_user.id,
        "username": message.from_user.username or "нет_юзернейма",
    }
    ORDERS_DB.append(order_info)

    admin_text = (
        f"🚨 <b>Новая заявка!</b>\n\n"
        f"👤 <b>Имя:</b> {data['name']}\n"
        f"📞 <b>Контакт:</b> {data['phone']}\n"
        f"💬 <b>User ID:</b> <code>{message.from_user.id}</code>\n"
        f"📋 <b>Задача:</b> {data['details']}"
    )

    try:
        await bot.send_message(
            chat_id=ADMIN_ID, text=admin_text, parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"Не удалось отправить сообщение админу: {e}")

    await message.answer(
        "Спасибо! Заявка принята, скоро с вами свяжутся.",
        reply_markup=main_kb(),
    )
    await state.clear()


# ==================== ЗАПУСК ====================
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())