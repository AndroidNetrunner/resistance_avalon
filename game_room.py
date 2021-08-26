from roles import *

class Game_room:
    def __init__(self) -> None:
        self.members = []
        self.roles = {
        'loyal': [MERLIN],
        'evil' : [ASSASSIN],
        }
        self.main_channel = None
        self.start = False
        self.can_join = False
        self.emojis = {
        "0\u20E3" : None,
        "1\u20E3" : None,
        "2\u20E3" : None,
        "3\u20E3" : None,
        "4\u20E3" : None,
        "5\u20E3" : None,
        "6\u20E3" : None,
        "7\u20E3" : None,
        "8\u20E3" : None,
        "9\u20E3" : None
        }

# game_room = {
#     'members': [],
#     'roles': {
#         'loyal': [MERLIN],
#         'evil' : [ASSASSIN],
#     },
#     'main_channel': None,
#     'start': False,
#     'can_join': False,
#     'emojis': {
#         "0\u20E3" : None,
#         "1\u20E3" : None,
#         "2\u20E3" : None,
#         "3\u20E3" : None,
#         "4\u20E3" : None,
#         "5\u20E3" : None,
#         "6\u20E3" : None,
#         "7\u20E3" : None,
#         "8\u20E3" : None,
#         "9\u20E3" : None
#     }
# }