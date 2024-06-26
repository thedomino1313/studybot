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
        return get_remaining_words(get_user(str(ctx.interaction.user.id)))

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

    @discord.ext.commands.slash_command(name="word_bank", guild_ids=[os.getenv("GUILD_ID")], description="Displays your current word bank")
    async def word_bank(self, ctx: discord.ApplicationContext):
        user_color = await self._get_user_color(ctx)
        embed = discord.Embed(
            title=f"Word Bank",
            color=user_color,
        )
        
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        
        embed.add_field(name="", value="\n".join(get_remaining_words(get_user(str(ctx.interaction.user.id)))))

        await ctx.send_response(embed=embed, ephemeral=True)
    
    @discord.ext.commands.slash_command(name="help", guild_ids=[os.getenv("GUILD_ID")], description="Show all useable commands")
    async def help(self, ctx: discord.ApplicationContext):
        user_color = await self._get_user_color(ctx)
        embed = discord.Embed(
            title=f"Commands List",
            color=user_color,
        )
        
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        for text in ["- `/select`: Provides a paginated menu of all quizzes that you can test yourself on. To select a quiz to study, press the check mark button between the navigation buttons.",
                     "- `/quiz <score (optional)>`: Shows the current state of the quiz you have selected.\n\t- Shows the image, all blanks and terms if you have filled in any, and your score (if the score parameter is set to True)",
                     "- `/word_bank`: Shows the user all of the words that they have not guessed for their selected quiz.\n\t- Created because Discord API autocomplete will only show a max of 25 terms, so without typing any letters you will not be able to see all items on some quizzes.",
                     "- `/guess <number> <term>`: Tell the bot your guess for one of the numbered problems.\n\t- Autofilled responses appear for both `number` and `term`, showing all valid numbered questions for `number` and all remaining `terms` for term.",
                     "- `/clear <number (optional)>`: Remove a guess from the quiz, or clear the whole quiz.\n\t- If a value for `number` is not provided, all answers to the quiz will be wiped.\n\t- If a value for `number` is provided, only the given number will be erased."]:
            embed.add_field(name="", value=text, inline=False)
        await ctx.send_response(embed=embed, ephemeral=True)