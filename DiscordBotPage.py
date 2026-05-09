import flask

flask_app = flask.Flask(__name__)
flask_app.run(port=os.getenv("PORT", 10000))

@flask_app.route("/status")
def status():
  if hasattr(bot, "ap_client") and bot.ap_client.game:
    return f"Connected to {bot.ap_client.game}"
  else:
    return "Not connected to any game"

@flask_app.route("/")
def index():
  return '<div class="tenor-gif-embed" data-postid="20072034" data-share-method="host" data-aspect-ratio="0.915625" data-width="100%"><a href="https://tenor.com/view/epic-win-fuuka-persona-persona3-fuuka-persona-gif-20072034">Epic Win Fuuka GIF</a>from <a href="https://tenor.com/search/epic+win-gifs">Epic Win GIFs</a></div> <script type="text/javascript" async src="https://tenor.com/embed.js"></script>'