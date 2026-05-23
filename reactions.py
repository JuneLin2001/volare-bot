import asyncio
import discord
from discord import app_commands
from discord.ext import commands


class ReactionsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="reactions", description="標記指定訊息的所有反應用戶")
    @app_commands.describe(
        message_id="目標訊息的 ID",
        custom_message="附加在 @mention 後的自訂訊息（可選）",
    )
    async def list_reactions(
        self,
        interaction: discord.Interaction,
        message_id: str,
        custom_message: str = "",
    ):
        await interaction.response.defer()

        try:
            target_msg = await interaction.channel.fetch_message(int(message_id))
        except ValueError:
            await interaction.followup.send("訊息 ID 必須是數字。", ephemeral=True)
            return
        except discord.NotFound:
            await interaction.followup.send("找不到該訊息。", ephemeral=True)
            return
        except discord.Forbidden:
            await interaction.followup.send("我沒有權限讀取該頻道。", ephemeral=True)
            return

        if not target_msg.reactions:
            await interaction.followup.send("該訊息沒有任何 ✅ 反應。", ephemeral=True)
            return

        seen = set()
        mentions = []
        for reaction in target_msg.reactions:
            if str(reaction.emoji) != "✅":
                continue
            async for user in reaction.users():
                if user.bot or user.id in seen:
                    continue
                seen.add(user.id)
                mentions.append(user.mention)

        if not mentions:
            await interaction.followup.send("該訊息沒有任何 ✅ 反應。", ephemeral=True)
            return

        safe_mentions = discord.AllowedMentions(everyone=False, users=True, roles=False)
        all_mentions = " ".join(mentions)
        message = f"{all_mentions}\n{custom_message}" if custom_message else all_mentions

        if len(message) <= 2000:
            await interaction.followup.send(message, allowed_mentions=safe_mentions)
            return

        chunks, current = [], ""
        for mention in mentions:
            if len(current) + len(mention) + 1 > 2000:
                chunks.append(current)
                current = mention
            else:
                current += (" " if current else "") + mention
        if current:
            chunks.append(current)

        for chunk in chunks[:-1]:
            await interaction.followup.send(chunk, allowed_mentions=safe_mentions)
            await asyncio.sleep(0.5)

        last = f"{chunks[-1]}\n{custom_message}" if custom_message else chunks[-1]
        await interaction.followup.send(last, allowed_mentions=safe_mentions)


async def setup(bot: commands.Bot):
    await bot.add_cog(ReactionsCog(bot))
