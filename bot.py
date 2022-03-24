# bot.py
import os

import discord
import pandas as pd
from discord.ext import commands
from discord.ext.commands.context import Context
from dotenv import load_dotenv

from catalogs import build_frame, update_pos_freq
from recommender import do_eliminate, do_guess

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
bot = commands.Bot(command_prefix="!")


@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")


user_userdata = {}

class UserFrames:
    df_latest: pd.DataFrame = None
    df_discriminating: pd.DataFrame = None
class UserData:
    def __init__(self, nordle: int):
        self.nordle = [UserFrames() for _ in range(nordle)]
        # self.df_latest: pd.DataFrame = None
        # self.df_discriminating: pd.DateFrame = None


def author_name(ctx: Context):
    return ctx.message.author.name

def reset_userdata(ctx: Context) -> None:
    global user_userdata
    if user_userdata.get(author_name(ctx=ctx)):
        user_userdata[author_name(ctx=ctx)] = None
    
def userdata(ctx: Context, nordle: int = 1) -> UserData:
    global user_userdata
    if not user_userdata.get(author_name(ctx=ctx)):
        user_userdata[author_name(ctx=ctx)] = UserData(nordle=nordle)
    return user_userdata[author_name(ctx=ctx)]


def make_recommendation(userdata: UserFrames, rank_strategy: str) -> pd.DataFrame:
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


df = build_frame()


@bot.command(
    name="new",aliases=["n"], help="Starts a new Wordle session with Stanford | Google catalog and (N)umber of *ordles to play"
)
async def new(ctx: Context, word_bank: str, nordle: int):
    global df
    if word_bank == "Stanford" or word_bank != "Google":
        new_df = df[df["Stanford"] == True]
    else:
        new_df = df[df["Google"] == True]
    
    reset_userdata(ctx=ctx)
    ud = userdata(ctx=ctx,nordle=nordle)

    for udf in ud.nordle:
        udf.df_latest = new_df.copy()
        udf.df_discriminating = new_df.copy()

    game = discord.Game("Wordle with {}".format(author_name(ctx=ctx)))
    await bot.change_presence(activity=game)
    await ctx.send(f"{author_name(ctx=ctx)} let's roll!")


@bot.command(
    name="recommend", aliases=["rec","r"], help="Provide recommendation: [lps|ups|gfreq|posps|discr]"
)
async def recommend(ctx: Context, strategy):
    # rec = make_recommendation(userdata=userdata(ctx=ctx), rank_strategy=strategy)
    recs = [make_recommendation(userdata=udf, rank_strategy=strategy)["word"].head(3).to_string(header=False,index=False) for udf in userdata(ctx=ctx).nordle]
    await ctx.send("{}".format("\n---\n".join(recs)))


@bot.command(name="guess",aliases=["g"], help="Provide guess and results", require_var_positional=True)
async def guess(ctx: Context, guess: str, *results: str):
    # df_sorted
    # word0 = "ghost"
    # result0="xgxyx"
    recs = []
    idx_results = zip(range(len(results)),results)
    for idx,result in idx_results:
        udf = userdata(ctx=ctx).nordle[idx]
        df_latest = do_guess(udf.df_latest, word=guess, result=result)
        # update positional freq within known dataset
        udf.df_latest = update_pos_freq(dfm=df_latest)

        udf.df_discriminating = do_eliminate(
            udf.df_discriminating, word=guess, result=result
        )
        recs.append(udf.df_latest["word"].head(3).to_string(header=False,index=False))
    await ctx.send("{}".format("\n---\n".join(recs)))


bot.run(TOKEN)
print("")
