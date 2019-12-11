import flask
import mysql.connector
from flask import request

mydb = mysql.connector.connect(
  host="104.154.143.166",
  user="xxuser",
  passwd="welcome1DB"
)

#print(mydb)
app = flask.Flask(__name__)

mycursor = mydb.cursor()
mycursor.execute("SELECT ITEM_NUMBER,DESCRIPTION FROM sampledb.XXIBM_PRODUCT_SKU")
myresult = mycursor.fetchall()
mycursor.close()
#for x in myresult:
 # print(x[0])


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

#app.run()
app.run(host='0.0.0.0',port=5000,debug=True)
