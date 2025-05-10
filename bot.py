import logging
import warnings
import asyncio
from datetime import datetime

from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from aiohttp import web
from pytz import timezone

from config import Config
import pyromod


# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# Dummy web server function (you can modify this)
async def web_server():
    async def handle(request):
        return web.Response(text="Bot is running!")
    app = web.Application()
    app.router.add_get("/", handle)
    return app


class Bot(Client):
    def __init__(self):
        super().__init__(
            name="PiratesBotRepo",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            workers=200,
            plugins={"root": "plugins"},
            sleep_threshold=15,
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.mention = me.mention
        self.username = me.username

        runner = web.AppRunner(await web_server())
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", Config.PORT)
        await site.start()

        logger.info(f"{me.first_name} ✅ Bot started successfully")

        for admin_id in Config.ADMIN:
            try:
                await self.send_message(admin_id, f"**__{me.first_name} is started.....✨️__**")
            except Exception as e:
                logger.warning(f"Failed to send start message to admin {admin_id}: {e}")

        if Config.LOG_CHANNEL:
            try:
                curr = datetime.now(timezone("Asia/Kolkata"))
                date = curr.strftime("%d %B, %Y")
                time = curr.strftime("%I:%M:%S %p")
                await self.send_message(
                    Config.LOG_CHANNEL,
                    f"**__{me.mention} is restarted !!__**\n\n"
                    f"📅 Date : `{date}`\n"
                    f"⏰ Time : `{time}`\n"
                    f"🌐 Timezone : `Asia/Kolkata`\n"
                    f"🤖 Version : `v{__version__} (Layer {layer})`"
                )
            except Exception:
                logger.warning("⚠️ Please make sure the bot is admin in your log channel!")

    async def stop(self, *args):
        await super().stop()
        logger.info("Bot stopped gracefully.")


# Start the bot
if __name__ == "__main__":
    warnings.filterwarnings("ignore", message="There is no current event loop")
    bot = Bot()
    asyncio.run(bot.start())
