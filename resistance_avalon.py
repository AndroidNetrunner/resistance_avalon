import asyncio
from typing import MutableMapping
from utils import add_role_in_active_roles, remove_role_from_active_roles
import discord
import random
from discord import activity
from discord import player
from discord.abc import User
from discord.ext import commands
from discord.enums import Status
from roles import *
from ready_game import merlin, ready_game
from game_room import game_room
from start_round import *
from mission import try_mission
from end_game import judge_merlin

token = open("C:/Users/byukim/Documents/python/discord_bot/resistance_avalon/token.txt",
             'r').read()
game = discord.Game("현재 대기")
bot = commands.Bot(command_prefix='!',
                   status=discord.Status.online, activity=game)
@bot.command()
async def 추가(ctx, role):
    if role == PERCIVAL:
        add_role_in_active_roles(role, game_room['roles']['loyal'])
    elif role in [MORDRED, MORGANA, OBERON]:
        add_role_in_active_roles(role, game_room['roles']['evil'])
    else:
        await ctx.send(f"존재하지 않는 역할입니다.")

@bot.command()
async def 삭제(ctx, role):
    if role == PERCIVAL:
        remove_role_from_active_roles(role, game_room['roles']['loyal'])
    elif role in [MORDRED, MORGANA, OBERON]:
        remove_role_from_active_roles(role, game_room['roles']['evil'])
    else:
        await ctx.send(f"존재하지 않는 역할입니다.")

@bot.command()
async def 순서(ctx):
    str_order = ""
    for member in game_room['members']:
        str_order += f"{member.name} -> " 
    str_order += game_room['members'][0].name
    await ctx.send(str_order)
    
@bot.command()
async def 시작(ctx):
    game_room['main_channel'] = ctx
    game_room['members'].append(ctx.message.author)
    game_room['can_join'] = True
    embed = discord.Embed(title="레지스탕스 아발론에 오신 것을 환영합니다!",
                          desciption="레지스탕스 아발론은 선과 악의 세력이 대립하는 마피아 게임입니다. 선과 악의 갈등 속에서 승리를 위해 진실을 파악하세요!")
    embed.add_field(
        name="참가 방법", value="게임에 참가하고 싶다면 !참가를 입력해주세요.", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def 참가(ctx):
    if game_room['can_join'] == True:
        player = ctx.message.author
        if player not in game_room['members']:
            game_room['members'].append(player)
            await ctx.send("{}님이 참가하셨습니다. 현재 플레이어 {}명".format(player.name, len(game_room['members'])))
        else:
            await ctx.send("{}님은 이미 참가중입니다.".format(player.name))
    else:
        await ctx.send("참가가 이미 마감되었습니다.")


@bot.command()
async def 마감(ctx):
	if len(game_room['members']) < 5:
		await ctx.send("플레이어 수가 4명 이하입니다. 게임을 시작할 수 없습니다.")
		return
	if game_room['can_join']:
		game_room['can_join'] = False
		await ctx.send("참가가 마감되었습니다.")
		await ready_game()
		await start_round()
	else:
		await ctx.send("현재 진행중인 게임이 없습니다.")

@bot.event
async def on_raw_reaction_add(payload):
    if str(payload.emoji) in game_room['emojis'] and game_room['emojis'][str(payload.emoji)]:
        if not game_status['assassination']:
            await add_teammate(payload, game_room['emojis'][str(payload.emoji)])
        else:
            await judge_merlin(payload)
    elif str(payload.emoji) == "👍" or str(payload.emoji) == "👎":
        person = None
        for member in game_room['members']:
            if member.id == payload.user_id:
                person = member
                await person.send("찬성에 투표하셨습니다." if str(payload.emoji) == "👍" else "반대에 투표하셨습니다.")
                await game_room['main_channel'].send(f"{person.name}님이 투표하셨습니다.")
                await vote_message[person].delete()
                del vote_message[person]
                current_round['agree'].append(member.name) if str(payload.emoji) == "👍" else current_round['disagree'].append(member.name)
                break
        if len(current_round['agree']) + len(current_round['disagree']) >= len(game_room['members']):
            await end_vote(len(current_round['agree']), len(current_round['disagree']))
    elif str(payload.emoji) == "⭕" or str(payload.emoji) == "❌":
        await try_mission(payload, current_round['team'])

@bot.event
async def on_raw_reaction_remove(payload):
    if str(payload.emoji) in game_room['emojis'] and game_room['emojis'][str(payload.emoji)]:
        await remove_teammate(payload, game_room['emojis'][str(payload.emoji)])

bot.run(token)