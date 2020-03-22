from flask import Flask, jsonify, request, render_template
from flask_pymongo import PyMongo
from bson.json_util import dumps
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv
import requests

load_dotenv()

dbname = os.getenv('dbname')
dburi = os.getenv('dburi')
allbountweb = os.getenv('pyallbountyweb')

app = Flask(__name__)

app.config['MONGO_DBNAME'] = dbname
app.config['MONGO_URI'] = dburi

mongo = PyMongo(app)

# TODO; Create GET to get all guilds in database

# This api call retrieves all banned people and the guilds they are banned
@app.route('/bounties', methods=['GET'])
def get_all_bounties():
    bounties = mongo.db.bounties.find()

    output = []
    for bount in bounties:
        temp_build = []
        for b in bount['guild_bans']:
            temp_build.append({'guild_id': b['guild_id'],
                               'guild_name': b['guild_name'], 'reason': b['reason']})
        temp_dict = {'bounty': bount['bounty_id'],
                     'bounty_name': bount['bounty_name'],
                     'bounty_avatar': bount['bounty_avatar'],
                     'discriminator': bount['discriminator'],
                     'bot': bount['bot'],
                     'banned_guilds': temp_build}
        output.append(temp_dict)

    return jsonify({'result': output})


# This api call will add a newly banned person into the database
@app.route('/new_bounty', methods=['POST'])
def add_new_bounty():
    bounties = mongo.db.bounties

    bounty_id = request.json['bounty_id']
    bounty_name = request.json['bounty_name']
    bounty_avatar = request.json['bounty_avatar']
    discriminator = request.json['discriminator']
    bot = request.json['bot']
    guild_id = request.json['guild_id']
    guild_name = request.json['guild_name']
    reason = request.json['reason']

    bounties.insert_one({'bounty_id': bounty_id, 'bounty_name': bounty_name, 'bounty_avatar': bounty_avatar,
                         'discriminator': discriminator, 'bot': bot, 'guild_bans': [{'guild_id': guild_id, 'guild_name': guild_name, 'reason': reason}]})

    output = {'bounty_name': bounty_name}

    return jsonify({'result': output})


# This API call will update an excisting bounty with a new guild ban
@app.route('/add_guild_bounty', methods=['POST'])
def bounty_addguild():
    bounties = mongo.db.bounties

    bounty_id = request.json['bounty_id']
    guild_id = request.json['guild_id']
    guild_name = request.json['guild_name']
    reason = request.json['reason']

    bounties.update_one(
        {'bounty_id': bounty_id}, {'$push': {'guild_bans': {
            'guild_id': guild_id, 'guild_name': guild_name, 'reason': reason}}}
    )

    output = {'bounty_name': bounty_id}

    return jsonify({'result': output})


if __name__ == '__main__':
    app.run(debug=True)
