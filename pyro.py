# rominimal Telegram bot to recive ratings and display TrackID in response
#os.cpu_count().
#
#mem_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')  # e.g. 4015976448
#mem_gib = mem_bytes/(1024.**3)

import re, pwd, os, platform, psutil, io
import math
import readline0
import logging, pymongo
import json
import random
import urllib.parse
from json2html import *
#import json2html

from bson.json_util import dumps
import hashlib

from datetime import datetime, timedelta, timezone
from timeit import default_timer as timer

from pprint import pprint, pformat
from pathlib import Path
from pyrogram import Client, filters, emoji
#from pyrogram import enums
from pyrogram.types import (InlineQueryResultArticle, InputTextMessageContent,
                            InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, Message)
from pyrogram.errors import BadRequest, Forbidden, FloodWait
import aiohttp

#from aio_yandex_translate.translator import Translator
#p = psutil.Process(os.getpid())
#pt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(p.create_tima()))

pt = datetime.now()

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
API_SESSION = os.getenv('SESSION_STRING')
BOT_TOKEN = os.getenv('BOT_TOKEN')
CACHE_TIME = os.getenv('CACHE_TIME') or 900 # seconds

metrics = {}
metrics['processed'] = 0

uid = pwd.getpwuid(os.getuid()).pw_name
uname = platform.uname()

superadmin_ids = [45137724]

# Wisla Skarbow
#LOG_TCHANNEL = -164881369
LOG_TCHANNEL = -761337680
LOG_PUBLIC_TCHANNEL = -745695294
TRACK_TCHANNEL = -1001325689803
MAIN_TCHANNEL = -1001163186712
POLIGON_TCHANNEL = -1001436849388
PING_NOWPLAYING_WEBHOOK = 'https://p.cld.yt/ping'

#app.send_message("madmike0", f'**CRASHED PLEASE HELP** Running as {uid}. {uname.system} {uname.node} {uname.release} {uname.version} {uname.machine}. Load: {os.getloadavg()}. While playing: `{nowpltrack}`')

ALL_TCHATS = [TRACK_TCHANNEL, MAIN_TCHANNEL]
VOTE_VALUES_MAP = {'emoji.WASTEBASKET': -1, '👎':0 , '1️⃣':1 ,'2️⃣': 2, '3️⃣': 3, '4️⃣': 4, '🔥': 5}
VOTE_VALUES_RESULTS = {'emoji.WASTEBASKET': -1, '👎':0 , '1️⃣':1 ,'0': 0, '3️⃣': 0, '4️⃣': 0, '🔥': 0}


MENTION = "[{}](tg://user?id={})"

VOTE_VALUES = [emoji.WASTEBASKET, "👎", "1️⃣",'2️⃣', '3️⃣', '4️⃣', '🔥']
re_votes_combined = combined = "(" + ")|(".join(VOTE_VALUES) + ")"

# Rominimal.club Track IDs -1001325689803
# Rominimal.club -1001163186712
logger = logging.getLogger('mainloop')

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] (%(module)s.%(funcName)s): %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
#client = pymongo.MongoClient("mongodb+srv://admin:<password>@rominimal0.o8op5.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
#db = client.test

#with Client("my_account", api_id, api_hash) as app:
#    app.send_message("madmike0", "Greetings from **Pyrogram**!")

mongo_con = os.getenv('MONGO_CON')
mongo = pymongo.MongoClient(mongo_con)
db = mongo.rominimal


ABOUT = """
👋 Welcome to the ROminimal.Club! 🥳

Over the years of being a DJ, playing and digging music, I’ve experienced a lot of sounds that create certain feelings. This process always took a lot of time and recently I've found myself with a lot of music that I did not have time to get into, but wanted to discover in an aesthetically pleasing way.

Which is - tracks perfectly mixed together. So, I’ve created a little software/music art project. 

I've plugged in some of my music library as well as crawling internet looking for rominimal sound, to be mixed live by a custom, audio processing setup that I’ve built to do what normal Dj would. And turned it into an on-line radio station 🎙. 

The tracks are mixed live in an unattended way, chosen semi-randomly in sets. You will see distinctive ▶ description via “currently playing” that represent current Dj actions.

** 🔥 More On Romanian Revolution **
https://rominimal.club/post/on-romanian-revolution/

[ℹ️ How to DJ using discovered tracks?](https://rominimal.club/post/dj-using-rominimal-tracks/)

💯 Powered by @madmike0 👾
"""

app = Client(API_SESSION, API_ID, API_HASH, bot_token=BOT_TOKEN)
keyboard =                 [
                    [  # First row
                        InlineKeyboardButton(  # Generates a callback query when pressed
                            emoji.WASTEBASKET,
                            callback_data="-1"
                            ),
                        InlineKeyboardButton(
                            "👎",
                            callback_data="0"
                        ),
                        InlineKeyboardButton(
                            "1️⃣",
                            callback_data="1"
                        ),
                        InlineKeyboardButton(
                            "2️⃣",
                            callback_data="2"
                        ),
                        InlineKeyboardButton(
                            "3️⃣",
                            callback_data="3"
                        ),
                        InlineKeyboardButton(
                            "4️⃣",
                            callback_data="4"
                        ),
                        InlineKeyboardButton(
                            "🔥",
                            callback_data="5"
                        ),
                   ],
                    [  # Second row
                        InlineKeyboardButton(
                            f'{emoji.ROBOT} Start Here',
                            url = 'https://t.me/xFadebot?start=Digging'
                        ),
                        InlineKeyboardButton(
                            f'{emoji.HEADPHONE} Tune-in',
                            url = 'https://rominimal.club/'
                        ),
                  ],
                    [
                        InlineKeyboardButton(
                            f"{emoji.HOT_BEVERAGE} Buy me Coffee {emoji.RED_HEART}",
                            url = 'https://www.buymeacoffee.com/rominimal'
                        ) 
                    ]
                ]
 
reply_markup2=ReplyKeyboardMarkup(
                [
                   ["", "❯❯❯ ROminimal.club DJ Console ❮❮❮"],
                   ["💁‍♂️ 23 Votes ❘ 💪 35 Rank ❘ 🏁 3.4 Avg"],
                    ["/top 10", "/export", "/stats", "/status"],  # Third row
                   [emoji.WASTEBASKET, "👎", "1️⃣", '3️⃣', '4️⃣', '🔥'],  # First row
                ],
                resize_keyboard=True  # Make the keyboard smaller
            )
reply_markup = InlineKeyboardMarkup(keyboard)
trackid_keyboard_markup = InlineKeyboardMarkup(
                [
                   [  # First row
                        InlineKeyboardButton(
                            "🔉 Soundcloud",
                            url = 'https://t.me/xFadeBot'
                        ),
                        InlineKeyboardButton(
                            "🔎 Google",
                            url = 'https://rominimal.club/'
                        ),
                  ]
               ]
            )
with app:
    #app.send_message(LOG_TCHANNEL, f'**Pyrogram** Reporting for Duty! Running as {uid}. {uname.system} {uname.node} {uname.release} {uname.version} {uname.machine}. Load: {os.getloadavg()}')
    #logger.info(db.command("serverStatus"))
    #r = db.rotracks.count({"author":"madmike0"})
    #logger.info(f'Madmike0 count ({r})')
    #session_string = app.export_session_string()
    logger.info(f'SESSION_STRING: {app.export_session_string()}')

def get_nowplaying():
    with open('/data/mediafiles/pyCrossfade/nowplaying.track.txt', 'r') as nowplfile:
        nowpltrack = nowplfile.read()
    return nowpltrack

# Scale mem units
def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

def get_chat_history(chat_id):
    logger.info(f'Get Chat History -> chat_id: {chat_id}')
    #return db.history.find({},{'chat_id': chat_id, })
    return db.history.find({'chat_id': chat_id}).sort("_id", pymongo.ASCENDING)
    #ll = [ log for log in db.history.find({},{'chat_id': chat_ id, }) ]
 
def get_logs_history(chat_id):
    logger.info(f'Get Logs History -> chat_id: {chat_id}')
    #return db.history.find({},{'chat_id': chat_id, })
    res = list(db.logs.find({'chat_id': chat_id}).sort("_id", pymongo.ASCENDING))
    logger.info(res)
    return res
    #ll = [ log for log in db.history.find({},{'chat_id': chat_ id, }) ]
 
async def admin_filter(_, __, m: Message):
    return bool(m.from_user and m.from_user.id in superadmin_ids)

is_admin = filters.create(admin_filter)

@app.on_message(filters.chat(TRACK_TCHANNEL) & filters.regex('Crashed') & ~filters.regex('▶'), group=2)
def crashed(client, message):
        logger.error("=======>> CRASH DETECTED <<=======")
        #app.send_message(MAIN_TCHANNEL, f'@madmike0 I have **CRASHED PLEASE HELP**', disable_notification=True)
        nowpltrack = get_nowplaying()
        app.send_message("madmike0", f'**CRASHED PLEASE HELP** Running as {uid}. Load: {os.getloadavg()}. While playing: `{nowpltrack}`')

#@app.on_message(filters.chat(TRACK_TCHANNEL) & ( filters.regex('masterdeck') | filters.regex('mixout')), group=2)
#def from_pyrogramchatng(client, message):
#        nowpltrack = get_nowplaying()
#        logger.info(f'New DJ message in @PyrogramTRACKS. Now Playing: {nowpltrack}')

#@app.on_message(filters.chat(TRACK_TCHANNEL) & filters.regex('test'), group=2)
#def from_pyrogramchat(client, message):
#        nowpltrack = get_nowplaying()
#        logger.info(f'New message in @PyrogramTRACKS. Now Playing: {nowpltrack}')


#@app.on_message(filters.chat(TRACK_TCHANNEL))
#def from_pyrogramchat(client, message):
#        #logger.info(message)
#        nowpltrack = get_nowplaying()
#        logger.info(f'New message in @PyrogramTRACKS. Now Playing: {nowpltrack}')

@app.on_message(filters.private & filters.command(["start"]) & is_admin )
def start_admin(app, message):
    #m = json.loads(str(message))
    #logger.info(m)
    #message.chat.id
    #messaet.chat.username
    l = {}
    l = { 
            'user_name': message.from_user.username,
            'user_id': message.from_user.id,
            'chat_id': message.chat.id,
            'command': message.command 
        }
    res = db.logs.update_one( 
        {    
            'user_name': message.from_user.username,
            'user_id': message.from_user.id,
            'chat_id': message.chat.id,
            'command': message.command 
        },
        {
            '$set': { 'command': message.command },
            '$currentDate': { 
                'lastModified': True,
                }
        },
        upsert = True
        ).modified_count
    logger.info(f'<{message.from_user.username}> New ADMIN /start [{res}]')
    #message.reply_text('🎛 Welcome to ROminimal.club DJ Console - Time to Play!')
    message.reply_text(
    """
🎛 Welcome to ROminimal.club DJ Console - Time to Dance & Play!
All systems loaded!

👋 Hi, I am a CrossFader, bot that helps discover & mix live new Rominimal Music Tracks.

I am part of a ROminimal.club, a software/music art project. I crawl internet in a search of new peculiar / rominimal sounds to be mixed live by a custom, audio processing setup that was created to do what normal Dj would.
    
The tracks are mixed live in an unattended way, chosen semi-randomly in sets. 

1. Go to ROminimal.club website and listen to the livestream ([also live video](https://s.rominimal.club/player.html))
2.👌 Rate the energy level of tracks in the main group to reveal ID. Enjoy! 🎵
ex: https://t.me/ROminimal_club/7426

[ℹ️ How to DJ using discovered tracks?](https://rominimal.club/post/dj-using-rominimal-tracks/)

🔥 Fire! Sharing is caring! Make sure to add your friends if you dig it!

** I felt the air in the music, the space and serenity. The sound filled the space with love, softness, pleasantness and elegance. Like a wind blowing from room to room. To me, it felt like a sort of miracle - a delicate, non-aggressive groove, restrained and patient, and at the same time so powerful, clubby, tribal and the most narcotic I could ever imagine. In my fantasy world, you could call it the Holy Grail.

👉 https://rominimal.club/post/on-romanian-revolution/
**


** Available Commands: **
  - /help - quick help
  - /about - about the project
  - /stats - your stats
  - /status - system status
  - /top <days|optional> - top diggers for last <days>
  - /export - export your voted track ratings playlist
    """)

@app.on_message(filters.command(["lasthistory"]) & is_admin )
def last_history(app, message):
    ll = [ log for log in db.history.find({},{'_id': False}).limit(10) ]
    #ll = [ log for log in db.history.find({}).limit(10) ]
    logger.info(ll)
    logger.info(f'<{message.from_user.username}> Lasthistory')
    message.reply_text(pformat(ll))

#@app.on_message( ~filters.edited & filters.chat(MAIN_TCHANNEL) & ( filters.regex('Selecting') | filters.regex('Mixing') ) )
#@app.on_message( ~filters.edited & filters.chat(MAIN_TCHANNEL) & filters.me & ( filters.regex('Selecting') | filters.regex('Mixing') ) )
#def progress_bar(app, message):
#    logger.info(message)
#    nh = { 'chat_id': message.chat.id,
#            'message_id': message.message_id,
#            'message_text': message.text,
#            'lastModified': datetime.now()
#            }
#
#    object_id = db.history.insert_one(nh).inserted_id
#    logger.info('DB INSERT -> {object_id}')

@app.on_message(filters.command(["clearhistory"]) & is_admin )
def clear_history(app, message):
    for chat_id in ALL_TCHATS:
        logger.info(f'Clear for {chat_id}')
        chat_history = get_chat_history(chat_id)
        ids = [ msg['message_id'] for msg in chat_history ]
        text = [ msg for msg in chat_history ]
        #logger.info(text)
        logger.info(f'IDS -> {ids}')
        ids = ids[:-1]
        logger.info(f'CUT IDS -> {ids}')

        chunk_size = 100
        
        # Splitting the list in chunks of 100 messages ids
        ids = [ids[i:i + chunk_size] for i in range(0, len(ids), chunk_size)] 
        for m_ids in ids:
            try:
                r = app.delete_messages(
                    chat_id,
                    m_ids
                )
                #logger.info(r)
                #db.history.remove({})
                d = db.history.delete_many( {'message_id': { '$in': m_ids} } )
                logger.info(f'Removed {m_ids}')
                #logger.info(d)
                #logger.info(pformat(r))

            except Exception as e:
                logger.error(e)
                message.reply_text(pformat(e))
                app.send_message(
                    message.chat.id,
                    f"An error occurred: {e}"
                )
                #break # Excepts errors given by Telegram, like floodwaits
 
        #logger.info(msg_ids)
        #try:
            #r = client.delete_messages(-1001325689803, a)
        #r = client.delete_messages(
        #        chat_id = -1001325689803, 
        #        message_ids = 122,
        #        revoke = True
        #        )
        ##except Exception as e:
        #    logger.error(e)


@app.on_message(filters.command(["lastlog"]))
def lastlog(app, message):
    #logger.info(message)
    ll = [ log for log in db.logs.find({},{'_id': False}).limit(10) ]
    logger.info(ll)
    logger.info(f'<{message.from_user.username}> Lastlog')
    message.reply_text(pformat(ll))

@app.on_message(filters.command(["getinvite"]) & is_admin )
def getinvite(app, message):
    logger.info(f'<{message.from_user.username}> Getinvite')
    il = app.get_chat_admin_invite_links()
    message.reply_text(pformat(il))


@app.on_message(filters.command(["lasttrack"]) & is_admin )
async def last_track(app, message):
    #m = json.loads(str(message))
    #logger.info(m)
    #message.chat.id
    #messaet.chat.
    #object_id = db.logs.insert_one(m).inserted_id
    #ll = db.logs.find().sort({$natural:1}).limit(50)
    ll = [ log for log in db.rotracks.find({},{'_id': False}).limit(10) ]
    logger.info(ll)    
    logger.info(f'<{message.from_user.username}> Lasttracks')
    await message.reply_text(pformat(ll))
    await app.send_message(
        "madmike0",  # Edit this
        "This is a ReplyKeyboardMarkup example",
        reply_markup=reply_markup2
    )
    ranking = getranking(99999)
    #await message.reply_text(ranking)

    #message.reply_text(rankingformat(getranking(int(99999)), 99999))

@app.on_message(filters.private & filters.command(["clearlog"]) & is_admin )
def clear_log(app, message):
    #logger.info(message)
    #m = json.loads(str(message))
    #logger.info(m)
    #message.chat.id
    #messaet.chat.username
    logger.info(f'<{message.from_user.username}> Clearing logs collection')
    res = db.logs.remove({})
    logger.info(res)    
    message.reply_text(res)

@app.on_message(filters.private & filters.command(["cleartracks"]) & is_admin )
def clear_tracks(app, message):
    #logger.info(message)
    #m = json.loads(str(message))
    #logger.info(m)
    #message.chat.id
    #messaet.chat.username
    logger.info(f'<{message.from_user.username}> Clearing tracks collection')
    res = db.rotracks.remove({})
    logger.info(res)    
    message.reply_text(res)

@app.on_message(~filters.private & filters.command(["start"]) & ~is_admin & ~filters.me & filters.chat(MAIN_TCHANNEL))
async def startredirect(app, message):
    logusername2db(message)
    await message.reply_text('Please talk to me on priv to start 👉  https://t.me/xFadebot?start=Digging')

@app.on_message(~filters.private & filters.command(["start"]) & is_admin & ~filters.me & filters.chat(MAIN_TCHANNEL))
async def startredirect(app, message):
        await message.reply_text('Please talk to me on priv to start 👉  https://t.me/xFadebot?start=Digging')

@app.on_message(filters.private & filters.command(["start"]) & ~is_admin & ~filters.me)
def start(app, message):
    #m = json.loads(str(message)) 
    #logger.info(m)
    logusername2db(message)
    l = {}
    l = { 
            'user_name': message.from_user.username,
            'user_id': message.from_user.id,
            'chat_id': message.chat.id,
            'command': message.command 
        }
    res = db.logs.update_one( 
        {    
            'user_name': message.from_user.username,
            'user_id': message.from_user.id,
            'chat_id': message.chat.id,
            'command': message.command 
        },
        {
            '$set': { 'command': message.command },
            '$currentDate': { 
                'lastModified': True,
                }
        },
        upsert = True
        ).modified_count
 
    #message.chat.id
    #messaet.chat.username
    #object_id = db.logs.replace_one(m).inserted_id
    logger.info(f'<{message.from_user.username}> New /start logged [{res}]')
    message.reply_text(
    """
🎛 Welcome to ROminimal.club DJ Console - Time to Dance & Play!
All systems loaded!

👋 Hi, I am a CrossFader, bot that helps discover & mix live new Rominimal Music Tracks.

I am part of a ROminimal.club, a software/music art project. I crawl internet in a search of new peculiar / rominimal sounds to be mixed live by a custom, audio processing setup that was created to do what normal Dj would.
    
The tracks are mixed live in an unattended way, chosen semi-randomly in sets. 

1. Go to ROminimal.club website and listen to the livestream ([also live video](https://s.rominimal.club/player.html))
2.👌 Rate the energy level of tracks in the main group to reveal ID. Enjoy! 🎵
ex: https://t.me/ROminimal_club/7426

[ℹ️ How to DJ using discovered tracks?](https://rominimal.club/post/dj-using-rominimal-tracks/)

🔥 Fire! Sharing is caring! Make sure to add your friends if you dig it!

** Available Commands: **
  - /help - quick help
  - /about - about the project
  - /stats - your stats
  - /status - system status
  - /top <days|optional> - top diggers for last <days>
  - /export - export your voted track ratings playlist
    """)

@app.on_message(filters.private & filters.command(["stop"]) & ~filters.me)
def stop(app, message):
    #m = json.loads(str(message)) 
    #logger.info(m)
    d = db.logs.delete_many( {'chat_id': message.chat.id  } )
    #message.chat.id
    #messaet.chat.username
    #object_id = db.logs.replace_one(m).inserted_id
    logger.info(f'<{message.from_user.username}> New /stop logged [{d.deleted_count}]')
    message.reply_text(f'Stop operation status ({d.deleted_count}). You should not receive any more notifications here.')

@app.on_message(filters.command(["help", "help@xFadeBot"]) & ~filters.me, group=2)
def help(app, message):
    logger.info(f'<{message.from_user.username}> /help')
    message.reply_text(
    f""" 
👋 Hi, I am a CrossFader, bot that helps discover & mix live new Rominimal Music Tracks.

I am part of a https://ROminimal.club, a software/music art project. I crawl internet in a search of new peculiar / rominimal sounds to be mixed live by a custom, audio processing setup that was created to do what normal Dj would.
    
The tracks are mixed live in an unattended way, chosen semi-randomly in sets. 

 1. Go to ROminimal.club website and listen to the livestream ([also live video](https://s.rominimal.club/player.html))
 2. Start a chat with CrossFader bot t.me/xFadeBot
 3.👌 Rate the energy level of tracks in the main group to reveal ID. Enjoy! 🎵
ex: https://t.me/ROminimal_club/7426

[ℹ️ How to DJ using discovered tracks?](https://rominimal.club/post/dj-using-rominimal-tracks/)

** Available Commands: **
 - /help
 - /about
 - /stats
 - /status

{emoji.RING_BUOY} Still need help? -  [Contact support](https://clubsupportrobot.t.me/)
    """
    )

@app.on_message(filters.private & filters.command(["about"]))
def about(app, message):
    logger.info(f'<{message.from_user.username}> /about')
    message.reply_text(ABOUT)

# Forward when fallen back to azuracast playlist
@app.on_message(filters.chat(TRACK_TCHANNEL) & filters.regex('Now playing ROminimal.club') & ~filters.regex('▶') & ~filters.regex('Live'), group=1)
def masterplaylist(app, message):
    logger.info('New MasterPlaylist Message')
    #logger.info(message)
    h = {}
    h = { 'chat_id': message.sender_chat.id,
            'message_id': message.message_id,
            'message_text': message.text,
            'lastModified': datetime.now()
        }
    logger.info('Forwarding MSG COPY')
    clear_history(app, message)
    nm = app.send_message(
            text = message.text,
            chat_id = MAIN_TCHANNEL,
            disable_notification = True
            )

    nh = { 'chat_id': nm.chat.id,
            'message_id': nm.message_id,
            'message_text': nm.text,
            'lastModified': datetime.now()
        }
 
    object_id = db.history.insert_one(nh).inserted_id
    logger.info(f'INSERT -> {object_id}')
    logger.info(f'{nh}')

@app.on_message(filters.chat(TRACK_TCHANNEL) & filters.regex('Now playing at ROminimal.club') & filters.regex('masterdeck|pitch|crossfade|mixout'), group=1)
def masterdeck(app, message):
    logger.info('New AutoDJ Message')
    #logger.info(message)
    h = {}
    h = { 'chat_id': message.sender_chat.id,
            'message_id': message.message_id,
            'message_text': message.text,
            'lastModified': datetime.now()
        }
    #object_id = db.history.insert_one(h).inserted_id
 
    message.edit_text(text = '[TRACK ID]: %s' % message.text, reply_markup=reply_markup)
    logger.info('Forwarding MSG COPY')
    for retry in range(3):
        logger.info(f'SENDING_MSG \tRETRY: {retry}')
        try:
           #nm = message.forward(MAIN_TCHANNEL)
           #logger.warning('------------')
           #logger.warning(nm)
           #mm = app.edit_message_reply_markup(chat_id=nm.chat.id, message_id=nm.message_id, reply_markup=reply_markup)

           action = message.text.replace('.', '').split(' ')[-6]
           new_action = f'`{action}`'
           new_text = message.text.replace(action, new_action)
           logger.info(f'ACTION {action} | {new_action}')
           if action in ('masterdeck', 'pitch', 'çrossfade'):
               message.text.replace(action, f'`{action}`')
           #new_action = f'```{new_action}```'
           #new_text = message.text.split(' ')[-2]
           #new_text += f' {new_action}'
           
           nm = app.send_message(
                text = f'[TRACK ID]:👌 {new_text}',
                chat_id = MAIN_TCHANNEL,
                reply_markup = reply_markup,
                disable_notification = True
                )

           break
        except FloodWait as e:
            logger.info(e)
            logger.info(f'FLOOD_WAIT {e.x}') 
            time.sleep(e.x+5)  # Wait "x" seconds before continuing


    #logger.info('-------- NEW MM M --------')
    #logger.info(nm)
    nh = { 'chat_id': nm.chat.id,
            'message_id': nm.message_id,
            'message_text': nm.text,
            'lastModified': datetime.now()
        }
    object_id = db.history.insert_one(nh).inserted_id
    logger.info(f'INSERT -> {object_id}')
    logger.info(f'{nh}')
    clear_history(app, message)
    app.send_chat_action(message.chat.id, "upload_audio")

    #message.forward("madmike0", message.text)
@app.on_message(filters.chat(POLIGON_TCHANNEL) & filters.regex('Now playing'), group=1)
def poligon(app, message):
    app.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id, reply_markup=reply_markup)
    logger.info('New POLIGON_AutoDJ Message')
 
@app.on_message(filters.command(["0x01"]))
def echo(app, message):
    logger.info('0x01 INVOKED')
    message.reply_text(message.text)

@app.on_message(filters.private & ~is_admin, group=4)
def private_message(app, message):
    logger.info(message)
    message.forward(LOG_TCHANNEL, message.text)
    #message.forward(LOG_TCHANNEL, message.text, disable_notification=True)

@app.on_message(filters.private & filters.regex(re_votes_combined), group=1)
#@app.on_message(filters.regex(emoji.KEYCAP_DIGIT_TWO))
def privvote(app, message):
    #logger.warning(message)
    message.reply_text(f'Vote recevied {message.text} / {VOTE_VALUES_MAP[message.text]}!')

@app.on_message(group=3)
def metric_counter(app, message):
    #logger.info(message)
    #message.forward("madmike0", message.text)
    metrics['processed'] += 1

def getmedal(x):#
    medals = { 1: '🏆',
            2: '🥇',
            3: '🥈',
            4: '🥉',
            }
    return medals[x] if x <= 4 else '🎵'

def getranking(days=99999):
    names = list(db.usernames.find({}))
    #print(names)
    namesflat = {}
    for item in names:
        try:
           namesflat[item['_id']] = item['name']
        except Exception as e:
            #logger.info(item)
            #logger.info(item['_id'])
            d = db.history.delete_many( {'message_id': item['_id']})
    #print(namesflat)

    ranking = []
    pipeline = [  { "$match": { "time": { "$gt": datetime.timestamp(datetime.now() + timedelta(days=-days)) },"user_id": { "$gte": 1} }}, { "$group": {"_id": "$user_id", "VoteCount": {"$sum": 1}, "TotalSum": {"$sum": "$rating"}} },{ "$sort":{"VoteCount":-1}}, { "$limit" : 10000 }]
 
    #pipeline = [  { "$match": { "time": { "$gt": datetime.timestamp(datetime.now() + timedelta(days=-days)) },"user_id": { "$gte": 1}, "chat_id": -1001163186712 }}, { "$group": {"_id": {"user_id":"$user_id", "user_name":"$user_name", "first_name":"$first_name", "last_name":"$last_name"}, "VoteCount": {"$sum": 1}, "TotalSum": {"$sum": "$rating"}} },{ "$sort":{"VoteCount":-1}}, { "$limit" : 10000 }]
    i = 1
    users = [ x for x in db.rotracks.aggregate(pipeline) ]
    #logger.info(users[:2])
    #logger.info(len(users))
    #print(namesflat)
    for user in users:
        #print(user)
        #logger.info(f'Processing {user}')
        #logger.info(user['_id'])
        #logger.error(a)
        #print(user, user.keys())
        if 'rank' not in user.keys():
            user['rank'] = i
            user['medal'] = getmedal(i)
            user['name'] = namesflat[user['_id']] if user['_id'] in namesflat.keys() else user['_id'] #'Unknown'
            user['VoteCount'] = user['VoteCount']
            user['TotalSum'] = user['TotalSum']
            user['AvgRating']= user['TotalSum'] / user['VoteCount']
        else:
            print(user)
        i += 1
        #logger.info(rank)
        ranking.append(user)
        #print(user, user.keys())
    print(ranking)
    return ranking

def rankingformat(userlist, lastdays=9999):
    logger.info('RANKING')
    lastdays_text = 'All' if int(lastdays) >= 999 else lastdays
    text = f'❯❯❯ Top {lastdays_text} day(s) Diggers ❮❮❮\n'
    text += f'🔝 `VoteCount TotalSum AvgRating`\n'
    print(userlist)
    for user in userlist:
        print(user)
        #logger.error(user)
        #if not user['name'].startswith('@'):
        #    user['name'] = f'@user["name"]'
        if user['name'] == '@None':
            user['name'] = user['_id']
        sender_name = MENTION.format(user['name'], user['_id'])
        text += f'{user["medal"]} `{user["VoteCount"]} {user["TotalSum"]} {user["AvgRating"]:.1f}` {sender_name}\n'
    text += '\n▶️ Played by @ROminimal_club - Track Discovery for DJs'
    logger.info(text)
    return text

def check_sender(message):
    try:
        sender = {}
        if message.from_user:
            sender['username'] = message.from_user.username
            sender['id'] = message.from_user.id
            sender['first_name'] = message.from_user.first_name
            sender['last_name'] = message.from_user.last_name
            sender['type'] = 'User'
            return sender
        elif message.sender_chat:
            sender['username'] = message.sender_chat.title
            sender['id'] = message.sender_chat.id
            sender['first_name'] = message.sender_chat.title
            sender['last_name'] = message.sender_chat.type
            sender['type'] = 'Chat'
            return sender
        else:
            return None
        #logger.info(message)
    except Exception as e:
        logger.warning('No Sender Found!')
        logger.warning(e)

@app.on_message(filters.command(["top"]), group=2)
async def echo(app, message):
    #logger.info(message)
    #db.rotracks.find({})
    #return db.rotracks.find({},{'chat_id': chat_id, })
    sender = check_sender(message)
    if sender['username'] != None and sender['username'] != '@None':
        sender['username'] = f"@{sender['username']}"
    sender_name = sender['username'] or sender['first_name'] or sender['last_name'] or sender['id'] or "Unknown"
    logger.info(f"<{sender_name}> Stats Invoked")

    #try:
    #r = db.voodoo.count_documents({"user_id":sender['id']}) if MONGO_CON else 0
    try:
        lastdays = int(message.command[1])
    except IndexError:
        lastdays = 9999
    #sender_id = check_sender(message)['id']
    logger.info(f'Using last days: {lastdays}')
    chat_id = -1001163186712 #message.chat.id
    ranking = getranking(lastdays)
    #r = db.mediahistory.count_documents({"sender_id":sender_id, "chat_id":chat_id}) if MONGO_CON else 0
    #await message.reply_text(f"👌 You {sender_name} have contributed [**{r}**] fine uploads for {chat_id}♥️🎶")
    if ranking != None and len(ranking) > 0:
        reply = rankingformat(ranking[:10], lastdays)
        #reply = "Got it"
    else:
        reply = f'Nothing found for chat_id: {chat_id}'
    await message.reply_text(reply)
    #except Exception as e:
    #    logger.warning(e)
#@app.on_message(filters.command(["status", "status@xFadeBot"]) & is_admin, group=1)
#def status(app, message):
#    s_time = timer()
#    cpufreq = psutil.cpu_freq()
#    svmem = psutil.virtual_memory()
#
#    cpusage = []
#    c = []
#    for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
#        cpusage.append(f"Core {i}: {percentage}%")
#    #logger.info(message)
#    #for collection in db.list_collection_names():
#    for collection in ['voodoo', 'rotracks', 'mediahistory']:
#        c.append((collection, db[collection].count_documents({})))
#
#    r_time = (timer() -  s_time)
#    r_time =  float("{:.2f}".format(r_time))
#    message.reply_text(f"""
#Db Collections: {c} 
#Bot Started: {pt}
#Bot Processed: {metrics["processed"]} 
#Os: {uname.system} {uname.node} {uname.release} {uname.version} {uname.machine}
#Os Running as: {uid}
#Os Load: {os.getloadavg()}
#Os Physical Cores: {psutil.cpu_count(logical=False)}
#Os Total Cores: {psutil.cpu_count(logical=True)}
#Os Total CPU Usage: {psutil.cpu_percent()}%
#Os Cpu Core Usage: {cpusage}
#Os Mem Total: {get_size(svmem.total)}
#Os Mem Available: {get_size(svmem.available)}
#Os Mem Used: {get_size(svmem.used)}
#Os Mem Percentage: {svmem.percent}%
#Generated in: {r_time}s
#"""
#    )
# 
@app.on_message(filters.command(["status", "status@xFadeBot"]) & ~filters.me, group=2)
def status(app, message):
    s_time = timer()
    cpufreq = psutil.cpu_freq()
    svmem = psutil.virtual_memory()

    cpusage = []
    c = []
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        cpusage.append(f"Core {i}: {percentage}%")
    #for collection in db.list_collection_names():
    for collection in ['voodoo', 'mediahistory']:
        if  mongo_con:
            c.append((collection, db[collection].count_documents({}))) 

    r_time = (timer() -  s_time)
    r_time =  float("{:.2f}".format(r_time))
    pipeline = [ { "$group": {"_id": "null", "TotalCount": {"$sum": "$file_size"}} } ]

    for collection in ['voodoo', 'rotracks', 'mediahistory']:
            c.append((collection, db[collection].count_documents({})))

    lavg = "%.1f, %.1f, %.1f" % os.getloadavg()
    message.reply_text(f"""
```Db Collections: {c}
Started: {pt}
Processed: {metrics["processed"]}
Load: {lavg}
Cpu: {psutil.cpu_percent()}%
Mem: {svmem.percent}%
Took: {r_time} s```
"""
    )
#
#@app.on_message(filters.command(["status", "status@xFadeBot"]) & ~is_admin, group=2)
#def status(app, message):
#    s_time = timer()
#    cpufreq = psutil.cpu_freq()
#    svmem = psutil.virtual_memory()
#
#    cpusage = []
#    c = []
#    for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
#        cpusage.append(f"Core {i}: {percentage}%")
#    #logger.info(message)
#    for collection in db.list_collection_names():
#        c.append((collection, db[collection].count_documents({})))
#
#    r_time = (timer() -  s_time)
#    message.reply_text(f"""
#Db Collections: {c} 
#Bot Started: {pt}
#Bot Processed: {metrics["processed"]} 
#Os: {uname.system} {uname.node} {uname.release} {uname.version} {uname.machine}
#Os Load: {os.getloadavg()}
#Os Total Cores: {psutil.cpu_count(logical=True)}
#Os Total CPU Usage: {psutil.cpu_percent()}%
#Os Mem Total: {get_size(svmem.total)}
#Os Mem Available: {get_size(svmem.available)}
#Os Mem Percentage: {svmem.percent}%
#Generated in: {r_time} s
#"""
#    )
 
#def echo(app, message):
#    print(message)
#    message.forward("madmike0", message.text)

#ALLOWED_COMMAND=['stats']
#@app.on_message(filters.private & ~filters.command(), group=2)
#def catch_privs(app, message):
#    logger.info('Other priv message')
#    message.forward("madmike0", message.text)
#    message.reply_text(f'I did not understand that. Use /help')
def logusername2db(message):
    #try:
    #logger.info(message)
    sender = check_sender(message)
    logger.info(sender)
    from_sender = sender['id']
    #if sender['username'] != None:
    #    sender['username'] = f"@{sender['username']}"
    logger.info(sender)
    db_insert_start = timer()
    object_id = db.usernames.replace_one(
            #{'message_id':message.message_id, '_id': int(message.chat.id)}, {'message_id':message.message_id, '_id': int(message.chat.id)},upsert=True).modified_count if MONGO_CON else None
            {'_id': int(from_sender)}, {'name': check_username(message), '_id': int(from_sender)},upsert=True).modified_count if mongo_con else None

    db_insert_end = timer()
    db_insert_time = (db_insert_end - db_insert_start) * 1000 #ms
    logger.info(f'DB Insert [ {sender} {check_username(message)} ] -> {db_insert_time}ms')
    #loigger.info(f'[{db_insert_time}ms / {object_id}] DB Insert {message.chat.title} / {media.file_name} {media.mime_type} {media.file_size}')
    #except Exception as e:
    #    logger.warning('Could not write username to a db')
    #    logger.warning(e)
    #    logger.warning(message)

def check_sender(message):
    try:
        sender = {}
        if message.from_user:
            sender['username'] = message.from_user.username
            sender['id'] = message.from_user.id
            sender['first_name'] = message.from_user.first_name
            sender['last_name'] = message.from_user.last_name
            return sender
        elif message.sender_chat:
            sender['username'] = message.sender_chat.title
            sender['id'] = message.sender_chat.id
            sender['first_name'] = 'Chat'
            sender['last_name'] = message.sender_chat.type
            return sender
        else:
            return None
        logger.info('-- SENDER --')
        logger.info(message)
        logger.info(sender)
        logger.info('-- EOF SENDER --')
    except Exception as e:
        logger.warning('No Sender Found!')
        logger.warning(e)

def check_username(message):
    try:
        if message.from_user:
            return message.from_user.username or message.from_user.first_name or message.from_user.last_name or "Unknown"
        elif message.sender_chat:
            return message.sender_chat.title
        elif message.forward_sender_name:
            return message.forward_sender_name
        else:
            return None
    except Exception as e:
        logger.warining('No User Found!')
        logger.warning(e)

def log_track_vote(callback_query, nowpl, station = 'ROminimal.club'):
    db_insert_start = timer()
    object_id = db.rotracks.insert_one({
        'time': callback_query.message.date,
        #'message': callback_query.message.text,
        'rating': int(callback_query.data),
        'user_name': callback_query.from_user.username,
        'first_name': callback_query.from_user.first_name,
        'last_name': callback_query.from_user.last_name,
        'track_id': nowpl,
        'user_id': callback_query.from_user.id,
        'chat_id': callback_query.message.chat.id,
        'station': station,
        'lastModified': datetime.now()
        }).inserted_id
    db_insert_end = timer()
    db_insert_time = (db_insert_end - db_insert_start) * 1000 #ms
    logger.info(f'[DB] Insert Rating ({callback_query.data}) for "{nowpl}" ({object_id} / {db_insert_time} ms)')

async def get_api_nowplaying(callback_query, station, rid=None):
    params = f'/{station}/nowplaying?rid={rid}' if rid != None else f'/{station}/nowplaying'
    logger.info(f'Using params: {params}')
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(PING_NOWPLAYING_WEBHOOK + params) as resp:
                now_playing = await resp.json() #(content_type='text/html')
                #print(await resp.json())
                #data = await resp.read()
                #now_playing = json.loads(data)
                logger.info(resp.status)
                logger.info(now_playing)
                logger.info(type(now_playing))
                nowpl = now_playing['result']['nowplaying']
                prev_track = now_playing['result']['prev_track'] or None
                next_track = now_playing['result']['next_track'] or None
                logger.info(f'NOW_PLAYING: {nowpl}')
                log_track_vote(callback_query, nowpl, station)
                return nowpl, prev_track, next_track
                #await callback_query.answer(f"👍 You voted [{callback_query.data}] at {station} for:\n🎵 {now_playing['result']['nowplaying']}", show_alert=True)
        except Exception as e:
            logger.error('Could not get  PING_NOWPLAYING_WEBHOOK')
            logger.error(e)


@app.on_message(filters.new_chat_members | filters.left_chat_member)
def service_members(app, message):
    logger.info('Service Joiners / Leavers')
    #logger.info(message)
    #message.reply_text(f'Your stats {message.from_user.username} are ({r}) ❤️')

@app.on_message(filters.command(["stats", "stats@xFadeBot"]) & ~filters.me, group=2)
def echo(app, message):
    sender = check_sender(message)
    if sender['username']:
        sender['username'] = f"@{sender['username']}"
    sender_name = sender['username'] or sender['first_name'] or sender['last_name'] or sender['id'] or "Unknown"
    logger.info(f'Stats invoked from {sender_name}')
    #logger.info(message)
    r = db.rotracks.count_documents({"user_id":message.from_user.id})
    message.reply_text(f'Your stats {sender_name} are [**{r}**] fine votes 🎶 \n\n📊 [Here is your always up to date tracklist, share it with your friends!](https://my.rominimal.club/charts/{sender["id"]}) \n👉 Like What You Hear? ☕️ [Buy Me a Coffee](https://www.buymeacoffee.com/rominimal) ♥️', disable_web_page_preview=True)
    #message.edit_text('0x01 I was here editer hi ho: "%s"' % message.text)

@app.on_message(~filters.private & filters.command(["export", "mycharts"]), group=1)
async def exportredirect(app, message):
    await app.send_chat_action(message.chat.id, "upload_document")
    await message.reply_text(f'📊 [Your always up to date tracklist](https://my.rominimal.club/charts/{message.from_user.id}). Share it with your friends!')
    #await message.reply_text('Please talk to me on priv to get your paylist 👉  https://t.me/xFadebot')
 
@app.on_message(filters.private & filters.command(["export"]) & ~filters.me, group=1)
async def export(app, message):
   # await message.reply_chat_action(enums.ChatAction.UPLOAD_DOCUMENT)
    await app.send_chat_action(message.chat.id, "upload_document")
    sender = check_sender(message)
    if sender['username']:
        sender['username'] = f"@{sender['username']}"
    sender_name = sender['username'] or sender['first_name'] or sender['last_name'] or sender['id'] or "Unknown"
    logger.info(f'Export invoked from {sender_name}')
    #logger.info(message)
    #r = db.rotracks.count_documents({"user_id":message.from_user.id})
    sender = check_sender(message)
    if sender['username'] != None and sender['username'] != '@None':
        sender['username'] = f"@{sender['username']}"
    sender_name = sender['username'] or sender['first_name'] or sender['last_name'] or sender['id'] or "Unknown"
    #sender_name = f'{sender["username"]} {sender["first_name"]} {sender["last_name"]}'

    r = list(db.rotracks.find({"user_id":message.from_user.id }, {"rating": 1, "track_id": 1, "_id": 0}))
    #for p in r:
    #    if not 'station' in p.keys():
    #        p['station'] = 'Track Selector'

    #r = [ o['url'] = f'<a href="{o["track_id"]}">{o["track_id"]}</a>' for o in r ]
    await message.reply_text(f'I have found [{len(r)}] results for user_id: {message.from_user.id}.\n\n 👉 Here is your always up to date tracklist, share it with your friends! https://my.rominimal.club/charts/{sender["id"]}')
    sio = io.StringIO(dumps(r))
    bio = io.BytesIO(sio.read().encode('utf8'))
    bio.name = 'just_a_stream'
    #print(bio.read())  # prints b'wello horld'
    # Do not send json for now
    await app.send_document(message.chat.id, bio, caption='Your ROminimal.club track list as take-away!\n\n 📂 To convert given json file to searchable table use this https://www.convertjson.com/json-to-html-table.htm or Excel', file_name=f'{message.from_user.id}-rominimal.club-playlist.json', reply_to_message_id=message.message_id)

    #sio = io.StringIO(json2html.convert(json = dumps(r)))
    #bio = io.BytesIO(sio.read().encode('utf8'))
    #bio.name = 'just_a_HTML_stream'
 
    #await app.send_document(message.chat.id, bio, caption='Your ROminimal.club track list!\n\n 📂 File with HTML.', file_name=f'{message.from_user.id}-rominimal.club-playlist.html', reply_to_message_id=message.message_id)
    ts = datetime.utcnow().replace(tzinfo=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    html_out = f'<html><head></head><meta charset="UTF-8"></meta>'
    html_out += '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/normalize/8.0.1/normalize.css"> <!-- Milligram CSS --> <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/milligram/1.4.1/milligram.css">'    
    html_out += '<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.12.1/css/common.css"><script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.12.1/js/jquery.js"></script>'
    html_out += '<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.12.1/css/jquery.dataTables.css"><script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.12.1/js/jquery.dataTables.js"></script><script type="text/javascript">$(document).ready( function () { $("#track_table").DataTable(); } );</script>'
    html_out += '<style>h1, h2, h3, h4, h5, h6 { font-weight: 300; letter-spacing: -.1rem; margin-bottom: 1rem; margin-top: 0; } table, th, td {font-family: monospace;}</style>'
    html_out += f'<body style="color: blue; background: linear-gradient(-180deg, rgba(255,255,255,0.50) 0%, rgba(0,0,0,0.50) 100%);"><div class="container"><div class="row"><div class="column"><h1><a href="https://t.me/ROminimal_club" target="_blank">ROminimal.club Track Discovery for DJs</h1><h6 style="font-family: monospace;">Telegram user id: {sender_name}. Generated at: {ts}</h6></a></div></div>'
    html_out += '<div class="row"><div class="column"><img src="https://rominimal.club/images/head-logo.png" width="160px"></img><a href="https://www.buymeacoffee.com/rominimal" target="_blank"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me Coffee&amp;emoji=&amp;slug=rominimal&amp;button_colour=FF5F5F&amp;font_colour=ffffff&amp;font_family=Cookie&amp;outline_colour=000000&amp;coffee_colour=FFDD00"></a></div><div class="column column-50 column-offset-25"><p style="margin-bottom: 5px; padding: 1px 1em 0px 1em;background: #2c3652;border-radius:15px 15px 15px 15px;"><iframe src="https://r2.rominimal.club/public/rominimal.club/embed" frameborder="0" allowtransparency="true" style="width: 100%; min-height: 150px; border: 0;margin-top: 5px;margin-bottom:5px;padding-top: 8px;"></iframe><a href="https://t.me/ROminimal_club" target="_blank"><h5 style=" text-align: center; ">❯❯❯ GET ROMINIMAL TRACK ID ❮❮❮</h5></a></p></div></div>'

    #html_out += '<div class="row"><div class="column"><a href="https://www.buymeacoffee.com/rominimal" target="_blank"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me Coffee&amp;emoji=&amp;slug=rominimal&amp;button_colour=FF5F5F&amp;font_colour=ffffff&amp;font_family=Cookie&amp;outline_colour=000000&amp;coffee_colour=FFDD00"></a></div></div>'

    html_out += '<div class="row"><div class="column"><h4 style=" text-align: center; "><a href="https://t.me/ROminimal_club" target="_blank">🎧 Discovered Track Names 🎵</a></h4>'
    html_out += json2html.convert(table_attributes='id="track_table", class="display cell-border"', json = dumps(r))
    html_out += f'</div></div></div></body></html>'
    sio = io.StringIO(html_out)
    bio = io.BytesIO(sio.read().encode('utf8'))
    bio.name = 'just_a_HTML_stream'
    # Do not send file for now
    #await app.send_document(message.chat.id, bio, caption='📊 Your ROminimal.club track list inside!\n\n 📂 Just open this file with any browser. If you have internet access it should render searchable and sortable document of all your track IDs. Like what you hear?', file_name=f'{message.from_user.id}-rominimal.club-playlist.html', reply_to_message_id=message.message_id)


    #logger.info(json2html.convert(json = dumps(r)))
    #await message.reply_text(f'Your stats {sender_name} are [**{r}**] fine votes 🎶\n👉 Like What You Hear? ☕️ [Buy Me a Coffee](https://www.buymeacoffee.com/rominimal) ♥️', disable_web_page_preview=True)
    #message.edit_text('0x01 I was here editer hi ho: "%s"' % message.text)


@app.on_callback_query()
async def callback_answer(app, callback_query):
    a_s_time = timer()
    FLIST='/data/mediafiles/pyCrossfade/flist.playing.txt'
    #logger.info(callback_query.message.text)
    #logger.info(callback_query)
    #print('---------------')
    #print(callback_query.message.text)
    update_votes = await app.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=callback_query.message.text+' '+emoji.STAR_STRUCK, reply_markup=reply_markup)
    logger.info(callback_query.message.text)
    track_info = re.search('.*Now playing at ([aA-zZ\._\W]+)?: (.*([0-9]+)\/([0-9]+)\/([0-9]+)\/([0-9]+) (masterdeck|pitch|crossfade|mixout)).*', callback_query.message.text)
    if track_info:
        station, trackmeta, trackno, number, maxtrack, timestamp, action = track_info.groups()
    else:
        logger.warning('Not valid track-rate message, ignoring.')
        await app.send_message("madmike0", f'NO_REGEX_TRACK_MESSAGE: while parsing: `{callback_query.message.text}`')
        return

    rid = hashlib.md5(f'{trackmeta}'.encode('utf-8')).hexdigest()
    #hashlib.md5('▶ 6/16/19/1544 masterdeck'.encode('utf-8')).hexdigest(
    #logger.info(track_info.groups())
    logger.info(f'META: "{trackmeta}" RID: {rid}')
    logger.info('------ EOF ---------')
    station = station.replace(' ', '_')
    #station = station.replace(' ', '_')

    logger.info(f'DETECTED: {station} {trackno} {number} {maxtrack} {timestamp} {action}')
    #dev = re.search('.*DEV Now playing.*', callback_query.message.text)

    nowpl = "<404 not found>"

    if station in ('dev_club', 'DEV_CLUB', 'ROminimal.club'):
        logger.warning('==== DoktoKV Lookupe ===')
        nowpl, prev_track, next_track = await get_api_nowplaying(callback_query, station, rid)
        logger.info(f'CURRENT_NOW_PLAYING: {nowpl} | PREV_TRACK: {prev_track} | NEXT_TRACK: {next_track}')
        logger.info(f'DONE NOW_PLAYING Webhook: {PING_NOWPLAYING_WEBHOOK}/{station}/nowplaying')
    else: # =============== OBSOLETE BELOW ======================
        logger.info(f'New Track Meta: {trackno}-{number}-{maxtrack}-{action}')
        #with open(FLIST,"r") as file:
        #        flist = [ line.decode() for line in readline0.readline0(file_=file, separator=b'\0')]
        flist = []
        with open(FLIST,"r") as file:
        # For some reason after container rebuild / upgrade - this returns wrong order of the file lines
        #    flist = [ line.decode() for line in readline0.readline0(file_=file, separator=b'\0')]
        #    print(flist)
             fcontent = file.read()
             print(fcontent)
             flist = [ line for line in fcontent.split('\0') ]
        logger.info(flist)
        #nowpl = flist[notrack]
        #logger.info(flist)
        #logger.info(len(flist))
        trackno = int(trackno)
        nowpl = Path(flist[trackno-1]).stem
        logger.info(f'Found track: {trackno} / {nowpl}')
        user_info = await app.get_users(callback_query.from_user.id)
        logger.info(user_info)
        logger.info(f'<{callback_query.from_user.username}/{callback_query.from_user.id}> Voted {trackno}/{maxtrack} ({callback_query.data}) -- {nowpl}')
        db_insert_start = timer()
        log_track_vote(callback_query, nowpl)
        #logger.info(callback_query)
        logusername2db(callback_query)
        #print(f'==> {nowpl}')
    #else:
    #    logger.info('===> DID NOT MATCH')
    #    logger.info(r)
    #client.send_message(callback_query.from_user.username, f"You voted '{callback_query.data}' for: {nowpl}")
    notice = ''
    if int(callback_query.data) == -1:
        notice = f'\n\n{emoji.RED_EXCLAMATION_MARK} Your vote to remove this track has been received'
 
    await app.send_message(LOG_TCHANNEL, f"{callback_query.from_user.first_name} {callback_query.from_user.last_name} @{callback_query.from_user.username} ({callback_query.from_user.id}) #voted ({callback_query.data}) #v{callback_query.data} for '{nowpl}'", disable_notification=True)
    await app.send_message(LOG_PUBLIC_TCHANNEL, f"#voted ({callback_query.data}) #v{callback_query.data} at {station} for '{nowpl}'", disable_notification=True)

    INFO_SNIPPETS = ['PS: Did you know you can promote music with us?']
    THANK_SNIPPETS = ['Great Job!' ,'Nice find!', 'Keep digging!', 'Real gem!', 'I like pizza better.', 'Can we not talk about it?', 'Secret weapon!', 'Bomb!', 'Real banger mate!', 'Proper mate!', "That's proper!", 'Proper init?', 'Bruv!', 'Ridicilous!', 'Say what?', "Not again?", "You joking?", 'Having bad day?', 'Having good day?', 'Nice one brother!',  'Nice one!'] 
    
    #await callback_query.answer(f"👌 {callback_query.data} - {random.choice(THANK_SNIPPETS)}\n🎵 {nowpl}{notice}", show_alert=True)
    await callback_query.answer(f"👌 Voted {callback_query.data} for:\n🎵 {nowpl}{notice}\n\n{emoji.LAST_TRACK_BUTTON} {prev_track}\n{emoji.NEXT_TRACK_BUTTON} {next_track}", show_alert=True)

    if len(get_logs_history(callback_query.from_user.id)) > 0:
       snowpl = f'site:soundcloud.com {nowpl}'

       await app.send_message(callback_query.from_user.id, f"👍 #v{callback_query.data} for 🎵 `{nowpl}` at {station}", disable_notification=False,
                reply_markup =  InlineKeyboardMarkup(
                [
                   [  # First row
                        InlineKeyboardButton(
                            "🔉 Soundcloud",
                            url = f'https://www.google.com/search?q={urllib.parse.quote_plus(bytes(snowpl, encoding="utf8"))}'
                        ),
                        InlineKeyboardButton(
                            "🔎 Google",
                            url = f'https://www.google.com/search?q={urllib.parse.quote_plus(bytes(nowpl, encoding="utf8"))}'
                        ),
                  ]
               ]
            )
        )
    a_e_time = timer()
    r_time = (a_e_time - a_s_time) * 1000
    logger.info(f'Callback {r_time} ms')

app.run()  # Automatically start() and idle()
