import boto3
import pandas as pd

stream = []
course = []
#other = []

### create Dataframe from AWS

dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
table = dynamodb.Table('Monster_DB')

response = table.scan()#get_item(Key={'Function': 'Specialisations'})#, AttributesToGet= ['Course','stream courses list'])
for item in response['Items']:
    if item['Function'] == 'Specialisations':
        stream.append(item)
    elif item['Function'] == 'Courses':
        course.append(item)

stream_info = pd.DataFrame(stream)
stream_info.set_index(["Course"], inplace=True)

course_info = pd.DataFrame(course)
course_info.set_index(["Course"], inplace=True)

#### graduate requirements
def graduate_req(epic1_return):
    ADK_nb = 0
    total_units = 0
    nb_projects = 0

    code_list = epic1_return['course']
    
    if code_list == []:
        return 'Please provide courses code.'
    
    courses = course_info.loc[code_list].T.to_dict()
    #print(courses)
    for course in courses:
        #print(course)
        if courses[course]['is ADK'] == 'Yes':
            ADK_nb += 1                             ######need more data to retrieve 
    if ADK_nb < 6:
        return f'No, you need more {6-ADK_nb} ADK courses to meet the graduation requirement.'
    
    '''
    for course_code in code_list:
        course_info = COURSE_INFO[course_code]
        if course_info['ADK'] == 'yes':
            ADK_nb += course_info['Units']
        if course_info['Project'] == 'yes':
            nb_projects += 1
        total_units += course_info['Units']
    

    # Remindful reply
    if total_units < 96:
        return f'No, you need to get {96 - total_units} more units to meet the graduate requirement.'
    if ADK_nb < 24 :
        return f'No, you need to get {24- ADK_nb} more units from ADK courses to meet the graduation requirement.'
    if nb_projects < 1:
        return 'No, you must enroll at least 1 project.'
    '''

    return 'Yes, congradulations!'
    
  
#### find basic course information
def basic_courses_info(epic1_return):
    info = ''
    handbook = epic1_return['handbook']
    timetable = epic1_return['time']
    outline = epic1_return['outline']
    #staff = epic1_return['staff']     #### need add 
    code_list = epic1_return['course']
    
    if code_list == []:
        return 'Please provide courses code.'
    
    courses = course_info.loc[code_list].T.to_dict()
    for course in courses:
        info += course + ' '
        if handbook != []:
            info += 'handbook link is ' + courses[course]['handbook link']+','
        if timetable != []:
            info += 'timetable link is ' + courses[course]['timetable link'] + '\n'
        #if handbook == [] and timetable == []:
        #    info += 'outline link is' + courses[course]['outline link'] + 'n'
    
    '''
    # ####################################################
    # # de-dupilcation
    # course_list = epic1_return['course_name']
    # code_list = epic1_return['code']
    # temp_code = code_replace(course_list)
    # for c in temp_code:
    #     if c not in code_list:
    #         code_list.append(c)
    # ####################################################
    for c in code_list:
        course_info = COURSE_INFO[c]

        if handbook != []:
            info += course_info['Handbook_link'] + '\n'
        elif timetable != []:
            info += course_info['timetable'] + '\n'
        elif staff != [] :
            for ppl in staff:
                info += f'{ppl} is:' + course_info[ppl] + '.' +'\n'
        else:
            info += f"{c}'s outline links is " + course_info['Outlinelink']
    '''
    return info
    
### stream rec
def stream_courses_rec(epic1_return):
    stream_name = epic1_return['stream_name']
    if stream_name == []:
        return 'please provide stream name.'
    info = ''
    
    streams = stream_info.loc[stream_name].T.to_dict()
    code_list = epic1_return['course']
    if code_list == []:
        for stream in streams:
            courses_list = streams[stream]['stream courses list']
            info += stream + ' has these courses that you can choose ' + ' '.join(courses_list) + '\n'
    else:
        for stream in streams:
            courses_list = list(set(streams[stream]['stream courses list'])-set(code_list))
            info += stream + ' has these courses that you can choose ' + ' '.join(courses_list) + '\n'
    
    return info
    '''
    # epic1_return['stream']
    # TODU:stream info table need to add 
    stream_file = open('stream_info_table')
    stream_table = json.loads(stream_file.read())[0]
    stream_name = epic1_return['stream_name'][0] # a string

    code_list = epic1_return['course']
    reco = set(stream_table[stream_name])
    

    return list(reco-set(code_list))'''
    
 
### course planning
def course_planning(epic1_return):
    info = ''
    code_list = epic1_return['course']
    if code_list == []:
        return 'Please provide courses code.'
    info += 'We not implement this function yet, sorry.'
    
    return info
    '''
    # ####################################################
    # # de-dupilcation
    # course_list = epic1_return['course_name']
    # code_list = epic1_return['code']
    # temp_code = code_replace(course_list)
    # for c in temp_code:
    #     if c not in code_list:
    #         code_list.append(c)
    # ####################################################

    for c in code_list:
        course_info = COURSE_INFO[c]
        info += f"{c}'s relative courses are: "
        for rel in course_info['Relative_courses']:
            info += ' '+rel + ','
        info += '\n'
    '''

### time clash check
def clash_check(epic1_return):

    check_list = []
    code_list = epic1_return['course']
    
    if code_list == []:
        return 'Please provide courses code.'
    
    info = 'We not implement this function yet, sorry.'
    return info
    
    # ####################################################
    # # de-dupilcation
    # course_list = epic1_return['course_name']
    # code_list = epic1_return['code']
    # temp_code = code_replace(course_list)
    # for c in temp_code:
    #     if c not in code_list:
    #         code_list.append(c)
    # ####################################################
    '''
    for c in code_list:
        course_info = COURSE_INFO[c]
        if course_info['timetable'] in check_list:
            return 'Yes, your courses clashed.'
        else:
            check_list.append(course_info['timetable'])
    return 'No, you arranged very well.'
    '''
    
    
### retrieve func
def retrieval_func(epic1):
    response = 'eorro'
    if epic1['intent'] == 'Graduate requirements':
        response = graduate_req(epic1)
    elif epic1['intent'] ==  'Stream courses recommendation':``
        response = stream_courses_rec(epic1)
    elif epic1['intent'] == 'Timetable clash':
        response =  clash_check(epic1)
    elif epic1['intent'] == 'Course planning':
        response = course_planning(epic1)
    elif epic1['intent'] == 'Basic courses information':
        response = basic_courses_info(epic1)
    return response
