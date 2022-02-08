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
        self.df_latest: pd.DataFrame = None
        self.df_discriminating: pd.DateFrame = None


def author_name(ctx: Context):
    return ctx.message.author.name


def userdata(ctx: Context) -> UserData:
    global user_userdata
    if not user_userdata.get(author_name(ctx=ctx)):
        user_userdata[author_name(ctx=ctx)] = UserData()
    return user_userdata[author_name(ctx=ctx)]


def make_recommendation(userdata: UserData, rank_strategy: str) -> pd.DataFrame:
    if rank_strategy == "lps":
        return userdata.df_latest.sort_values(["letterprobsum"], ascending=False)
    elif rank_strategy == "ups":
        return userdata.df_latest.sort_values(["uniqueprobsum"], ascending=False)
    elif rank_strategy == "discr":
        return userdata.df_discriminating.sort_values(
            ["uniqueprobsum"], ascending=False
        )
    elif rank_strategy == "posps":
        return userdata.df_latest.sort_values(["posprobsum"], ascending=False)
    elif rank_strategy == "gfreq":
        return userdata.df_latest.sort_values(["wordfreq"], ascending=False)
    else:
        raise Exception("invalid option chosen: [lps|ups|posps|discr|gfreq]")


from catalogs import build_frame

df = build_frame()


@bot.command(
    name="new", help="Starts a new Wordle session with Standford | Google catalog"
)
async def new(ctx: Context, word_bank: str):
    global df
    if word_bank == "Stanford" or word_bank != "Google":
        new_df = df[df["Standford"] == True]
    else:
        new_df = df[df["Google"] == True]

    userdata(ctx=ctx).df_latest = new_df
    userdata(ctx=ctx).df_discriminating = new_df.copy()
    import discord

    game = discord.Game("Wordle with {}".format(author_name(ctx=ctx)))
    await bot.change_presence(activity=game)
    await ctx.send(f"{author_name(ctx=ctx)} let's roll!")


@bot.command(
    name="recommend", help="Provide recommendation: [lps|ups|gfreq|posps|discr]"
)
async def recommend(ctx: Context, strategy):
    rec = make_recommendation(userdata=userdata(ctx=ctx), rank_strategy=strategy)
    await ctx.send("{}".format(rec["word"].head(3).to_string(header=False,index=False)))


@bot.command(name="guess", help="Provide guess and result")
async def guess(ctx: Context, guess: str, result: str):
    # df_sorted
    # word0 = "ghost"
    # result0="xgxyx"
    from recommender import do_guess, do_eliminate
    from catalogs import update_pos_freq

    df_latest = do_guess(userdata(ctx=ctx).df_latest, word=guess, result=result)
    # update positional freq within known dataset
    userdata(ctx=ctx).df_latest = update_pos_freq(dfm=df_latest)

    userdata(ctx=ctx).df_discriminating = do_eliminate(
        userdata(ctx=ctx).df_discriminating, word=guess, result=result
    )
    await ctx.send("{}".format(userdata(ctx=ctx).df_latest["word"].head(3).to_string(header=False,index=False)))


bot.run(TOKEN)
print("")
