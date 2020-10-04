from slack import WebClient
from decouple import config

slack = WebClient(config('SLACK_BOT_TOKEN'))

res = slack.rtm_connect(with_team_state=False)

print(res)