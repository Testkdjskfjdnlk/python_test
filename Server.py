
## the server connected with Facebook


### the library import
import random
from flask import Flask,request
from pymessenger.bot import Bot


facebook_verify = 'we'   #the verify token
## may need change everytime
access_token = 'EAADkSAAGGFcBANBEhgqBQ1nV1obaMJ5iGquSbZA6kHQh28vJjrkiKhgwjwQ67DlqQ4hTiZBSfNpiuBRsYJmYTZCrxZBkt9NU8vZCZCtVMZAhigS3UsSIfgmqTB7Vu0DhNqCEQOcqApZBHWbrcvjqCwCXZAJAEeDN5DK12kEvfUeTk7QZDZD'    #the access token
server = Bot(access_token)



app = Flask(__name__)
#api = Api(app,default = "COMP9900",title ="X_Bot")


#check the facebook verification token if matches the token by developer sent
@app.route('/',methods = ['GET'])

def verify_facebook():
    verify_token = request.args.get("hub.verify_token")
    if verify_token == facebook_verify:
        #request.args.get("hub.challenge")
        return request.args.get("hub.challenge")
    return 'Can not match Facebook verification!'


#processing the message sent by user and return response searched by Chatbot
@app.route('/',methods = ['POST'])

def recieve_message():
    user_input = request.get_json()
    #get user ID to response back
    for event in user_input['entry']:
          messaging = event['messaging']
          for message in messaging:
            if message.get('message'):
                #Facebook Messenger ID for user so we know where to send response back to
                user_ID = message['sender']['id']
                reponse = get_message()
                reply_user(user_ID,reponse)
    return "Message Processed"
    
    '''
    #check content sent by user
    if data.get('text'):    # if user sent text
        text = data.get('text')
        chatbot_process(text)  ###########################   modify need
    else:  #is user sent nontext
        message = 'Please send text'
        reply_user(user_ID,message)
    '''

#chooses a random message to send to the user
def get_message():
    sample_responses = ["Hello!", "Select course.", "Monster_K_O!", "See you"]
    # return selected item to the user
    return random.choice(sample_responses)



#### send back message back to user
def reply_user(user_ID,message):
    '''
    response = {
        'recipient': {'id': user_ID},
        'message': {'text': message}
        }
    send = request.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + access_token, json = response)
    '''
    server.send_text_message(user_ID,message)
    return 'ok'


if __name__ == '__main__':
    app.run(debug=True)


### chatbot process text
#def chatbot(text):      ####need add
#    pass

