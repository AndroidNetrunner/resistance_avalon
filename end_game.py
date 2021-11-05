import asyncio
from utils import is_bot
import discord
import random
from roles import ASSASSIN, EVIL, MERLIN, MORDRED, MORGANA
from active_games import active_games

async def end_game(current_game):
    game_status = current_game['game_status']
    if game_status.round_success == 3:
        await start_assassination(current_game)
    else:
        embed=discord.Embed(title="게임 결과, 악의 하수인이 승리하였습니다!", description="3번의 미션 실패로 인한 악의 하수인 승리")
        await reveal_role(current_game, embed)
		
async def reveal_role(current_game, embed):
    roles = current_game['game_status'].roles
    str_roles = ""
    for player in roles:
        str_roles += f"{player.name} : {roles[player]}\n"
    embed.add_field(name="각 플레이어의 역할은 다음과 같습니다.", value=str_roles)
    await current_game['game_room'].main_channel.send(embed=embed)
    del active_games[current_game['game_room'].main_channel.channel.id]
    print(f"game_end {current_game['game_room'].main_channel.channel.id}")
 
async def start_assassination(current_game):
    game_status = current_game['game_status']
    game_room = current_game['game_room']
    game_status.assassination = True
    invalid_targets, assassin = get_invalid_targets(game_status)
    message = await send_embed_for_assassination(game_room, assassin, invalid_targets) 
    await add_reaction_for_assassination_message(game_room, message, invalid_targets)

def get_invalid_targets(game_status):
    invalid_targets = []
    roles = game_status.roles
    for player in roles:
        if roles[player] == ASSASSIN:
            assassin = player
            invalid_targets.append(player)
        elif roles[player] in [MORDRED, MORGANA, EVIL]:
            invalid_targets.append(player)
    return (invalid_targets, assassin)

async def add_reaction_for_assassination_message(game_room, message, invalid_targets):
    for emoji in game_room.emojis:
        if game_room.emojis[emoji] and game_room.emojis[emoji] not in invalid_targets:
            await message.add_reaction(emoji)

async def send_embed_for_assassination(game_room, assassin, invalid_targets):
    embed = discord.Embed(title="미션이 3번 성공되었습니다.", description="이제 암살자에게는 멀린을 암살할 기회가 주어집니다.")
    embed.add_field(name=f"암살자는 {assassin.name}입니다.", value="암살자는 DM으로 한 명을 지목해 암살해주세요.")
    await game_room.main_channel.send(embed=embed)
    embed = discord.Embed(title="이제 멀린을 암살할 차례입니다.", description="이모티콘을 통해 멀린이라고 생각되는 한 명을 지목해주세요.")
    player_emojis = ""
    for emoji in game_room.emojis:
        player_emojis += f"{emoji} : {game_room.emojis[emoji]}\n" if game_room.emojis[emoji] and game_room.emojis[emoji] not in invalid_targets else ""
    embed.add_field(name="각 이모티콘이 의미하는 플레이어는 다음과 같습니다.", value=player_emojis)
    return await assassin.send(embed=embed) 

async def judge_merlin(payload, current_game):
    if is_bot(payload.user_id, current_game['game_room']):
        return
    nominated = current_game['game_room'].emojis[str(payload.emoji)]
    await successful_assassination(current_game) if current_game['game_status'].roles[nominated] == MERLIN else await unsuccessful_assassination(current_game)

async def successful_assassination(current_game):
	embed = discord.Embed(title="게임 결과, 악의 하수인이 승리하였습니다!", description="멀린 암살 성공으로 인한 악의 하수인 승리")
	await reveal_role(current_game, embed)
	
async def unsuccessful_assassination(current_game):
	embed = discord.Embed(title="게임 결과, 선의 세력이 승리하였습니다!", description="3번의 미션 성공 및 멀린 암살 실패로 인한 선의 세력 승리")
	await reveal_role(current_game, embed)