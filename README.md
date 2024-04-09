# studybot
StudyBot is a small side project that I made to help my girlfriend study for anatomy.

## Disclaimer
This cog works with `py-cord` (shown in `requirements.txt`). If you have other installations of discord libraries such as `discord.py`, the code may not work correctly.

## Files you need to pay attention to

Each directory in `assets/quizzes` represents a "quiz".
- The bot takes the name of the quiz from the name of the folder. 
- The questions are part of `image.jpg`.
  - In the case of the examples, they are numbered labels on diagrams of a human skull.
- `answers.txt` is a list of the correct answers to the questions in numerical order to match the numbers on `image.jpg`.
- `url.txt` contains a valid url to image.jpg.
  - This is unfortunately needed because of the way that Paginators work in PyCord, they will not accept local image files as sources.
  - The easiest way to get a url is to send the image once in Discord, and use the link that is generated.

`bot.py` is a simple bot example file. If you want to add this suite of code to an already existing discord bot, you can use the below code to add the commands to it.
```python
from study_cog import StudyBot
bot.add_cog(StudyBot(bot))
```

`.env` contains two terms:
- GUILD_ID
  - The id of the guild/server that you would like to add these commands to
- BOT_TOKEN
  - The token needed to connect to your bot.
  - If you are connecting the cog to an existing bot as seen above, you do not need this parameter.
  

`users.json` carries a cache of all users who have interacted with the Study Bot. This does not need to be created or modified by you, the bot will take care of creation if it cannot find the file.

## Commands
- `/select`: Provides the user with a paginated menu of all quizzes that the bot can see in `assets/quizzes`. To select a quiz to study, the user must simply press the check mark button between the navigation buttons.
- `/quiz <score (optional)>`: Shows the user the current state of the quiz they are working on
  - Users can see the image, all questions and the answers if they have provided any, and their score (if the score parameter is set to True)
- `/guess <number> <term>`: Users tell the bot their guess for one of the numbered problems.
  - Autofilled responses appear for both `number` and `term`, showing all valid numbered questions for `number` and all remaining `terms` for term.
    - This provides users with a word bank.
- `/clear <number (optional)>`: Allows the user to remove a guess from the quiz, or clear the whole quiz.
  - If a value for `number` is not provided, all answers to the quiz will be wiped.
  - If a value for `number` is provided, only the given number will be erased.