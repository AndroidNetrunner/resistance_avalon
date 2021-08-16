import asyncio
import discord
import random
from roles import *
from game_room import game_room
from start_round import current_round
async def start_mission(team):
	mission_message = []
	embed = discord.Embed(title="이제 미션을 수행할 차례입니다!", description=f"현재 팀원은 {current_round['team']}입니다.")
	embed.add_field(name="아래 이모티콘을 통해 성공과 실패 중 하나를 골라주세요!", value="성공은 ⭕를, 실패는 ❌를 누르시면 됩니다!")
	for player in team:
		mission_message[player] = await player.send(embed=embed)
		await mission_message[player].add_reaction("⭕")
		if roles[player] in [MORDRED, MORGANA, OBERON, EVIL, ASSASSIN]:
			await mission_message[player].add_reaction("❌")