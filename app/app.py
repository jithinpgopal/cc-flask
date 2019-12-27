import flask
import mysql.connector
from flask import request
import ibm_boto3
from ibm_botocore.client import Config, ClientError
from flask import send_file
from flask_cors import CORS,cross_origin
import os
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import pprint
import json
from requests.auth import HTTPBasicAuth
import requests


# Constants for IBM COS values
COS_ENDPOINT = "https://s3.us-south.cloud-object-storage.appdomain.cloud" # Current list avaiable at https://control.cloud-object-storage.cloud.ibm.com/v2/endpoints
COS_API_KEY_ID = "_bAzHuCAN1yPz4Rcg5CZY1Tbp0UOpshuMhpoNkIvJAa3"
COS_AUTH_ENDPOINT = "https://iam.cloud.ibm.com/identity/token"
COS_RESOURCE_CRN = "crn:v1:bluemix:public:cloud-object-storage:global:a/693fe8ead49b44b192004113d21b15c2:fce26086-5b77-42cc-b1aa-d388aa2853d7::" # eg "crn:v1:bluemix:public:cloud-object-storage:global:a/3bf0d9003abfb5d29761c3e97696b71c:d6f04d83-6c4f-4a62-a165-696756d63903::"

# Create resource
cos = ibm_boto3.resource("s3",
    ibm_api_key_id=COS_API_KEY_ID,
    ibm_service_instance_id=COS_RESOURCE_CRN,
    ibm_auth_endpoint=COS_AUTH_ENDPOINT,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT
                         )

mydb = mysql.connector.connect(
  host="104.154.143.166",
  user="xxuser",
  passwd="welcome1DB"
)

authenticator = IAMAuthenticator('GPA4EoS1rdCv5JXfLCa4jy9DaW82d6BuTuJ0bTKKx1CT')
speech_to_text = SpeechToTextV1(
    authenticator=authenticator
)

speech_to_text.set_service_url('https://api.us-east.speech-to-text.watson.cloud.ibm.com')




#mydb = mysql.connector.connect(
#  host="mysql.gamification.svc.cluster.local",
#  user="xxuser",
#  passwd="welcome1"
#)

#print(mydb)

## Couchbase Full Text Search

CB_URL = "http://35.208.159.10:8094/api/index/prodsearch/query"
cb_auth=HTTPBasicAuth('Administrator', 'asdf1234')
CB_QRY_URL  = "http://35.208.159.10:8093/query/service"

## Flask 
app = flask.Flask(__name__)
# CORS(app)
CORS(app, resources={r"/*": {"origins": "https://frontendcontainercrush-cloud-warriors.inmbzp8022.in.dst.ibm.com"}})

mycursor = mydb.cursor()
mycursor.execute("SELECT ITEM_NUMBER,DESCRIPTION FROM sampledb.XXIBM_PRODUCT_SKU")
myresult = mycursor.fetchall()
mycursor.close()
#for x in myresult:
 # print(x[0])

def get_buckets():
    print("Retrieving list of buckets")
    try:
        buckets = cos.buckets.all()
        for bucket in buckets:
            print("Bucket Name: {0}".format(bucket.name))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to retrieve list buckets: {0}".format(e))

def get_bucket_contents(bucket_name):
    print("Retrieving bucket contents from: {0}".format(bucket_name))
    try:
        files = cos.Bucket(bucket_name).objects.all()
        for file in files:
            print("Item: {0} ({1} bytes).".format(file.key, file.size))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to retrieve bucket contents: {0}".format(e))

# CC Bucket name  =  gamification-cos-standard-tkq

def create_text_file(bucket_name, item_name, file_text):
    print("Creating new item: {0}".format(item_name))
    try:
        cos.Object(bucket_name, item_name).put(
            Body=file_text
        )
        print("Item: {0} created!".format(item_name))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to create text file: {0}".format(e))


def create_bucket(bucket_name):
    print("Creating new bucket: {0}".format(bucket_name))
    try:
        cos.Bucket(bucket_name).create(
            CreateBucketConfiguration={
                "LocationConstraint":COS_BUCKET_LOCATION
            }
        )
        print("Bucket: {0} created!".format(bucket_name))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to create bucket: {0}".format(e))

def delete_bucket(bucket_name):
    print("Deleting bucket: {0}".format(bucket_name))
    try:
        cos.Bucket(bucket_name).delete()
        print("Bucket: {0} deleted!".format(bucket_name))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to delete bucket: {0}".format(e))

def delete_item(bucket_name, item_name):
    print("Deleting item: {0}".format(item_name))
    try:
        cos.Object(bucket_name, item_name).delete()
        print("Item: {0} deleted!".format(item_name))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to delete item: {0}".format(e))

def get_item(bucket_name, item_name):
    print("Retrieving item from bucket: {0}, key: {1}".format(bucket_name, item_name))
    try:
        file = cos.Object(bucket_name, item_name).get()
        print("File Contents: {0}".format(file["Body"].read()))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to retrieve file contents: {0}".format(e))

def get_image(bucket_name, item_name):
    print("Retrieving item from bucket: {0}, key: {1}".format(bucket_name, item_name))
    try:
        file = cos.Object(bucket_name, item_name).get()
        # print (type((file["Body"].read())))
        # image_file = open("9015.jpg", "wb")
        # image_file.write(file["Body"].read())
        # image_file.close()
        image_file_byte=file["Body"]
        return image_file_byte
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to retrieve file contents: {0}".format(e))




# create_text_file('cloud-warriors', 'trial.txt', "Hellow")
# get_buckets()
# get_bucket_contents('gamification-cos-standard-tkq')
# create_bucket('cloud-warriors')
# delete_item('cloud-warriors', 'trial.txt')
# delete_bucket('cloud-warrior')

# get_buckets()
# get_bucket_contents('cloud-warriors')
# get_bucket_contents('gamification-cos-standard-tkq')

  
@app.route('/', methods=['GET'])
def home():
    return '''<h1>Container Crush testing page</h1>
<p>Lorem lipsum</p>
<p> try /first or /listall or /search?searchterm=Shirt</p>
'''

@app.route('/listall', methods=['GET'])
@cross_origin()
def list_all():
    all_list = {}
    for x in myresult:
        all_list[x[0]]=x[1]
    return all_list

@app.route('/search', methods=['GET'])
@cross_origin()
def search():
    searchterm = request.args.get('searchterm')
    mycursor2 = mydb.cursor()
    search_qry = "SELECT ITEM_NUMBER,DESCRIPTION FROM sampledb.XXIBM_PRODUCT_SKU where DESCRIPTION like '%{}%'".format(searchterm)
    print(search_qry)
    mycursor2.execute(search_qry)
    searchresult = mycursor2.fetchall()
    mycursor2.close()
    searched_list = {}
    for x in searchresult:
        searched_list[x[0]]=x[1]
    return searched_list
  
@app.route('/find_image', methods=['GET'])
@cross_origin()
def find_image():
    imagenum = request.args.get('imagenum')
    image_name = imagenum + ".jpg"
    print(image_name)
    try:
        img_byte = get_image('gamification-cos-standard-tkq', image_name)
        return send_file(img_byte, mimetype='image/gif')
    except Exception as e:
        return ("Image Not Found")

@app.route('/watson_search', methods=['POST'])
# @cross_origin()
def watson_search():
    myfile  = request.files['file']
    #json_file =  request.get_json(force=True)
    #pprint(json_file)
    for i in request.files:
        print ("One more file")
    for i in request.headers.items():
        print(i)
    speech_recognition_results = speech_to_text.recognize(audio=myfile).get_result()
#     resp = flask.Response(speech_recognition_results)
#     resp.headers['Access-Control-Allow-Origin'] = "https://frontendcontainercrush-cloud-warriors.inmbzp8022.in.dst.ibm.com"
#     print("Watson response Headers : ")
#     print(resp.headers['Access-Control-Allow-Origin'])
    #result_word = str(speech_recognition_results['results'][0]['alternatives'][0]['transcript']).split(' ', 1)[0]
    print(speech_recognition_results)
#     print(resp)
#     return resp
    return speech_recognition_results
    #return("Return complete")

@app.route('/prod_search', methods=['GET'])
@cross_origin()
def prod_search():
    search_string = request.args.get('searchwords')
    search_array = search_string.split(' ')
    conj_array = []
    for i in search_array:
        sub_qry = {}
        sub_qry["match"] = "*" + str(i) + "*"
        conj_array.append(sub_qry)
    qry = {"conjuncts": conj_array}
    r = requests.post(url=CB_URL, auth=cb_auth, json={"fields": ['*'], "highlight": {}, "query": qry, "size": 20})
    data = r.json()
    result_keys = []
    for i in data['hits']:
        result_keys.append(i['id'])
    select_qry = "SELECT *  FROM CCPRODCTLG use keys {}".format(str(result_keys))
    print(select_qry)
    select_qry_json = {"statement": select_qry}
#     print(select_qry_json)
    w = requests.post(url=CB_QRY_URL, auth=cb_auth, json=select_qry_json)
    data1 = w.json()
    qry_res = data1['results']
#     print(qry_res)
    resultarray = []
    search_return = {}
    for i in qry_res:
        one_row = i['CCPRODCTLG']
        resultarray.append(one_row)
#         print(i['CCPRODCTLG'])
    search_return["plannedEvents"] = resultarray
#     print(search_return)
    return search_return

 
#app.run()
app.run(host='0.0.0.0',port=5000,debug=True)
