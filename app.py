from flask import Flask, Response, request, render_template, jsonify
from pymongo import MongoClient
import json
import os
from bson import json_util

app=Flask(__name__)  # Flask App initialisation

try:
    mongo = MongoClient("mongodb+srv://test:test@cluster0.ypm4xvo.mongodb.net/?retryWrites=true&w=majority")
    #print(mongo)
    db = mongo.ADB #connect to mongodb1
    mongo.server_info() #trigger exception if cannot connect to dbc
except:
    print("Error -connect to db")
    
@app.route("/")
def home():
    return "<h1>Home Page </h1>"

@app.route('/netflix', methods=['POST'])
def insertdata():
  try:
    data = request.get_json()
    dbResponse = db.netflix.insert_one(data)
    response = Response("New Record added",status=201,mimetype='application/json')
    return response
  except Exception as ex:
    response = Response("Insert New Record Error!!",status=500,mimetype='application/json')
    return response 

@app.route('/netflix', methods=['GET'])
def retrieveall():
  try:
    documents = db.netflix.find()
    output = [{item: data[item] for item in data if item != '_id'} for data in documents]
    return jsonify(output)
  except Exception as ex:
    response = Response("Search Records Error!!",status=500,mimetype='application/json')
    return response

@app.route('/netflix/<string:fname>', methods=['GET'])
def retrieveOne(fname):
  try:
    document = db.netflix.find_one({"title":fname})
    print(document)
    if document:
        return json.loads(json_util.dumps(document))
    else:
        return jsonify({"message": "Document not found"}), 404
  except Exception as ex:
    response = Response("Search Record Error!!"+str(ex),status=500,mimetype='application/json')
    return response

@app.route('/netflix/<string:fname>', methods=['DELETE'])
def deleteByTitle(fname):
  try:
    result= db.netflix.delete_one({"title":fname})
    if result.deleted_count == 1:
        response = Response("Document Deleted Successfully !",status=200,mimetype='application/json')
    else:
        response = Response("Document not found or not deleted !",status=200,mimetype='application/json')
    return response
  except Exception as ex:
    response = Response("Deleting Record Error!!",status=500,mimetype='application/json')
    return response

@app.route('/netflix/<string:fname>', methods=['PATCH'])
def UpdateByTitle(fname):
    
    try:
        document = db.netflix.find_one({"title": fname})
        if document is None:
            return jsonify({"message": "Document not found"}), 404

        update_data = request.json
        for key, value in update_data.items():
            if key in ['id','title','description','runtime','imdb_score']:
                document[key] = value

        db.netflix.update_one({"title":fname}, {"$set": document})

        return jsonify({"message": "Document updated successfully"})
    except Exception as ex:
        response = Response("Updating Record Error!!",status=500,mimetype='application/json')
    return response
    

if __name__ == '__main__':
    app.run(port=5000, debug=True)

