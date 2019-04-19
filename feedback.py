
import boto3


dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
table = dynamodb.Table('Monster_DB')

def feedback(user_id, user_input, intent):

	return table.put_item(Item = {'Function': 'Feedback', 'Course': user_id, 'input': user_input, 'intent': intent})
