#!/usr/bin/env python3
import re
from datetime import datetime

def extract_percentage(text):
    """Extract growth percentages for 5m, 1h, 6h (fix: match lower values)"""
    # Primary pattern
    pattern = r'📈\s*5m \| 1h \| 6h:\s*\*\*([\d,.]+)%\*\*\s*\|\s*\*\*([\d,.]+)%\*\*\s*\|\s*\*\*([\d,.]+)%\*\*'
    match = re.search(pattern, text)
    if match:
        try:
            percent_5m = float(match.group(1).replace(',', ''))
            percent_1h = float(match.group(2).replace(',', ''))
            percent_6h = float(match.group(3).replace(',', ''))
            return percent_5m, percent_1h, percent_6h
        except Exception as e:
            print(f"Error processing percentages: {e}")
    
    # Fallback pattern
    fallback_pattern = r'5m \| 1h \| 6h:\s*\*\*([\d,.]+)%\*\*\s*\|\s*\*\*([\d,.]+)%\*\*\s*\|\s*\*\*([\d,.]+)%\*\*'
    fallback_match = re.search(fallback_pattern, text)
    if fallback_match:
        try:
            percent_5m = float(fallback_match.group(1).replace(',', ''))
            percent_1h = float(fallback_match.group(2).replace(',', ''))
            percent_6h = float(fallback_match.group(3).replace(',', ''))
            return percent_5m, percent_1h, percent_6h
        except Exception as e:
            print(f"Error processing percentages (fallback): {e}")
            
    return 0, 0, 0

def extract_txs_vol(text):
    """Extract transaction count and volume (fix: match lower values)"""
    pattern = r'🎲\s*5m TXs/Vol:\s*\*\*(\d+)\*\*/\*\*\$([0-9,.]+)([KMB]?)\*\*'
    match = re.search(pattern, text)
    if match:
        try:
            txs = int(match.group(1))
            vol_str = match.group(2).replace(',', '')
            vol_unit = match.group(3)
            vol = float(vol_str)
            if vol_unit == 'K':
                vol = vol
            elif vol_unit == 'M':
                vol = vol * 1000 
            elif vol_unit == 'B':
                vol = vol * 1000000
            return txs, vol
        except Exception as e:
            print(f"Error processing TXs/Vol: {e}")
    
    # Alternative pattern without emojis
    alt_pattern = r'5m TXs/Vol:\s*\*\*(\d+)\*\*/\*\*\$([0-9,.]+)([KMB]?)\*\*'
    alt_match = re.search(alt_pattern, text)
    if alt_match:
        try:
            txs = int(alt_match.group(1))
            vol_str = alt_match.group(2).replace(',', '')
            vol_unit = alt_match.group(3)
            vol = float(vol_str)
            if vol_unit == 'K':
                vol = vol
            elif vol_unit == 'M':
                vol = vol * 1000
            elif vol_unit == 'B':
                vol = vol * 1000000
            return txs, vol
        except Exception as e:
            print(f"Error processing TXs/Vol (alt): {e}")
    return 0, 0

def extract_mcp_value(text):
    """Extract MCP value (fix: match lower values)"""
    pattern = r'💡\s*MCP:\s*\*\*\$([\d,.]+)([KMB]?)\*\*'
    match = re.search(pattern, text)
    if match:
        try:
            value_str = match.group(1).replace(',', '')
            unit = match.group(2)
            value = float(value_str)
            if unit == 'K':
                return value
            elif unit == 'M':
                return value * 1000
            elif unit == 'B':
                return value * 1000000
            return value
        except Exception as e:
            print(f"Error processing MCP: {e}")
    
    # Alternative pattern without emoji
    alt_pattern = r'MCP:\s*\*\*\$([\d,.]+)([KMB]?)\*\*'
    alt_match = re.search(alt_pattern, text)
    if alt_match:
        try:
            value_str = alt_match.group(1).replace(',', '')
            unit = alt_match.group(2)
            value = float(value_str)
            if unit == 'K':
                return value
            elif unit == 'M':
                return value * 1000
            elif unit == 'B':
                return value * 1000000
            return value
        except Exception as e:
            print(f"Error processing MCP (alt): {e}")
    return 0

def extract_liquidity(text):
    """Extract liquidity value (fix: match lower values)"""
    pattern = r'💧\s*Liq:\s*\*\*([\d,.]+)\*\*\s*\*\*SOL\*\*'
    match = re.search(pattern, text)
    if match:
        try:
            sol_value = float(match.group(1).replace(',', ''))
            return sol_value
        except Exception as e:
            print(f"Error processing liquidity: {e}")
            
    # Alternative pattern
    alt_pattern = r'Liq:\s*\*\*([\d,.]+)\*\*\s*\*\*SOL\*\*'
    alt_match = re.search(alt_pattern, text)
    if alt_match:
        try:
            sol_value = float(alt_match.group(1).replace(',', ''))
            return sol_value
        except Exception as e:
            print(f"Error processing liquidity (alt): {e}")
            
    # Another alternative pattern
    alt_pattern2 = r'Liq:\s*\*\*([\d,.]+)\*\*\s*SOL'
    alt_match2 = re.search(alt_pattern2, text)
    if alt_match2:
        try:
            sol_value = float(alt_match2.group(1).replace(',', ''))
            return sol_value
        except Exception as e:
            print(f"Error processing liquidity (alt2): {e}")
            
    return 0

def extract_holders(text):
    """Extract number of holders (fix: match lower values)"""
    pattern = r'👥\s*Holder:\s*\*\*(\d+)\*\*'
    match = re.search(pattern, text)
    if match:
        try:
            holders = int(match.group(1).replace(',', ''))
            return holders
        except Exception as e:
            print(f"Error processing holder count: {e}")
    
    # Alternative without emoji
    alt_pattern = r'Holder:\s*\*\*(\d+)\*\*'
    alt_match = re.search(alt_pattern, text)
    if alt_match:
        try:
            holders = int(alt_match.group(1).replace(',', ''))
            return holders
        except Exception as e:
            print(f"Error processing holder count (alt): {e}")
            
    return 0

def extract_open_time(text):
    """Extract open time and convert to seconds (fix: support min)"""
    pattern = r'🕒\s*Open:\s*\*\*(\d+)(min|s|h|d|y)\*\*\s*\*\*ago\*\*'
    match = re.search(pattern, text)
    if match:
        try:
            value = int(match.group(1))
            unit = match.group(2)
            if unit == 's':
                return value
            elif unit == 'min':
                return value * 60
            elif unit == 'h':
                return value * 3600
            elif unit == 'd':
                return value * 86400
            elif unit == 'y':
                return value * 31536000
            else:
                return 0
        except Exception as e:
            print(f"Error processing open time: {e}")

    # Try alternative pattern
    alt_pattern = r'Open:\s*\*\*(\d+)(min|s|h|d|y)\*\*'
    alt_match = re.search(alt_pattern, text)
    if alt_match:
        try:
            value = int(alt_match.group(1))
            unit = alt_match.group(2)
            if unit == 's':
                return value
            elif unit == 'min':
                return value * 60
            elif unit == 'h':
                return value * 3600
            elif unit == 'd':
                return value * 86400
            elif unit == 'y':
                return value * 31536000
            else:
                return 0
        except Exception as e:
            print(f"Error processing open time (alt): {e}")
    return 0

def extract_kol_count(text):
    """Extract KOL Buy count (fix: match various formats)"""
    # Try to match patterns like '** 5 KOL Buy **' or '** 4 KOL Buy **'
    pattern = r'\*\*\s*(\d+)\s+KOL Buy\s*\*\*'
    match = re.search(pattern, text)
    if match:
        try:
            return int(match.group(1))
        except Exception as e:
            print(f"Error processing KOL Buy count: {e}")
    
    # Try to match patterns like '5 KOL Buy' (without bold)
    alt_pattern = r'(\d+) KOL Buy'
    alt_match = re.search(alt_pattern, text)
    if alt_match:
        try:
            return int(alt_match.group(1))
        except Exception as e:
            print(f"Error processing KOL Buy count (alt): {e}")
            
    # Try to match pattern '👤 **3 KOL**'
    new_pattern = r'👤\s*\*\*(\d+)\s*KOL\*\*'
    new_match = re.search(new_pattern, text)
    if new_match:
        try:
            return int(new_match.group(1))
        except Exception as e:
            print(f"Error processing KOL count (new): {e}")
            
    # Try without emoji: '**3 KOL**'
    simple_pattern = r'\*\*(\d+)\s*KOL\*\*'
    simple_match = re.search(simple_pattern, text)
    if simple_match:
        try:
            return int(simple_match.group(1))
        except Exception as e:
            print(f"Error processing KOL count (simple): {e}")
    
    return 0

def extract_token_name(text):
    """Extract token name"""
    pattern = r'\*\*\[?\*\*([^\*\[\]]+)\*\*\]?\*\*'
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    
    # Alternative pattern
    alt_pattern = r'KOL Buy \*\*\[\*\*([^\*\[\]]+)\*\*\]'
    alt_match = re.search(alt_pattern, text)
    if alt_match:
        return alt_match.group(1)
    
    # Another alternative pattern
    alt_pattern2 = r'KOL Buy \*\*\[\*\*([^\*\[\]]+)\*\*\]\('
    alt_match2 = re.search(alt_pattern2, text)
    if alt_match2:
        return alt_match2.group(1)
    
    # Simple pattern for plaintext
    alt_pattern3 = r'KOL Buy @([^\s]+)'
    alt_match3 = re.search(alt_pattern3, text)
    if alt_match3:
        return alt_match3.group(1)
    
    return "Unknown"

def extract_token_address(text):
    """Extract token address"""
    pattern = r'`([A-Za-z0-9]+)`'
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    
    return "Unknown"

def extract_dev_status(text):
    """Extract DEV status - whether it's 'Sell All' or not (fix: match link)"""
    pattern = r'⏳\s*DEV:\s*\[🚨\s*Sell\s*All\]'
    match = re.search(pattern, text)
    if match:
        return True
    
    # Alternative without emoji
    alt_pattern = r'DEV:\s*\[🚨\s*Sell\s*All\]'
    alt_match = re.search(alt_pattern, text)
    if alt_match:
        return True
        
    return False

def extract_token_link(text):
    """Extract clickable link to token"""
    pattern = r'\*\*\[\*\*[^\*\[\]]+\*\*\]\(([^)]+)\)'
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    
    # Alternative pattern
    alt_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    alt_match = re.search(alt_pattern, text)
    if alt_match:
        return alt_match.group(2)
    
    return "Unknown"

def extract_token_metrics(text):
    """Extract all token metrics from a message"""
    # Extract all metrics
    kol_count = extract_kol_count(text)
    percent_5m, percent_1h, percent_6h = extract_percentage(text)
    txs, vol = extract_txs_vol(text)
    mcp = extract_mcp_value(text)
    liquidity = extract_liquidity(text)
    holders = extract_holders(text)
    open_time = extract_open_time(text)
    dev_sell_all = extract_dev_status(text)
    
    # Log raw extraction results to help debug
    print(f"\n📊 RAW EXTRACTION RESULTS for message:")
    print(f"KOL Count: {kol_count}")
    print(f"Percentage: 5m={percent_5m}%, 1h={percent_1h}%, 6h={percent_6h}%")
    print(f"TXs: {txs}, Vol: {vol}K")
    print(f"MCP: {mcp}K")
    print(f"Liquidity: {liquidity} SOL")
    print(f"Holders: {holders}")
    print(f"Open Time: {open_time} seconds")
    print(f"DEV Sell All: {dev_sell_all}")
    print("-" * 50)
    
    return {
        'kol_count': kol_count,
        'percent_5m': percent_5m,
        'percent_1h': percent_1h,
        'percent_6h': percent_6h,
        'txs': txs,
        'vol': vol,
        'mcp': mcp,
        'liquidity': liquidity,
        'holders': holders,
        'open_time': open_time,
        'dev_sell_all': dev_sell_all
    }

def check_criteria_type_1(metrics):
    """Check if token meets criteria type 1 (original criteria)"""
    if not (metrics['kol_count'] == 3):
        return False
    if not (metrics['txs'] <= 1100):
        return False
    if not (metrics['mcp'] >= 190): 
        return False
    if not (3000 <= metrics['percent_6h'] <= 8600):
        return False
    return True

def check_criteria_type_2(metrics):
    """Check if token meets criteria type 2 (alternative criteria)"""
    if not (metrics['kol_count'] == 3):
        return False
    if not (3000 <= metrics['percent_6h']):
        return False
    return True

def check_criteria(message):
    """Check if message meets the original criteria (for backward compatibility)"""
    text = message.get('text', '')
    metrics = extract_token_metrics(text)
    return check_criteria_type_1(metrics)

def format_token_output(message):
    """Format token data for human-readable output"""
    text = message.get('text', '')
    
    token_name = extract_token_name(text)
    token_address = extract_token_address(text)
    kol_count = extract_kol_count(text)
    percent_5m, percent_1h, percent_6h = extract_percentage(text)
    txs, vol = extract_txs_vol(text)
    mcp = extract_mcp_value(text)
    liquidity = extract_liquidity(text)
    holders = extract_holders(text)
    open_time = extract_open_time(text)
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Format output with each field on a new line
    output = f"Token Name: {token_name}\n"
    output += f"Token Address: {token_address}\n"
    output += f"Date: {date}\n"
    output += f"KOL Count: {kol_count}\n"
    output += f"Growth 5m: {percent_5m:.1f}%\n"
    output += f"Growth 1h: {percent_1h:.1f}%\n"
    output += f"Growth 6h: {percent_6h:.1f}%\n"
    output += f"Transactions (5m): {txs}\n"
    output += f"Volume (5m): ${vol:.1f}K\n"
    output += f"MCP: ${mcp:.1f}K\n"
    output += f"Liquidity: {liquidity:.2f} SOL\n"
    output += f"Holders: {holders}\n"
    output += f"Open Time: {open_time} seconds\n"
    output += f"DEV Status: 🚨 Sell All\n"
    output += "-" * 50  # Separator line
    
    return output
