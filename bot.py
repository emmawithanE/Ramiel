import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()

bot = commands.Bot(
	command_prefix="R: ",
	owner_id=268721746708791297,
	intents = intents
	)

@bot.event
async def on_ready():
    print('Logged in as {0.user}, now printing more'.format(bot))

# testing responding to keywords

@bot.command()
async def ping(ctx):
	await ctx.send('pong!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('OwO') or message.content.startswith('uwu'):
        await message.channel.send('Ew, furry')

    await bot.process_commands(message)


bot.run(TOKEN)