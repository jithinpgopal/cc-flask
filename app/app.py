import flask
import mysql.connector
from flask import request
import ibm_boto3
from ibm_botocore.client import Config, ClientError
from flask import send_file

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

#mydb = mysql.connector.connect(
#  host="mysql.gamification.svc.cluster.local",
#  user="xxuser",
#  passwd="welcome1"
#)

#print(mydb)
app = flask.Flask(__name__)

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
#         print (type((file["Body"])))
        image_file = open("9015.jpg", "wb")
        image_file.write(file["Body"].read())
        image_file.close()
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

get_buckets()
# get_bucket_contents('cloud-warriors')
# get_bucket_contents('gamification-cos-standard-tkq')

get_image('gamification-cos-standard-tkq', '9015.jpg')
  
  
@app.route('/', methods=['GET'])
def home():
    return '''<h1>Container Crush testing page</h1>
<p>Lorem lipsum</p>
<p> try /first or /listall or /search?searchterm=Shirt</p>
'''


# A route to return all of the available entries in our catalog.
@app.route('/first', methods=['GET'])
def first():
    return '''<h1>Container Crush Testing</h1>
<p>I have no idea what to type here</p>'''

@app.route('/listall', methods=['GET'])
def list_all():
    all_list = {}
    for x in myresult:
        all_list[x[0]]=x[1]
    return all_list

@app.route('/search', methods=['GET'])
def search():
    searchterm = request.args.get('searchterm')
    mycursor = mydb.cursor()
    search_qry = "SELECT ITEM_NUMBER,DESCRIPTION FROM sampledb.XXIBM_PRODUCT_SKU where DESCRIPTION like '%{}%'".format(searchterm)
    print(search_qry)
    mycursor.execute(search_qry)
    searchresult = mycursor.fetchall()
    mycursor.close()
    searched_list = {}
    for x in searchresult:
        searched_list[x[0]]=x[1]
    return searched_list
  
@app.route('/find_image', methods=['GET'])
def find_image():
    imagenum = request.args.get('imagenum')
    return send_file('9015.jpg', mimetype='image/gif')
  
  
  
#app.run()
app.run(host='0.0.0.0',port=5000,debug=True)
