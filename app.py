
## the server connected with Facebook


### the library import
import random
import os
from flask import Flask,request
from pymessenger.bot import Bot
import boto3
from textblob import TextBlob

import IntentClassification as intent_classify
import keyword_extraction as keyword_extract
import retrieve_data as retrieve

import time
import ssl


facebook_verify = 'haha' #os.environ['facebook_verify'] #'we'   #the verify token
## may need change everytime
access_token = 'EAAD1PpqbNz0BAE1C2ZAkvzg2eotZA66Ad3rQZAFKyX2WfOxNZBUQhLtFpIOlNuUyJwRzHLt5euP07q3bZAb1wKjCO5S5xSpqzp7lxVnq9XfLdqZCAT7KTmXsZC6NTW2l9d7VZBuIXAuFsxEQZCayYtn3bIHWCpnO0vIFom6uCZC2v5hgZDZD' #os.environ['access_token']    #the access token
server = Bot(access_token)


# store the key info by user id
global store
store = {}   # store = {'id':{'input': '','re_intent':'','keyword':{}, 're_ask': Flase, 'time': float, 'response':''}}



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

button = [{'type':'postback', 'title': 'It helps me!','payload': 'Yes'}, {'type':'postback', 'title': 'It does no help!','payload': 'No'}]

continue_button = [{'type':'postback', 'title': 'I want continue.','payload': '1'}, {'type':'postback', 'title': 'I do not want continue.','payload': '0'}]

intent_bound = 0.4    ## least accuracy rate
#processing the message sent by user and return response searched by Chatbot
@app.route('/',methods = ['POST'])

def recieve_message():
    #global re_ask
    #global re_intent
    global store
    user_input = request.get_json()
    #get user ID to response back
    if user_input.get('entry'):#for event in user_input['entry']:
          event = user_input['entry'][0]
          if event.get('messaging'):#for message in messaging:
            message = event['messaging'][0]
            if message.get('message'):
                #Facebook Messenger ID for user so we know where to send response back to
                
                text = message['message'].get('text')
                user_ID = message['sender']['id']
                
                sent_time = time.time()   ## current time
                if user_ID not in store.keys():
                    store[user_ID] = {'input': '', 're_intent':'', 'keyword':{}, 're_ask': False, 'time': sent_time, 'intent_acc':0.0,'response':''}
                else:
                    break_time = sent_time - store[user_ID]['time']
                    if break_time > 120:  # longer than 2 mins
                        store[user_ID] = {'input': '', 're_intent':'','keyword':{}, 're_ask': False, 'time': sent_time, 'intent_acc':0.0,'response':''}
                    else:
                        store[user_ID]['time'] = sent_time
                
                if store[user_ID]['re_ask'] == False:
                    new_text = intent_classify.preprocessing(text)
                    #new_text = TextBlob(text).correct()
                    #new_text = str(new_text)
                    intent,intent_acc = intent_classify.intent_classification(new_text)    ####  need return a accuracy
                    store[user_ID]['intent_acc'] = intent_acc
                    
                    if intent == 'Greetings':
                        response = 'Hi, I am here to help you!'
                        if store[user_ID]['intent_acc'] <= intent_bound:
                            store[user_ID]['response'] = response
                            res = 'We think your input may lead to wrong response, do you want continue?'
                            server.send_button_message(user_ID, res, continue_button)
                            return "Message Processed"
                        else:
                            server.send_text_message(user_ID,response)
                            return "Message Processed"
                    elif intent == 'Goodbye':
                        response = 'See you soon!'
                        if store[user_ID]['intent_acc'] <= intent_bound:
                            store[user_ID]['response'] = response
                            res = 'We think your input may lead to wrong response, do you want continue?'
                            server.send_button_message(user_ID, res, continue_button)
                            return "Message Processed"
                        else:
                            server.send_text_message(user_ID,response)
                            return "Message Processed"
                    
                    store[user_ID]['input'] = text
                    
                else:
                    print(store[user_ID])
                    intent = store[user_ID]['re_intent']
                    text = store[user_ID]['input'] + ' ' + text
                    print('new reask text is '+ text)
                
                keyword = keyword_extract.keyword_extraction(intent,text)
                print('keyword is ' + str(keyword))
                
                response = retrieve.retrieval_func(keyword)
                print('data retrieve is '+response)
                
                if response == 'Please provide courses code.':
                    
                    if store[user_ID]['keyword']!={}:
                        print(store[user_ID])
                        if store[user_ID]['keyword']['course'] != []:
                            store[user_ID]['keyword']['intent'] = intent
                            #print(store[user_ID]['keyword'])
                            keyword['course'] = store[user_ID]['keyword']['course']
                            response = retrieve.retrieval_func(keyword)
                            if store[user_ID]['intent_acc'] <= intent_bound:
                                store[user_ID]['response'] = response
                                res = 'We think your input may lead to wrong response, do you want continue?'
                                server.send_button_message(user_ID, res, continue_button)
                            else:
                                res = intent + ' ' + response + ' ' + str(store[user_ID]['re_ask'])
                                if res > 999:
                                    server.send_text_message(user_ID,res)
                                else:
                                    server.send_button_message(user_ID,res,button)
                        else:
                            store[user_ID]['re_ask'] = True
                            store[user_ID]['re_intent'] = intent
                            store[user_ID]['keyword'] = keyword
                            if store[user_ID]['intent_acc'] <= intent_bound:
                                store[user_ID]['response'] = response
                                res = 'We think your input may lead to wrong response, do you want continue?'
                                server.send_button_message(user_ID, res, continue_button)
                            else:
                                res = intent + ' ' + response + ' ' + str(store[user_ID]['re_ask'])
                                server.send_text_message(user_ID,res)
                    else:
                        store[user_ID]['re_ask'] = True
                        store[user_ID]['re_intent'] = intent
                        store[user_ID]['keyword'] = keyword
                        if store[user_ID]['intent_acc'] <= intent_bound:
                            store[user_ID]['response'] = response
                            res = 'We think your input may lead to wrong response, do you want continue?'
                            server.send_button_message(user_ID, res, continue_button)
                        else:
                            res = intent + ' ' + response + ' ' + str(store[user_ID]['re_ask'])
                            server.send_text_message(user_ID,res)
                elif response == 'please provide stream name.':
                    
                    if store[user_ID]['keyword']!={}:
                        if store[user_ID]['keyword']['stream_name'] != []:
                            store[user_ID]['keyword']['intent'] = intent
                            keyword['stream_name'] = store[user_ID]['keyword']['stream_name']
                            response = retrieve.retrieval_func(keyword)
                            if store[user_ID]['intent_acc'] <= intent_bound:
                                store[user_ID]['response'] = response
                                res = 'We think your input may lead to wrong response, do you want continue?'
                                server.send_button_message(user_ID, res, continue_button)
                            else:
                                res = intent + ' ' + response + ' ' + str(store[user_ID]['re_ask'])
                                if res > 999:
                                    server.send_text_message(user_ID,res)
                                else:
                                    server.send_button_message(user_ID,res,button)
                        else:
                            store[user_ID]['re_ask'] = True
                            store[user_ID]['re_intent'] = intent
                            store[user_ID]['keyword'] = keyword
                            if store[user_ID]['intent_acc'] <= intent_bound:
                                store[user_ID]['response'] = response
                                res = 'We think your input may lead to wrong response, do you want continue?'
                                server.send_button_message(user_ID, res, continue_button)
                            else:
                                res = intent + ' ' + response + ' ' + str(store[user_ID]['re_ask'])
                                server.send_text_message(user_ID,res)
                    else:
                        store[user_ID]['re_ask'] = True
                        store[user_ID]['re_intent'] = intent
                        store[user_ID]['keyword'] = keyword
                        if store[user_ID]['intent_acc'] <= intent_bound:
                            store[user_ID]['response'] = response
                            res = 'We think your input may lead to wrong response, do you want continue?'
                            server.send_button_message(user_ID, res, continue_button)
                        else:
                            res = intent + ' ' + response + ' ' + str(store[user_ID]['re_ask'])
                            server.send_text_message(user_ID,res)
                else:
                    store[user_ID]['re_ask'] = False
                    store[user_ID]['keyword'] = keyword
                    store[user_ID]['re_intent'] = ''
                    if store[user_ID]['intent_acc'] <= intent_bound:
                        store[user_ID]['response'] = response
                        res = 'We think your input may lead to wrong response, do you want continue?'
                        server.send_button_message(user_ID, res, continue_button)
                    else:
                        res = intent + ' ' + response + ' ' + str(store[user_ID]['re_ask'])
                        ####send feed back
                        if len(res) > 999:
                            server.send_text_message(user_ID,res)
                        else:
                            server.send_button_message(user_ID,res,button)
                    
                
                
            elif message.get('postback'):
                user_ID = message['sender']['id']
                recipient_id = message["recipient"]["id"]
                    
                payload = message["postback"]["payload"]
                if payload == 'Yes':
                    res = 'Thank you for your use!'
                    server.send_text_message(user_ID,res)
                elif payload == 'No':
                    res = 'We will improve soon!'
                    server.send_text_message(user_ID,res)
                elif payload == '1':   ### want continue
                    res = store[user_ID]['response']
                    if store[user_ID]['re_ask'] == False:
                        server.send_button_message(user_ID,res,button)
                    else:
                        res = store[user_ID]['re_intent'] + ' ' + res + ' ' + str(store[user_ID]['re_ask'])
                        server.send_text_message(user_ID,res)
                elif payload == '0':
                    res = 'Please reinput with more details.'
                    sent_time = time.time()
                    store[user_ID] = {'input': '', 're_intent':'', 'keyword':{}, 're_ask': False, 'time': sent_time, 'response':''}
                    server.send_text_message(user_ID,res)
                    
                    
    return "Message Processed"
    


key_file = "/etc/letsencrypt/live/www.monsterko.ml/privkey.pem"
cert_file = "/etc/letsencrypt/live/www.monsterko.ml/fullchain.pem"
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(certfile = cert_file, keyfile = key_file)

if __name__ == '__main__':
    #print(test_get_dynamodb())
    app.run(ssl_context = context, host = '0.0.0.0', port = '55555',threaded = True,debug = True)



