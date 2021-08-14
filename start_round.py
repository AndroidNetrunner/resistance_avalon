from discord import player
from game_room import *
import asyncio
import discord
import random
from discord import activity
from discord.abc import User
from quest_sheet import quest_sheet
current_round = {'decision': 0}

async def decide_team(num):
	player_emojis = ""
	embed = discord.Embed(title="원정대장님, 원정대를 결성해주셔야 합니다.", description=f"이번 라운드에 데려갈 인원은 {quest_sheet[len(game_room['player'])][current_round['round'] - 1]}입니다.")
	for emoji in game_room['emojis']:
		player_emojis += f"{emoji} : {game_room['emojis'][emoji]}\n"
	embed.add_field(name="원정대로 데려가고 싶은 사람의 이모티콘을 눌러주세요!", value=f"각 이모티콘이 의미하는 숫자는 다음과 같습니다.\n{player_emojis}")
	message = game_room['leader'].send(embed=embed)
	for emoji in game_room['emojis']:
		message.add_reaction(emoji)
		
async def start_round(num):
	if num > 5:
		return
	current_round['round'] = num + 1
	embed = discord.Embed(title=f"{current_round['round']}라운드가 시작되었습니다!")
	embed.add_field(name=f"현재 원정대장은 {game_room['leader']}입니다.", value=f"이번 라운드에 데려갈 인원은 {quest_sheet[len(game_room['player'])][num]}명입니다.")
	await game_room['main_channel'].send(embed=embed)
	await decide_team(current_round['round'])

async def start_voting(team):
	embed = discord.Embed(title=f"원정대장이 {current_round['decision'] + 1}번째 팀을 결정했습니다.")
	embed.add_field(name="결정한 팀 구성원은...", value=f"{current_round['team']}입니다!")
	embed.add_field(name="원정대장의 결정에 찬/반 투표를 실행해주세요.", value=f"찬성하시려면 👍을, 반대하시려면 👎을 눌러주세요!")
	for player in game_room['members']:
		message = player.send(embed=embed)
		message.add_reaction("👍")
		message.add_reaction("👎")
	await game_room['main_channel'].send(embed=embed)
