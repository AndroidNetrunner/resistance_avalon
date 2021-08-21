from game_room import game_room

def is_bot(author_id):
	for member in game_room['members']:
		if member.id == author_id:
			return False
	return True

async def add_role_in_active_roles(role, active_roles):
    if role not in active_roles:
        active_roles.append(role)
        await game_room['main_channel'].send(f"{role} 역할이 추가되었습니다.")
    else:
        await game_room['main_channel'].send(f"{role}은 이미 추가된 역할입니다.")

async def remove_role_from_active_roles(role, active_roles):
    if role in active_roles:
        active_roles.remove(role)
        await game_room['main_channel'].send(f"{role} 역할이 삭제되었습니다.")
    else:
        await game_room['main_channel'].send(f"{role}은 추가되지 않은 역할입니다.")