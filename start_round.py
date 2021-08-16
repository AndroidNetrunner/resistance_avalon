from discord import player
from game_room import *
import asyncio
import discord
import random
from discord import activity
from discord.abc import User
from quest_sheet import quest_sheet
current_round = {'decision': 0,
'agree': [],
'disagree': []}
message = None
vote_message = {}

async def end_vote(agree, disagree):
	embed = discord.Embed(title="개표 결과, 원정대는 가결되었습니다." if agree > disagree else "개표 결과, 원정대는 부결되었습니다.", description="각 인원의 투표는 다음과 같습니다.")
	embed.add_field(name="원정대에 찬성한 사람들은 다음과 같습니다.", value=current_round['agree'], inline=False)
	embed.add_field(name="원정대에 반대한 사람들은 다음과 같습니다.", value=current_round['disagree'], inline=False)
	await game_room['main_channel'].send(embed=embed)
	# if agree > disagree:
	# 	start_mission(current_round['team'])

async def add_teammate(payload, player):
	global message
	if payload.user_id == current_round['leader'].id:
		current_round['team'].append(player)
		await current_round['leader'].send(f"{player.name}이 원정대에 추가되었습니다.")
		if len(current_round['team']) == quest_sheet[len(game_room['members'])][current_round['round'] - 1]:
			await message.delete()
			await start_voting(current_round['team'])
		
async def decide_team(num):
	global message
	current_round['team'] = []
	player_emojis = ""
	embed = discord.Embed(title="원정대장님, 원정대를 결성해주셔야 합니다.", description=f"이번 라운드에 데려갈 인원은 {quest_sheet[len(game_room['members'])][current_round['round'] - 1]}입니다.")
	for emoji in game_room['emojis']:
		player_emojis += f"{emoji} : {game_room['emojis'][emoji]}\n" if game_room['emojis'][emoji] else ""
	embed.add_field(name="원정대로 데려가고 싶은 사람의 이모티콘을 눌러주세요!", value=f"각 이모티콘이 의미하는 플레이어는 다음과 같습니다.\n{player_emojis}")
	message = await current_round['leader'].send(embed=embed)
	for emoji in game_room['emojis']:
		if game_room['emojis'][emoji]:
			await message.add_reaction(emoji)
			
async def start_round(num):
	if num > 5:
		return
	current_round['leader'] = random.choice(game_room['members'])
	current_round['round'] = num + 1
	embed = discord.Embed(title=f"{current_round['round']}라운드가 시작되었습니다!")
	embed.add_field(name=f"현재 원정대장은 {current_round['leader'].name}입니다.", value=f"이번 라운드에 데려갈 인원은 {quest_sheet[len(game_room['members'])][num]}명입니다.")
	await game_room['main_channel'].send(embed=embed)
	await decide_team(current_round['round'])

async def start_voting(team):
	embed = discord.Embed(title=f"원정대장이 {current_round['round']}라운드 {current_round['decision'] + 1}번째 팀을 결정했습니다.")
	str_team = ""
	for player in current_round['team']:
		str_team += f"{player.name} "
	embed.add_field(name="결정한 팀 구성원은...", value=f"{str_team}입니다!", inline=False)
	embed.add_field(name="원정대장의 결정에 찬/반 투표를 실행해주세요.", value=f"찬성하시려면 👍을, 반대하시려면 👎을 눌러주세요!", inline=False)
	for player in game_room['members']:
		message = await player.send(embed=embed)
		vote_message[player] = message
		await message.add_reaction("👍")
		await message.add_reaction("👎")
	await game_room['main_channel'].send(embed=embed)
