import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()


class VolareBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.load_extension("reactions")
        await self.tree.sync()

    async def on_ready(self):
        print(f"已登入：{self.user}（ID：{self.user.id}）")
        print(f"已同步 {len(self.tree.get_commands())} 個斜線指令")


async def main():
    async with VolareBot() as bot:
        await bot.start(os.getenv("DISCORD_TOKEN"))


asyncio.run(main())
