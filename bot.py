import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
SESSION_STRING = os.environ["SESSION_STRING"]

DESTINATION = os.getenv("DESTINATION", "@GoalZone_fotball")

SOURCES = [
    "@ADAK_IR",
    "@FOTBALL",
    "@FOOTBALFA",
    "@HVARZESHVARONE",
]

user_client = TelegramClient(
    StringSession(SESSION_STRING),
    API_ID,
    API_HASH
)

bot_client = TelegramClient(
    StringSession(),
    API_ID,
    API_HASH
)


@user_client.on(events.NewMessage(chats=SOURCES))
async def forward_new_post(event):
    try:
        message = event.message

        if message.media:
            await bot_client.send_file(
                DESTINATION,
                message.media,
                caption=message.text or "",
                parse_mode=None
            )

        elif message.text:
            await bot_client.send_message(
                DESTINATION,
                message.text,
                link_preview=False
            )

        print(
            f"Transferred: {event.chat_id} / {message.id}",
            flush=True
        )

    except Exception as error:
        print(
            f"Transfer error: {type(error).__name__}: {error}",
            flush=True
        )


async def main():
    await user_client.start()

    print("GoalZone Auto Bot is ONLINE.", flush=True)
    print("Sources:", ", ".join(SOURCES), flush=True)
    print("Destination:", DESTINATION, flush=True)

    await asyncio.gather(
        user_client.run_until_disconnected(),
        bot_client.run_until_disconnected()
    )


if __name__ == "__main__":
    asyncio.run(main())
