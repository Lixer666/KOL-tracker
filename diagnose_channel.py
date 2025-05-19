from telethon import TelegramClient, events
import asyncio
import json
import re

# Дані Telegram
api_id = '21412253'
api_hash = '26a846f4cf5d1a873985b6b3a5fda7bf'
chat_id = 'gmgnsignals'  # Використовуйте username каналу

# Use persistent session file
session_file = '../session/gmgnsignals_sol_persistent'
client = TelegramClient(session_file, api_id, api_hash)

# Troubleshooting script
async def diagnose_channel():
    print(f"🔍 Diagnosing connection to {chat_id}...")
    
    # Connect to Telegram
    print("1️⃣ Attempting to connect to Telegram...")
    
    if not client.is_connected():
        await client.connect()
        print("   ✅ Connected to Telegram")
    else:
        print("   ✅ Already connected to Telegram")
    
    if not await client.is_user_authorized():
        print("   ❌ Not authorized - please run setup_session.py first")
        return
    
    print("   ✅ User is authorized")
    
    # Try to find the chat entity
    print(f"\n2️⃣ Looking up channel: {chat_id}")
    
    try:
        entity = await client.get_entity(chat_id)
        print(f"   ✅ Found channel: {entity.title if hasattr(entity, 'title') else chat_id}")
        print(f"   ℹ️ Channel type: {type(entity).__name__}")
        print(f"   ℹ️ Channel ID: {entity.id}")
    except Exception as e:
        print(f"   ❌ Error finding channel: {e}")
        print("   🔄 Trying alternative approaches to find the channel...")
        
        # Try alternative approaches
        try:
            # Try with @ prefix
            if not chat_id.startswith('@'):
                alt_chat_id = f"@{chat_id}"
                print(f"   🔄 Trying with @: {alt_chat_id}")
                alt_entity = await client.get_entity(alt_chat_id)
                print(f"   ✅ Found channel using @: {alt_entity.title if hasattr(alt_entity, 'title') else alt_chat_id}")
                entity = alt_entity
                chat_id = alt_chat_id
            else:
                raise Exception("Already has @ prefix")
        except:
            # Try getting dialogs and looking for the channel
            print("   🔄 Getting all dialogs to find channel...")
            dialogs = await client.get_dialogs()
            for d in dialogs:
                if hasattr(d.entity, 'username') and d.entity.username == chat_id.replace('@', ''):
                    print(f"   ✅ Found channel in dialogs: {d.name}")
                    entity = d.entity
                    break
            else:
                print(f"   ❌ Couldn't find channel in {len(dialogs)} dialogs")
                print("   📋 Available channels/groups:")
                for i, d in enumerate(dialogs[:10]):  # Show first 10 only
                    print(f"      {i+1}. {d.name} ({'channel' if hasattr(d.entity, 'broadcast') and d.entity.broadcast else 'chat/group'})")
                return
    
    # Try to access messages
    print(f"\n3️⃣ Accessing messages from: {chat_id}")
    
    try:
        messages = await client.get_messages(entity, limit=10)
        print(f"   ✅ Successfully retrieved {len(messages)} messages")
        
        if messages:
            # Check for KOL Buy messages
            kol_messages = []
            for msg in messages:
                if re.search(r'kol', msg.text, re.IGNORECASE) and re.search(r'buy', msg.text, re.IGNORECASE):
                    kol_messages.append(msg)
            
            print(f"   ℹ️ Found {len(kol_messages)} messages with 'KOL' and 'Buy' mentions")
            
            # Show a sample of each message
            print("\n📝 Recent messages preview:")
            for i, msg in enumerate(messages[:3]):
                preview = msg.text.replace('\n', ' ')[:100]
                print(f"   Message {i+1}: {preview}...")
        else:
            print("   ⚠️ No messages retrieved")
    except Exception as e:
        print(f"   ❌ Error retrieving messages: {e}")
    
    # Try to monitor for new messages
    print("\n4️⃣ Setting up message monitor for 30 seconds...")
    
    message_count = 0
    
    @client.on(events.NewMessage(chats=entity))
    async def message_listener(event):
        nonlocal message_count
        message_count += 1
        print(f"   📩 New message received: {event.message.text[:50]}...")
    
    print("   ✅ Message listener set up - waiting for 30 seconds")
    
    # Wait for messages
    await asyncio.sleep(30)
    
    print(f"   ℹ️ Received {message_count} new messages in 30 seconds")
    
    print("\n✅ Diagnosis complete!")

# Run the diagnostic function
with client:
    client.loop.run_until_complete(diagnose_channel())
