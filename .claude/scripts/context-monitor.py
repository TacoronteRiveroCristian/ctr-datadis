#!/usr/bin/env python3
"""
Claude Code Context Monitor
Real-time context usage monitoring with visual indicators and session analytics

OVERVIEW:
This script generates a comprehensive status line for Claude Code that displays:
- Model information with context-aware coloring
- Project directory navigation
- Real-time context window usage with visual progress bars
- Session metrics including cost, time, and code changes

STATUS LINE FORMAT:
[Model] │ PROJ:directory │ CTX:[progress_bar] percentage% status (tokens) │ metrics

CONTEXT MONITORING (CTX):
- Shows real-time usage of Claude's context window (conversation memory)
- Format: CTX:[████████████▒▒▒▒▒▒▒▒] 65.3% 🟡MED (125kt)
- Progress bar: 20 segments with filled (█) and empty (▒) characters
- Percentage: Decimal precision showing context utilization
- Status levels with icons:
  * 🔵 MIN (0-30%): Minimal usage, plenty of context available
  * 🟢 LOW (30-60%): Low usage, normal conversation state
  * 🟡 MED (60-80%): Medium usage, monitor for efficiency
  * 🟠 WARN (80-90%): Warning level, consider context optimization
  * ⚠️ HIGH (90-95%): High usage, nearing context limits
  * 🚨 CRIT (95%+): Critical usage, auto-compaction imminent
- Token count: Current tokens in kilotons (kt) or raw count
- Special alerts:
  * 🔄 AUTO-COMPACT: Context will be compressed soon
  * ⚡ CONTEXT-LOW: System warning about low context
- Context reset prediction: Estimates when context window will refresh
  * →RESET! (red): Imminent reset/compaction (90%+ usage)
  * →~Xmsg (yellow): Estimated messages until reset (75-90% usage)
  * →OK (green): Stable, plenty of context remaining (50-75% usage)
  * Based on current usage patterns and remaining capacity

SESSION METRICS:
- COST: Session expense in USD or cents
  * Green ($0.000-$0.049): Economical usage
  * Yellow ($0.050-$0.099): Moderate cost
  * Red ($0.100+): Expensive session
- TIME: Session duration with precision
  * Format: XmYs for minutes/seconds, Xs for seconds only
  * Green (<30min): Normal session length
  * Yellow (30min+): Extended session
- CODE: Lines of code modified
  * Format: +X/-Y or ±XL for net changes
  * Green (+): Net additions to codebase
  * Red (-): Net deletions from codebase
  * Yellow (±0): Neutral changes
  * Breakdown: (+added/-removed) for significant changes

REAL-TIME PRECISION:
- Reads last 8KB of transcript for performance
- Multiple detection methods for accuracy:
  1. Usage tokens: Most accurate, from API responses
  2. System warnings: Backup method from Claude alerts
  3. Tool estimation: Fallback based on tool usage patterns
- Updates with each Claude response for real-time monitoring

VISUAL INDICATORS:
- Color coding throughout for quick status assessment
- Pipe separators (│) for clear section boundaries
- Icons for immediate recognition of status levels
- Compact format suitable for terminal status lines

TECHNICAL DETAILS:
- Context window: Assumes 200k tokens for Claude Sonnet 4
- File reading: Efficient tail reading for large transcripts
- Error handling: Graceful fallbacks for missing data
- Unicode support: Proper handling of progress bar characters
"""

import json
import sys
import os
import re

def parse_context_from_transcript(transcript_path):
    """Parse context usage from transcript file with enhanced real-time precision."""
    if not transcript_path or not os.path.exists(transcript_path):
        return None
    
    try:
        # Read file more efficiently for real-time updates
        with open(transcript_path, 'rb') as f:
            # Seek to end and read backwards for latest data
            f.seek(0, 2)  # Seek to end
            file_size = f.tell()
            
            # Read last 8KB for better real-time performance
            chunk_size = min(8192, file_size)
            f.seek(max(0, file_size - chunk_size))
            content = f.read().decode('utf-8', errors='ignore')
        
        # Split into lines and get the most recent ones
        lines = content.split('\n')
        recent_lines = [line for line in lines[-25:] if line.strip()]  # More lines for better accuracy
        
        context_data = {'percent': 0, 'tokens': 0, 'method': 'none'}
        
        for line in reversed(recent_lines):
            try:
                data = json.loads(line.strip())
                
                # Method 1: Most accurate - Parse usage tokens from assistant messages
                if data.get('type') == 'assistant':
                    message = data.get('message', {})
                    usage = message.get('usage', {})
                    
                    if usage:
                        input_tokens = usage.get('input_tokens', 0)
                        cache_read = usage.get('cache_read_input_tokens', 0)
                        cache_creation = usage.get('cache_creation_input_tokens', 0)
                        output_tokens = usage.get('output_tokens', 0)
                        
                        # More accurate context calculation including output tokens
                        total_input = input_tokens + cache_read + cache_creation
                        total_tokens = total_input + output_tokens
                        
                        # Dynamic context window detection (200k for Sonnet 4, adjust as needed)
                        context_window = 200000
                        if total_tokens > 0:
                            percent_used = min(100, (total_tokens / context_window) * 100)
                            return {
                                'percent': percent_used,
                                'tokens': total_tokens,
                                'input_tokens': total_input,
                                'output_tokens': output_tokens,
                                'method': 'usage',
                                'timestamp': data.get('timestamp', '')
                            }
                
                # Method 2: System warnings (backup method)
                elif data.get('type') == 'system_message':
                    content = data.get('content', '')
                    
                    # Enhanced pattern matching for context warnings
                    patterns = [
                        (r'Context left until auto-compact: (\d+(?:\.\d+)?)%', 'auto-compact'),
                        (r'Context low \((\d+(?:\.\d+)?)% remaining\)', 'low'),
                        (r'Context usage: (\d+(?:\.\d+)?)%', 'usage-report'),
                        (r'Context window: (\d+(?:\.\d+)?)% used', 'window-report')
                    ]
                    
                    for pattern, warning_type in patterns:
                        match = re.search(pattern, content)
                        if match:
                            value = float(match.group(1))
                            percent_used = 100 - value if 'remaining' in pattern or 'left' in pattern else value
                            
                            return {
                                'percent': percent_used,
                                'warning': warning_type,
                                'method': 'system',
                                'timestamp': data.get('timestamp', '')
                            }
                
                # Method 3: Estimate from tool usage patterns (fallback)
                elif data.get('type') == 'tool_use':
                    tool_name = data.get('name', '')
                    if tool_name in ['Read', 'Grep', 'MultiEdit']:
                        # Estimate context growth from tool usage
                        if not context_data.get('tokens'):
                            context_data['tokens'] = 15000  # Base estimate
                            context_data['percent'] = (context_data['tokens'] / 200000) * 100
                            context_data['method'] = 'estimated'
            
            except (json.JSONDecodeError, KeyError, ValueError, TypeError):
                continue
        
        # Return estimated data if no precise data found
        return context_data if context_data['method'] != 'none' else None
        
    except (FileNotFoundError, PermissionError, UnicodeDecodeError):
        return None

def calculate_context_reset_prediction(context_info):
    """Calculate when context might be reset/compacted based on current usage."""
    if not context_info or context_info.get('method') not in ['usage', 'system']:
        return None
    
    percent = context_info.get('percent', 0)
    
    # Context typically gets auto-compacted around 90-95%
    if percent >= 90:
        return "imminent"  # Reset very soon
    elif percent >= 85:
        remaining_percent = 90 - percent
        # Rough estimate: each response uses ~2-5% context
        estimated_responses = max(1, int(remaining_percent / 3))
        return f"~{estimated_responses}msg"
    elif percent >= 75:
        remaining_percent = 90 - percent  
        estimated_responses = max(2, int(remaining_percent / 3))
        return f"~{estimated_responses}msg"
    elif percent >= 50:
        return "stable"  # Good amount of context left
    else:
        return None  # Too early to predict

def get_context_display(context_info):
    """Generate context display with visual indicators and reset prediction."""
    if not context_info:
        return "\033[90mCTX:\033[0m \033[94m[??????????]\033[0m \033[90m?%\033[0m"
    
    percent = context_info.get('percent', 0)
    warning = context_info.get('warning')
    tokens = context_info.get('tokens', 0)
    
    # Calculate context reset prediction
    reset_prediction = calculate_context_reset_prediction(context_info)
    
    # Color based on usage level with status indicators
    if percent >= 95:
        color = "\033[31;1m"  # Blinking red
        status = "CRIT"
        icon = "🚨"
    elif percent >= 90:
        color = "\033[31m"    # Red  
        status = "HIGH"
        icon = "⚠️"
    elif percent >= 80:
        color = "\033[91m"   # Light red
        status = "WARN"
        icon = "🟠"
    elif percent >= 60:
        color = "\033[33m"   # Yellow
        status = "MED"
        icon = "🟡"
    elif percent >= 30:
        color = "\033[32m"   # Green
        status = "LOW"
        icon = "🟢"
    else:
        color = "\033[36m"   # Cyan
        status = "MIN"
        icon = "🔵"
    
    # Create high-precision progress bar
    segments = 20
    filled = int((percent / 100) * segments)
    bar = "█" * filled + "░" * (segments - filled)
    
    # Special warnings override
    if warning == 'auto-compact':
        status = "AUTO-COMPACT"
        icon = "🔄"
    elif warning == 'low':
        status = "CONTEXT-LOW"
        icon = "⚡"
    
    reset = "\033[0m"
    
    # Format tokens display
    if tokens > 1000:
        token_display = f"{tokens//1000}k"
    else:
        token_display = str(tokens)
    
    # Add reset prediction display
    reset_display = ""
    if reset_prediction:
        if reset_prediction == "imminent":
            reset_display = f" \033[31m→RESET!\033[0m"
        elif reset_prediction == "stable":
            reset_display = f" \033[32m→OK\033[0m"
        elif "msg" in reset_prediction:
            reset_display = f" \033[33m→{reset_prediction}\033[0m"
    
    # Compact display with clear labels and reset prediction
    return f"\033[90mCTX:\033[0m{color}[{bar}]{reset} \033[90m{percent:.1f}%\033[0m {icon} {status} \033[90m({token_display}t){reset_display}\033[0m"

def get_directory_display(workspace_data):
    """Get directory display name."""
    current_dir = workspace_data.get('current_dir', '')
    project_dir = workspace_data.get('project_dir', '')
    
    if current_dir and project_dir:
        if current_dir.startswith(project_dir):
            rel_path = current_dir[len(project_dir):].lstrip('/')
            return rel_path or os.path.basename(project_dir)
        else:
            return os.path.basename(current_dir)
    elif project_dir:
        return os.path.basename(project_dir)
    elif current_dir:
        return os.path.basename(current_dir)
    else:
        return "unknown"

def get_session_metrics(cost_data):
    """Get enhanced session metrics display with labels."""
    if not cost_data:
        return ""
    
    metrics = []
    
    # Cost with label
    cost_usd = cost_data.get('total_cost_usd', 0)
    if cost_usd > 0:
        if cost_usd >= 0.10:
            cost_color = "\033[31m"  # Red for expensive
        elif cost_usd >= 0.05:
            cost_color = "\033[33m"  # Yellow for moderate
        else:
            cost_color = "\033[32m"  # Green for cheap
        
        cost_str = f"{cost_usd*100:.0f}¢" if cost_usd < 0.01 else f"${cost_usd:.3f}"
        metrics.append(f"\033[90mCOST:\033[0m{cost_color}{cost_str}\033[0m")
    
    # Duration with better precision
    duration_ms = cost_data.get('total_duration_ms', 0)
    if duration_ms > 0:
        minutes = duration_ms / 60000
        seconds = (duration_ms % 60000) / 1000
        
        if minutes >= 30:
            duration_color = "\033[33m"  # Yellow for long sessions
        else:
            duration_color = "\033[32m"  # Green
        
        if minutes >= 1:
            duration_str = f"{int(minutes)}m{int(seconds)}s"
        elif seconds >= 10:
            duration_str = f"{int(seconds)}s"
        else:
            duration_str = f"{seconds:.1f}s"
        
        metrics.append(f"\033[90mTIME:\033[0m{duration_color}{duration_str}\033[0m")
    
    # Lines changed with more detail
    lines_added = cost_data.get('total_lines_added', 0)
    lines_removed = cost_data.get('total_lines_removed', 0)
    if lines_added > 0 or lines_removed > 0:
        net_lines = lines_added - lines_removed
        
        if net_lines > 0:
            lines_color = "\033[32m"  # Green for additions
            sign = "+"
        elif net_lines < 0:
            lines_color = "\033[31m"  # Red for deletions
            sign = ""
        else:
            lines_color = "\033[33m"  # Yellow for neutral
            sign = "±"
        
        metrics.append(f"\033[90mCODE:\033[0m{lines_color}{sign}{abs(net_lines)}L\033[0m")
        
        # Show breakdown if significant changes
        if lines_added > 10 or lines_removed > 10:
            metrics.append(f"\033[90m(+{lines_added}/-{lines_removed})\033[0m")
    
    return f" \033[90m│\033[0m {' '.join(metrics)}" if metrics else ""

def main():
    try:
        # Read JSON input from Claude Code
        data = json.load(sys.stdin)
        
        # Extract information
        model_name = data.get('model', {}).get('display_name', 'Claude')
        workspace = data.get('workspace', {})
        transcript_path = data.get('transcript_path', '')
        cost_data = data.get('cost', {})
        
        # Parse context usage
        context_info = parse_context_from_transcript(transcript_path)
        
        # Build status components
        context_display = get_context_display(context_info)
        directory = get_directory_display(workspace)
        session_metrics = get_session_metrics(cost_data)
        
        # Model display with context-aware coloring
        if context_info:
            percent = context_info.get('percent', 0)
            if percent >= 90:
                model_color = "\033[31m"  # Red
            elif percent >= 75:
                model_color = "\033[33m"  # Yellow
            else:
                model_color = "\033[32m"  # Green
            
            model_display = f"{model_color}[{model_name}]\033[0m"
        else:
            model_display = f"\033[94m[{model_name}]\033[0m"
        
        # Enhanced status line with clear sections
        sections = [
            f"{model_display}",
            f"\033[90mPROJ:\033[0m\033[93m{directory}\033[0m",
            f"{context_display}",
            session_metrics
        ]
        
        # Filter out empty sections
        status_line = " \033[90m│\033[0m ".join([s for s in sections if s.strip()])
        
        print(status_line)
        
    except Exception as e:
        # Fallback display on any error
        print(f"\033[94m[Claude]\033[0m \033[93m📁 {os.path.basename(os.getcwd())}\033[0m 🧠 \033[31m[Error: {str(e)[:20]}]\033[0m")

if __name__ == "__main__":
    main()