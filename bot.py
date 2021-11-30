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

bot.remove_command('help')

Jnames = ("James", "Jacob", "Joseph", "Jackson", "Jayden", "John", "Jack", "Julian", "Joshua", "Jaxon", "Josiah", "Jonathan", "Jeremiah", "Jordan", "Jaxson", "Jose", "Jace", "Jason", "Jameson", "Justin", "Juan", "Jayce", "Jesus", "Jonah", "Jude", "Joel", "Jasper", "Jesse", "Jeremy", "Judah", "Jax", "Javier", "Jaden", "Jorge", "Josue", "Jake", "Jett", "Jaiden", "Jayceon", "Jeffrey", "Jase", "Julius", "Jensen", "Jaylen", "Johnny", "Johnathan", "Joaquin", "Jaxton", "Jay", "Jared", "Jamison", "Jonas", "Jayson", "Jaime", "Julio", "Johan", "Jerry", "Jamari", "Justice", "Jasiah", "Jimmy", "Jalen", "Julien", "Jakob", "Jagger", "Joe", "Jedidiah", "Jefferson", "Jamir", "Jaziel", "Jadiel", "Jaxen", "Jon", "Jeffery", "Jamal", "Jamie", "Joziah", "Juelz", "Jacoby", "Joey", "Jordy", "Jermaine", "Javion", "Jaxxon", "Jerome", "Junior", "Jairo", "Jabari", "Judson", "Jessie", "Javon", "Jad", "Jeremias", "Jovanni", "Jaxx", "Justus", "Jamarion", "Jesiah", "Jericho", "Jonathon")
version_number = "1.0.5"

# get the Google Sheet used for tracking things people like
# use creds to create a client to interact with the Google Drive API
scope = ['https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
sheet = client.open("Secret Santa Responses")
page = sheet.get_worksheet(0)



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
#perms are a dict of role to be limited : role required to have it
messagestocheck.append(reactset(
	link="686753804137267207/686753804137267288/811388529438883870",
	roles={
		"💜": "Heart",
		"🔑": "PuzzleSolver"} ))

#Test to make sure perms was working, kept around to demonstrate for future reference how to target custom emoji
#messagestocheck.append(reactset(
#	link="413975787427987457/689268656135471116/813726033689313330",
#	roles={
#		"🏳️‍🌈": "biggayrole",
#		"<:trans:702513977472581633>": "transrole",
#		"🚴": "birole"},
#	perms={
#		"transrole": "transpermission",
#		"birole": "transpermission"} ))

#https://discord.com/channels/413975787427987457/676348033285357568/817998671827173376
# Actual message in #welcome of the club
messagestocheck.append(reactset(
	link="413975787427987457/676348033285357568/817998671827173376",
	roles={
		"⭐": "Dog Star",
		"🍆": "OH&S hazard",
		"🏖️": "heypeople",
		"📝": "Master of Games",
		"📖": "book club"},
	perms={
		"Dog Star": "People who definitely exist",
		"OH&S hazard": "People who definitely exist",
		"heypeople": "People who definitely exist",
		"Master of Games": "People who definitely exist",
		"book club": "People who definitely exist"} ))

#https://discord.com/channels/413975787427987457/414025610113974274/826821211123351593
elements = reactset(
	link="413975787427987457/414025610113974274/826821211123351593",
	roles={
		"🔥": "Fire",
		"🌊": "Water",
		"⛰️": "Earth",
		"💨": "Air"}
	)



#https://discord.com/channels/413975787427987457/414025610113974274/826821211123351593
elements = reactset(
	link="413975787427987457/414025610113974274/826821211123351593",
	roles={
		"🔥": "Fire",
		"🌊": "Water",
		"⛰️": "Earth",
		"💨": "Air"}
	)




#TODO - Import class contents from file???



async def changememberrole(role,user,remove=False):
	if user.id == 268721746708791297:
		return

	if remove:
		try:
			member = await role.guild.fetch_member(user.id) #This is the dumbest fucking thing
			await member.remove_roles(role,reason="Removed reaction")
			print(f"Removed role {role.name} from {str(user)}")
		except Exception as e:
			print(f"Failed to remove role {role.name} from {str(user)} - {e}")
	else:
		try:
			member = await role.guild.fetch_member(user.id) #This is the dumbest fucking thing
			await member.add_roles(role,reason="Added reaction")
			print(f"Added role {role.name} to {str(user)}")
		except Exception as e:
			print(f"Failed to add role {role.name} to {str(user)} - {e}")
	pass



async def roleaddremove(reactemoji,user,msg,reactobj,remove=False):
	#attempts to get a role from reactemoji and reactobj, then add it to the user if the user is allowed to have it

	#print("roleaddremove beginning here :)")
	#role:
	try:
		role = discord.utils.get(msg.guild.roles, name = reactobj.reactdict[str(reactemoji)])
	except Exception as e:
		print(f"Failed to get role for emoji {reactemoji.name} - error {e}")
		print(f"Reaction changed by {str(user)} on message in {msg.guild.name}, channel {msg.channel.name}, ID: {msg.id}")
		return

	#print(f"successfully found a role {role.name}")

	# If role has a permission role and the person has it, give role, else print note and return
	if reactobj.permdict != None:
		prereq = reactobj.permdict.get(role.name)
		if prereq != None:
			roleneeded = discord.utils.get(msg.guild.roles, name = prereq)
			if user not in roleneeded.members:
				print(f"{str(user)} tried to add or remove role {role.name} but could not as they do not have role {prereq}")
				return

	#print("User appears to have permission, passing to changememberrole")
	await changememberrole(role=role,user=user,remove=remove)



async def rolecheck():
	#https://discord.com/channels/686753804137267207/686753804137267288/811388529438883870 test message in my server

	for message in messagestocheck:

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



@bot.command()
async def enter(ctx, arg):
	realname = arg
	userID = ctx.author.id
	discname = str(ctx.author)

	names.append((realname,userID,discname))
	await ctx.send(f"Added {realname} with Discord name {discname} to my Secret Santa list!")

@bot.command()
async def addperson(ctx, name, ID: int):
	if 	(ctx.channel.id != 413979914900078592 and ctx.channel.id != 686928934411173912):
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


@bot.command()
async def listnames(ctx):
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



@bot.command()
async def fire(ctx):
	allowed = [268721746708791297, 218978216805793794, 180597311309742080]
	if ctx.author.id not in allowed:
		await ctx.send(f"Sorry, this command can only be used by {bot.fetch_user(268721746708791297).name} (or, temporarily, her partners).")
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
			open("DONT_FUCKING_OPEN_THIS.txt", "x")
			print('Created DONT_FUCKING_OPEN_THIS.txt')
		except:
			pass

		DONT = open("DONT_FUCKING_OPEN_THIS.txt","w+")
		DONT.write("Recipients, in order of names.txt:\n\n")
		for name, ID, username in recipients:
			DONT.write(name + "\n")
		DONT.close()
		await ctx.send("Created DONT_FUCKING_OPEN_THIS.txt!")

@bot.command()
async def retry(ctx):
	allowed = [268721746708791297, 218978216805793794, 180597311309742080]
	if ctx.author.id not in allowed:
		await ctx.send(f"Sorry, this command can only be used by {bot.fetch_user(268721746708791297).name} (or, temporarily, her partners).")
		return
	recipients = []
	with open("DONT_FUCKING_OPEN_THIS.txt", "r") as recip:
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



def rollk3(n):
	rolls = []
	for i in range(0,n):
		rolls.append(random.randint(1,6))

	return sum((sorted(rolls,reverse=True))[:3])

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




@bot.command()
async def d10000(ctx):
	await ctx.send(f"Rolled a d10000: {random.randint(1,10000)}")

@bot.event
async def on_ready():
	print(f"Logged in as {bot.user}")
	await rolecheck()
	print("Initial rolecheck complete")
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
	target = await bot.fetch_user(268721746708791297)
	await target.send("uwu what's this")



@bot.command()
async def list(ctx):
	Emma = await bot.fetch_user(268721746708791297)
	message = f"```Ramiel v{version_number} commands:\n"
	message += " - list: lists bot commands.\n"
	message += " - ping: prompt a basic response.\n"
	message += f" - annoyEmma: sends a message to Emma ({str(Emma)}).\n"
	message += " - annoyEmmaByUser: sends a different message to Emma, using a different targeting method.\n"
	message += " - role: tells the bot to update member roles based on reactions. Currently only applies to a test server.\n"
	message += " - repeat: repeats what you say back to you. WARNING: In Progress."
	message += "```"

	await ctx.send(message)



@bot.command()
async def repeatbutnotmixedup(ctx, *args):
	text = ' '.join(args) # the text of the message as a string
	await ctx.send(text)

@bot.command()
async def repeat(ctx):
	text = ctx.message.content[(len(ctx.prefix)+7):] # the text of the message as a string

	# reverse
	flipped = text[::-1]

	key = "onethreeseven"
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



@bot.command()
async def pleaseacceptimage(ctx, *, name):
	# Gets an image from the message attachment, saves it as "[name] - [submitter]" and posts it in the bot channel

	image_types = ["png", "jpeg", "gif", "jpg"]
	channel = bot.get_guild(413975787427987457).get_channel(689268656135471116)

	if len(ctx.message.attachments) == 0:
		ctx.send("No attachments found.")
		return

	count = 0

	for att in ctx.message.attachments:
		if any(att.filename.lower().endswith(image) for image in image_types):
			filename = ctx.author.name + " - " + name + str(count) + "." + att.filename.split(".")[-1];
			count += 1

			await att.save(filename)
			await channel.send(file = await att.to_file(), content = filename)



@bot.command()
async def itsmybirthday(ctx):
	# If it's Emily, send her an "image"

	if (ctx.author.id != 293678032730980352 and ctx.author.id != 268721746708791297) :
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

	notify = await bot.fetch_user(268721746708791297)
	await notify.send("I just sent my birthday present!")



@bot.command()
@commands.is_owner()
async def update(ctx):
	await ctx.send("Restarting!")
	p = asyncio.create_subprocess_exec('git', 'pull')
	await p.wait()
	sys.exit()
	


@bot.command()
@commands.is_owner()
async def goodnight(ctx):
	await ctx.send("Good night :)")
	sys.exit(1)

@bot.command()
@commands.is_owner()
async def kill(ctx):
	await ctx.send("Please no I beg you-")
	sys.exit(1)

#@bot.command()
#async def emojiping(ctx,)


#----------------------------------------------------------------

@bot.event
async def on_message(message):
	if message.author == bot.user:
		return

	# Ignore Pride Club for the moment
	if message.channel.type is not discord.ChannelType.private:
		if message.guild.id == 697695776339394600:
			return

	if message.content.lower().startswith(('owo','uwu','hewwo')):
		await message.channel.send('Ew, furry')

	await bot.process_commands(message)




async def payloadhandle(payload,remove=False):
	#print(f"Parsing payload-----")
	for message in [a for a in messagestocheck if a.msg == payload.message_id]:
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



@bot.event
async def on_reaction_add(reaction, member):
	pass
	#try:
	#	print(f"Reaction noticed in {reaction.message.channel.name} on message ID {reaction.message.id} - emoji name {reaction.emoji.name}")
	#except:
	#	print(f"Reaction noticed in {reaction.message.channel.name} on message ID {reaction.message.id} - emoji name {reaction.emoji}")

@bot.event
async def on_reaction_remove(reaction, member):
	pass
	#print(f"Reaction removed in {reaction.message.channel.name} on message ID {reaction.message.id}")

@bot.event
async def on_message_delete(message):
	if message.author.id == 438606605496483850 and message.guild.id == 413975787427987457:
		msg = Jnames[random.randrange(100)]
		msg += " deleted a message, but I caught it! It said:\n```"
		msg += message.content
		msg += "\n```"
		await message.channel.send(msg)


bot.run(TOKEN)
