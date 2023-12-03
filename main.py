from flask import Flask, request, jsonify
from flsak_limiter import Limiter
from flask_caching import Cache
import requests

app = Flask(__name__)
limiter = Limiter(
  get_remote_address,
  app=app,
  default_limits["200 per day", "50 per hour"],
  storage_uri="memory://"
)

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

BASE_URL = "https://api-web.nhle.com/v1/"

nlp = spacy.load("en_core_web_sm")

VALID_TEAMS = [
   "ANA", "ARI", "BOS", "BUF", "CAR", "CBJ", "CGY", "CHI", "COL", "DAL", "DET", "EDM",
    "FLA", "LAK", "MIN", "MTL", "NJD", "NSH", "NYI", "NYR", "OTT", "PHI", "PIT", "SJS",
    "STL", "TBL", "TOR", "VAN", "VGK", "WPG", "WSH"
]

def extract_game_id(user_input):
  tokens = user_input.split()
  for token in tokens:
    if token.isdigit() and len(token) == 10:
      return token
  return None


def get_game_score(game_id):
  url = f"{BASE_URL}/score/{game_id}"

  response = requests.get(url)
  if response.status_code == 200:
    game_data = response.json()
    score = game_data.get("score")
    status = game_data.get("gameState")
    return score, status
  else:
    return None, None

@app.route("/get_score", methods=["POST"])
def get_score():
    user_input = request.json.get("query")
    game_id = extract_game_id(user_input)

    if game_id:
        score, status = game_data.get(game_id), None
        if score is None:
            score, status = get_game_score(game_id)
        if score:
            return jsonify({"score": score, "status": status})

    return jsonify({"error": "Unable to retrieve the score."})

if __name__ == "__main__":
    app.run(debug=True, port=8080)
