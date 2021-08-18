from discord import player
from game_room import *
import asyncio
import discord
import random
from mission import start_mission
from discord import activity
from discord.abc import User
from quest_sheet import quest_sheet
from game_info import game_info

current_round = {
    'decision': 0,
    'agree': [],
    'disagree': [],
	'team': []
}

message = None
vote_message = {}

async def end_vote(agree, disagree):
	embed = discord.Embed(title="개표 결과, 원정대는 가결되었습니다." if agree >
	                      disagree else "개표 결과, 원정대는 부결되었습니다.", description="각 인원의 투표는 다음과 같습니다.")
	embed.add_field(name="원정대에 찬성한 사람들은 다음과 같습니다.",
	                value=current_round['agree'], inline=False)
	embed.add_field(name="원정대에 반대한 사람들은 다음과 같습니다.",
	                value=current_round['disagree'], inline=False)
	if agree > disagree:
		await game_room['main_channel'].send(embed=embed)
		await start_mission(current_round['team'])
	else:
		await next_vote(embed)
	current_round['agree'].clear()
	current_round['disagree'].clear()

async def next_vote(embed):
	game_info['leader'] = game_room['members'][(game_room['members'].index(game_info['leader']) + 1) % len(game_room['members'])]
	if current_round['decision'] < 5:
		embed.add_field(name=f"새로운 원정대장은 {game_info['leader']}입니다.",value="원정대장님은 새로운 원정대를 결정해주세요.")
		await game_room['main_channel'].send(embed=embed)
		await decide_team(game_info['round'])
	else:
		embed.add_field(name="원정대가 연속 5번 부결되었습니다.", value="미션은 자동실패되며 다음 라운드로 넘어갑니다.")
		await game_room['main_channel'].send(embed=embed)
		await start_round()
		
async def add_teammate(payload, player):
	global message
	if payload.user_id == game_info['leader'].id:
		current_round['team'].append(player)
		await game_info['leader'].send(f"{player.name}님이 원정대에 추가되었습니다.")
		if len(current_round['team']) == quest_sheet[len(game_room['members'])][game_info['round'] - 1]:
			await message.delete()
			await start_voting(current_round['team'])

async def remove_teammate(payload, player):
	if payload.user_id == game_info['leader'].id:
		current_round['team'].remove(player)
		await game_info['leader'].send(f"{player.name}님이 원정대에서 제거되었습니다.")
		
async def decide_team(num):
	global message
	current_round['team'].clear()
	current_round['decision'] += 1
	player_emojis = ""
	embed = discord.Embed(title="원정대장님, 원정대를 결성해주셔야 합니다.",
	                      description=f"이번 라운드에 데려갈 인원은 {quest_sheet[len(game_room['members'])][game_info['round'] - 1]}명입니다.")
	for emoji in game_room['emojis']:
		player_emojis += f"{emoji} : {game_room['emojis'][emoji]}\n" if game_room['emojis'][emoji] else ""
	embed.add_field(name="원정대로 데려가고 싶은 사람의 이모티콘을 눌러주세요!",
	                value=f"각 이모티콘이 의미하는 플레이어는 다음과 같습니다.\n{player_emojis}")
	message = await game_info['leader'].send(embed=embed)
	for emoji in game_room['emojis']:
		if game_room['emojis'][emoji]:
			await message.add_reaction(emoji)

async def start_round():
	if game_info['round'] > 5:
		return
	game_info['round'] += 1
	embed = discord.Embed(title=f"{game_info['round']}라운드가 시작되었습니다!")
	embed.add_field(name=f"현재 원정대장은 {game_info['leader'].name}입니다.",
	                value=f"이번 라운드에 데려갈 인원은 {quest_sheet[len(game_room['members'])][game_info['round'] - 1]}명입니다.")
	await game_room['main_channel'].send(embed=embed)
	await decide_team(game_info['round'])


async def start_voting(team):
	embed = discord.Embed(
		title=f"원정대장이 {game_info['round']}라운드 {current_round['decision']}번째 팀을 결정했습니다.")
	str_team = ""
	for player in current_round['team']:
		str_team += f"{player.name} "
	embed.add_field(name="결정한 팀 구성원은...", value=f"{str_team}입니다!", inline=False)
	embed.add_field(name="원정대장의 결정에 찬/반 투표를 실행해주세요.",
	                value=f"찬성하시려면 👍을, 반대하시려면 👎을 눌러주세요!", inline=False)
	for player in game_room['members']:
		message = await player.send(embed=embed)
		vote_message[player] = message
		await message.add_reaction("👍")
		await message.add_reaction("👎")
	await game_room['main_channel'].send(embed=embed)