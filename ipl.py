import pandas as pd
import numpy as np
import json

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

ipl_matches = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRy2DUdUbaKx_Co9F0FSnIlyS-8kp4aKv_I0-qzNeghiZHAI_hw94gKG22XTxNJHMFnFVKsO4xWOdIs/pub?gid=1655759976&single=true&output=csv"
matches = pd.read_csv(ipl_matches)

ipl_ball = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRu6cb6Pj8C9elJc5ubswjVTObommsITlNsFy5X0EiBY7S-lsHEUqx3g_M16r50Ytjc0XQCdGDyzE_Y/pub?output=csv"
balls = pd.read_csv(ipl_ball)

ball_withmatch = balls.merge(matches, on='ID', how='inner').copy()
ball_withmatch['BowlingTeam'] = ball_withmatch.Team1 + ball_withmatch.Team2
ball_withmatch['BowlingTeam'] = ball_withmatch[['BowlingTeam', 'BattingTeam']].apply(
    lambda x: x.values[0].replace(x.values[1], ''), axis=1
)
batter_data = ball_withmatch[np.append(balls.columns.values, ['BowlingTeam', 'Player_of_Match'])]

bowler_data = batter_data.copy()
bowler_data['bowler_run'] = np.where(
    bowler_data['extra_type'].isin(['penalty', 'legbyes', 'byes']),
    0,
    bowler_data['total_run']
)
bowler_data['isBowlerWicket'] = np.where(
    bowler_data['kind'].isin(['caught', 'caught and bowled', 'bowled', 'stumped', 'lbw', 'hit wicket']),
    bowler_data['isWicketDelivery'],
    0
)


# ─── Teams ────────────────────────────────────────────────────────────────────

def teamsAPI():
    teams = list(set(list(matches['Team1']) + list(matches['Team2'])))
    return json.dumps({'teams': teams}, cls=NpEncoder)


# ─── Team vs Team ─────────────────────────────────────────────────────────────

def teamVteamAPI(team1, team2):
    valid_teams = list(set(list(matches['Team1']) + list(matches['Team2'])))

    if team1 not in valid_teams or team2 not in valid_teams:
        return json.dumps({'message': 'invalid team name'})

    temp_df = matches[
        ((matches['Team1'] == team1) & (matches['Team2'] == team2)) |
        ((matches['Team1'] == team2) & (matches['Team2'] == team1))
    ]
    total_matches = temp_df.shape[0]
    matches_won_team1 = temp_df['WinningTeam'].value_counts().get(team1, 0)
    matches_won_team2 = temp_df['WinningTeam'].value_counts().get(team2, 0)
    draws = total_matches - (matches_won_team1 + matches_won_team2)

    return json.dumps({
        'total_matches': total_matches,
        team1: matches_won_team1,
        team2: matches_won_team2,
        'draws': draws
    }, cls=NpEncoder)


# ─── Team Record ──────────────────────────────────────────────────────────────

def team1vsteam2(team, team2):
    df = matches[
        ((matches['Team1'] == team) & (matches['Team2'] == team2)) |
        ((matches['Team2'] == team) & (matches['Team1'] == team2))
    ].copy()
    mp = df.shape[0]
    won = df[df.WinningTeam == team].shape[0]
    nr = df[df.WinningTeam.isnull()].shape[0]
    loss = mp - won - nr
    return {'matchesplayed': mp, 'won': won, 'loss': loss, 'noResult': nr}


def allRecord(team):
    df = matches[(matches['Team1'] == team) | (matches['Team2'] == team)].copy()
    mp = df.shape[0]
    won = df[df.WinningTeam == team].shape[0]
    nr = df[df.WinningTeam.isnull()].shape[0]
    loss = mp - won - nr
    nt = df[(df.MatchNumber == 'Final') & (df.WinningTeam == team)].shape[0]
    return {'matchesplayed': mp, 'won': won, 'loss': loss, 'noResult': nr, 'title': nt}


def teamAPI(team):
    self_record = allRecord(team)
    TEAMS = matches.Team1.unique()
    against = {team2: team1vsteam2(team, team2) for team2 in TEAMS}
    return json.dumps({team: {'overall': self_record, 'against': against}}, cls=NpEncoder)


# ─── Batsman ──────────────────────────────────────────────────────────────────

def batsmanRecord(batsman, df):
    if df.empty:
        return np.nan
    out = df[df.player_out == batsman].shape[0]
    df = df[df['batter'] == batsman]
    inngs = df.ID.unique().shape[0]
    runs = df.batsman_run.sum()
    fours = df[(df.batsman_run == 4) & (df.non_boundary == 0)].shape[0]
    sixes = df[(df.batsman_run == 6) & (df.non_boundary == 0)].shape[0]
    avg = runs / out if out else np.inf
    nballs = df[~(df.extra_type == 'wides')].shape[0]
    strike_rate = runs / nballs * 100 if nballs else 0
    gb = df.groupby('ID').sum()
    fifties = gb[(gb.batsman_run >= 50) & (gb.batsman_run < 100)].shape[0]
    hundreds = gb[gb.batsman_run >= 100].shape[0]
    try:
        highest_score = gb.batsman_run.sort_values(ascending=False).head(1).values[0]
        hsindex = gb.batsman_run.sort_values(ascending=False).head(1).index[0]
        highest_score = str(highest_score) if (df[df.ID == hsindex].player_out == batsman).any() else str(highest_score) + '*'
    except:
        highest_score = gb.batsman_run.max()
    not_out = inngs - out
    mom = df[df.Player_of_Match == batsman].drop_duplicates('ID', keep='first').shape[0]
    return {
        'innings': inngs, 'runs': runs, 'fours': fours, 'sixes': sixes,
        'avg': avg, 'strikeRate': strike_rate, 'fifties': fifties,
        'hundreds': hundreds, 'highestScore': highest_score,
        'notOut': not_out, 'mom': mom
    }


def batsmanVsTeam(batsman, team, df):
    return batsmanRecord(batsman, df[df.BowlingTeam == team].copy())


def batsmanAPI(batsman, balls=batter_data):
    df = balls[balls.innings.isin([1, 2])]
    self_record = batsmanRecord(batsman, df=df)
    TEAMS = matches.Team1.unique()
    against = {team: batsmanVsTeam(batsman, team, df) for team in TEAMS}
    return json.dumps({batsman: {'all': self_record, 'against': against}}, cls=NpEncoder)


# ─── Bowler ───────────────────────────────────────────────────────────────────

def bowlerRecord(bowler, df):
    df = df[df['bowler'] == bowler]
    inngs = df.ID.unique().shape[0]
    nballs = df[~(df.extra_type.isin(['wides', 'noballs']))].shape[0]
    runs = df['bowler_run'].sum()
    eco = runs / nballs * 6 if nballs else 0
    fours = df[(df.batsman_run == 4) & (df.non_boundary == 0)].shape[0]
    sixes = df[(df.batsman_run == 6) & (df.non_boundary == 0)].shape[0]
    wicket = df.isBowlerWicket.sum()
    avg = runs / wicket if wicket else np.inf
    strike_rate = nballs / wicket * 100 if wicket else np.nan
    gb = df.groupby('ID').sum()
    w3 = gb[(gb.isBowlerWicket >= 3)].shape[0]
    best_wicket = gb.sort_values(['isBowlerWicket', 'bowler_run'], ascending=[False, True])[
        ['isBowlerWicket', 'bowler_run']].head(1).values
    best_figure = f'{best_wicket[0][0]}/{best_wicket[0][1]}' if best_wicket.size > 0 else np.nan
    mom = df[df.Player_of_Match == bowler].drop_duplicates('ID', keep='first').shape[0]
    return {
        'innings': inngs, 'wicket': wicket, 'economy': eco, 'average': avg,
        'avg': avg, 'strikeRate': strike_rate, 'fours': fours, 'sixes': sixes,
        'best_figure': best_figure, '3+W': w3, 'mom': mom
    }


def bowlerVsTeam(bowler, team, df):
    return bowlerRecord(bowler, df[df.BattingTeam == team].copy())


def bowlerAPI(bowler, balls=bowler_data):
    df = balls[balls.innings.isin([1, 2])]
    self_record = bowlerRecord(bowler, df=df)
    TEAMS = matches.Team1.unique()
    against = {team: bowlerVsTeam(bowler, team, df) for team in TEAMS}
    return json.dumps({bowler: {'all': self_record, 'against': against}}, cls=NpEncoder)