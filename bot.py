import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

import gspread
from oauth2client.service_account import ServiceAccountCredentials

import random

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN_RAM')

intents = discord.Intents.default()
intents.members = True
intents.reactions = True

bot = commands.Bot(
	command_prefix=("R: ","R:","Ramiel, "),
	owner_id=268721746708791297,
	intents = intents
	)


#reactdict = {
#	"💜": "Heart",
#	"🔑": "PuzzleSolver"
#}

class reactset:
	def __init__(self,link,roles,perms=None):
		linklist = link.split("/")
		self.svr = int(linklist[0])
		self.chnl = int(linklist[1])
		self.msg = int(linklist[2])

		self.reactdict = roles #give as dict
		self.permdict = perms

messagestocheck = []

#append new messages to check
messagestocheck.append(reactset(link="686753804137267207/686753804137267288/811388529438883870",roles={"💜": "Heart","🔑": "PuzzleSolver"}))

#WIP - Roles based on reactions?
#TODO - Import class contents from file???

async def roleadd(self,reactemoji,user,msg,reactobj):
	#attempts to get a role from reactemoji and reactobj, then add it to the user if the user is allowed to have it

	#role:
	try:
		role = discord.utils.get(msg.guild.roles, name = message.reactdict[str(reactemoji)])
	except Exception as e:
		print(f"Failed to get role for emoji {str(reaction.emoji)} - error {e}")
		print(f"Reaction by {str(user)} on message in {msg.guild.name}, channel {msg.channel.name}, ID: {msg.id}")
		return


async def rolecheck():
	#https://discord.com/channels/686753804137267207/686753804137267288/811388529438883870 test message in my server

	for message in messagestocheck:

		print(f"Working message at svr: {message.svr}, chnl: {message.chnl}, msg: {message.msg}\n\n")
	
		msg = await bot.get_guild(message.svr).get_channel(message.chnl).fetch_message(message.msg)
	
		for reaction in msg.reactions:
			try:
				role = discord.utils.get(msg.guild.roles, name = message.reactdict[str(reaction.emoji)])
			except Exception as e:
				print(f"Failed to get role for emoji {str(reaction.emoji)} - error {e}")
				continue
	
			reactmembers = await reaction.users().flatten() #List of people who have made that reaction
			rolemembers = role.members #List of people who have the associated role
	
			addrole = set(reactmembers) - set(rolemembers) #people who reacted but don't have the role, and thus need it
			remrole = set(rolemembers) - set(reactmembers) #people who have the role but did not react, and thus need it removed
	
			#print(reactmembers)
			#print(rolemembers)
			#print(addrole)
			#print(remrole)
	
			for user in addrole:
				if user.id == 268721746708791297:
					continue
	
				try:
					member = await msg.guild.fetch_member(user.id) #This is the dumbest fucking thing
					await member.add_roles(role)
					print(f"Added role {str(role)} to {str(user)}")
				except Exception as e:
					print(f"Failed to add role {str(role)} to {str(user)} - {e}")
	
			for user in remrole:
				try:
					member = await msg.guild.fetch_member(user.id)
					await member.remove_roles(role)
					print(f"Removed role {str(role)} from {str(user)}")
				except Exception as e:
					print(f"Failed to remove role {str(role)} from {str(user)} - {e}")



@bot.event
async def on_ready():
	print(f"Logged in as {bot.user}")
	# await bot.change_presence(status=discord.Status.invisible)

# basic feedback
@bot.command()
async def ping(ctx):
	await ctx.send('pong!')

@bot.command()
async def role(ctx):
	await rolecheck()
	await ctx.send("Roles updated, hopefully")

@bot.command()
async def annoyEmma(ctx):
	channel = await bot.fetch_channel(686928934411173912)
	await channel.send("owo what's this")



@bot.command()
async def annoyEmmaByUser(ctx):
	target = bot.fetch_user(268721746708791297)
	await target.send("uwu what's this")



@bot.command()
async def list(ctx):
	Emma = await bot.fetch_user(268721746708791297)
	message = "```Ramiel v1.0.3 commands:\n"
	message += " - list: lists bot commands.\n"
	message += " - ping: prompt a basic response.\n"
	message += f" - annoyEmma: sends a message to Emma ({str(Emma)}).\n"
	message += " - annoyEmmaByUser: sends a different message to Emma, using a different targeting method.\n"
	message += " - role: tells the bot to update member roles based on reactions. Currently only applies to a test server.\n"
	message += " - repeat: repeats what you say back to you. WARNING: In Progress."
	message += "```"

	await ctx.send(message)



@bot.command()
async def repeatthislineproperlyplease(ctx, *args):
	text = ' '.join(args) # the text of the message as a string
	await ctx.send(text)

@bot.command()
async def repeat(ctx, *args):
	text = ' '.join(args) # the text of the message as a string

	# reverse
	flipped = text[::-1]

	key = "onethreeseven"
	letters = 0 #for tracking and skipping not-letters correctly

	output = ""

	# vigenere cipher - only process on letters
	for char in flipped:
		if char.isalpha():
			offset = 0
			if char.islower():
				offset = 97 #'a'
			else:
				offset = 65 #'A'

			num = ord(char) - offset
			encoded = ( ( num + ( ord( key[letters % len(key)]) -97)) % 26) + offset

			output += chr(encoded)

			letters += 1

		elif char.isnumeric():
			encoded = 105 - ord(char)

			output += chr(encoded)

		else:
			output+= char



	await ctx.send(output)

#----------------------------------------------------------------

@bot.event
async def on_message(message):
	if message.author == bot.user:
		return

	if message.content.lower().startswith(('owo','uwu','hewwo')):
		await message.channel.send('Ew, furry')

	await bot.process_commands(message)

@bot.event
async def on_reaction_add(reaction, member):
	print(f"Reaction noticed in {reaction.message.channel.name} on message ID {reaction.message.id}")

@bot.event
async def on_raw_reaction_add(payload):
	for message in messagestocheck if message.msg == payload.message_id:



@bot.event
async def on_reaction_remove(reaction, member):
	print(f"Reaction removed in {reaction.message.channel.name} on message ID {reaction.message.id}")




bot.run(TOKEN)

