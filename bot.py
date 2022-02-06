# bot.py
import os
import pandas as pd

from dotenv import load_dotenv
from discord.ext import commands
from discord.ext.commands.context import Context

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
bot = commands.Bot(command_prefix="!")


@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")


user_userdata = {}


class UserData:
    def __init__(self):
        self.df: pd.DataFrame = None
        self.df_latest: pd.DataFrame = None
        self.df_discriminating: pd.DateFrame = None


def author_name(ctx: Context):
    return ctx.message.author.name


def userdata(ctx: Context) -> UserData:
    if not user_userdata.get(author_name(ctx=ctx)):
        user_userdata[author_name(ctx=ctx)] = UserData()
    return user_userdata[author_name(ctx=ctx)]


def recommend(userdata: UserData, rank_strategy: str) -> pd.DataFrame:
    if rank_strategy == "lps":
        return userdata.df_latest.sort_values(["letterprobsum"], ascending=False)
    elif rank_strategy == "ups":
        return userdata.df_latest.sort_values(["uniqueprobsum"], ascending=False)
    elif rank_strategy == "discr":
        userdata.df_discriminating.sort_values(["letterprobsum"], ascending=False)
    elif rank_strategy == "posps":
        return userdata.df_latest.sort_values(["posprobsum"], ascending=False)
    elif rank_strategy == "gfreq":
        return userdata.df_latest.sort_values(["wordfreq"], ascending=False)
    else:
        raise Exception("invalid option chosen: [lps|ups|posps|discr|gfreq]")


@bot.command(
    name="new", help="Starts a new Wordle session with Standford | Google catalog"
)
async def new(ctx: Context, word_bank: str):
    from .catalogs import Stanford, GoogleNGram, build_frame

    if word_bank == "Stanford" or word_bank != "Google":
        lines = Stanford()
    else:
        lines = GoogleNGram()
    df = build_frame(lines=lines)
    userdata(ctx=ctx).df = df
    userdata(ctx=ctx).df_latest = df.copy()
    userdata(ctx=ctx).df_discriminating = df.copy()

    await ctx.send(f"{author_name(ctx=ctx)} let's roll!")


@bot.command(
    name="recommend", help="Provide recommendation: [lps|ups|gfreq|posps|discr]"
)
async def recommend(ctx: Context, strategy):
    rec = recommend(userdata=user_userdata(ctx=ctx), rank_strategy=strategy)
    await ctx.send(f"{rec.head(3)}")


@bot.command(name="guess", help="Provide guess and result")
async def guess(ctx: Context, guess: str, result: str):
    # df_sorted
    # word0 = "ghost"
    # result0="xgxyx"
    from .recommender import do_guess, do_eliminate

    userdata(ctx=ctx).df_latest = do_guess(
        userdata(ctx=ctx).df_latest, word=guess, result=result
    )
    userdata(ctx=ctx).df_discriminating = do_eliminate(
        user_userdata(ctx=ctx).df, word=guess, result=result
    )
    await ctx.send(f"{userdata(ctx=ctx).df_latest.head(3)}")


bot.run(TOKEN)
print("")
