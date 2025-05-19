from get_signal import send_telegram_notification, extract_token_metrics
from token_filters import check_criteria_type_1, check_criteria_type_2, format_token_output

# Sample message with KOL Buy signal (dummy data)
sample_message = """
👑 **3 KOL** 

**[**DOGE ROCKET**](https://t.me/dogerocket_sol)** | `FFoYx9eLTo5G62q9JPpCFW8HN5SXGc9iPgGVKVd27TZP`

📈 5m | 1h | 6h: **100.2%** | **500.1%** | **3050.5%**
🎲 5m TXs/Vol: **123**/**$200K**
💡 MCP: **$200K**
💧 Liq: **50** **SOL**
👥 Holder: **500**
🕒 Open: **2h** **ago**
⏳ DEV: [Trusted Team]
"""

# Create a message object similar to what we'd get from Telegram
message_data = {
    "id": 12345,
    "date": "2023-05-19 12:00:00",
    "sender_id": 123456789,
    "text": sample_message
}

print("🧪 Running token detector test with sample message...")
print("-" * 80)
print(sample_message)
print("-" * 80)

# Extract metrics
metrics = extract_token_metrics(sample_message)

# Check filter criteria
matches_filter1 = check_criteria_type_1(metrics)
matches_filter2 = check_criteria_type_2(metrics)

print(f"\n📋 Filter Results:")
print(f"✓ Filter 1 (stricter): {'Matched ✅' if matches_filter1 else 'Not matched ❌'}")
print(f"✓ Filter 2 (relaxed): {'Matched ✅' if matches_filter2 else 'Not matched ❌'}")

# Format and display token output
if matches_filter1 or matches_filter2:
    formatted_output = format_token_output(message_data)
    print("\n📝 Formatted Output:")
    print(formatted_output)
    
    print("\n🚀 Sending test notification to Telegram...")
    notification = "🧪 TEST NOTIFICATION\n\n" + formatted_output
    send_telegram_notification(notification)
else:
    print("\n❌ Token did not match any criteria")
