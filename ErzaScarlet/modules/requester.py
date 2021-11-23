from telethon.tl.types import ChannelParticipantsAdmins
from telethon.utils import get_display_name
from telethon import *
from pymongo import MongoClient
from ErzaScarlet import API_ID, API_HASH, TOKEN, OWNER , telethn as tbot
from ErzaScarlet.events import register
from ErzaScarlet.modules.helper_funcs.requestModule import *
import logging
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

IN_GRP = -1001415010098
bot = asst = tbot
REQ_GO =  -1001509437008
on = tbot.on
auth = OWNER 

mongoDbSTR = "" # Connnection String of MongoDB

'''Connecting To Database'''
mongo_client = MongoClient(mongoDbSTR)
db_bot = mongo_client['RequestTrackerBot']
collection_ID = db_bot['channelGroupID']
query = {
    "groupID" : [
        "channelID",
        "userID"
    ]
}
if not collection_ID.find_one(query):
    collection_ID.insert_one(query)


@tbot.on(events.NewMessage(chats=IN_GRP))
async def filter_requests(event):
    if event.fwd_from:
        return
    if "#request" in event.text:
      #  await asst.send_message(IN_GRP,
        #                    f"**We are not taking any requests for some days.\n\nSorry for inconvenience 😶**",
        #                    buttons=[
        #                        [Button.url("💠 Channel 💠", url="https://t.me/AN1ME_HUB"),
        #                        Button.url("⚜️ Group ⚜️", url="https://t.me/an1me_hub_discussion")],
        #                        [Button.url("📜 Index 📜", url="https://t.me/index_animehub"),
        #                        Button.url("🎬 Movies 🎬", url="https://t.me/AN1ME_HUB_MOVIES")],
        #                        [Button.url("💌 AMV 💌", url="https://t.me/AnimeHub_Amv")]])
        if (event.reply_to_msg_id):
            msg = (await event.get_reply_message()).message
        else:
            msg = event.text
        try:
            global user
            sender = event.sender
            if sender.bot:
                return
            if not sender.username:
                user = f"[{get_display_name(sender)}](tg://user?id={event.sender_id})"
            else:
                user = "@" + str(sender.username)
        except BaseException:
            user = f"[User](tg://user?id={event.sender_id})"
        chat_id = (str(event.chat_id)).replace("-100", "")
        username = ((await bot.get_entity(REQ_GO)).username)
        hel_ = "#request"
        if hel_ in msg:
            global anim
            anim = msg.replace(hel_, "")
        x = await asst.send_message(REQ_GO,
                                f"**Request By {user}**\n\n{msg}",
                                buttons=[
                                    [Button.url("Requested Message", url=f"https://t.me/c/{chat_id}/{event.message.id}")],
                                    [Button.inline("🚫 Reject", data="reqdelete"),
                                    Button.inline("Done ✅", data="isdone")],
                                    [Button.inline("⚠️ Unavailable ⚠️", data="unavl")]])
        btns = [
            [Button.url("⏳ Request Status ⏳", url=f"https://t.me/{username}/{x.id}")],
            [Button.url("💠 Channel 💠", url="https://t.me/indianimei"),
            Button.url("⚜️ Group ⚜️", url="https://t.me/indianimein")],
            [Button.url("📜 Index 📜", url="https://t.me/IndianimeNetwork"),
            Button.url("Base", url="https://t.me/indianimebase")],
            [Button.url("Ongoing Anime", url="https://t.me/Ongoing_Anime1")]]
        await event.reply(f"**👋 Hello {user} !!**\n\n📍 Your Request for  `{anim}`  has been submitted to the admins.\n\n🚀 Your Request Will Be Uploaded In 48hours or less.\n📌 Please Note that Admins might be busy. So, this may take more time. \n\n**👇 See Your Request Status Here 👇**", buttons=btns)
        if not auth:
            async for x in bot.iter_participants("@indianimein", filter=ChannelParticipantsAdmins):
                auth.append(x.id)

# For Adding group & channel ID in database for #request feature
@tbot.on(events.NewMessage(pattern = "/add"))
async def addIDHandler(event):
    msg = event.message.text.split(" ")
    if len(msg) == 3:
        _, groupID, channelID = msg
        try:
            int(groupID)
            int(channelID)
        except ValueError:
            await event.respond(
                "<b>Group ID & Channel ID should be integer type😒.</b>",
                parse_mode = "html"
            )
        else:
            document = collection_ID.find_one(query)
            try:
                document[groupID]
            except KeyError:
                if not idExtractor(channelID, document):
                    document[groupID] = [channelID, event.sender_id]
                    collection_ID.update_one(
                        query,
                        {
                            "$set" : document
                        }
                    )
                    await event.respond(
                        "<b>Your Group and Channel has now been added SuccessFully🥳.</b>",
                        parse_mode = "html"
                    )
                else:
                    await event.respond(
                        "<b>Your Channel ID already Added🤪.</b>",
                        parse_mode = "html"
                    )
            else:
                await event.respond(
                    "<b>Your Group ID already Added🤪.</b>",
                    parse_mode = "html"
                )
    else:
        await event.respond(
            "<b>Invalid Format😒\
            \nSend Group ID & Channel ID in this format <code>/add GroupID ChannelID</code>.</b>",
            parse_mode = "html"
        )

# For Removing group & channel ID from database
@tbot.on(events.NewMessage(pattern = "/remove"))
async def removeIDHandler(event):
    msg = event.message.text.split(" ")
    if len(msg) == 2:
        _, groupID = msg
        document = collection_ID.find_one(query)
        for key in document:
            if key == groupID:
                if document[key][1] == event.sender_id:
                    del document[key]
                    collection_ID.update_one(
                        query,
                        {
                            "$set" : document
                            }
                    )
                    await event.respond(
                        "<b>Your Channel ID & Group ID has now been Deleted😢 from our Database.\
                        \nYou can add them again by using <code>/add GroupID ChannelID</code>.</b>",
                        parse_mode = "html"
                    )
                    break
                else:
                    await event.respond(
                        "<b>😒You are not the one who added this Channel ID & Group ID.</b>",
                        parse_mode = "html"
                    )
        else:
            await event.respond(
                "<b>Given Group ID is not found in our Database🤔.</b>",
                parse_mode = "html"
            )
    else:
        await event.respond(
            "<b>Invalid Command😒\
            \nUse <code>/remove GroupID</code></b>.",
            parse_mode = "html"
        )

@tbot.on(events.callbackquery.CallbackQuery(data="reqdelete"))
async def delete_message(event):
    if not auth:
        async for x in bot.iter_participants("@indianimein", filter=ChannelParticipantsAdmins):
             auth.append(x.id)
    if event.sender_id in auth:
        x = await bot.get_messages(event.chat_id, ids=event.message_id)
        xx = x.raw_text
        btns = [
            [Button.url("💠 Channel 💠", url="https://t.me/indianimei"),
            Button.url("⚜️ Group ⚜️", url="https://t.me/indianimein")],
            [Button.url("📜 Index 📜", url="https://t.me/IndianimeNetwork"),
            Button.url("Base", url="https://t.me/indianimebase")],
            [Button.url("Ongoing Anime", url="https://t.me/Ongoing_Anime1")]]
       
        await event.edit(f"**REJECTED**\n\n~~{xx}~~", buttons=[Button.inline("Request Rejected 🚫", data="ndone")])
        await tbot.send_message(-1001415010098, f"**⚠️ Request Rejected By Admin !!**\n\n~~{xx}~~", buttons=btns)
    else:
        await event.answer("Who TF are you? This is for admins only..", alert=True, cache_time=0)
        
@tbot.on(events.callbackquery.CallbackQuery(data="unavl"))
async def delete_message(event):
    if not auth:
        async for x in bot.iter_participants("@indianimein", filter=ChannelParticipantsAdmins):
             auth.append(x.id)
    if event.sender_id in auth:
        x = await bot.get_messages(event.chat_id, ids=event.message_id)
        xx = x.raw_text
        btns = [
            [Button.url("💠 Channel 💠", url="https://t.me/indianimei"),
            Button.url("⚜️ Group ⚜️", url="https://t.me/indianimein")],
            [Button.url("📜 Index 📜", url="https://t.me/IndianimeNetwork"),
            Button.url("Base", url="https://t.me/indianimebase")],
            [Button.url("Ongoing Anime", url="https://t.me/Ongoing_Anime1")]]
       
        await event.edit(f"**UNAVAILABLE**\n\n~~{xx}~~", buttons=[Button.inline("❗ Unavailable ❗", data="navl")])
        await tbot.send_message(-1001415010098, f"**⚠️ Request Unavailable ⚠️**\n\n~~{xx}~~", buttons=btns)
    else:
        await event.answer("Who TF are you? This is for admins only..", alert=True, cache_time=0)
        
        
@tbot.on(events.callbackquery.CallbackQuery(data="isdone"))
async def isdone(e):
    if not auth:
        async for x in bot.iter_participants("@indianimein", filter=ChannelParticipantsAdmins):
             auth.append(x.id)
    if e.sender_id in auth:
        x = await bot.get_messages(e.chat_id, ids=e.message_id)
        xx = x.raw_text
        btns = [
            [Button.url("💠 Channel 💠", url="https://t.me/indianimei"),
            Button.url("⚜️ Group ⚜️", url="https://t.me/indianimein")],
            [Button.url("📜 Index 📜", url="https://t.me/IndianimeNetwork"),
            Button.url("Base", url="https://t.me/indianimebase")],
            [Button.url("Ongoing Anime", url="https://t.me/Ongoing_Anime1")]]
       
        await e.edit(f"**COMPLETED**\n\n~~{xx}~~", buttons=[Button.inline("Request Completed ✅", data="donne")])
        await tbot.send_message(-1001415010098, f"**Request Completed**\n\n~~{xx}~~", buttons=btns)
    else:
        await e.answer("Who TF are you? This is for admins only..", alert=True, cache_time=0)
        
    
@tbot.on(events.callbackquery.CallbackQuery(data="donne"))
async def ans(e):
    await e.answer("This Request Is Completed... Checkout @indianimei 💖", alert=True, cache_time=0)
        
@tbot.on(events.callbackquery.CallbackQuery(data="navl"))
async def ans(e):
    await e.answer("This Request Is Marked Unavailable By Admins", alert=True, cache_time=0)
        
        
@tbot.on(events.callbackquery.CallbackQuery(data="ndone"))
async def ans(e):
    await e.answer("This Request is unavailable... Ask Admins in @indianimein for help. 💞", alert=True, cache_time=0)