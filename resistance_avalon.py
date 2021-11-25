import asyncio
from utils import add_role_in_active_roles, get_current_game, is_open, remove_role_from_active_roles
import discord
import datetime
from discord.ext import commands
from roles import *
from ready_game import ready_game
from Game_room import Game_room
from start_round import *
from mission import try_mission
from end_game import judge_merlin
from active_games import active_games

token = open("token.txt", 'r').read()
game = discord.Game(f">명령어")
bot = commands.Bot(command_prefix='>',
                   status=discord.Status.online, activity=game)
lock_for_vote = asyncio.Lock()
lock_for_mission = asyncio.Lock()
with open('resistance_avalon.jpg', 'rb') as f:
    image = f.read()

@bot.command()
async def 명령어(ctx):
    await ctx.send("""
>명령어 : 사용할 수 있는 명령어 목록을 출력합니다.
>시작 : 참가할 수 있는 게임을 만듭니다. 같은 채널에 이미 시작한 게임이 있다면 사용할 수 없습니다.
>참가 : 시작한 게임을 참가합니다. 시작한 게임이 존재하지 않거나 게임이 마감된 상태라면 사용할 수 없습니다.
>마감 : 참가를 마감하고 게임을 시작하기 위한 명령어입니다. 마감되지 않은 게임이 없다면 사용할 수 없습니다.
>리셋 : 진행 중인 게임을 초기화합니다. 새로운 게임을 시작할 수 있는 상태가 됩니다.
>순서 : 현재 원정대장이 옮겨가는 순서를 출력합니다. 진행 중인 게임이 없다면 실행할 수 없습니다.
>추가 X : 새로운 직업을 추가합니다. X는 추가할 직업을 뜻합니다. 참가를 받는 동안에만 사용할 수 있습니다. 예) >추가 퍼시발
>삭제 X : 추가한 직업을 삭제합니다. X는 삭제할 직업을 뜻합니다. 참가를 받는 동안에만 사용할 수 있습니다. 예) >삭제 퍼시발
    """)

@bot.command()
async def 추가(ctx, role):
    if ctx.channel.id not in active_games:
        await ctx.send("시작한 게임이 존재하지 않습니다.")
        return
    room_info = active_games[ctx.channel.id]['game_room']
    if role == PERCIVAL:
        await add_role_in_active_roles(role, room_info.roles['loyal'], room_info)
    elif role in [MORDRED, MORGANA, OBERON]:
        await add_role_in_active_roles(role, room_info.roles['evil'], room_info)
    else:
        await ctx.send(f"존재하지 않는 역할입니다.")

@bot.command()
async def 삭제(ctx, role):
    if ctx.channel.id not in active_games:
        await ctx.send("시작한 게임이 존재하지 않습니다.")
        return
    room_info = active_games[ctx.channel.id]['game_room']
    if role == PERCIVAL:
        await remove_role_from_active_roles(role, room_info.roles['loyal'], room_info)
    elif role in [MORDRED, MORGANA, OBERON]:
        await remove_role_from_active_roles(role, room_info.roles['evil'], room_info)
    else:
        await ctx.send(f"존재하지 않는 역할입니다.")

@bot.command()
async def 순서(ctx):
    if ctx.channel.id not in active_games:
        await ctx.send("시작한 게임이 존재하지 않습니다.")
        return
    room_info = active_games[ctx.channel.id]['game_room']
    str_order = ""
    for member in room_info.members:
        str_order += f"{member.name} -> " 
    str_order += room_info.members[0].name
    await ctx.send(str_order)
    
@bot.command()
async def 시작(ctx):
    if ctx.channel.id in active_games:
        await ctx.send("이미 시작한 게임이 존재합니다.")
        return
    print(f"{datetime.datetime.now()} : <start> {ctx.channel.id}")
    current_game = {
        'game_room': Game_room()
    }
    active_games[ctx.channel.id] = current_game
    room_info = current_game['game_room']
    room_info.main_channel = ctx
    room_info.members.append(ctx.message.author)
    room_info.can_join = True
    embed = discord.Embed(title="레지스탕스 아발론에 오신 것을 환영합니다!",
                          desciption="레지스탕스 아발론은 선과 악의 세력이 대립하는 마피아 게임입니다. 선과 악의 갈등 속에서 승리를 위해 진실을 파악하세요!")
    embed.add_field(
        name="참가 방법", value="게임에 참가하고 싶다면 >참가를 입력해주세요.", inline=False)
    await bot.change_presence(activity=discord.Game(name=f"{len(active_games)}개 게임"))
    await ctx.send(embed=embed)

@bot.command()
async def 참가(ctx):
    room_info = await is_open(ctx)
    if not room_info:
        return
    player = ctx.message.author
    if player not in room_info.members:
        room_info.members.append(player)
        await ctx.send("{}님이 참가하셨습니다. 현재 플레이어 {}명".format(player.name, len(room_info.members)))
    else:
        await ctx.send("{}님은 이미 참가중입니다.".format(player.name))

@bot.command()
async def 마감(ctx):
    if ctx.channel.id not in active_games:
        await ctx.send("시작한 게임이 존재하지 않습니다.")
        return
    current_game = active_games[ctx.channel.id]
    if len(current_game['game_room'].members) < 5:
    	await ctx.send("플레이어 수가 4명 이하입니다. 게임을 시작할 수 없습니다.")
    	return
    if not current_game['game_room'].can_join:
        await ctx.send("게임이 이미 시작되었습니다.")
        return
    current_game['game_room'].can_join = False
    await ctx.send("참가가 마감되었습니다.")
    await ready_game(current_game)
    await start_round(current_game)

@bot.command()
async def 리셋(ctx):
    if ctx.channel.id not in active_games:
        await ctx.send("시작한 게임이 존재하지 않습니다.")
        return
    del active_games[ctx.channel.id]
    await bot.change_presence(activity=discord.Game(name=f"{len(active_games)}개 게임"))
    await ctx.send("진행하는 게임을 중단합니다.")

@bot.event
async def on_ready():
    await bot.user.edit(avatar=image)

@bot.event
async def on_raw_reaction_add(payload):
    current_game = get_current_game(payload.user_id)
    room_info = current_game['game_room'] if current_game else None
    game_status = current_game['game_status'] if current_game and 'game_status' in current_game else None
    if not (room_info and game_status):
        return
    current_round = game_status.round_info
    if str(payload.emoji) in room_info.emojis and room_info.emojis[str(payload.emoji)]:
        await judge_merlin(payload, current_game) if game_status.assassination else await add_teammate(payload, room_info.emojis[str(payload.emoji)], current_game)          
    elif str(payload.emoji) in ["👍","👎"]:
        asyncio.ensure_future(vote(current_game, current_round, payload, lock_for_vote))
    elif str(payload.emoji) in ["⭕", "❌"]:
        asyncio.ensure_future(try_mission(payload, current_round['team'], current_game, lock_for_mission))

@bot.event
async def on_raw_reaction_remove(payload):
    current_game = get_current_game(payload.user_id)
    room_info = current_game['game_room'] if current_game else None
    if not room_info:
        return
    if str(payload.emoji) in room_info.emojis and room_info.emojis[str(payload.emoji)]:
        await remove_teammate(payload, room_info.emojis[str(payload.emoji)], current_game)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"{ctx.message.content} 는 존재하지 않는 명령어입니다.")
        return
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send(f"엇! 제가 다른 분들에게 메세지를 보낼 수 없어요! 아마 제게 메세지를 발송할 권한이 주어지지 않은 것 같아요. 혹시 모르는 사람의 DM을 차단한 분이 계시지 않을까요?")
        return
    await ctx.send("오류가 발생하였습니다. >리셋을 통해 게임을 새로고침해주세요.")
    print(f"resistance_avalon - {datetime.datetime.now()} : <Error> {ctx.channel.id}, error: {error}")
    
bot.run(token)
