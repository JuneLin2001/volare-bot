import asyncio
import discord
from discord.ext import commands


class ReactionsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="reactions")
    async def list_reactions(
        self,
        ctx: commands.Context,
        *,
        custom_message: str = "",
    ):
        """
        用法：回覆一則訊息，再輸入 !reactions 自訂訊息
        """
        no_ping = discord.AllowedMentions(everyone=False, users=False, roles=False)

        if not ctx.message.reference:
            await ctx.reply("請回覆一則訊息後再使用此指令。", allowed_mentions=no_ping)
            return

        try:
            target_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        except discord.NotFound:
            await ctx.reply("找不到該訊息。", allowed_mentions=no_ping)
            return
        except discord.Forbidden:
            await ctx.reply("我沒有權限讀取該頻道。", allowed_mentions=no_ping)
            return

        if not target_msg.reactions:
            await ctx.reply("該訊息沒有任何反應。", allowed_mentions=no_ping)
            return

        seen = set()
        mentions = []
        for reaction in target_msg.reactions:
            async for user in reaction.users():
                if user.bot or user.id in seen:
                    continue
                seen.add(user.id)
                mentions.append(user.mention)

        if not mentions:
            await ctx.reply("該訊息沒有任何反應。", allowed_mentions=no_ping)
            return

        safe_mentions = discord.AllowedMentions(everyone=False, users=True, roles=False)
        all_mentions = " ".join(mentions)
        message = f"{custom_message}\n{all_mentions}" if custom_message else all_mentions

        if len(message) <= 2000:
            await ctx.send(message, allowed_mentions=safe_mentions)
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

        first = f"{custom_message}\n{chunks[0]}" if custom_message else chunks[0]
        await ctx.send(first, allowed_mentions=safe_mentions)
        for chunk in chunks[1:]:
            await ctx.send(chunk, allowed_mentions=safe_mentions)
            await asyncio.sleep(0.5)


async def setup(bot: commands.Bot):
    await bot.add_cog(ReactionsCog(bot))
