import os
import time
import re
from slackclient import SlackClient

# BOT OAuth Token
slack_client = SlackClient('xoxb-329959312851-ADCpKwqog4Uq5adzt0LvVsmQ')
starterbot_id = None

# constants
READ_WEBSOCKET_DELAY = 1 # 1 second between reading from the RTM
BOT_ID = "U9PU796R1"
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If it is not found, then this function returns None, None.
    """

    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then I can do that!"

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )

def queue_request_msg(command, channel, user):
    default_response = "Estou aprendendo ainda. Espere um pouco."

    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=default_response
    )

def listen():
    while True:
        try:
            command, channel, user = parse_slack_output(slack_client.rtm_read())
            if command and channel and user:
                queue_request_msg(command, channel, user)
            time.sleep(READ_WEBSOCKET_DELAY)
        except Exception as e:
            print("Erro ao ler mensagens. %s" % str(e))


def parse_slack_output(slack_rtm_output):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        #print(output_list)
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text'] and 'user' in output:
                msg = output['text'].replace(AT_BOT, "").strip().lower()
                print("Inc msg: %s"%(msg))
                return msg, output['channel'], output['user']
    return None, None, None

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method 'auth.test'
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        # Inicializa o Web Socket e fica escutando indefinidamente...
        listen()

    else:
        print("Connection failed. Exception traceback printed above.")
