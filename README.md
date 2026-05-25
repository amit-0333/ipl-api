# 🏏 IPL API

A REST API built with **Flask** that provides IPL cricket statistics — team records, head-to-head results, batting and bowling stats — powered by real IPL match data.

---

## 📁 Project Structure

```
ipl-api/
├── ipl.py       # All data loading and API logic
├── app.py       # Flask routes
└── README.md
```

---

## ⚙️ Installation

**Requirements:** Python 3.7+

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/ipl-api.git
   cd ipl-api
   ```

2. **Install dependencies**
   ```bash
   pip install flask pandas numpy
   ```

3. **Run the app**
   ```bash
   python app.py
   ```

4. **Open in browser**
   ```
   http://127.0.0.1:5000
   ```

---

## 📡 API Endpoints

### `GET /api/teams`
Returns a list of all IPL teams.

```
http://127.0.0.1:5000/api/teams
```

**Response:**
```json
{
  "teams": ["Mumbai Indians", "Chennai Super Kings", "Royal Challengers Bangalore", "..."]
}
```

---

### `GET /api/teamvteam`
Head-to-head record between two teams.

| Parameter | Type   | Required | Description      |
|-----------|--------|----------|------------------|
| `team1`   | string | Yes      | First team name  |
| `team2`   | string | Yes      | Second team name |

```
http://127.0.0.1:5000/api/teamvteam?team1=Mumbai Indians&team2=Chennai Super Kings
```

**Response:**
```json
{
  "total_matches": "34",
  "Mumbai Indians": "20",
  "Chennai Super Kings": "14",
  "draws": "0"
}
```

---

### `GET /api/team-record`
Overall record of a team including wins, losses, and titles.

| Parameter | Type   | Required | Description |
|-----------|--------|----------|-------------|
| `team`    | string | Yes      | Team name   |

```
http://127.0.0.1:5000/api/team-record?team=Mumbai Indians
```

**Response:**
```json
{
  "Mumbai Indians": {
    "overall": {
      "matchesplayed": 234,
      "won": 134,
      "loss": 95,
      "noResult": 5,
      "title": 5
    },
    "against": { "...": "..." }
  }
}
```

---

### `GET /api/batting-record`
Batting statistics for a player.

| Parameter | Type   | Required | Description  |
|-----------|--------|----------|--------------|
| `batsman` | string | Yes      | Player name  |

```
http://127.0.0.1:5000/api/batting-record?batsman=V Kohli
```

**Response:**
```json
{
  "V Kohli": {
    "all": {
      "innings": 237,
      "runs": 7263,
      "fours": 644,
      "sixes": 253,
      "avg": 37.03,
      "strikeRate": 131.6,
      "fifties": 50,
      "hundreds": 8,
      "highestScore": "113",
      "notOut": 41,
      "mom": 23
    },
    "against": { "...": "..." }
  }
}
```

---

### `GET /api/bowling-record`
Bowling statistics for a player.

| Parameter | Type   | Required | Description |
|-----------|--------|----------|-------------|
| `bowler`  | string | Yes      | Player name |

```
http://127.0.0.1:5000/api/bowling-record?bowler=JJ Bumrah
```

**Response:**
```json
{
  "JJ Bumrah": {
    "all": {
      "innings": 120,
      "wicket": 145,
      "economy": 7.41,
      "average": 23.1,
      "strikeRate": 18.7,
      "best_figure": "5/10",
      "3+W": 12,
      "mom": 10
    },
    "against": { "...": "..." }
  }
}
```

---

## 📊 Data Source

Live IPL data is fetched from Google Sheets (publicly published CSV):

- **Matches data** — match-level results, teams, winners
- **Ball-by-ball data** — every delivery with runs, wickets, extras

---

## 🛠️ Tech Stack

| Layer     | Technology          |
|-----------|---------------------|
| Backend   | Python, Flask       |
| Data      | Pandas, NumPy       |
| Data Source | Google Sheets (CSV) |

---

## 📝 Notes

- Player names must match the dataset exactly (e.g. `V Kohli` not `Virat Kohli`)
- Use `/api/teams` first to get the correct team name spellings
- Super overs are excluded from all batting and bowling records

---

## 📄 License

MIT License — free to use and modify.
