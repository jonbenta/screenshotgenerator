class Screenshot:
    focused_score: float
    path: str
    portrait_score: float

    def __init__(self, path: str, focused_score: float, portrait_score: float):
        self.focused_score = focused_score
        self.path = path
        self.portrait_score = portrait_score
