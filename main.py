from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
import requests
from datetime import datetime
import spacy

app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

BASE_URL = "https://api-web.nhle.com/v1/"

nlp = spacy.load("en_core_web_sm")

VALID_TEAMS = [
   "ANA", "ARI", "BOS", "BUF", "CAR", "CBJ", "CGY", "CHI", "COL", "DAL", "DET", "EDM",
    "FLA", "LAK", "MIN", "MTL", "NJD", "NSH", "NYI", "NYR", "OTT", "PHI", "PIT", "SJS",
    "STL", "TBL", "TOR", "VAN", "VGK", "WPG", "WSH"
]

TEAM_NAME_MAPPING = {
    "ANA": "Anaheim Ducks",
    "ARI": "Arizona Coyotes",
    "BOS": "Boston Bruins",
    "BUF": "Buffalo Sabres",
    "CAR": "Carolina Hurricanes",
    "CBJ": "Columbus Blue Jackets",
    "CGY": "Calgary Flames",
    "CHI": "Chicago Blackhawks",
    "COL": "Colorado Avalanche",
    "DAL": "Dallas Stars",
    "DET": "Detroit Red Wings",
    "EDM": "Edmonton Oilers",
    "FLA": "Florida Panthers",
    "LAK": "Los Angeles Kings",
    "MIN": "Minnesota Wild",
    "MTL": "Montreal Canadiens",
    "NJD": "New Jersey Devils",
    "NSH": "Nashville Predators",
    "NYI": "New York Islanders",
    "NYR": "New York Rangers",
    "OTT": "Ottawa Senators",
    "PHI": "Philadelphia Flyers",
    "PIT": "Pittsburgh Penguins",
    "SJS": "San Jose Sharks",
    "STL": "St. Louis Blues",
    "TBL": "Tampa Bay Lightning",
    "TOR": "Toronto Maple Leafs",
    "VAN": "Vancouver Canucks",
    "VGK": "Vegas Golden Knights",
    "WPG": "Winnipeg Jets",
    "WSH": "Washington Capitals",
}
 
@app.route('/team-stats', methods=['POST'])
@limiter.limit("10 per minute")
def get_team_stats():
  data = request.get_json()
  user_query = data['query']

  team_name = extract_team_name(user_query)

  if not is_valid_team(team_name):
    return jsonify({'error': 'Invalid team name'}), 400

  latest_season = get_latest_season()
  
  url = f"{BASE_URL}club-stats-season/{team_name}?season={latest_season}"


  cached_data = cache.get(url)
  if cached_data: 
    return jsonify(cached_data)

  response = requests.get(url)
  if response.status_code != 200:
    return jsonify({'error': 'Failed to retrieve team statistics'}), 500
  
  team_stats = response.json()

  cache.set(url, team_stats, timeout=3600)

  return jsonify(team_stats)

def extract_team_name(user_query):
  doc = nlp(user_query)
  for token in doc: 
    if token.text.upper() in VALID_TEAMS:
      return TEAM_NAME_MAPPING.get(token.text.upper(), token.text.upper())
  return None

def is_valid_team(team_name):
  return team_name in VALID_TEAMS

def get_latest_season():  
  current_date = datetime.now()
  
  if current_date.month < 10:
    latest_season = current_date.year - 1
  else:
    latest_season = current_date.year
  
  return latest_season

if __name__ == "__main__":
    app.run(debug=True, port=8080)
