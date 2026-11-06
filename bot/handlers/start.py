"""Menu inicial. Os módulos entram em handlers próprios nas próximas tarefas."""

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

router = Router(name="start")

MENU_BUTTONS = ("🏋️ Treino", "🥗 Dieta", "💧 Água", "✅ Tarefas")

HELP = (
    "<b>Omnifit</b>\n\n"
    "/start — menu principal\n"
    "/ajuda — esta mensagem\n\n"
    "Os registros por mensagem serão habilitados módulo a módulo."
)


def main_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for label in MENU_BUTTONS:
        builder.button(text=label)
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


@router.message(CommandStart())
async def start(message: Message) -> None:
    name = message.from_user.first_name if message.from_user else ""
    greeting = f"Olá, {name}!" if name else "Olá!"
    await message.answer(
        f"{greeting} Sou o <b>Omnifit</b>.\nEscolha um módulo para começar.",
        reply_markup=main_menu(),
    )


@router.message(Command("ajuda"))
async def help_command(message: Message) -> None:
    await message.answer(HELP)


@router.message(F.text)
async def fallback(message: Message) -> None:
    await message.answer("Ainda não implementado. Use /ajuda.")
