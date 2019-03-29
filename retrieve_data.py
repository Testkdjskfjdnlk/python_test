import boto3
import pandas as pd
import copy
import datetime

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
            ADK_nb += 1

        if courses[course]['is project'] == 'Yes':
            nb_projects += 1
        total_units += int(courses[course]['units'])
    


    if ADK_nb < 6:
        return f'No, you need more {6-ADK_nb} 6-units ADK courses to meet the graduation requirement.'
    if total_units < 96:
        return f'No, you need to get {96 - total_units} more units to meet the graduate requirement.'
    if nb_projects < 1:
        return 'No, you must enroll at least 1 project.'

    return 'Yes, congradulations!'
    
  
#### find basic course information
def basic_courses_info(epic1_return):
    info = ''
    handbook = epic1_return['handbook']
    timetable = epic1_return['time']
    outline = epic1_return['outline']
    staff = epic1_return['staff']     #### need add 
    location = epic1_return['location']
    code_list = epic1_return['course']
    related = epic1_return['related']    ### database data type question ????
    
    if code_list == []:
        return 'Please provide courses code.'
    
    courses = course_info.loc[code_list].T.to_dict()
    
    for course in courses:
        info += course + 'info are: \n'
        if handbook != []:
            info += 'Handbook link is: ' + courses[course]['handbook link'] +' \n'
        if outline != []:
            info += 'Outline link is: '+ courses[course]['outline link']+',' + 'outline is: ' + courses[course]['outline text']+' \n'
        if timetable != []:
            info += 'Time link is: ' + courses[course]['timetable link']+',' + 'timetable is: ' + str(courses[course]['timetable'])+' \n'
        if staff != []:
            info += 'staff is: '+ str(courses[course]['staff']) + ' \n'
        if location != []:
            info += 'location is: '+ str(courses[course]['location']) + ' \n'
        if related != []:
            if courses[course]['prerequisite'] == 'N/a':
                info += 'There is no prerequisite course'+ ' \n'
            else:
                info += courses[course]['prerequisite'] + ' \n'
            if courses[course]['exclusion list'] == []:
                info += 'There is no exclusion course'+ ' \n'
            else:
                info += ' '.join(courses[course]['prerequisite']) + ' \n'
    
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
    
 
### course planning
def course_planning(epic1_return):
    info = ''
    code_list = epic1_return['course']
    if code_list == []:
        return 'You can choose basic courses like COMP9021, COMP9020, COMP9311, GSOE9820.'
    courses = course_info.loc[code_list].T.to_dict()

    for course in courses:
        #print(course)
        if courses[course]['prerequisite'] != 'N/a':
            info += 'For ' + course + ' you can choose: '
            info += courses[course]['prerequisite'] +'\n'
        else:
            if courses[course]['exclusion list'] != []:
                info += 'For ' + course + ' you can choose: \n'
                info += 'Exclusions: ' + ' '.join(courses[course]['exclusion list']) + '\n'
            else:
                info += 'There is no related course with ' + course + '\n'
    
    return info

### time clash check
def check_hour(t11,t12,t21,t22):
    if t22 <= t11:
        return True
    if t21 >= t12:
        return True
    if t11 <= t21 and t21 < t12:
        return False
    if t21 <= t11 and t11 < t22:
        return False
    if t11 <= t21 and t22 <= t12:
        return False
    if t21 <= t11 and t12 <= t22:
        return False

def check_time(table1,table2):
    days = ''
    if table1 == {} or table2 == {}:
        return days
    else:
        for day in table1:
            if day in table2.keys():
                t1 = table1[day]
                t2 = table2[day]
                for t in t1:
                    t11 = datetime.datetime.strptime(t[0:6].strip(), '%H:%M')
                    t12 = datetime.datetime.strptime(t[8:].strip(), '%H:%M')
                    for tt in t2:
                        t21 = datetime.datetime.strptime(tt[0:6].strip(), '%H:%M')
                        t22 = datetime.datetime.strptime(tt[8:].strip(), '%H:%M')
                        result = check_hour(t11,t12,t21,t22)
                        if result == False:
                            days += day + ' '
        return days

def clash_check(epic1_return):

    code_list = copy.copy(epic1_return['course'])
    
    if code_list == []:
        return 'Please provide courses code.'
    
    if len(code_list) < 2:
        return 'Ther is no clash for one course.'
    
    info = ''
    
    times = course_info.loc[code_list,['timetable']].T.to_dict()
    for course in code_list:
        timetable = times[course]['timetable']
        code_list.remove(course)
        for other in code_list:
            other_timetable = times[other]['timetable']
            for t in timetable:
                result = check_time(timetable[t],other_timetable[t])
                if result != '':
                    info += course + ' and ' + other
                    info += 'has clash in Term ' + t + ' in ' + result + '\n'
    if info == '':
        print(epic1_return['course'])
        info += 'There is no clash between ' + ' and '.join(epic1_return['course']) + '\n'
            
    return info
    
    
### retrieve func
def retrieval_func(epic1):
    response = 'eorro'
    if epic1['intent'] == 'Graduate requirements':
        response = graduate_req(epic1)
    elif epic1['intent'] ==  'Stream course recommendation':
        response = stream_courses_rec(epic1)
    elif epic1['intent'] == 'Time clash checking':
        response =  clash_check(epic1)
    elif epic1['intent'] == 'Course planning':
        response = course_planning(epic1)
    elif epic1['intent'] == 'Basic courses information':
        response = basic_courses_info(epic1)
    return response
