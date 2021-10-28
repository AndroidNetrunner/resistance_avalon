from active_games import active_games

def is_bot(author_id, game_room):
	for member in game_room.members:
		if member.id == author_id:
			return False
	return True

async def is_open(ctx):
    if ctx.channel.id not in active_games:
        await ctx.send("시작한 게임이 존재하지 않습니다.")
        return
    room_info = active_games[ctx.channel.id]['game_room']
    if not room_info.can_join:
        await ctx.send("참가가 이미 마감되었습니다.")
        return
    if len(room_info.members) >= 10:
        await ctx.send("제한 인원(10명)을 초과하였습니다.")
        return
    return room_info

async def add_role_in_active_roles(role, active_roles, game_room):
    if role not in active_roles:
        active_roles.append(role)
        await game_room.main_channel.send(f"{role} 역할이 추가되었습니다.")
    else:
        await game_room.main_channel.send(f"{role}는(은) 이미 추가된 역할입니다.")

async def remove_role_from_active_roles(role, active_roles, game_room):
    if role in active_roles:
        active_roles.remove(role)
        await game_room.main_channel.send(f"{role} 역할이 삭제되었습니다.")
    else:
        await game_room.main_channel.send(f"{role}는(은) 추가되지 않은 역할입니다.")

def get_current_game(user_id):
    for channel_id in active_games:
        for member in active_games[channel_id]['game_room'].members:
            if user_id == member.id:
                return active_games[channel_id]
    return None