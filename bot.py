import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from discord.ext.commands.errors import MemberNotFound, NotOwner, UserNotFound, GuildNotFound, NSFWChannelRequired, NotOwner, CommandOnCooldown

intents = discord.Intents().all()
aliases = ['j!', 'J!', 'jeanne ', 'Jeanne ']
bot = commands.Bot(command_prefix=aliases, intents=intents)

bot.remove_command('help')

bot.load_extension("cogs.moderation")
bot.load_extension("cogs.help")
bot.load_extension("cogs.misc")
bot.load_extension("cogs.fun")
bot.load_extension("cogs.manage")
bot.load_extension("cogs.info")
bot.load_extension("cogs.owner")
bot.load_extension("cogs.reactions")


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game('DiscordBots'))
    print('Connected to bot: {}'.format(bot.user.name))
    print('Bot ID: {}'.format(bot.user.id))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, NotOwner):
       embed = discord.Embed(
           title="Owner only command", description="This command failed to commit because you are not the bot owner", color=0xff0000)
       await ctx.send(embed=embed)
    elif isinstance(error, GuildNotFound):
        embed = discord.Embed(
            description="Bot is not in this server", color=0xff0000)
        await ctx.send(embed=embed)
    elif isinstance(error, UserNotFound):
            no_user = discord.Embed(
                title="User does not exist", description="Please make sure the USER_ID is valid or maybe they have deleted their account.", color=0xff0000)
            await ctx.send(embed=no_user)
    elif isinstance(error, CommandOnCooldown):
        embed = discord.Embed(
            title="Command On Cooldown", description=f"This command is on cooldown. Please wait at least {error.retry_after: .2f} seconds to use it again.", color=0xff0000)
        await ctx.send(embed=embed)
    elif isinstance(error, NSFWChannelRequired):
        error = discord.Embed(
            title='Hentai Failed', description="Hentai couldn't be sent in this channel", color=0xff0000)
        error.add_field(
            name="Reason", value="Channel is not NSFW enabled")
        await ctx.send(embed=error)

load_dotenv()
TOKEN = os.getenv("token")
bot.run(TOKEN)
