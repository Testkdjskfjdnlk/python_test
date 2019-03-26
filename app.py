
## the server connected with Facebook


### the library import
import random
import os
from flask import Flask,request
from pymessenger.bot import Bot
import boto3

import IntentClassification as intent_classify
import keyword_extraction as keyword_extract

'''
client = boto3(
    'dynamodb',
    aws_access_key_id = os.environ['aws-accesss-id'],
    aws_secret_access_key = os.environ['aws-access-key'])
'''

#greeting = ['hello','hi','how are you','nice to meet you']

#goodbye = ['bye','goodbye','see you','thank you']



facebook_verify = os.environ['facebook_verify'] #'we'   #the verify token
## may need change everytime
access_token = os.environ['access_token'] #'EAADkSAAGGFcBANBEhgqBQ1nV1obaMJ5iGquSbZA6kHQh28vJjrkiKhgwjwQ67DlqQ4hTiZBSfNpiuBRsYJmYTZCrxZBkt9NU8vZCZCtVMZAhigS3UsSIfgmqTB7Vu0DhNqCEQOcqApZBHWbrcvjqCwCXZAJAEeDN5DK12kEvfUeTk7QZDZD'    #the access token
server = Bot(access_token)

re_ask = False
re_intent = ''

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
                text = message['message'].get('text')
                user_ID = message['sender']['id']
                
                if re_ask == False:
                    intent = intent_classify.intent_classification(text)
                    if intent == 'Greeting':
                        reponse = 'Hi, I am here to help you!'
                        reply_user(user_ID,response)
                        return "Message Processed"
                    elif intent == 'Goodbye':
                        reponse = 'See you soon!'
                        reply_user(user_ID,response)
                        return "Message Processed"
                 else：
                    intent = re_intent
                 keyword = keyword_extract.keyword_extraction(intent,text)
                 '''
                 response = 
                 if response == 'More infor about courses':
                     re_ask = True
                     re_intent = intent
                 '''
                
                response = 'intent is '+ intent +', keyword is ' + str(keyword)
                
                reply_user(user_ID,response)
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

# test dynamodb
def test_get_dynamodb():
# Connect to aws Dynamobd, get required data
    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
    table = dynamodb.Table('Monster_DB')

    response = table.get_item(Key={'Function': 'Basic_courses_information', 'Course': 'COMP9900'}, AttributesToGet=['handbook_link'])
    print(response)
    link = response['Item']['handbook_link']
    return link

if __name__ == '__main__':
    #print(test_get_dynamodb())
    app.run(debug=True)



