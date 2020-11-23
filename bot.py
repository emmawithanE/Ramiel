import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

import random

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()

bot = commands.Bot(
	command_prefix=("R: ","R:","Ramiel, "),
	owner_id=268721746708791297,
	intents = intents
	)


# creation and loading of storage file
# namefile = open("names.txt", "r+")
# names = namefile.readlines()
# namefile.close()

# Generate names.txt if it doesn't exist already
try:
	open("names.txt", "x")
	print('Created names.txt - was it deleted or moved?')
except:
	pass

# Load current names.txt into local list
names = []
with open("names.txt", "r") as file:
	for i in file:
		line = i.split("|")
		names.append((line[0], int(line[1]), line[2][:-1]))

@bot.event
async def on_ready():
	print(f"Logged in as {bot.user}")

# testing responding to keywords

@bot.command()
async def ping(ctx):
	await ctx.send('pong!')

@bot.command()
async def enter(ctx, arg):
	realname = arg
	userID = ctx.author.id
	discname = str(ctx.author)

	names.append((realname,userID,discname))
	await ctx.send(f"Added {realname} with Discord name {discname} to my Secret Santa list!")

@bot.command()
async def addperson(ctx, name, ID: int):
	if 	ctx.channel.id != 413979914900078592:
		await ctx.send("This command can only be used in the Council channel.")
		return
	try:
		target = await bot.fetch_user(ID)
	except:
		await ctx.send(f"Could not find a user with ID {ID}.")
		return
	names.append((name,ID,str(target)))
	await ctx.send(f"Added {name}, {str(target)} on Discord, to my Secret Santa list.")
	await target.send(f"Hi there! {str(ctx.author)} added you to my Secret Santa list! If this is a mistake, please contact a club council member. Since James is currently testing this function, you should probably do that anyway.")


@bot.command()
async def list(ctx):
	for row in names:
		await ctx.send(row)

@bot.command()
async def save(ctx):
	namefile = open("names.txt","w+")
	for name, ID, username in names:
		namefile.write(name + "|" + str(ID) + "|" + username + "\n")
	namefile.close()
	await ctx.send("Saved!")

@bot.command()
async def annoyJame(ctx):
	channel = await bot.fetch_channel(686928934411173912)
	await channel.send("owo what's this")

@bot.command()
async def annoyJameByUser(ctx):
	target = bot.fetch_user(268721746708791297)
	await target.send("uwu what's this")

@bot.command()
async def feedback(ctx):
	for name, ID, username in names:
		print(ID)
		user = await bot.fetch_user(ID)
		print(f"{name}  {user}  {username}") 
		await user.send(f"Hello {name}!")

@bot.command()
async def fire(ctx):
	if ctx.author.id != 268721746708791297:
		await ctx.send(f"Sorry, this command can only be used by {bot.fetch_user(268721746708791297).name}.")
	else:
		recipients = names.copy()

		# randomly shuffle recipients list
		random.shuffle(recipients)
		print("Shuffling first time!")

		matched = True

		# shuffle again as long as any names are in the same place between the two
		while matched == True:

			matched = False

			for a, b in zip(names,recipients):

				# compare user IDs as they are most guaranteed separate and unchanging
				if a[1] == b[1]:
					#need to reshuffle and try again
					random.shuffle(recipients)
					print("Match! Shuffled again.")
					matched = True
					break

		print("Shuffle complete, hopefully! Sending names...")

		for a, b in zip(names,recipients):
			recname = b[0]
			recdisc = b[2]

			givname = a[0]
			givID = a[1]

			# send a message through givID to givname, naming recname and recdisc
			giver = await bot.fetch_user(givID)
			await giver.send(f"Hi {givname}! I have randomly allocated Secret Santa names, and you got: {recname} ({recdisc} on Discord). If this is you, please yell at Jame!")



@bot.event
async def on_message(message):
	if message.author == bot.user:
		return

	if message.content.startswith('OwO') or message.content.startswith('uwu') or message.content.startswith('owo'):
		await message.channel.send('Ew, furry')

	await bot.process_commands(message)


bot.run(TOKEN)