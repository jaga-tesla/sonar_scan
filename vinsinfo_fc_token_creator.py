# Created By : jagadeesh.P
# Created date : 25/11/2022
# Created for : FC team [token creator]
import json
import boto3
import datetime
import time
import datetime
import smtplib
from smtplib import SMTPException;
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from operator import itemgetter
from boto3.dynamodb.conditions import Key, Attr
# initial setup for the dynamobd table get
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('vinsinfo_fc_daily_token')
lunch_tokentable = dynamodb.Table('vinsinfo_fc_token_history')
# time validation
def time_in_range():
    print ("Time validation start")
    start = datetime.time(0, 30, 0)
    end = datetime.time(5, 0, 0)
    current = datetime.datetime.now().time()
    print (start <= current <= end)
    return start <= current <= end
# User check user exit or not
def user_check(emp_id):
    now = datetime.datetime.now()
    today_date = now.strftime("%m/%d/%Y")
    # dynamodb table connect the users details
    dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
    table = dynamodb.Table('vinsinfo_fc_daily_token')
    response = table.scan()
    data = response['Items']
    # initialy user check set as false, token and issue time also
    user_check = False
    today_token = ""
    issuetime = ""
    # Check user Id is present or not from the DynamoDB
    for i in data :
        if (emp_id==i["user_id"]) :
            user_check = True
            employee_name = i["name"]
            print (employee_name)   
    # user details get from the history table
    try :
        emp_id = int(emp_id)
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('vinsinfo_fc_token_history')
        print (today_date)
        response = table.scan(FilterExpression=Attr('update_date').eq(str(today_date)) & Attr('employee_id').eq(emp_id))
        print (response)
        data = response['Items']
    except Exception as e:
        print (e)     
    # if the user already get the token collet the details from the history table
    if (len(data) > 0) :
        print ("user alredy get token status")
        data = data [0]
        # user_check == True
        token_status = True
        today_token = data ['token_id']
        issuetime = data ['token_issue_time']
    else :
        print ("user not exist")
        #user_check == False
        token_status = False
        today_token = ""
    if (user_check == True) :
        details_set = {"user_check" : user_check, "token_status" : token_status, "employee_name": employee_name, "token": today_token, "issuetime": issuetime, 'time_out' : time_in_range()}
        return (details_set)
    else :
        return ("not_exist")
# token creator
def token_gen(emp_id, lunch, gravy):
    # Collect the datatimes for dynamoDB Updating
    now = datetime.datetime.now()
    now =now + datetime.timedelta(hours = 5, minutes=30)
    token_issue_time = now.strftime("%m/%d/%Y - %H:%M %p")
    update_date_time = now.strftime("%b_%d")
    index = str(update_date_time) + str(emp_id)
    update_item_date = now.strftime("%m/%d/%Y")
    expire_time = now + datetime.timedelta(days = 90)
    expire_time = expire_time.timestamp()
    # collect the employee detailes for finding tower
    try :
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('vinsinfo_fc_daily_token')
        response = table.scan(FilterExpression=Attr('user_id').eq(emp_id))
        data = response['Items'][0]
        tower = data['tower']
        name = data['name']
        tamil_name = data['tamil_name']
        print (data['tower'])
        try :
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table('vinsinfo_fc_token_history')
            response = table.scan(FilterExpression=Attr('update_date').eq(now.strftime("%m/%d/%Y")) & Attr('tower').eq(tower))
            print(len(response['Items']))
            token = len(response['Items']) + 1
            dynamodb = boto3.client('dynamodb')
            response = dynamodb.put_item(TableName='vinsinfo_fc_token_history', Item={'id':{'S':index},'employee_id':{'N':str(emp_id)}, 'tamil_name':{'S' :str(tamil_name)}, 'token_id':{'N':str(token)},'token_issue_time':{'S':token_issue_time}, 'tower':{'S':str(tower)}, 'expire_time':{'N' : str(expire_time)}, 'update_date':{'S':update_item_date}, 'name':{'S':name}, 'lunch':{'N':str(lunch)}, 'gravy':{'N':str(gravy)}})
            detail_set = {"token": token, "time_issued": token_issue_time}
            return (detail_set)
        except Exception as e:
            print (e)
        return 0
    except Exception as e:
        print (e)
    return(0)
# mail sending funtion
def inform_main (content_one, content_two, content_one_egg, content_two_egg, count_one, count_two) :
    now = datetime.datetime.now()
    DATE = now.strftime("%d-%b-%Y")
    smtpusername =str(os.environ['smtpusername']);
    smtppassword =str(os.environ['smtppassword']);
    fromaddress =str(os.environ['fromaddress']);
    toaddress =os.environ['toaddress'].split(',');
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Lunch Count - "+str(DATE)+" - Mercury ("+str(count_one)+") - Venus ("+str(count_two)+")"
    msg['From'] = fromaddress
    msg['To'] = ",".join(toaddress)
    msg['X-Priority'] = '2'
    html = """\
    <html><body style="font-family:calibri">
    <h3>Mercury Tower - """ + DATE + """</h3>""" + content_one + """
    <h3>Mercury Tower - """ + DATE + """</h3>""" + content_one_egg + """ 
    """
    part_1 = MIMEText(html, 'html');
    msg.attach(part_1);
    try:
        smtp_server = smtplib.SMTP("email-smtp.us-east-1.amazonaws.com",587);
        smtp_server.starttls();
        smtp_server.login(smtpusername,smtppassword);
        smtp_server.sendmail(fromaddress,toaddress,msg.as_string())          
        print("Successfully Email Sent")
    except SMTPException as exc:
        print("Unable To Sent")
        print(str(exc))
    msg = MIMEMultipart('alternative')
    msg['From'] = fromaddress
    msg['To'] = ",".join(toaddress)
    msg['X-Priority'] = '2'
    msg['Subject'] = "Lunch Count - "+str(DATE)+" - Mercury ("+str(count_one)+") - Venus ("+str(count_two)+")"
    html = """\
    <html><body style="font-family:calibri">
    <h3>Venus Tower - """ + DATE + """</h3>""" + content_two + """
    <h3>Venus Tower - """ + DATE + """</h3>""" + content_two_egg + """ 
    """
    part = MIMEText(html, 'html');
    msg.attach(part);
    try:
        smtp_server = smtplib.SMTP("email-smtp.us-east-1.amazonaws.com",587);
        smtp_server.starttls();
        smtp_server.login(smtpusername,smtppassword);
        smtp_server.sendmail(fromaddress,toaddress,msg.as_string())          
        print("Successfully Email Sent")
    except SMTPException as exc:
        print("Unable To Sent")
        print(str(exc))
def lunch_count_content_formate(data) :
    number_of_orders = 0
    s_no = 1
    th_content = "".join([str(i) for i in ['<th style="width:75px;border: 1px solid black;">'+i+'</th>' for i in ["S.No", "EMP ID", "TOKEN NO", "NAME", "NAME", "LUNCH", "EGG GRAVY", "TAKEN", "PAID"]]])
    content = """<table style="border: 1px solid black;text-align:center;"><tr>"""+th_content+"""</tr>"""
    for i in data :
        lunch = ""
        gravy = ""
        if (str(i["lunch"]) == "1") :
            lunch = "Yes"
        if (str(i["gravy"]) == "1") :
            gravy = "Yes"
        content = str(content) + """
            <tr>
                <td style="width:75px;border: 1px solid black;">"""+str(s_no)+"""</td>
                <td style="width:50px;border: 1px solid black;">"""+str(i["employee_id"])+"""</td>
                <td style="width:50px;border: 1px solid black;">"""+str(i["token_id"])+"""</td>
                <td style="width:200px;border: 1px solid black;text-align:left;padding:0px 5px;">"""+str(i["tamil_name"])+"""</td>
                <td style="width:200px;border: 1px solid black;text-align:left;padding:0px 5px;">"""+str(i["name"])+"""</td>
                <td style="width:50px;border: 1px solid black;text-align:left;padding:0px 5px;">"""+lunch+"""</td>
                <td style="width:50px;border: 1px solid black;text-align:left;">"""+gravy+"""</td>
                <td style="width:50px;border: 1px solid black;text-align:left;"></td>
                <td style="width:50px;border: 1px solid black;text-align:left;"></td>
            </tr> """
        number_of_orders = number_of_orders + 1
    th_content = "".join([str('<th style="width:50px;border: 1px solid black;"></th>') range(8)])
    for i in range(number_of_orders, number_of_orders+4):
        content = str(content) + """ 
            <tr>
                <th style="width:75px;border: 1px solid black;">"""+str(i)+"""</th>"""+th_content+"""
            </tr>
        """      
    content = content + """</table></br>"""
    result_content = [content, number_of_orders]
    return (result_content)  
def gravy_count_content_formate (data) :
    th_content = "".join([str(i) for i in ['<th style="width:75px;border: 1px solid black;">'+i+'</th>' for i in ["S.No", "EMP ID", "TOKEN NO", "NAME", "NAME", "LUNCH", "EGG GRAVY", "TAKEN", "PAID"]]])
    content = """<table style="border: 1px solid black;text-align:center;"><tr>"""+th_content+"""</tr>"""
    number_of_orders = 1
    for i in data :
        gravy = ""
        if (str(i["gravy"]) == "1") :
            gravy = "Yes"
        content = str(content) + """
            <tr>
                <td style="width:75px;border: 1px solid black;">"""+str(number_of_orders)+"""</td>
                <td style="width:50px;border: 1px solid black;">"""+str(i["employee_id"])+"""</td>
                <td style="width:50px;border: 1px solid black;">"""+str(i["token_id"])+"""</td>
                <td style="width:200px;border: 1px solid black;text-align:left;padding:0px 5px;">"""+str(i["tamil_name"])+"""</td>
                <td style="width:200px;border: 1px solid black;text-align:left;padding:0px 5px;">"""+str(i["name"])+"""</td>
                <td style="width:50px;border: 1px solid black;text-align:left;">"""+gravy+"""</td>
                <td style="width:50px;border: 1px solid black;text-align:left;"></td>
                <td style="width:50px;border: 1px solid black;text-align:left;"></td>
            </tr> """
        number_of_orders = number_of_orders + 1
    content = content + """ </table>"""
    return (content)  
        
def lambda_handler(event, context):
    if (event['type'] == "mail_send") :
        now = datetime.datetime.now()
        try :
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table('vinsinfo_fc_token_history')
            response_one = table.scan(FilterExpression=Attr('update_date').eq(now.strftime("%m/%d/%Y")) & Attr('tower').eq('Mercury') & Attr('lunch').eq(1))
            response_two = table.scan(FilterExpression=Attr('update_date').eq(now.strftime("%m/%d/%Y")) & Attr('tower').eq('Venus') & Attr('lunch').eq(1))
        except Exception as e:
            print (e)
        # Content Creation for Mercury tower
        content_one = ""
        content_two = ""
        content_one_egg = ""
        content_two_egg = ""
        c_one = 0
        c_two = 0

        # Table content of mercury lunch count 
        data = response_one['Items']
        if (len(data) > 0) :
            for sub in data:
                sub['token_id'] = int(sub['token_id'])
            data_mercury = sorted(data, key=itemgetter('token_id')) 
            
            content_details = lunch_count_content_formate(data_mercury)
            content_one = str(content_one) + str(content_details[0])
            c_one = content_details [1]
        else :
            content_one = "Today Lunch Not Placed"
        # Table content of venus lunch count
        data = response_two['Items']
        if (len(data) > 0) :
            for sub in data:
                sub['token_id'] = int(sub['token_id'])
            data_venus = sorted(data, key=itemgetter('token_id'))
            
            content_details = lunch_count_content_formate(data_venus)
            content_two = str(content_two) + str(content_details[0])
            c_two = content_details [1]
        else :
            content_two = "Today Lunch Not Placed"
        dynamodb = boto3.resource('dynamodb')
        try :
            table = dynamodb.Table('vinsinfo_fc_token_history')
            response_egg_one = table.scan(FilterExpression=Attr('update_date').eq(now.strftime("%m/%d/%Y")) & Attr('tower').eq('Mercury') & Attr('gravy').eq(1) & Attr('lunch').eq(0))
            response_egg_two = table.scan(FilterExpression=Attr('update_date').eq(now.strftime("%m/%d/%Y")) & Attr('tower').eq('Venus') & Attr('gravy').eq(1) & Attr('lunch').eq(0))
        except Exception as e:
            print (e) 
        data = response_egg_one['Items']
        if (len(data) > 0) :   
            for sub in data:
                sub['token_id'] = int(sub['token_id'])
            data = sorted(data, key=itemgetter('token_id'))
            content_details = gravy_count_content_formate(data)
            content_one_egg = str(content_one_egg) + str(content_details)
        else :
            content_one_egg = "Today Egg Gravy Not Placed"
        data = response_egg_two['Items']
        if (len(data) > 0):
            for sub in data:
                sub['token_id'] = int(sub['token_id'])
            data = sorted(data, key=itemgetter('token_id'))
            content_details = gravy_count_content_formate(data)
            content_two_egg = str(content_two_egg) + str(content_details)
        else :
            content_two_egg = "Today Egg Gravy Not Placed"
        print ((content_one, content_two, content_one_egg, content_two_egg, c_one, c_two))
        # call the mail sender
        inform_main (content_one, content_two, content_one_egg, content_two_egg, c_one, c_two)
        return ("mail sended")
# ----------------------------------------------------------------------------------------------------------------------------------------------------------
    if (event['type'] == "user_check") :
        print ("user check runing")
        resource = user_check(event['emp_id'])
        if (resource != "not_exist") :
            print (resource)
            return(resource)
        else :
            return("Sorry user not exist")
#-----------------------------------------------------------------------------------------------------------------------------------------------------------
    if (event['type'] == "get_token") :
        print ("get token runing")
        if (time_in_range()):
            response = token_gen(event['emp_id'], event['lunch'], event['gravy'])
            print (response)
            if (response !=0) :
                return (response)
            else :
                return ("sorry token not created")
        else :
            return ("sorry time out")
#-----------------------------------------------------------------------------------------------------------------------------------------------------------
    if (event['type'] == "get_details") :
        date = event['data_time']
        dynamodb = boto3.resource('dynamodb')
        lunch_tokentable = dynamodb.Table('vinsinfo_fc_token_history')
        lunch_tokentable = lunch_tokentable.scan(FilterExpression=Attr('update_date').eq(str(date)))
        last_day_updated_item = []
        for i in lunch_tokentable["Items"] :
            if (i['update_date'] == date):
                detail_set = {"token_id" : int(i['token_id']) , "employee_id" : i['employee_id'], "token_issue_time" : i['token_issue_time'], "name" : i['name'], "tower": i['tower'], "lunch": i['lunch'], "gravy": i['gravy']}
                last_day_updated_item.append(detail_set)
        last_day_updated_item = sorted(last_day_updated_item, key=itemgetter('token_id'))
        
        return (last_day_updated_item)
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------
    if (event['type'] == "token_page_content") :
        now = datetime.datetime.now()
        try :
            # connect the dynamoDB
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table('vinsinfo_fc_token_history')
            # scan the dynamoDB table to get the today count
            response_one = table.scan(FilterExpression=Attr('update_date').eq(now.strftime("%m/%d/%Y")) & Attr('tower').eq('Mercury'))
            response_two = table.scan(FilterExpression=Attr('update_date').eq(now.strftime("%m/%d/%Y")) & Attr('tower').eq('Venus'))
            # created the date with mercury ,venus count and today 
            now =now + datetime.timedelta(hours = 5, minutes=30)
            lunch_from_mercury = 0
            gravy_from_mercury = 0
            lunch_from_venus = 0
            gravy_from_venus = 0
            for i in response_one['Items'] :
                if (i['gravy'] == 1) :
                    gravy_from_mercury = gravy_from_mercury + 1
                if (i['lunch'] == 1) :
                    lunch_from_mercury = lunch_from_mercury + 1
            mercury_count = str(lunch_from_mercury)+"/"+str(gravy_from_mercury)
            for i in response_two['Items'] :
                if (i['gravy'] == 1) :
                    gravy_from_venus = gravy_from_venus + 1
                if (i['lunch'] == 1) :
                    lunch_from_venus = lunch_from_venus + 1
            venus_count = str(lunch_from_venus)+"/"+str(gravy_from_venus)
            detail_set = {"mercury_count" : mercury_count, "venus_count" : venus_count, "today_date" : str(now.strftime("%m/%d/%Y - %H:%M %p" ))}
            return (detail_set)
        except Exception as e:
            print(e)
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    if (event['type'] == "lunch_availability") :
        print (os.environ['lunch_availability'])
        if (str(os.environ['lunch_availability']) == "yes") :
            return (1)
        else :
            return (0)
    return (0)
#------- new update last  commit