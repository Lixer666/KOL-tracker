from telethon import TelegramClient, events
import json
import re
import os
import asyncio
import time
import requests
from token_filters import (
    check_criteria, format_token_output, 
    extract_token_name, extract_token_address,
    extract_kol_count, extract_percentage, extract_txs_vol,
    extract_mcp_value, extract_liquidity, extract_holders,
    extract_open_time, extract_dev_status,
    extract_token_metrics, check_criteria_type_1, check_criteria_type_2
)

# Дані Telegram
api_id = '21412253'
api_hash = '26a846f4cf5d1a873985b6b3a5fda7bf'
chat_id = 'gmgnsignals'  # Використовуйте username каналу

# Налаштування Telegram бота для надсилання сповіщень
BOT_TOKEN = '8056273767:AAFvxylYmzStNKLuMJ4EJL_SUfA7EbLtm5E'  # Токен вашого бота від BotFather
# Telegram chat ID. Для особистих чатів це ID має бути числовим значенням.
# Отримайте його через @userinfobot або @myidbot в Telegram.
NOTIFICATION_CHAT_ID = ['7232791762', '7760875761']

# Файли для збереження результатів для обох типів критеріїв
FILTER1_JSON_FILE = 'JSON/filter1_tokens_result.json'
FILTER1_TEXT_FILE = 'JSON/filter1_tokens_readable.txt'
FILTER2_JSON_FILE = 'JSON/filter2_tokens_result.json'
FILTER2_TEXT_FILE = 'JSON/filter2_tokens_readable.txt'

# Забезпечуємо існування папки JSON
if not os.path.exists('JSON'):
    os.makedirs('JSON')

# Створення/перевірка файлів результатів
for json_file in [FILTER1_JSON_FILE, FILTER2_JSON_FILE]:
    if not os.path.exists(json_file):
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False)

for text_file in [FILTER1_TEXT_FILE, FILTER2_TEXT_FILE]:
    if not os.path.exists(text_file):
        with open(text_file, 'w', encoding='utf-8') as f:
            pass

# Для зворотної сумісності
FILTERED_JSON_FILE = FILTER1_JSON_FILE
FILTERED_TEXT_FILE = FILTER1_TEXT_FILE

# Лічильник збережених токенів
saved_tokens_counter = 0

# Налаштування дебаг режиму
DEBUG = False  # Встановіть True для виведення дебаг інформації

def debug_print(message):
    """Print debug messages if debug mode is enabled"""
    if DEBUG:
        print(f"[DEBUG] {message}")

def send_telegram_notification(message):
    """Send notification via Telegram bot to all chat IDs in the list"""
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE' or not NOTIFICATION_CHAT_ID:
        print("⚠️ Telegram bot not configured. Please set BOT_TOKEN and NOTIFICATION_CHAT_ID.")
        return False
    all_ok = True
    for chat_id in NOTIFICATION_CHAT_ID:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                'chat_id': chat_id.strip(),
                'text': message,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                pass  # OK
            else:
                print(f"❌ Failed to send Telegram notification to {chat_id}: {response.text}")
                all_ok = False
        except Exception as e:
            print(f"❌ Error sending Telegram notification to {chat_id}: {e}")
            all_ok = False
    return all_ok

def save_to_specific_files(message_data, formatted_output, json_file, text_file, filter_type):
    """Save filtered message to specific JSON and human-readable files"""
    global saved_tokens_counter
    
    # Append to JSON file
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            messages = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        messages = []
    
    messages.append(message_data)
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)
    
    # Append to text file
    with open(text_file, 'a', encoding='utf-8') as f:
        # Додаємо позначку типу фільтра до виводу
        filter_label = f"[Filter: {filter_type}]\n"
        f.write(filter_label + formatted_output + "\n\n")
    
    return formatted_output

def save_to_files(message_data, formatted_output, filter_types=None):
    """Save filtered message to JSON and human-readable files based on filter types"""
    global saved_tokens_counter
    
    # За замовчуванням використовуємо фільтр 1 (для зворотної сумісності)
    if filter_types is None:
        filter_types = ['filter1']
    
    # Зберігаємо в файли відповідно до типів фільтрів
    if 'filter1' in filter_types:
        save_to_specific_files(message_data, formatted_output, FILTER1_JSON_FILE, FILTER1_TEXT_FILE, 'TYPE 1')
    
    if 'filter2' in filter_types:
        save_to_specific_files(message_data, formatted_output, FILTER2_JSON_FILE, FILTER2_TEXT_FILE, 'TYPE 2')
    
    # Increment counter and display
    saved_tokens_counter += 1
    filter_labels = ', '.join(filter_types).upper()
    print(f"💰 Saved token #{saved_tokens_counter}: {extract_token_name(message_data.get('text', ''))} [Filters: {filter_labels}]")
    
    # --- Send notification about file save ---
    token_address = extract_token_address(message_data.get('text', ''))
    token_name = extract_token_name(message_data.get('text', ''))
    gmgn_link = f"https://gmgn.ai/sol/token/{token_address}"
    save_message = f"💾 Token <b>{token_name}</b> (<code>{token_address}</code>) записано у файл! <a href='{gmgn_link}'>GMGN</a>"
    send_telegram_notification(save_message)
    
    return formatted_output

# --- Hide all setup/connection prints unless DEBUG ---
if DEBUG:
    print("""
🔧 Налаштування Telegram бота для сповіщень:
1. Створіть бота через @BotFather в Telegram
2. Отримайте токен бота
3. Відкрийте цей скрипт і замініть 'YOUR_BOT_TOKEN_HERE' на отриманий токен
4. Знайдіть ваш Chat ID через @userinfobot і замініть 'YOUR_CHAT_ID_HERE'
5. Перезапустіть скрипт для отримання сповіщень
""")

# Use a persistent session file
session_file = '../session/gmgnsignals_sol_persistent'
client = TelegramClient(session_file, api_id, api_hash)

@client.on(events.NewMessage(chats=chat_id))
async def handle_new_message(event):
    try:
        if not event.message.text:
            debug_print("Received message without text")
            return
        
        message_text = event.message.text
        # Only print incoming token messages (first 50 chars) if DEBUG
        debug_print(f"📩 Received message: {message_text[:50]}...")
        
        # Перевіряємо, чи є обидва слова "KOL" і "Buy" у тексті (незалежно від регістру)
        if re.search(r'kol', message_text, re.IGNORECASE) and re.search(r'buy', message_text, re.IGNORECASE):
            # Створюємо об'єкт повідомлення для фільтра
            message_data = {
                "id": event.message.id,
                "date": str(event.message.date),
                "sender_id": event.message.sender_id,
                "text": message_text
            }
            
            # Витягуємо адресу токена
            try:
                token_address = extract_token_address(message_text)
                token_name = extract_token_name(message_text)
                
                # Print token info always
                print(f"\n📩 Token received: {token_name} ({token_address})")
                
                # Витягуємо всі метрики токена
                metrics = extract_token_metrics(message_text)
                
                # Перевірка на відповідність різним критеріям
                matches_filter1 = check_criteria_type_1(metrics)
                matches_filter2 = check_criteria_type_2(metrics)
                
                # Якщо відповідає хоча б одному набору критеріїв
                if matches_filter1 or matches_filter2:
                    # Форматуємо дані для читабельного виводу
                    formatted_output = format_token_output(message_data)
                    
                    # Визначаємо, яким фільтрам відповідає токен
                    filter_types = []
                    if matches_filter1:
                        filter_types.append('filter1')
                    if matches_filter2:
                        filter_types.append('filter2')
                    
                    # Print filter match result always
                    if filter_types:
                        print(f"✅ Token matches: {', '.join(filter_types).upper()}")
                    else:
                        print(f"❌ Token does not match any filter")
                    
                    if filter_types:
                        # Зберігаємо у відповідні файли
                        save_to_files(message_data, formatted_output, filter_types)
                        
                        # Формуємо повідомлення про знайдений токен
                        notification_message = format_telegram_notification(token_name, token_address, formatted_output)
                        notification_message += f"\n\n<b>Відповідає фільтрам:</b> {', '.join(filter_types).upper()}"
                        send_telegram_notification(notification_message)
                    else:
                        debug_print(f"Token {token_name} does not meet any criteria.")
                        
                        # Додатковий детальний дебаг для відхилених токенів
                        if DEBUG:
                            debug_print(f"Values: KOL={metrics['kol_count']}, 5m={metrics['percent_5m']}%, " + \
                                        f"1h={metrics['percent_1h']}%, 6h={metrics['percent_6h']}%, " +
                                        f"TXs={metrics['txs']}, Vol={metrics['vol']}K, MCP={metrics['mcp']}K, " +
                                        f"Liq={metrics['liquidity']}, Holders={metrics['holders']}, " +
                                        f"Open={metrics['open_time']}s, DEV Sell All={metrics['dev_sell_all']}")
            except Exception as e:
                print(f"Error processing message: {e}")
    except Exception as e:
        print(f"Error in handle_new_message: {e}")


async def check_bot_connection():
    """Check if the Telegram bot is properly configured and can send messages"""
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE' or NOTIFICATION_CHAT_ID == 'YOUR_CHAT_ID_HERE':
        if DEBUG:
            print("⚠️ WARNING: Telegram notification bot is not configured!")
            print("To receive notifications, edit the script and set BOT_TOKEN and NOTIFICATION_CHAT_ID.")
        return False
    try:
        if DEBUG:
            print("\n🔍 Testing Telegram bot connection...")
            print(f"🤖 Bot token: {BOT_TOKEN[:5]}...{BOT_TOKEN[-5:]}")
            print(f"💬 Chat ID: {NOTIFICATION_CHAT_ID}")
        # Спробуємо отримати інформацію про бота
        bot_info = get_bot_info()
        if bot_info:
            if DEBUG:
                print(f"✅ Bot is valid and active!")
                print(f"Bot name: @{bot_info['username']} ({bot_info['name']})")
                print(f"Bot ID: {bot_info['id']}")
                print("\n📱 To interact with your bot, open Telegram and search for:")
                print(f"@{bot_info['username']}")
                print("\nMake sure you've sent a /start message to the bot!")
        else:
            if DEBUG:
                print("❌ Could not retrieve bot information. Check your BOT_TOKEN.")
            return False
        if DEBUG:
            print("\nAttempting to send test message...")
        test_message = "✅ Bot connection test: Monitoring system is starting up"
        success = send_telegram_notification(test_message)
        if success:
            if DEBUG:
                print("✅ Telegram bot connection successful!")
                print("You should have received a test message in your Telegram!")
            return True
        else:
            if DEBUG:
                print("\n❓ Bot connection failed. Please check these common issues:")
                print("1. Have you started your bot by sending it a /start message in Telegram?")
                print(f"2. Try searching for @{bot_info['username'] if bot_info else 'YOUR_BOT'} in Telegram")
                print("3. Send a /start message to your bot")
                print(f"4. Check if your Chat ID ({NOTIFICATION_CHAT_ID}) is correct")
                print("5. Get your correct Chat ID by messaging @userinfobot or @myidbot")
                print("6. Update the NOTIFICATION_CHAT_ID in this script and restart")
                # Спробуємо додати більше діагностики
                if NOTIFICATION_CHAT_ID.isdigit():
                    print("\n🔍 Your Chat ID appears to be numeric, which is correct for personal chats.")
                elif NOTIFICATION_CHAT_ID.startswith('-'):
                    print("\n🔍 Your Chat ID appears to be for a group chat.")
                else:
                    print("\n⚠️ Your Chat ID doesn't appear to be in the expected format (should be numeric).")
                    print("Get your correct ID by sending a message to @userinfobot in Telegram.")
            return False
    except Exception as e:
        if DEBUG:
            print(f"❌ Error connecting to Telegram bot: {e}")
        return False

async def check_channel_connection():
    """Verify connection to the target channel"""
    if DEBUG:
        print("\n🔍 Checking connection to target channel...")
        print(f"Channel ID: {chat_id}")
    try:
        # Attempt to get entity info for the chat
        entity = await client.get_entity(chat_id)
        if entity:
            if DEBUG:
                print(f"✅ Successfully connected to channel: {entity.title if hasattr(entity, 'title') else chat_id}")
                print(f"Channel type: {type(entity).__name__}")
            # Try to get some recent messages as a test
            messages = await client.get_messages(entity, limit=5)
            if messages:
                if DEBUG:
                    print(f"✅ Successfully retrieved {len(messages)} recent messages from the channel")
                    # Show a sample message
                    print("\n📝 Sample recent message:")
                    sample = messages[0]
                    print(f"Date: {sample.date}")
                    print(f"Text preview: {sample.text[:100]}...\n")
                    # Check if any message matches our KOL criteria
                    for msg in messages:
                        if re.search(r'kol', msg.text, re.IGNORECASE) and re.search(r'buy', msg.text, re.IGNORECASE):
                            print("✅ Found a recent message containing 'KOL' and 'Buy'!")
                            # Extract some metrics as a test
                            metrics = extract_token_metrics(msg.text)
                            print(f"Sample metrics: KOL={metrics['kol_count']}, 6h Growth={metrics['percent_6h']}%")
                            # Test our relaxed criteria against this message
                            filter1 = check_criteria_type_1(metrics)
                            filter2 = check_criteria_type_2(metrics)
                            print(f"Matches Filter1: {filter1}, Filter2: {filter2}")
                            break
            else:
                if DEBUG:
                    print("⚠️ Connected to channel but couldn't retrieve messages")
            return True
        else:
            if DEBUG:
                print("❌ Failed to get channel entity")
            return False
    except Exception as e:
        if DEBUG:
            print(f"❌ Error checking channel connection: {e}")
            print("⚠️ Please verify the channel ID/username is correct")
        return False

# --- Move health_check here ---
async def health_check():
    """Perform regular health checks and report status"""
    start_time = time.time()
    last_check_time = start_time
    while True:
        current_time = time.time()
        uptime = current_time - start_time
        messages_received = getattr(client, '_message_counter', 0)
        if current_time - last_check_time >= 300:
            hours = int(uptime / 3600)
            minutes = int((uptime % 3600) / 60)
            status = f"✅ Bot running for {hours}h {minutes}m | Messages: {messages_received} | Tokens saved: {saved_tokens_counter}"
            print(status)
            if hours > 0 and minutes % 30 < 5:
                send_telegram_notification(f"🤖 Bot Status: {status}")
            last_check_time = current_time
        await asyncio.sleep(60)

def format_telegram_notification(token_name, token_address, formatted_output):
    """Format notification for Telegram with clickable links and formatted text"""
    solscan_link = f"https://solscan.io/token/{token_address}"
    raydium_link = f"https://raydium.io/swap/?inputCurrency=sol&outputCurrency={token_address}"
    birdeye_link = f"https://birdeye.so/token/{token_address}?chain=solana"
    dexscreener_link = f"https://dexscreener.com/solana/{token_address}"
    gmgn_link = f"https://gmgn.ai/sol/token/{token_address}"
    message = f"🔥 <b>GMGN TOKEN ALERT</b> 🔥\n\n"
    message += f"<b>Token:</b> {token_name}\n"
    message += f"<code>{token_address}</code>\n"
    message += f"<a href='{gmgn_link}'>GMGN</a>\n\n"
    lines = formatted_output.split('\n')
    important_fields = ["KOL Count:", "Growth", "Transactions", "Volume", "MCP:", "Liquidity:"]
    for line in lines:
        for field in important_fields:
            if field in line:
                message += line + "\n"
                break
    message += "\n<b>🔎 Перевірка:</b>\n"
    message += f"• <a href='{solscan_link}'>Solscan</a> | "
    message += f"<a href='{birdeye_link}'>Birdeye</a> | "
    message += f"<a href='{dexscreener_link}'>DexScreener</a>\n"
    message += f"\n<b>💱 Торгівля:</b>\n"
    message += f"• <a href='{raydium_link}'>Trade on Raydium</a>\n"
    return message

async def main():
    # --- Remove all connection/startup prints and notifications ---
    # Add message counter attribute to client
    setattr(client, '_message_counter', 0)
    
    # Hook into the message event to count messages
    @client.on(events.NewMessage)
    async def count_messages(event):
        client._message_counter += 1
    
    # Перевіряємо підключення бота
    await check_bot_connection()
    
    # Check connection to the target channel
    await check_channel_connection()
    
    # Start health check task
    asyncio.create_task(health_check())
    
    # --- Remove initial notification ---
    # Тримаємо скрипт активним
    while True:
        await asyncio.sleep(1)

# Запуск клієнтаце
with client:
    client.loop.run_until_complete(main())

def run_code_health_check():
    """Run a quick health check using sample token messages and print the result."""
    print("\n🩺 Running code health check with sample tokens...")
    # Example test messages (add more if needed)
    test_messages = [
        "** 3 KOL Buy **[**TEST**](https://gmgn.ai/sol/token/TEST)** `TESTADDRESS`\n📈 5m | 1h | 6h:**10.0%** | **20.0%** | **3000.0%**\n🎲 5m TXs/Vol:**100**/**$10.0K**\n💡 MCP:**$200K**\n💧 Liq:**50** **SOL**\n👥 Holder:**100**\n🕒 Open:**5min** **ago**\n⏳ DEV:[🚨 Sell All]",
        "** 3 KOL Buy **[**SAMPLE**](https://gmgn.ai/sol/token/SAMPLE)** `SAMPLEADDR`\n📈 5m | 1h | 6h:**5.0%** | **10.0%** | **4000.0%**\n🎲 5m TXs/Vol:**900**/**$5.0K**\n💡 MCP:**$300K**\n💧 Liq:**20** **SOL**\n👥 Holder:**50**\n🕒 Open:**10min** **ago**",
        "** 2 KOL Buy **[**FAIL**](https://gmgn.ai/sol/token/FAIL)** `FAILADDR`\n📈 5m | 1h | 6h:**1.0%** | **2.0%** | **100.0%**\n🎲 5m TXs/Vol:**2000**/**$1.0K**\n💡 MCP:**$50K**\n💧 Liq:**5** **SOL**\n👥 Holder:**10**\n🕒 Open:**1min** **ago**"
    ]
    from token_filters import extract_token_metrics, check_criteria_type_1, check_criteria_type_2
    all_passed = True
    for idx, msg in enumerate(test_messages):
        metrics = extract_token_metrics(msg)
        filter1 = check_criteria_type_1(metrics)
        filter2 = check_criteria_type_2(metrics)
        if idx < 2:
            # These should pass at least one filter
            if not (filter1 or filter2):
                print(f"❌ Test token {idx+1} did NOT pass any filter (should pass)")
                all_passed = False
        else:
            # This should not pass
            if filter1 or filter2:
                print(f"❌ Test token {idx+1} PASSED a filter (should NOT pass)")
                all_passed = False
    if all_passed:
        print("✅ Code health check PASSED: All test tokens processed as expected.")
    else:
        print("❌ Code health check FAILED: See details above.")

# Run health check at the very start
run_code_health_check()