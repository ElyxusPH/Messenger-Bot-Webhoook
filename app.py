#Simplified Python API for Facebook Messenger Bot Webhoook
try:
    from colorama import Fore, Style
    from flask import Flask, request
    from datetime import datetime
    from dotenv import load_dotenv
    load_dotenv()
    import logging
    import requests
    import os, sys
except ImportError:
    print('Requirements Missing, try running "pip install -r requirements.txt"') 

logging.basicConfig(
    level=logging.INFO,
    format='\r' + Fore.GREEN + '[%(asctime)s]: ' + Style.RESET_ALL + '%(message)s', datefmt="%H:%M:%S"
)

def log(message):
    try:
        logging.info(message)
    except:
        print(str(message))
    finally:
        sys.stdout.flush()
    

app = Flask(__name__)
verify_token: str = os.getenv('VERIFY_TOKEN')
access_token: str = os.getenv('ACCESS_TOKEN')

@app.route('/', methods=['GET'])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == verify_token:
            return "Invalid Token", 403
        return request.args["hub.challenge"], 200
    return "Verified", 200

@app.route('/', methods=['POST'])
def webhook():
    
    data = request.get_json()
    log(data) 
    
    if data["object"] == "page": 
        for entry in data["entry"]:
            for event in entry["messaging"]:

                if event.get("message"): 
                    sender_id = event["sender"]["id"] #facebook user id 
                    recipient_id = event["recipient"]["id"] #facebook page id
                    if "text" in event["message"]:
                        message_text = event["message"]["text"] #received message
                        #simple_command(sender_id, message_text)
                else:
                    log("Webhook received unknown event: " + event)

    return "ok", 200

def simple_command(sid, msg): #sample command function
    if str(msg)[:5] == "/time": # if user sends "/time", we'll send back the current time
        time = datetime.now().strftime("%H:%M:%S")
        data = {
            "recipient": {
                "id": sid
            },
            "message": {
                "text": time, #current time
            }
        }
        call_api(data)

def send_message(sid, msg):
    data = {
      "recipient": {
        "id": sid
      },
      "message": {
        "text": msg, #change with message u want to send back
      }
    }
    call_api(data)

def call_api(data):
    
    uri = 'https://graph.facebook.com/v2.6/me/messages'
    
    try:
        r = requests.post(uri, 
            params={"access_token": access_token }, 
            headers={'Content-Type': 'application/json'},
            data=data)
        code = r.status_code
        if code != 200:
            log(r.text)
            log(code)
            return False
        log(r.text)
        log('Message Sent')
    except Exception as e: 
        log(e)
        
if __name__ == '__main__':
    app.run()
