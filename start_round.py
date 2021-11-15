from discord import player
import asyncio
import discord
import random
from mission import start_mission
from discord import activity
from discord.abc import User
from quest_sheet import quest_sheet
import time

async def vote(current_game, current_round, payload, lock):
    await lock.acquire()
    room_info = current_game['game_room']
    person = None
    for member in room_info.members:
        if member.id == payload.user_id:
            person = member
            if person not in current_round['vote_message'] or current_round['vote_message'][person].id != payload.message_id:
                lock.release()
                return
            await person.send("찬성에 투표하셨습니다." if str(payload.emoji) == "👍" else "반대에 투표하셨습니다.")
            await room_info.main_channel.send(f"{person.name}님이 투표하셨습니다.")
            await current_round['vote_message'][person].delete()
            del current_round['vote_message'][person]
            current_round['agree'].append(member.name) if str(payload.emoji) == "👍" else current_round['disagree'].append(member.name)
            break
    if len(current_round['agree']) + len(current_round['disagree']) >= len(room_info.members):
        await end_vote(current_game)
    lock.release()

async def end_vote(current_game):
    current_round = current_game['game_status'].round_info
    game_room = current_game['game_room']
    embed = discord.Embed(title="개표 결과, 원정대는 가결되었습니다." if len(current_round['agree']) >
                          len(current_round['disagree']) else "개표 결과, 원정대는 부결되었습니다.", description="각 인원의 투표는 다음과 같습니다.")
    embed.add_field(name="원정대에 찬성한 사람들은 다음과 같습니다.",
                    value=current_round['agree'], inline=False)
    embed.add_field(name="원정대에 반대한 사람들은 다음과 같습니다.",
                    value=current_round['disagree'], inline=False)
    if len(current_round['agree']) > len(current_round['disagree']):
    	await game_room.main_channel.send(embed=embed)
    	await start_mission(current_game)
    else:
    	await next_vote(embed, current_game)
    current_round['agree'].clear()
    current_round['disagree'].clear()

async def next_vote(embed, current_game):
    game_status = current_game['game_status']
    game_room = current_game['game_room']
    current_round = game_status.round_info
    game_status.leader = game_room.members[(game_room.members.index(
        game_status.leader) + 1) % len(game_room.members)]
    if current_round['decision'] < 5:
        embed.add_field(name=f"새로운 원정대장은 {game_status.leader}입니다.", value="원정대장님은 새로운 원정대를 결정해주세요.")
        await game_room.main_channel.send(embed=embed)
        await decide_team(game_room, game_status)
    else:
        embed.add_field(name="원정대가 연속 5번 부결되었습니다.", value="미션은 자동실패되며 다음 라운드로 넘어갑니다.")
        await game_room.main_channel.send(embed=embed)
        await start_round(current_game)


async def add_teammate(payload, player, current_game):
    current_round = current_game['game_status'].round_info
    if payload.user_id != current_game['game_status'].leader.id:
        return
    if payload.message_id != current_round['message'].id:
        return
    current_round['team'].append(player)
    await current_game['game_status'].leader.send(f"{player.name}님이 원정대에 추가되었습니다.")
    if len(current_round['team']) == quest_sheet[len(current_game['game_room'].members)][current_game['game_status'].round - 1]:
        await current_round['message'].delete()
        await start_voting(current_game)


async def remove_teammate(payload, player, current_game):
    game_status = current_game['game_status']
    current_round = game_status.round_info
    if payload.user_id == game_status.leader.id:
        current_round['team'].remove(player)
        await game_status.leader.send(f"{player.name}님이 원정대에서 제거되었습니다.")

async def decide_team(game_room, game_status):
    current_round = game_status.round_info
    current_round['team'].clear()
    current_round['decision'] += 1
    player_emojis = ""
    embed = discord.Embed(title="원정대장님, 원정대를 결성해주셔야 합니다.",
                          description=f"이번 라운드에 데려갈 인원은 {quest_sheet[len(game_room.members)][game_status.round - 1]}명입니다.")
    for emoji in game_room.emojis:
        player_emojis += f"{emoji} : {game_room.emojis[emoji]}\n" if game_room.emojis[emoji] else ""
    embed.add_field(name="원정대로 데려가고 싶은 사람의 이모티콘을 눌러주세요!",
                    value=f"각 이모티콘이 의미하는 플레이어는 다음과 같습니다.\n{player_emojis}")
    message = await game_status.leader.send(embed=embed)
    current_round['message'] = message
    for emoji in game_room.emojis:
        if game_room.emojis[emoji]:
            await message.add_reaction(emoji)


async def start_round(current_game):
    game_room = current_game['game_room']
    game_status = current_game['game_status']
    current_round = {
        'decision': 0,
        'agree': [],
        'disagree': [],
        'team': [],
        'message': None,
        'vote_message': {}
        }
    game_status.round_info = current_round
    if game_status.round > 5:
        return
    game_status.round += 1
    embed = discord.Embed(title=f"{game_status.round}라운드가 시작되었습니다!")
    embed.add_field(name=f"현재 원정대장은 {game_status.leader.name}입니다.",
                    value=f"이번 라운드에 데려갈 인원은 {quest_sheet[len(game_room.members)][game_status.round - 1]}명입니다.")
    await game_room.main_channel.send(embed=embed)
    await decide_team(game_room, game_status)

async def start_voting(current_game):
    team = current_game['game_status'].round_info['team']
    embed = discord.Embed(
        title=f"{current_game['game_status'].leader.name}님이 {current_game['game_status'].round}라운드 {current_game['game_status'].round_info['decision']}번째 팀을 결정했습니다.")
    str_team = ""
    for player in team:
        str_team += f"{player.name}, "
    str_team = str_team[:-2]
    embed.add_field(name="결정한 팀 구성원은...", value=f"{str_team}입니다!", inline=False)
    embed.add_field(name="원정대장의 결정에 찬/반 투표를 실행해주세요.",
                    value=f"찬성하시려면 👍을, 반대하시려면 👎을 눌러주세요!", inline=False)
    for player in current_game['game_room'].members:
        message = await player.send(embed=embed)
        current_game['game_status'].round_info['vote_message'][player] = message
        await message.add_reaction("👍")
        await message.add_reaction("👎")
    await current_game['game_room'].main_channel.send(embed=embed)