class Game_status:
    def __init__(self) -> None:
        self.round = 0
        self.round_success = 0
        self.round_fail = 0
        self.leader = None
        self.assassination = False
        self.roles = {}
        self.round_info = {}
        self.mission_result = {
            "success": 0,
            "fail": 0
            }
        self.mission_message = {}
