import discord
from discord.ext import commands
from discord import User
from discord_slash import cog_ext, SlashContext

format = "%a, %d %b %Y | %H:%M:%S %ZGMT"
class owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @cog_ext.cog_slash(description="See where which servers Jeanne is in (CREATOR ONLY)")
    @commands.is_owner()
    async def botmutuals(self, ctx:SlashContext):
        mutuals = [str(x) for x in ctx.bot.guilds]
        embed = discord.Embed(color=0xF7FF00)
        embed.add_field(name="Mutuals", value=len(ctx.bot.guilds), inline=True)
        if len(mutuals) > 25:
            mutuals = mutuals[:25]
        embed.add_field(name="Servers", value=" \n".join(
            mutuals), inline=False)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(owner(bot))
