import asyncio
import discord
import random

from discord.colour import Color
from roles import *
from end_game import end_game
from threading import Lock

lock_for_mission = Lock()

async def start_mission(current_game):
    game_status = current_game['game_status']
    team = game_status.round_info['team']
    game_status.mission_result = {
        "success": 0,
        "fail": 0
        }
    mission_message = game_status.mission_message
    mission_message.clear()
    name_team = [member.name for member in team]
    embed = discord.Embed(title="이제 미션을 수행할 차례입니다!",
                        description=f"현재 팀원은 {' '.join(name_team)}입니다.")
    embed.add_field(name="아래 이모티콘을 통해 성공과 실패 중 하나를 골라주세요!",
                    value="성공은 ⭕를, 실패는 ❌를 누르시면 됩니다!")
    for player in team:
        mission_message[player] = await player.send(embed=embed)
        await mission_message[player].add_reaction("⭕")
        if game_status.roles[player] in [MORDRED, MORGANA, OBERON, EVIL, ASSASSIN]:
            await mission_message[player].add_reaction("❌")


async def try_mission(payload, team, current_game, lock):
    await lock.acquire()
    person = None
    game_status = current_game['game_status']
    mission_result = game_status.mission_result
    for member in current_game['game_room'].members:
        if member.id == payload.user_id:
            person = member
    if not person:
        lock.release()
        return
    if payload.message_id != game_status.mission_message[person].id:
        lock.release()
        return
    if str(payload.emoji) == "⭕":
        mission_result['success'] += 1
        await person.send("미션 성공을 선택하셨습니다.")
    else:
        mission_result["fail"] += 1
        await person.send("미션 실패를 선택하셨습니다.")
    await game_status.mission_message[person].delete()
    if mission_result['success'] + mission_result['fail'] == len(team):
        await judge_mission(current_game)
    lock.release()

async def judge_mission(current_game):
    game_status = current_game['game_status']
    mission_result = game_status.mission_result
    game_room = current_game['game_room']
    embed = discord.Embed(title=f"원정대의 미션 결과는 다음과 같습니다.")    
    if not mission_result['fail'] or (mission_result['fail'] == 1 and len(game_room.members) >= 7 and game_status.round == 4):
        embed.add_field(name="원정대는 무사히 미션을 성공하였습니다!",
                        value=f"성공: {mission_result['success']} 실패: {mission_result['fail']}", inline=False)
        game_status.round_success += 1
        embed.color = Color.blue()
    else:
        embed.add_field(name="원정대는 아쉽게도 미션을 실패하였습니다...",
                        value=f"성공: {mission_result['success']} 실패: {mission_result['fail']}", inline=False)
        game_status.round_fail += 1
        embed.color = Color.red()
    embed.add_field(name="현재 라운드까지의 미션 결과는 다음과 같습니다.",
                    value=f"선의 세력: {game_status.round_success}, 악의 하수인: {game_status.round_fail}", inline=False)
    await game_room.main_channel.send(embed=embed)
    await next_round(current_game)


async def next_round(current_game):
    game_status = current_game['game_status']
    mission_result = game_status.mission_result
    game_room = current_game['game_room']
    from start_round import start_round
    mission_result['success'] = 0
    mission_result['fail'] = 0
    if not (game_status.round_success == 3 or game_status.round_fail == 3):
        game_status.leader = game_room.members[(game_room.members.index(
            game_status.leader) + 1) % len(game_room.members)]
        await start_round(current_game)
    else:
        await end_game(current_game)
