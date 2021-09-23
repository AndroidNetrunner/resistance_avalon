from roles import *
import random
import discord
from Game_status import Game_status

async def merlin(merlin_player, roles):
    evils = []
    for player in roles:
        if roles[player] in [MORGANA, OBERON, EVIL, ASSASSIN]:
            evils.append(player.name)
    embed = discord.Embed(title="당신의 역할은 멀린입니다.", description="모드레드를 제외한 모든 악의 세력을 알 수 있지만, 당신이 암살당한다면 선의 세력은 패배합니다!")
    embed.add_field(name="당신의 눈에 보이는 악의 세력은...", value=f"{evils}입니다!")
    await merlin_player.send(embed=embed)

async def assassin(assassin_player, roles):
    evils = []
    for player in roles:
        if roles[player] in [MORDRED, MORGANA, EVIL]:
            evils.append(player.name)
    embed = discord.Embed(title="당신의 역할은 암살자입니다.", description="악의 세력이 패배하기 직전, 딱 1명을 암살할 수 있습니다. 멀린을 암살하면 역전승합니다!")
    embed.add_field(name="당신의 눈에 보이는 악의 세력은...", value=f"{evils}입니다!")
    await assassin_player.send(embed=embed)

async def loyal(loyal_player):
    embed = discord.Embed(title="당신의 역할은 선의 세력입니다.", description="다른 선의 세력을 찾아 미션을 성공시켜 게임에서 승리하세요!")
    await loyal_player.send(embed=embed)

async def evil(evil_player, roles):
    evils = []
    for player in roles:
        if player != evil_player and roles[player] in [MORDRED, MORGANA, EVIL, ASSASSIN]:
            evils.append(player.name)
    embed = discord.Embed(title="당신의 역할은 악의 하수인입니다.", description="다른 악의 하수인 동료들과 함께 미션을 실패시키거나 멀린을 찾아 게임에서 승리하세요!")
    embed.add_field(name="당신의 눈에 보이는 악의 세력은...", value=f"{evils}입니다!")
    await evil_player.send(embed=embed)

async def percival(percival_player, roles):
    merlin_candidate = []
    for player in roles:
        if roles[player] in [MERLIN, MORGANA]:
            merlin_candidate.append(player.name)
    embed = discord.Embed(title="당신의 역할은 퍼시발입니다.", description="당신은 멀린의 정체를 알고 게임을 시작할 수 있습니다.")
    embed.add_field(name="당신의 눈에 보이는 멀린(들)은...", value=f"{merlin_candidate}입니다!")
    await percival_player.send(embed=embed)
    
async def mordred(mordred_player, roles):
    evils = []
    for player in roles:
        if roles[player] in [MORGANA, EVIL, ASSASSIN]:
            evils.append(player.name)
    embed = discord.Embed(title="당신의 역할은 모드레드입니다.", description="멀린은 당신이 악의 세력인지 모르고 시작합니다.")
    embed.add_field(name="당신의 눈에 보이는 악의 세력은...", value=f"{evils}입니다!")
    await mordred_player.send(embed=embed)

async def morgana(morgana_player, roles):
    evils = []
    for player in roles:
        if roles[player] in [MORDRED, EVIL, ASSASSIN]:
            evils.append(player.name)
    embed = discord.Embed(title="당신의 역할은 모르가나입니다.", description="퍼시발에게 당신은 멀린 후보로 보입니다.")
    embed.add_field(name="당신의 눈에 보이는 악의 세력은...", value=f"{evils}입니다!")
    await morgana_player.send(embed=embed)

async def oberon(oberon_player):
    embed = discord.Embed(title="당신의 역할은 오베론입니다.", description="악의 하수인이지만 다른 악의 하수인들을 알 수 없고, 악의 하수인들도 당신의 정체를 모릅니다.")
    await oberon_player.send(embed=embed)

async def show_roles(roles):
    for player in roles:
        role = roles[player]
        if role == MERLIN:
            await merlin(player, roles)
        elif role == ASSASSIN:
            await assassin(player, roles)
        elif role == PERCIVAL:
            await percival(player, roles)
        elif role == MORDRED:
            await mordred(player, roles)
        elif role == MORGANA:
            await morgana(player, roles)
        elif role == OBERON:
            await oberon(player)
        elif role == LOYAL:
            await loyal(player)
        elif role == EVIL:
            await evil(player, roles)

def add_normal_roles(room_info):
    players = len(room_info.members)
    loyal = players // 2 + 1 if players != 9 else 6
    evil = players - loyal
    while len(room_info.roles['loyal']) < loyal:
        room_info.roles['loyal'].append(LOYAL)
    while len(room_info.roles['evil']) < evil:
        room_info.roles['evil'].append(EVIL)

def assign_roles(room_info, roles):
    add_normal_roles(room_info)
    current_roles = room_info.roles['loyal'] + room_info.roles['evil']
    random.shuffle(current_roles)
    for i in range(len(current_roles)):
        roles[room_info.members[i]] = current_roles[i]

def assign_numbers(room_info):
    copied_players = room_info.members.copy()
    for emoji in room_info.emojis:
        if copied_players:
            room_info.emojis[emoji] = copied_players.pop(0)
        else:
            break
        
async def ready_game(current_game):
    room_info = current_game['game_room']
    current_game['game_status'] = Game_status()
    roles = current_game['game_status'].roles
    assign_numbers(room_info)
    assign_roles(room_info, roles)
    await show_roles(roles)
    embed = discord.Embed()
    await room_info.main_channel.send("모든 플레이어에게 직업이 할당되었습니다.")
    current_game['game_status'].leader = random.choice(room_info.members)