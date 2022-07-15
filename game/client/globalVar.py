class globalVariable:
    def __init__(self) -> None:
        self.Crouch = False
        self.Running = False
        self.Reload = False
        self.Aiming = False
        self.Shooting = False
        self.Build = False


def initialize():
    global connection  # netwoek connect
    connection = None
