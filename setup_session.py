from telethon import TelegramClient

# Telegram credentials
api_id = '21412253'
api_hash = '26a846f4cf5d1a873985b6b3a5fda7bf'
chat_id = 'gmgnsignals'  # Channel username

# Create a persistent session file
session_file = '../session/gmgnsignals_sol_persistent'
client = TelegramClient(session_file, api_id, api_hash)

async def main():
    print("🔄 Connecting to Telegram...")
    await client.start()
    print("✅ Successfully authenticated and created session file!")
    
    print("\n🔍 Checking connection to target channel...")
    print(f"Channel ID: {chat_id}")
    
    # Attempt to get entity info for the chat
    entity = await client.get_entity(chat_id)
    if entity:
        print(f"✅ Successfully connected to channel: {entity.title if hasattr(entity, 'title') else chat_id}")
        print(f"Channel type: {type(entity).__name__}")
        
        # Try to get some recent messages as a test
        messages = await client.get_messages(entity, limit=5)
        if messages:
            print(f"✅ Successfully retrieved {len(messages)} recent messages from the channel")
            
            # Show a sample message
            if messages:
                print("\n📝 Sample recent message:")
                sample = messages[0]
                print(f"Date: {sample.date}")
                print(f"Text preview: {sample.text[:100]}...")
    else:
        print("❌ Failed to get channel entity")
    
    print("\n🔑 Session file created at:", session_file)
    print("\nYou can now run the main script which will use this session file.")

# Run the async function
with client:
    client.loop.run_until_complete(main())
