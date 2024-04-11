import discord
from discord.ext.commands import Bot
from discord.ext.pages import Paginator, PaginatorButton
from collections import defaultdict
from dotenv import load_dotenv
import numpy as np
import cv2

from quiz import *

load_dotenv()

class StudyBot(discord.ext.commands.Cog):

    _quiz_cache = defaultdict(lambda: None)
    
    def __init__(self, bot: Bot):
        """Initializes the API connection and cache

        Args:
            bot (discord.ext.commands.Bot): Discord bot instance
            root (str): Link to the root folder
        """
        self.bot = bot
        update_tests()
        
    async def _get_user_color(self, ctx: discord.ApplicationContext) -> discord.Colour:
        avatar_byte_array = await ctx.author.display_avatar.with_format("png").read()
        arr = np.asarray(bytearray(avatar_byte_array), dtype=np.uint8)
        img = cv2.imdecode(arr, -1)
        
        red = int(np.average(img[:, :, 0]))
        green = int(np.average(img[:, :, 1]))
        blue = int(np.average(img[:, :, 2]))
        
        color_as_hex = int(f"0x{red:02x}{green:02x}{blue:02x}", base=16)

        return discord.Colour(color_as_hex)


    @discord.ext.commands.slash_command(name="select", guild_ids=[os.getenv("GUILD_ID")], description="Select which image to study")
    async def select_func(self, ctx: discord.ApplicationContext):
        items = browse()
        names = []
        for item in items:
            with open(f"./assets/quizzes/{item}/url.txt", 'r') as f:
                names.append(f.read().strip())

        paginated_list = Paginator(
            author_check=True,
            loop_pages=True,
            pages=[
                discord.Embed(
                    title=f"Select an image to study",
                    author=discord.EmbedAuthor(name=ctx.author.name, icon_url=ctx.author.display_avatar.url),
                    description=items[i],
                    color=await self._get_user_color(ctx),
                    image=names[i]
                )
                for i in range(len(items))
            ]
        )
        confirm = PaginatorButton(button_type="page_indicator", emoji="✅", disabled=False)
        
        async def callback_func(interaction: discord.Interaction):
            user = str(interaction.user.id)

            message = select(user, items[paginated_list.current_page])
            await ctx.send_followup(message, ephemeral=True)
            await paginated_list.goto_page(
                page_number=paginated_list.current_page, interaction=interaction
            )

        confirm.callback = callback_func
        paginated_list.add_button(confirm)
        
        await paginated_list.respond(ctx.interaction, ephemeral=True)
    
    @discord.ext.commands.slash_command(name="quiz", guild_ids=[os.getenv("GUILD_ID")], description="Show the currently selected quiz")
    async def show_quiz(self, ctx: discord.ApplicationContext, score:bool=True):
        user = str(ctx.author.id)
        selection = get_selection(user)
        with open(f"./assets/quizzes/{selection}/url.txt", 'r') as f:
            img_url = f.read().strip()
        guesses = format_guesses(user)
        guesses += [""] * (len(guesses) % 3)
        interval = len(guesses)//3
        embed = discord.Embed(
                    title=f"Quiz screen",
                    author=discord.EmbedAuthor(name=ctx.author.name, icon_url=ctx.author.display_avatar.url),
                    description=f"Current quiz: {selection}",
                    color=await self._get_user_color(ctx),
                    fields=[discord.EmbedField(name="", value="\n".join(guesses[i:i+interval]), inline=True) for i in range(0, len(guesses), interval)],
                    image=img_url,
                    footer=discord.EmbedFooter(text=evaluate_score(user) if score else "")
                )
        
        return await ctx.send_response(embed=embed, ephemeral=True)
    
    async def autocomplete_numbers(ctx: discord.AutocompleteContext):
        return list(range(1, 2+len(get_current_guesses(get_user(str(ctx.interaction.user.id))))))

    async def autocomplete_guesses(ctx: discord.AutocompleteContext):
        return sorted(get_remaining_words(get_user(str(ctx.interaction.user.id))))

    @discord.ext.commands.slash_command(name="guess", guild_ids=[os.getenv("GUILD_ID")], description="Show the currently selected quiz")
    async def guess(self, ctx: discord.ApplicationContext,
                    number: discord.Option(int, "Pick a number to match to a word!", autocomplete=discord.utils.basic_autocomplete(autocomplete_numbers)), # type: ignore
                    term: discord.Option(str, "Pick a word from the word bank!", autocomplete=discord.utils.basic_autocomplete(autocomplete_guesses)), # type: ignore
                    score:bool=True):
        user = str(ctx.author.id)
        message = guess_term(user, number, term)
        new_msg = await self.show_quiz(ctx, score)
        await ctx.send_followup(message, ephemeral=True)
        try:
            if (msg := self._quiz_cache[user]):
                await msg.delete_original_response()
        except:
            pass
        self._quiz_cache[user] = new_msg

    @discord.ext.commands.slash_command(name="clear", guild_ids=[os.getenv("GUILD_ID")], description="Clear an item from the quiz")
    async def clear_entry(self, ctx: discord.ApplicationContext,
                    number: discord.Option(int, "Pick a number to clear! (Leave blank to clear all answers)", autocomplete=discord.utils.basic_autocomplete(autocomplete_numbers))=None): # type: ignore
        user = str(ctx.author.id)
        await ctx.send_response(clear(user, number=number), ephemeral=True)

    @discord.ext.commands.slash_command(name="help", guild_ids=[os.getenv("GUILD_ID")], description="Show all useable commands")
    async def help(self, ctx: discord.ApplicationContext):
        user_color = await self._get_user_color(ctx)
        embed = discord.Embed(
            title=f"Commands List",
            color=user_color,
        )
        
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        for text in "`/clear <number (optional)>`: Clears the currently selected quiz. If <number> is provided, only that line will be cleared.\n`/guess <number> <term> <score (optional)>`: Guess the term for a number. Number and term both autofill. If <score> is true, your current score will be displayed.\n`/quiz <score (optional)>`: Displays the currently selected quiz. If <score> is true, the score will be displayed.\n`/select`: Cycles through all available quizzes. Hit the button with the checkmark to select a quiz.".split("\n"):
            embed.add_field(name="", value=text, inline=False)
        await ctx.send_response(embed=embed, ephemeral=True)