from game_room import game_room
from roles import *
import random
import discord

async def merlin(merlin_player):
    evils = []
    for player in roles:
        if roles[player] in [MORGANA, OBERON, EVIL, ASSASSIN]:
            evils.append(player.name)
    embed = discord.Embed(title="당신의 역할은 멀린입니다.", description="모드레드를 제외한 모든 악의 세력을 알 수 있지만, 당신이 암살당한다면 선의 세력은 패배합니다!")
    embed.add_field(name="당신의 눈에 보이는 악의 세력은...", value=f"{evils}입니다!")
    await merlin_player.send(embed=embed)

async def assassin(assassin_player):
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

async def evil(evil_player):
    evils = []
    for player in roles:
        if player != evil_player and roles[player] in [MORDRED, MORGANA, EVIL, ASSASSIN]:
            evils.append(player.name)
    embed = discord.Embed(title="당신의 역할은 악의 하수인입니다.", description="다른 악의 하수인 동료들과 함께 미션을 실패시키거나 멀린을 찾아 게임에서 승리하세요!")
    embed.add_field(name="당신의 눈에 보이는 악의 세력은...", value=f"{evils}입니다!")
    await evil_player.send(embed=embed)

async def percival(percival_player):
    merlin_candidate = []
    for player in roles:
        if roles[player] in [MERLIN, MORGANA]:
            merlin_candidate.append(player.name)
    embed = discord.Embed(title="당신의 역할은 퍼시발입니다.", description="당신은 멀린의 정체를 알고 게임을 시작할 수 있습니다.")
    embed.add_field(name="당신의 눈에 보이는 멀린(들)은...", value=f"{merlin_candidate}입니다!")

async def mordred(mordred_player):
    evils = []
    for player in roles:
        if roles[player] in [MORGANA, EVIL, ASSASSIN]:
            evils.append(player.name)
    embed = discord.Embed(title="당신의 역할은 모드레드입니다.", description="멀린은 당신이 악의 세력인지 모르고 시작합니다.")
    embed.add_field(name="당신의 눈에 보이는 악의 세력은...", value=f"{evils}입니다!")
    await mordred_player.send(embed=embed)

async def morgana(morgana_player):
    evils = []
    for player in roles:
        if roles[player] in [MORDRED, EVIL, ASSASSIN]:
            evils.append(player.name)
    embed = discord.Embed(title="당신의 역할은 모르가나입니다.", description="퍼시발에게 당신은 멀린 후보로 보입니다.")
    embed.add_field(name="당신의 눈에 보이는 악의 세력은...", value=f"{evils}입니다!")
    await morgana_player.send(embed=embed)

async def oberon(oberon_player):
    embed = discord.Embed(title="당신의 역할은 오베론입니다.", description="다른 악의 하수인들을 알 수 없고, 악의 하수인들도 당신의 정체를 모릅니다.")
    await oberon_player.send(embed=embed)

async def show_roles():
    for player in roles:
        role = roles[player]
        if role == MERLIN:
            await merlin(player)
        elif role == ASSASSIN:
            await assassin(player)
        elif role == PERCIVAL:
            await percival(player)
        elif role == MORDRED:
            await mordred(player)
        elif role == MORGANA:
            await morgana(player)
        elif role == OBERON:
            await oberon(player)
        elif role == LOYAL:
            await loyal(player)
        elif role == EVIL:
            await evil(player)

def assign_roles():
    players = len(game_room['members'])
    loyal = players // 2 + 1
    evil = players - loyal
    while len(game_room['roles']['loyal']) < loyal:
        game_room['roles']['loyal'].append(LOYAL)
    while len(game_room['roles']['evil']) < evil:
        game_room['roles']['evil'].append(EVIL)
    current_roles = game_room['roles']['loyal'] + game_room['roles']['evil']
    random.shuffle(current_roles)
    for i in range(len(current_roles)):
        roles[game_room['members'][i]] = current_roles[i]

async def ready_game():
    assign_roles()
    await show_roles()