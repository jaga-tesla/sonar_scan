import json
import boto3
 
# Instance details for both us-east-1 and us-east-2
instance_east_1 = [["ARTICLE-ES7.5-MAINTENANCE [Articale]", "i-0b65960a2e98191c0"], ["PRODUCT-ES7.5-MAINTENANCE [Product]", "i-046c02a9a85717c52"], ["Export chart test - Ubuntu 20", "i-0315e7891ab073ac7"], ["R-SYSTEM", "i-0b321b6047f51e577"], ["Dev-Innova-WP-New", "i-05ba34a3fbfb88b08"], ["InnovaMarketInsights-DotNetCore	", "i-04d2bb09907a8d474"]]
instance_east_2 = [["Active-Directory", "i-0a2ac752786c4a510"], ["ADFS-2016", "i-04b33bb7c4e46c4c3"]]

print ("*****************Viriginia******************")
ec2 = boto3.client('ec2', region_name="us-east-1")
for i in instance_east_1:
    try:
       response = ec2.describe_instances(InstanceIds=[i[1]])
       print (i[0], response['Reservations'][0]['Instances'][0]['State']['Name'])
    except Exception as e:
        print (e)

print ("******************Ohio*********************")
print ("**********************")
ec2 = boto3.client('ec2', region_name="us-east-2")
for i in instance_east_2:
    try:
       response = ec2.describe_instances(InstanceIds=[i[1]])
       print (i[0], response['Reservations'][0]['Instances'][0]['State']['Name'])
    except Exception as e:
        print (e)





