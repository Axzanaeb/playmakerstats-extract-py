class Match:
    def __init__(self, team_a, team_b, result, match_date):
        self.team_a = team_a
        self.team_b = team_b
        self.result = result
        self.match_date = match_date

    def __str__(self):
        return f"{self.team_a} {self.result} {self.team_b}"

    def to_json(self):
        return {
            'team_a': self.team_a,
            'team_b': self.team_b,
            'result': self.result,
            'match_date': self.match_date,
        }
