import asyncio
from utils import add_role_in_active_roles, remove_role_from_active_roles
import discord
from discord import activity
from discord import player
from discord.abc import User
from discord.ext import commands
from discord.enums import Status
from roles import *
from ready_game import merlin, ready_game
from Game_room import Game_room
from start_round import *
from mission import try_mission
from end_game import judge_merlin

token = open("token.txt", 'r').read()
game = discord.Game("현재 대기")
bot = commands.Bot(command_prefix='!',
                   status=discord.Status.online, activity=game)

active_game = {}

@bot.command()
async def 추가(ctx, role):
    room_info = active_game[ctx.channel.id]['game_room']
    if role == PERCIVAL:
        await add_role_in_active_roles(role, room_info.roles['loyal'], room_info)
    elif role in [MORDRED, MORGANA, OBERON]:
        await add_role_in_active_roles(role, room_info.roles['evil'], room_info)
    else:
        await ctx.send(f"존재하지 않는 역할입니다.")

@bot.command()
async def 삭제(ctx, role):
    room_info = active_game[ctx.channel.id]['game_room']
    if role == PERCIVAL:
        await remove_role_from_active_roles(role, room_info.roles['loyal'], room_info)
    elif role in [MORDRED, MORGANA, OBERON]:
        await remove_role_from_active_roles(role, room_info.roles['evil'], room_info)
    else:
        await ctx.send(f"존재하지 않는 역할입니다.")

@bot.command()
async def 순서(ctx):
    room_info = active_game[ctx.channel.id]['game_room']
    str_order = ""
    for member in room_info.members:
        str_order += f"{member.name} -> " 
    str_order += room_info.members[0].name
    await ctx.send(str_order)
    
@bot.command()
async def 시작(ctx):
    current_game = {
        'game_room': Game_room()
    }
    active_game[ctx.channel.id] = current_game
    room_info = current_game['game_room']
    room_info.main_channel = ctx
    room_info.members.append(ctx.message.author)
    room_info.can_join = True
    embed = discord.Embed(title="레지스탕스 아발론에 오신 것을 환영합니다!",
                          desciption="레지스탕스 아발론은 선과 악의 세력이 대립하는 마피아 게임입니다. 선과 악의 갈등 속에서 승리를 위해 진실을 파악하세요!")
    embed.add_field(
        name="참가 방법", value="게임에 참가하고 싶다면 !참가를 입력해주세요.", inline=False)
    await bot.change_presence(activity=discord.Game(name="게임 진행"))
    await ctx.send(embed=embed)

@bot.command()
async def 참가(ctx):
    room_info = active_game[ctx.channel.id]['game_room']
    if room_info.can_join == True:
        player = ctx.message.author
        if player not in room_info.members:
            room_info.members.append(player)
            await ctx.send("{}님이 참가하셨습니다. 현재 플레이어 {}명".format(player.name, len(room_info.members)))
        else:
            await ctx.send("{}님은 이미 참가중입니다.".format(player.name))
    else:
        await ctx.send("참가가 이미 마감되었습니다.")


@bot.command()
async def 마감(ctx):
    current_game = active_game[ctx.channel.id]
    # if len(room_info.members) < 5:
    # 	await ctx.send("플레이어 수가 4명 이하입니다. 게임을 시작할 수 없습니다.")
    # 	return
    if current_game['game_room'].can_join:
        current_game['game_room'].can_join = False
        await ctx.send("참가가 마감되었습니다.")
        await ready_game(current_game)
        await start_round(current_game)
    else:
        await ctx.send("현재 진행중인 게임이 없습니다.")

@bot.event
async def on_raw_reaction_add(payload):
    current_game = None
    for channel_id in active_game:
        for member in active_game[channel_id]['game_room'].members:
            if payload.user_id == member.id:
                current_game = active_game[channel_id]
                break
    room_info = current_game['game_room'] if current_game else None
    game_status = current_game['game_status'] if current_game else None
    if not (room_info and game_status):
        return
    current_round = game_status.round_info
    if str(payload.emoji) in room_info.emojis and room_info.emojis[str(payload.emoji)]:
        if not game_status.assassination:
            await add_teammate(payload, room_info.emojis[str(payload.emoji)], current_game)
        else:
            await judge_merlin(payload, current_game)
    elif str(payload.emoji) == "👍" or str(payload.emoji) == "👎":
        person = None
        for member in room_info.members:
            if member.id == payload.user_id:
                person = member
                await person.send("찬성에 투표하셨습니다." if str(payload.emoji) == "👍" else "반대에 투표하셨습니다.")
                await room_info.main_channel.send(f"{person.name}님이 투표하셨습니다.")
                await current_round['vote_message'][person].delete()
                del current_round['vote_message'][person]
                current_round['agree'].append(member.name) if str(payload.emoji) == "👍" else current_round['disagree'].append(member.name)
                break
        if len(current_round['agree']) + len(current_round['disagree']) >= len(room_info.members):
            await end_vote(current_game)
    elif str(payload.emoji) == "⭕" or str(payload.emoji) == "❌":
        await try_mission(payload, current_round['team'], current_game)

@bot.event
async def on_raw_reaction_remove(payload):
    for channel_id in active_game:
        for member in active_game[channel_id].members:
            if payload.user_id == member.id:
                current_game = active_game[channel_id]
                break
    room_info = current_game['game_room'] if current_game else None
    if not room_info:
        return
    if str(payload.emoji) in room_info.emojis and room_info.emojis[str(payload.emoji)]:
        await remove_teammate(payload, room_info.emojis[str(payload.emoji)], current_game)

bot.run(token)