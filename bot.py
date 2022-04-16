import os
import sys
import random
import asyncio

import discord
from discord.ext import commands
from dotenv import load_dotenv

from pydrive.drive import GoogleDrive 
from pydrive.auth import GoogleAuth 
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import var
import inst_var

# TODO: Investigate if this should just be bot.run(inst_var.token) at the end
# or if the dotenv intermediate does something useful
load_dotenv()
TOKEN = os.getenv(inst_var.token_name)

intents = discord.Intents.default()
intents.members = True
intents.reactions = True

bot = commands.Bot(
	command_prefix=inst_var.prefixes,
	owner_id=var.usr_owner,
	intents = intents
	)

# Help command removed to hide the existence of some commands
# TODO: Limit these commands more directly, as needed
bot.remove_command('help')

# Get the Google Sheet used for tracking things people like
# Use creds to create a client to interact with the Google Drive API
scope = ['https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
sheet = client.open("Secret Santa Responses")
page = sheet.get_worksheet(0)



# Initialise data structure used for Secret Santa

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



# Either give specified role to specified user, or take it away
async def changememberrole(role,user,remove=False):
	if user.id == bot.owner_id:
		return

	if remove:
		try:
			member = await role.guild.fetch_member(user.id)
			await member.remove_roles(role,reason="Removed reaction")
			print(f"Removed role {role.name} from {str(user)}")
		except Exception as e:
			print(f"Failed to remove role {role.name} from {str(user)} - {e}")
	else:
		try:
			member = await role.guild.fetch_member(user.id)
			await member.add_roles(role,reason="Added reaction")
			print(f"Added role {role.name} to {str(user)}")
		except Exception as e:
			print(f"Failed to add role {role.name} to {str(user)} - {e}")
	pass


# Attempts to get a role from reactemoji and reactobj, then add it to the user if the user is allowed to have it
async def roleaddremove(reactemoji,user,msg,reactobj,remove=False):

	# Determine what role is to be added
	try:
		role = discord.utils.get(msg.guild.roles, name = reactobj.reactdict[str(reactemoji)])
	except Exception as e:
		print(f"Failed to get role for emoji {reactemoji.name} - error {e}")
		print(f"Reaction changed by {str(user)} on message in {msg.guild.name}, channel {msg.channel.name}, ID: {msg.id}")
		return

	# If role has a permission role and the person has it, or if there is no permission role, give role, else print note and return
	if reactobj.permdict != None:
		prereq = reactobj.permdict.get(role.name)
		if prereq != None:
			roleneeded = discord.utils.get(msg.guild.roles, name = prereq)
			if user not in roleneeded.members:
				print(f"{str(user)} tried to add or remove role {role.name} but could not as they do not have role {prereq}")
				return

	await changememberrole(role=role,user=user,remove=remove)


# For all messages that should be checked, check them (and update roles as needed)
async def rolecheck():

	for message in inst_var.messagestocheck:

		print(f"Working message at svr: {message.svr}, chnl: {message.chnl}, msg: {message.msg}\n")
	
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

			#Only add role to people who have permission for it
			if message.permdict != None:
				prereq = message.permdict.get(role.name)
				if prereq != None:
					roleneeded = discord.utils.get(msg.guild.roles, name = prereq)
					permitted = roleneeded.members
					addrole = addrole & set(permitted)

			for user in addrole:
				if user.id == bot.owner_id:
					continue

				try:
					member = await msg.guild.fetch_member(user.id)
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



# Bot commands begin here

# Enter the user to the current Secret Santa list
@bot.command()
async def enter(ctx, arg):
	realname = arg
	userID = ctx.author.id
	discname = str(ctx.author)

	names.append((realname,userID,discname))
	await ctx.send(f"Added {realname} with Discord name {discname} to my Secret Santa list!")

# Enter another user to the current Secret Santa list, limited to official channels to prevent misuse
@bot.command()
async def addperson(ctx, name, ID: int):
	if 	(ctx.channel.id != var.chn_council and ctx.channel.id != var.chn_ownerDM):
		await ctx.send("This command can only be used in the Council channel.")
		return
	try:
		target = await bot.fetch_user(ID)
	except:
		await ctx.send(f"Could not find a user with ID {ID}.")
		return
	names.append((name,ID,str(target)))
	await ctx.send(f"Added {name}, {str(target)} on Discord, to my Secret Santa list.")
	await target.send(f"Hi there! {str(ctx.author)} added you to my Secret Santa list under the name {name}! When I get to allocating names, you will be sent a message in this channel. If this is a mistake, please contact a club council member.")

# List the current people in the Secret Santa list
@bot.command()
async def listnames(ctx):
	for row in names:
		await ctx.send(row)

# Write the current state of the Secret Santa list to names.txt
@bot.command()
async def save(ctx):
	namefile = open("names.txt","w+")
	for name, ID, username in names:
		namefile.write(name + "|" + str(ID) + "|" + username + "\n")
	namefile.close()
	await ctx.send("Saved!")

# Show the Google Sheet responses for a named user (technically any string that can be found in the Sheet)
# TODO: Limit search range to the relevant column of the Google Sheet?
@bot.command()
async def showlikes(ctx, arg):
	try:
		row = page.find(arg).row
	except:
		print(f"Could not find cell containing {arg}.\n\n")
		return
	likes = page.row_values(row)
	labels = ["Timestamp","IRL Name","Discord Name","Hobbies or fandoms","Colours/aesthetics","Foods","Sounds/music","Smells","Texture","Don't want or have","Someone you could ask for ideas"]

	msg = ''
	paragraph = ''

	for i in range(1,11):
		paragraph = f"**{labels[i]}:** {likes[i]}\n\n"
		if (len(msg) + len(paragraph) < 1990):
			# paragraph can fit in message still
			msg += paragraph
			print(f"Combining line {i} into msg")
		else:
			#paragraph is too large to add, send message and start a new one
			await ctx.send(msg)
			msg = paragraph
			print(f"Printing message at line {i-1}")

	await ctx.send(msg)

# Randomly assign each person in the Secret Santa list a giftee, then send allocation information in DMs
# Logs the list of assignments in DO_NOT_OPEN.txt, for reference if needed
@bot.command()
async def fire(ctx):
	if ctx.author.id != bot.owner_id and ctx.author.id != var.usr_partner:
		await ctx.send(f"Sorry, this command can only be used by {bot.fetch_user(bot.owner_id).name} (or her partner).")
		return
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
			await giver.send(f"Hi {givname}! I have randomly allocated Secret Santa names, and you got: {recname} ({recdisc} on Discord). If this is you, please yell at Emma!")

			try:
				row = page.find(recdisc).row

				likes = page.row_values(row)
				labels = ["Timestamp","IRL Name","Discord Name","Hobbies or fandoms","Colours/aesthetics","Foods","Sounds/music","Smells","Texture","Don't want or have","Someone you could ask for ideas"]

				await giver.send("Here are the things that person wrote on their Google Form:\n\n")
				msg = ''
				paragraph = ''

				for i in range(1,11):
					paragraph = f"**{labels[i]}:** {likes[i]}\n\n"
					if (len(msg) + len(paragraph) < 1990):
						# paragraph can fit in message still
						msg += paragraph
						print(f"Combining line {i} into msg")
					else:
						#paragraph is too large to add, send message and start a new one
						await giver.send(msg)
						msg = paragraph
						print(f"Printing message at line {i-1}")

				await giver.send(msg)

			except:
				print(f"Could not find cell containing {recdisc}.\n\n")
				await giver.send("I failed to find a Google Sheet row for that person! Definitely yell at Emma!")

		try:
			open("DO_NOT_OPEN.txt", "x")
			print('Created DO_NOT_OPEN.txt')
		except:
			pass

		DONT = open("DO_NOT_OPEN.txt","w+")
		DONT.write("Recipients, in order of names.txt:\n\n")
		for name, ID, username in recipients:
			DONT.write(name + "|" + str(ID) + "|" + username + "\n")
		DONT.close()
		await ctx.send("Created DO_NOT_OPEN.txt!")

# Attempt to send allocations again, without reshuffling
# TODO: Function is untested and possibly broken, test before potential use
@bot.command()
async def retry(ctx):
	if ctx.author.id != bot.owner_id and ctx.author.id != var.usr_partner:
		await ctx.send(f"Sorry, this command can only be used by {bot.fetch_user(bot.owner_id).name} (or, temporarily, her partner).")
		return
	recipients = []
	with open("DO_NOT_OPEN.txt", "r") as recip:
		for i in recip:
			line = i.split("|")
			recipients.append((line[0], int(line[1]), line[2][:-1]))

	for a, b in zip(names,recipients):
			recname = b[0]
			recdisc = b[2]

			givname = a[0]
			givID = a[1]

			# send a message through givID to givname, naming recname and recdisc
			giver = await bot.fetch_user(givID)
			await giver.send(f"Hi {givname}! I have randomly allocated Secret Santa names, and you got: {recname} ({recdisc} on Discord). If this is you, please yell at Emma!")

			try:
				row = page.find(recdisc).row

				likes = page.row_values(row)
				labels = ["Timestamp","IRL Name","Discord Name","Hobbies or fandoms","Colours/aesthetics","Foods","Sounds/music","Smells","Texture","Don't want or have","Someone you could ask for ideas"]

				await giver.send("Here are the things that person wrote on their Google Form:\n\n")
				msg = ''
				paragraph = ''

				for i in range(1,11):
					paragraph = f"**{labels[i]}:** {likes[i]}\n\n"
					if (len(msg) + len(paragraph) < 1990):
						# paragraph can fit in message still
						msg += paragraph
						print(f"Combining line {i} into msg")
					else:
						#paragraph is too large to add, send message and start a new one
						await giver.send(msg)
						msg = paragraph
						print(f"Printing message at line {i-1}")

				await giver.send(msg)

			except:
				print(f"Could not find cell containing {recdisc}.\n\n")
				await giver.send("I failed to find a Google Sheet row for that person! Definitely yell at Emma!")

# Dice roll: rolls n 6 sided dice and returns the sum of the three highest rolls
def rollk3(n):
	rolls = []
	for i in range(0,n):
		rolls.append(random.randint(1,6))

	return sum((sorted(rolls,reverse=True))[:3])

# Roll a 6 by 6 grid of n six sided dice keep 3, for obscure D&D stat generation method
@bot.command()
async def matrix(ctx,n: int):
	message = f"Rolling a matrix of {n}d6k3:\n```\n"

	for row in range(0,6):
		line = ""
		for col in range(0,6):
			line += str(rollk3(n)).rjust(3)
		message += line
		message += '\n'
	message += "```"

	await ctx.send(message)

# Dice roll: rolls a 10,000 sided dice
@bot.command()
async def d10000(ctx):
	await ctx.send(f"Rolled a d10000: {random.randint(1,10000)}")

# Basic feedback to check responsiveness
@bot.command()
async def ping(ctx):
	await ctx.send('pong!')

# Initiate a check for changes in roles that the bot is tracking
@bot.command()
async def role(ctx):
	await rolecheck()
	await ctx.send("Roles updated, hopefully")

# Send me a DM (testing function that was left in because people enjoy using it on me)
@bot.command()
async def annoyEmma(ctx):
	channel = await bot.fetch_channel(var.chn_ownerDM)
	await channel.send("owo what's this")

# Send me a DM (testing function that was left in because people enjoy using it on me)
@bot.command()
async def annoyEmmaByUser(ctx):
	target = await bot.fetch_user(bot.owner_id)
	await target.send("uwu what's this")

# List the currently available commands
# Some commands not listed to hide their existence
@bot.command()
async def list(ctx):
	Emma = await bot.fetch_user(bot.owner_id)
	message = f"```Ramiel v{var.version_number} commands:\n"
	message += " - list: lists bot commands.\n"
	message += " - ping: prompt a basic response.\n"
	message += f" - annoyEmma: sends a message to Emma ({str(Emma)}).\n"
	message += " - annoyEmmaByUser: sends a different message to Emma, using a different targeting method.\n"
	message += " - emojiping [emoji]: When used as a reply to another message, pings users who reacted to the original message with [emoji].\n"
	message += " - repeat: repeats what you say back to you. WARNING: In Progress."
	message += "```"

	await ctx.send(message)

# Repeat the text of the comment back without modification
@bot.command()
async def repeatbutnotmixedup(ctx, *args):
	text = ' '.join(args) # the text of the message as a string
	await ctx.send(text)

# Repeat the text of the comment after application of a simple code encryption
# Was used as a fun puzzle for people
@bot.command()
async def repeat(ctx):
	text = ctx.message.content[(len(ctx.prefix)+7):] # the text of the message as a string

	# reverse
	flipped = text[::-1]

	key = var.key
	letters = 0 #for tracking and skipping not-letters correctly

	output = ""

	# vigenere cipher - only process on letters
	for char in flipped:
		if char.isalpha(): #If the character is alphanumeric (a letter from a-z, upper or lower case)
			offset = 0
			if char.islower():
				offset = 97 #'a'
			else:
				offset = 65 #'A'

			num = ord(char) - offset #convert letter to a number, A = 0, B = 1 and so on

			encoded = ( ( num + ( ord( key[letters % len(key)]) -97)) % 26) + offset #"Add" number for the appropriate key character, loop around at Z=25, then shift back to letters

			output += chr(encoded) #Add character to string

			letters += 1

		elif char.isnumeric(): #If character is not a letter but is a digit:
			encoded = 105 - ord(char) #Encoding

			output += chr(encoded) #Add it to the string

		else: #If it's not a letter or a number:
			output+= char

	await ctx.send(output)

# Get image attachments to the message and save them locally as "[filename] - [submitter]", as well as posting it in a channel
@bot.command()
async def pleaseacceptimage(ctx, *, name):

	image_types = ["png", "jpeg", "gif", "jpg"]
	channel = bot.get_guild(var.svr_club).get_channel(var.chn_bot)

	if len(ctx.message.attachments) == 0:
		ctx.send("No attachments found.")
		return

	count = 0

	for att in ctx.message.attachments:
		if any(att.filename.lower().endswith(image) for image in image_types):
			filename = ctx.author.name + " - " + name + str(count) + "." + att.filename.split(".")[-1]
			count += 1

			await att.save(filename)
			await channel.send(file = await att.to_file(), content = filename)

# For a specific account belonging to a friend, deliver a "birthday present"
@bot.command()
async def itsmybirthday(ctx):
	if (ctx.author.id != var.usr_birthday and ctx.author.id != bot.owner_id) :
		await ctx.send("Are you sure? I wasn't told that...")
		return

	msg1  = "Oh, hi! You'll be here for your present, then! Let me just go fetch it...\n\n"
	msg1 += "Printing present.png...\n"
	msg1 += "Error: file present.png corrupted, dumping file data to output."
	await ctx.send(msg1)

	await asyncio.sleep(2)
	await ctx.send(".")
	await asyncio.sleep(2)
	await ctx.send("..")
	await asyncio.sleep(2)
	await ctx.send("...")

	dumpmsg = ""

	with open("maze.txt", "r") as file:
		for row in file:
			if ((len(dumpmsg) + len(row)) < 1990):
				dumpmsg += row

			else:
				await ctx.send(dumpmsg)
				dumpmsg = row

		await ctx.send(dumpmsg)

	await ctx.send("-----\n\nData stream complete. Returning to normal operation.\n\n-----")
	await ctx.send("I hope you enjoy it. Happy Birthday~")
	notify = await bot.fetch_user(bot.owner_id)
	await notify.send("I just sent my birthday present!")

# Update the bot using git pull and then restart it
@bot.command()
@commands.is_owner()
async def update(ctx):
	await ctx.send("Trying to update code...")
	p = await asyncio.create_subprocess_exec('git', 'pull')
	await p.wait()
	await ctx.send("Update complete. Restarting, be back soon :)")
	sys.exit()
	
# Shut down the bot, exiting the script that restarts it again for the update command
@bot.command()
@commands.is_owner()
async def goodnight(ctx):
	await ctx.send("Good night :)")
	sys.exit(1)

# Equivalent to goodnight, but with a different message
@bot.command()
@commands.is_owner()
async def kill(ctx):
	await ctx.send("Please no I beg you-")
	sys.exit(1)

# Ping all users that replied to a given message with a given emoji
# Experimental
@bot.command()
async def emojiping(ctx, msg):
	ref = ctx.message.reference
	if not ref:
		await ctx.send("This command can only be used in a reaction to another message.")
		return

	origin = await bot.get_guild(ref.guild_id).get_channel(ref.channel_id).fetch_message(ref.message_id)
	# await ctx.send(f"reacted to: '{origin.content}' with {len(origin.reactions)} unique reactions")
	for reaction in origin.reactions:
		if reaction.emoji == msg:
			print(f"Reaction found: {reaction.count} users")
			mentionlist = f"Pinging users reacting with {reaction.emoji}: "
			async for user in reaction.users():
				if (len(mentionlist) < 1950):
					# mention can fit in message still
					mentionlist += user.mention + " "
				else:
					# don't risk messages that are too long, send message and start a new one
					await ctx.send(mentionlist)
					mentionlist = user.mention + " "
			
			await ctx.send(mentionlist)
			return
	
	await ctx.send(f"Did not find {msg} as a reaction to the replied message")

#----------------------------------------------------------------

@bot.event
async def on_ready():
	print(f"Logged in as {bot.user}")
	await rolecheck()
	print("Initial rolecheck complete")

@bot.event
async def on_message(message):
	if message.author == bot.user:
		return

	# Ignore all messages from a specific server that the bot is only in for checking
	if message.channel.type is not discord.ChannelType.private:
		if message.guild.id == var.svr_ignore:
			return

	if message.content.lower().startswith(('owo','uwu','hewwo')) and message.guild.id == var.svr_club:
		await message.channel.send('Ew, furry')

	await bot.process_commands(message)

# Process a reaction payload to pass relevant data on to other functions
async def payloadhandle(payload,remove=False):
	#print(f"Parsing payload-----")
	for message in [a for a in inst_var.messagestocheck if a.msg == payload.message_id]:
		#print("Reaction message ID matches a reactset, passing to roleaddremove\n")
		target = await bot.fetch_user(payload.user_id)
		msg = await bot.get_guild(payload.guild_id).get_channel(payload.channel_id).fetch_message(payload.message_id)
		await roleaddremove(reactemoji=payload.emoji,user=target,msg=msg,reactobj=message,remove=remove)


@bot.event
async def on_raw_reaction_add(payload):
	#print(f"\n\nReaction payload: {payload.emoji.name} by {str(payload.member)} ({payload.user_id}), add")
	await payloadhandle(payload=payload,remove=False)

@bot.event
async def on_raw_reaction_remove(payload):
	#print(f"\n\nReaction payload: {payload.emoji.name} by {str(payload.member)} ({payload.user_id}), remove")
	await payloadhandle(payload=payload,remove=True)

# Poke fun at a particular user when one of their messages is deleted
@bot.event
async def on_message_delete(message):
	if message.author.id == var.usr_j and message.guild.id == var.svr_club:
		msg = var.jnames[random.randrange(100)]
		msg += " deleted a message, but I caught it! It said:\n```"
		msg += message.content
		msg += "\n```"
		await message.channel.send(msg)

bot.run(TOKEN)
