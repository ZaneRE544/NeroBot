import argparse
from random import randint
from discord import Color, Embed, HTTPException, Message
from discord.ext.commands import Bot, Cog, group, Context, Range, BucketType
import discord.ext.commands as Jeanne
from functions import BetaTest, Botban, Command, Hentai, shorten_url
from typing import Literal, Optional
from assets.components import ReportContent, ReportSelect


class nsfw(Cog, name="hentai"):
    def __init__(self, bot: Bot):
        self.bot = bot

    rating_parser = argparse.ArgumentParser(add_help=False)
    rating_parser.add_argument(
        "--rating",
        "-r",
        type=str,
        choices=["questionable", "explicit", "e", "q"],
        help="questionable | explicit | q | e",
        required=False,
        default=None,
    )

    hentai_api_parser = argparse.ArgumentParser(add_help=False)
    hentai_api_parser.add_argument(
        "--rating",
        "-r",
        type=str,
        choices=["questionable", "explicit", "e", "q"],
        required=False,
        default=None,
    )
    hentai_api_parser.add_argument(
        "--tags", "-t", type=str, nargs="+", required=False, default=[], help="tags"
    )
    hentai_api_parser.add_argument(
        "--plus", "-p", action="store_true", help="Enable plus mode"
    )

    @Jeanne.command(description="Get a random hentai from Jeanne", nsfw=True)
    @Jeanne.cooldown(1, 5, type=BucketType.member)
    async def hentai(
        self, ctx: Context, *, words: str = None, parser=rating_parser
    ) -> None:
        if Botban(ctx.author).check_botbanned_user:
            return

        if Command(ctx.guild).check_disabled(self.hentai.qualified_name):
            await ctx.send(
                "This command is disabled by the server's managers", ephemeral=True
            )
            return
        check = await BetaTest(self.bot).check(ctx.author)

        if check == True:

            await ctx.defer()
            try:
                parser = parser.parse_args(words.split())
                rating = parser.rating
            except SystemExit:
                await ctx.send(
                    embed=Embed(
                        description=f"You are missing some arguments or using incorrect arguments for this command",
                        color=Color.red(),
                    )
                )
                return
            except AttributeError:
                rating = None

            hentai, source = await Hentai().hentai(rating)
            is_mp4 = hentai.endswith("mp4")

            if is_mp4:
                view = ReportContent(shorten_url(hentai))
                m = await ctx.send(hentai, view=view)
            else:
                embed = (
                    Embed(color=Color.purple())
                    .set_image(url=hentai)
                    .set_footer(
                        text="Fetched from {} • Credits must go to the artist".format(
                            source
                        )
                    )
                )
                view = ReportContent(shorten_url(hentai))
                m: Message = await ctx.send(embed=embed, view=view)

            await view.wait()

            if view.value is None:
                await m.edit(view=None)
                return
        await ctx.send(
            embed=Embed(
                description="Uh Oh!\n\nIt seems you are trying something that is meant for beta users.\nIf you wish to join the beta programme, join [Orleans](https://discord.gg/Vfa796yvNq) and ask the bot developer.",
                color=Color.red(),
            ),
            ephemeral=True,
        )

    @hentai.error
    async def hentai_error(self, ctx: Context, error: Jeanne.CommandError):
        if isinstance(error, Jeanne.CommandInvokeError) and isinstance(
            error.original, HTTPException
        ):
            check = await BetaTest(self.bot).check(ctx.author)
            if Command(ctx.guild).check_disabled(self.hentai.qualified_name):
                await ctx.send(
                    "This command is disabled by the server's managers", ephemeral=True
                )
                return
            if check == True:
                slow = Embed(
                    description="WOAH! Slow down!\nI know you are horny but geez... I am at my limit",
                    color=Color.red(),
                )
                await ctx.send(embed=slow)
                return
            await ctx.send(
                embed=Embed(
                    description="Uh Oh!\n\nIt seems you are trying something that is meant for beta users.\nIf you wish to join the beta programme, join [Orleans](https://discord.gg/Vfa796yvNq) and ask the bot developer.",
                    color=Color.red(),
                ),
                ephemeral=True,
            )
            return
        if isinstance(error, Jeanne.CommandOnCooldown):
            if check == True:
                slow = Embed(
                    description="WOAH! Slow down!\nI know you are horny but geez... I am at my limit",
                    color=Color.red(),
                )
                await ctx.send(embed=slow)
                return
            await ctx.send(
                embed=Embed(
                    description="Uh Oh!\n\nIt seems you are trying something that is meant for beta users.\nIf you wish to join the beta programme, join [Orleans](https://discord.gg/Vfa796yvNq) and ask the bot developer.",
                    color=Color.red(),
                ),
                ephemeral=True,
            )

    @Jeanne.command(description="Get a random media content from Gelbooru", nsfw=True)
    @Jeanne.cooldown(1, 5, type=BucketType.member)
    async def gelbooru(
        self,
        ctx: Context,
        *words: str,
        parser=hentai_api_parser,
    ) -> None:
        if Botban(ctx.author).check_botbanned_user:
            return
        if Command(ctx.guild).check_disabled(self.gelbooru.qualified_name):
            await ctx.send(
                "This command is disabled by the server's managers", ephemeral=True
            )
            return
        check = await BetaTest(self.bot).check(ctx.author)

        if check == True:
            await ctx.defer()

            try:
                parsed_args, unknown = parser.parse_known_args(words)
                tags = parsed_args.tags + unknown
                tags = " ".join(tags)

                plus = parsed_args.plus
                rating = parsed_args.rating
            except SystemExit:
                await ctx.send(
                    embed=Embed(
                        description=f"You are missing some arguments or using incorrect arguments for this command",
                        color=Color.red(),
                    )
                )
                return

            image = await Hentai(plus).gelbooru(rating, tags)

            if plus:
                images = [image[randint(1, len(image)) - 1] for _ in range(4)]
                view = ReportSelect(*[img["file_url"] for img in images])

                vids = [i for i in images if "mp4" in i["file_url"]]
                media = [j["file_url"] for j in vids]

                if media:
                    m: Message = await ctx.send("\n".join(media), view=view)
                    await view.wait()

                    if view.value is None:
                        await m.edit(view=None)
                    return

                color = Color.random()
                embeds = [
                    Embed(color=color, url="https://gelbooru.com")
                    .set_image(url=img["file_url"])
                    .set_footer(
                        text="Fetched from Gelbooru • Credits must go to the artist"
                    )
                    for img in images
                ]
                m: Message = await ctx.send(embeds=embeds, view=view)
                await view.wait()

                if view.value is None:
                    await m.edit(view=None)
                return

            try:
                view = ReportContent(image)
                if str(image).endswith("mp4"):
                    m: Message = await ctx.send(image, view=view)
                    await view.wait()
                    if view.value is None:
                        await m.edit(view=None)
                    return

                embed = (
                    Embed(color=Color.purple())
                    .set_image(url=image)
                    .set_footer(
                        text="Fetched from Gelbooru • Credits must go to the artist"
                    )
                )
                m: Message = await ctx.send(embed=embed, view=view)
                await view.wait()

                if view.value is None:
                    await m.edit(view=None)
            except:
                if str(image).endswith("mp4"):
                    await ctx.send(image)
                    return

                embed = (
                    Embed(color=Color.purple())
                    .set_image(url=image)
                    .set_footer(
                        text="Fetched from Gelbooru • Credits must go to the artist\nIf you see an illegal content, please use /botreport and attach the link when reporting"
                    )
                )
                await ctx.send(embed=embed)
                return
        await ctx.send(
            embed=Embed(
                description="Uh Oh!\n\nIt seems you are trying something that is meant for beta users.\nIf you wish to join the beta programme, join [Orleans](https://discord.gg/Vfa796yvNq) and ask the bot developer.",
                color=Color.red(),
            ),
            ephemeral=True,
        )

    @gelbooru.error
    async def gelbooru_error(self, ctx: Context, error: Jeanne.CommandError):
        if isinstance(error, Jeanne.CommandInvokeError) and isinstance(
            error.original, (IndexError, KeyError, ValueError)
        ):
            check = await BetaTest(self.bot).check(ctx.author)

            if check == True:
                if Command(ctx.guild).check_disabled(self.gelbooru.qualified_name):
                    await ctx.send(
                        "This command is disabled by the server's managers", ephemeral=True
                    )
                    return
                no_tag = Embed(
                    description="The hentai could not be found", color=Color.red()
                )
                await ctx.send(embed=no_tag)
                return
            await ctx.send(
                embed=Embed(
                    description="Uh Oh!\n\nIt seems you are trying something that is meant for beta users.\nIf you wish to join the beta programme, join [Orleans](https://discord.gg/Vfa796yvNq) and ask the bot developer.",
                    color=Color.red(),
                ),
                ephemeral=True,
            )
        if isinstance(error, Jeanne.CommandInvokeError) and isinstance(
            error.original, HTTPException
        ):
            check = await BetaTest(self.bot).check(ctx.author)

            if check == True:
                if Command(ctx.guild).check_disabled(self.gelbooru.qualified_name):
                    await ctx.send(
                        "This command is disabled by the server's managers", ephemeral=True
                    )
                    return
                slow = Embed(
                    description="WOAH! Slow down!\nI know you are horny but geez... I am at my limit",
                    color=Color.red(),
                )
                await ctx.send(embed=slow)
                return
            await ctx.send(
                embed=Embed(
                    description="Uh Oh!\n\nIt seems you are trying something that is meant for beta users.\nIf you wish to join the beta programme, join [Orleans](https://discord.gg/Vfa796yvNq) and ask the bot developer.",
                    color=Color.red(),
                ),
                ephemeral=True,
            )

    @Jeanne.command(description="Get a random hentai from Yande.re", nsfw=True)
    @Jeanne.cooldown(1, 5, type=BucketType.member)
    async def yandere(
        self, ctx: Context, *words: str, parser=hentai_api_parser
    ) -> None:
        if Botban(ctx.author).check_botbanned_user:
            return
        if Command(ctx.guild).check_disabled(self.yandere.qualified_name):
            await ctx.send(
                "This command is disabled by the server's managers", ephemeral=True
            )
            return
        check = await BetaTest(self.bot).check(ctx.author)

        if check == True:
            await ctx.defer()

            try:
                parsed_args, unknown = parser.parse_known_args(words)
                tags = parsed_args.tags + unknown
                tag = " ".join(tags)

                plus = parsed_args.plus
                rating = parsed_args.rating
            except SystemExit:
                await ctx.send(
                    embed=Embed(
                        description=f"You are missing some arguments or using incorrect arguments for this command",
                        color=Color.red(),
                    )
                )
                return

            if tag == "02":
                await ctx.send(
                    "Tag has been blacklisted due to it returning extreme content"
                )
                return

            image = await Hentai(plus).yandere(rating, tag)

            if plus:
                images = [image[randint(1, len(image)) - 1] for _ in range(4)]
                shortened_urls = [shorten_url(img["file_url"]) for img in images]
                view = ReportSelect(*shortened_urls)
                color = Color.random()
                embeds = [
                    Embed(color=color, url="https://yande.re")
                    .set_image(url=(str(url)))
                    .set_footer(
                        text="Fetched from Yande.re • Credits must go to the artist"
                    )
                    for url in shortened_urls
                ]
                footer_text = "Fetched from Yande.re • Credits must go to the artist"
                try:
                    m: Message = await ctx.send(embeds=embeds, view=view)
                    await view.wait()
                    if view.value == None:
                        await m.edit(view=None)

                except:
                    footer_text += "\nIf you see an illegal content, please use /botreport and attach the link when reporting"
                    for embed in embeds:
                        embed.set_footer(text=footer_text)
                    await ctx.send(embeds=embeds)
                return
            color = Color.random()
            shortened_url = shorten_url(str(image))
            embed = Embed(color=color, url="https://yande.re")
            embed.set_image(url=shortened_url)
            footer_text = "Fetched from Yande.re • Credits must go to the artist"
            try:
                view = ReportContent(shortened_url)
                embed.set_footer(text=footer_text)
                m: Message = await ctx.send(embed=embed, view=view)
                await view.wait()

                if view.value == None:
                    await m.edit(view=None)
            except:
                footer_text += "\nIf you see an illegal content, please use /botreport and attach the link when reporting"
                embed.set_footer(text=footer_text)
                await ctx.send(embed=embed)
                return
        await ctx.send(
            embed=Embed(
                description="Uh Oh!\n\nIt seems you are trying something that is meant for beta users.\nIf you wish to join the beta programme, join [Orleans](https://discord.gg/Vfa796yvNq) and ask the bot developer.",
                color=Color.red(),
            ),
            ephemeral=True,
        )

    @yandere.error
    async def yandere_error(self, ctx: Context, error: Jeanne.CommandError):
        if isinstance(error, Jeanne.CommandInvokeError) and isinstance(
            error.original, (IndexError, KeyError, ValueError)
        ):
            check = await BetaTest(self.bot).check(ctx.author)

            if check == True:
                if Command(ctx.guild).check_disabled(self.yandere.qualified_name):
                    await ctx.send(
                        "This command is disabled by the server's managers",
                        ephemeral=True,
                    )
                    return
                no_tag = Embed(
                    description="The hentai could not be found", color=Color.red()
                )
                await ctx.send(embed=no_tag)
                return
            await ctx.send(
                embed=Embed(
                    description="Uh Oh!\n\nIt seems you are trying something that is meant for beta users.\nIf you wish to join the beta programme, join [Orleans](https://discord.gg/Vfa796yvNq) and ask the bot developer.",
                    color=Color.red(),
                ),
                ephemeral=True,
            )
        if isinstance(error, Jeanne.CommandInvokeError) and isinstance(
            error.original, HTTPException
        ):
            check = await BetaTest(self.bot).check(ctx.author)

            if check == True:
                if Command(ctx.guild).check_disabled(self.yandere.qualified_name):
                    await ctx.send(
                        "This command is disabled by the server's managers",
                        ephemeral=True,
                    )
                    return
                slow = Embed(
                    description="WOAH! Slow down!\nI know you are horny but geez... I am at my limit",
                    color=Color.red(),
                )
                await ctx.send(embed=slow)
                return
            await ctx.send(
                embed=Embed(
                    description="Uh Oh!\n\nIt seems you are trying something that is meant for beta users.\nIf you wish to join the beta programme, join [Orleans](https://discord.gg/Vfa796yvNq) and ask the bot developer.",
                    color=Color.red(),
                ),
                ephemeral=True,
            )

    @Jeanne.command(description="Get a random hentai from Konachan", nsfw=True)
    @Jeanne.cooldown(1, 5, type=BucketType.member)
    async def konachan(
        self, ctx: Context, *words: str, parser=hentai_api_parser
    ) -> None:
        if Botban(ctx.author).check_botbanned_user:
            return

        if Command(ctx.guild).check_disabled(self.konachan.qualified_name):
            await ctx.send(
                "This command is disabled by the server's managers", ephemeral=True
            )
            return
        check = await BetaTest(self.bot).check(ctx.author)

        if check == True:
            await ctx.defer()

            try:
                parsed_args, unknown = parser.parse_known_args(words)
                tags = parsed_args.tags + unknown
                tag = " ".join(tags)

                plus = parsed_args.plus
                rating = parsed_args.rating
            except SystemExit:
                await ctx.send(
                    embed=Embed(
                        description=f"You are missing some arguments or using incorrect arguments for this command",
                        color=Color.red(),
                    )
                )
                return

            image = await Hentai(plus).konachan(rating, tag)

            if plus:
                images = [image[randint(1, len(image)) - 1] for _ in range(4)]
                try:
                    shortened_urls = [shorten_url(img["file_url"]) for img in images]
                    view = ReportSelect(*shortened_urls)
                    color = Color.random()
                    embeds = [
                        Embed(color=color, url="https://konachan.com")
                        .set_image(url=str(url))
                        .set_footer(
                            text="Fetched from Konachan • Credits must go to the artist"
                        )
                        for url in shortened_urls
                    ]
                    footer_text = (
                        "Fetched from Konachan • Credits must go to the artist"
                    )

                    m: Message = await ctx.send(embeds=embeds, view=view)
                    await view.wait()
                    if view.value == None:
                        await m.edit(view=None)

                except:
                    color = Color.random()
                    embeds = [
                        Embed(color=color, url="https://konachan.com")
                        .set_image(url=str(url["image_url"]))
                        .set_footer(
                            text="Fetched from Konachan • Credits must go to the artist"
                        )
                        for url in images
                    ]
                    footer_text += "\nIf you see an illegal content, please use /botreport and attach the link when reporting"
                    for embed in embeds:
                        embed.set_footer(text=footer_text)
                    await ctx.send(embeds=embeds)
                return

            color = Color.random()
            embed = Embed(color=color, url="https://konachan.com")
            embed.set_image(url=shorten_url(str(image)))
            footer_text = "Fetched from Konachan • Credits must go to the artist"
            try:
                view = ReportContent(shorten_url(str(image)))
                embed.set_footer(text=footer_text)
                m: Message = await ctx.send(embed=embed, view=view)
                await view.wait()

                if view.value == None:
                    await m.edit(view=None)
            except:
                footer_text += "\nIf you see an illegal content, please use /botreport and attach the link when reporting"
                embed.set_footer(text=footer_text)
                await ctx.send(embed=embed)
                return
        await ctx.send(
            embed=Embed(
                description="Uh Oh!\n\nIt seems you are trying something that is meant for beta users.\nIf you wish to join the beta programme, join [Orleans](https://discord.gg/Vfa796yvNq) and ask the bot developer.",
                color=Color.red(),
            ),
            ephemeral=True,
        )

    @konachan.error
    async def konachan_error(self, ctx: Context, error: Jeanne.CommandError):
        if isinstance(error, Jeanne.CommandInvokeError) and isinstance(
            error.original, (IndexError, KeyError, ValueError)
        ):
            check = await BetaTest(self.bot).check(ctx.author)

            if check == True:
                if Command(ctx.guild).check_disabled(self.konachan.qualified_name):
                    await ctx.send(
                        "This command is disabled by the server's managers",
                        ephemeral=True,
                    )
                    return
                no_tag = Embed(
                    description="The hentai could not be found", color=Color.red()
                )
                await ctx.send(embed=no_tag)
                return
            await ctx.send(
                embed=Embed(
                    description="Uh Oh!\n\nIt seems you are trying something that is meant for beta users.\nIf you wish to join the beta programme, join [Orleans](https://discord.gg/Vfa796yvNq) and ask the bot developer.",
                    color=Color.red(),
                ),
                ephemeral=True,
            )
        if isinstance(error, Jeanne.CommandInvokeError) and isinstance(
            error.original, HTTPException
        ):
            check = await BetaTest(self.bot).check(ctx.author)

            if check == True:
                if Command(ctx.guild).check_disabled(self.konachan.qualified_name):
                    await ctx.send(
                        "This command is disabled by the server's managers",
                        ephemeral=True,
                    )
                    return
                slow = Embed(
                    description="WOAH! Slow down!\nI know you are horny but geez... I am at my limit",
                    color=Color.red(),
                )
                await ctx.send(embed=slow)
                return
            await ctx.send(
                embed=Embed(
                    description="Uh Oh!\n\nIt seems you are trying something that is meant for beta users.\nIf you wish to join the beta programme, join [Orleans](https://discord.gg/Vfa796yvNq) and ask the bot developer.",
                    color=Color.red(),
                ),
                ephemeral=True,
            )

    @Jeanne.command(description="Get a random media content from Danbooru", nsfw=True)
    @Jeanne.cooldown(1, 5, type=BucketType.member)
    async def danbooru(
        self, ctx: Context, *words: str, parser=hentai_api_parser
    ) -> None:
        if Botban(ctx.author).check_botbanned_user:
            return
        if Command(ctx.guild).check_disabled(self.danbooru.qualified_name):
            await ctx.send(
                "This command is disabled by the server's managers", ephemeral=True
            )
            return
        check = await BetaTest(self.bot).check(ctx.author)

        if check == True:
            await ctx.defer()
            try:
                parsed_args, unknown = parser.parse_known_args(words)
                tags = parsed_args.tags + unknown
                tag = " ".join(tags)

                plus = parsed_args.plus
                rating = parsed_args.rating
            except SystemExit:
                await ctx.send(
                    embed=Embed(
                        description=f"You are missing some arguments or using incorrect arguments for this command",
                        color=Color.red(),
                    )
                )
                return
            image = await Hentai(plus).danbooru(rating, tag)

            if plus:
                images = [image[randint(1, len(image)) - 1] for _ in range(4)]
                view = ReportSelect(*[img["file_url"] for img in images])
                vids = [i for i in images if "mp4" in i["file_url"]]
                media = [j["file_url"] for j in vids]

                if media:
                    m: Message = await ctx.send("\n".join(media), view=view)
                    await view.wait()
                    if view.value == None:
                        await m.edit(view=None)
                    return

                color = Color.random()
                embeds = [
                    Embed(color=color, url="https://danbooru.donmai.us/")
                    .set_image(url=img["file_url"])
                    .set_footer(
                        text="Fetched from Danbooru • Credits must go to the artist"
                    )
                    for img in images
                ]
                await ctx.send(embeds=embeds, view=view)
                return

            try:
                view = ReportContent(image)
                if str(image).endswith("mp4"):
                    await ctx.send(image, view=view)
                    return

                embed = (
                    Embed(color=Color.purple())
                    .set_image(url=image)
                    .set_footer(
                        text="Fetched from Danbooru • Credits must go to the artist"
                    )
                )
                m: Message = await ctx.send(embed=embed, view=view)
                await view.wait()

                if view.value == None:
                    await m.edit(view=None)
            except:
                if str(image).endswith("mp4"):
                    await ctx.send(image)
                    return

                embed = (
                    Embed(color=Color.purple())
                    .set_image(url=image)
                    .set_footer(
                        text="Fetched from Danbooru • Credits must go to the artist\nIf you see an illegal content, please use /botreport and attach the link when reporting"
                    )
                )
                await ctx.send(embed=embed)
                return
        await ctx.send(
            embed=Embed(
                description="Uh Oh!\n\nIt seems you are trying something that is meant for beta users.\nIf you wish to join the beta programme, join [Orleans](https://discord.gg/Vfa796yvNq) and ask the bot developer.",
                color=Color.red(),
            ),
            ephemeral=True,
        )

    @danbooru.error
    async def danbooru_error(self, ctx: Context, error: Jeanne.CommandError):
        if isinstance(error, Jeanne.CommandInvokeError) and isinstance(
            error.original, (IndexError, KeyError, ValueError)
        ):
            check = await BetaTest(self.bot).check(ctx.author)

            if check == True:
                if Command(ctx.guild).check_disabled(self.danbooru.qualified_name):
                    await ctx.send(
                        "This command is disabled by the server's managers",
                        ephemeral=True,
                    )
                    return
                no_tag = Embed(
                    description="The hentai could not be found", color=Color.red()
                )
                await ctx.send(embed=no_tag)
                return
            await ctx.send(
                embed=Embed(
                    description="Uh Oh!\n\nIt seems you are trying something that is meant for beta users.\nIf you wish to join the beta programme, join [Orleans](https://discord.gg/Vfa796yvNq) and ask the bot developer.",
                    color=Color.red(),
                ),
                ephemeral=True,
            )
        if isinstance(error, Jeanne.CommandInvokeError) and isinstance(
            error.original, HTTPException
        ):
            check = await BetaTest(self.bot).check(ctx.author)

            if check == True:
                if Command(ctx.guild).check_disabled(self.danbooru.qualified_name):
                    await ctx.send(
                        "This command is disabled by the server's managers",
                        ephemeral=True,
                    )
                    return
                slow = Embed(
                    description="WOAH! Slow down!\nI know you are horny but geez... I am at my limit",
                    color=Color.red(),
                )
                await ctx.send(embed=slow)
                return
            await ctx.send(
                embed=Embed(
                    description="Uh Oh!\n\nIt seems you are trying something that is meant for beta users.\nIf you wish to join the beta programme, join [Orleans](https://discord.gg/Vfa796yvNq) and ask the bot developer.",
                    color=Color.red(),
                ),
                ephemeral=True,
            )


async def setup(bot: Bot):
    await bot.add_cog(nsfw(bot))
