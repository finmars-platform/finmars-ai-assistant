import os
from datetime import datetime

try:
    from zoneinfo import ZoneInfo
except ImportError:
    # Fallback for Python < 3.9
    from datetime import timezone

    ZoneInfo = None

from langchain_core.prompts import StringPromptTemplate


def build_system_msg(sys_msg: StringPromptTemplate, get_string: bool = False) -> StringPromptTemplate | str:
    # Get timezone from environment variable, default to UTC
    tz_name = os.getenv("TZ", "UTC")

    # Get current date, time, and timezone
    try:
        if ZoneInfo:
            tz = ZoneInfo(tz_name)
            current_time = datetime.now(tz)
        else:
            # Fallback for older Python versions
            from datetime import timezone

            current_time = datetime.now(timezone.utc)
            tz_name = "UTC"  # Force UTC for fallback
    except Exception:
        # If timezone is invalid, fall back to UTC
        if ZoneInfo:
            tz = ZoneInfo("UTC")
            current_time = datetime.now(tz)
            tz_name = "UTC"
        else:
            from datetime import timezone

            current_time = datetime.now(timezone.utc)
            tz_name = "UTC"

    # Format the datetime information
    datetime_info = f"\n\n### Current date and time: {current_time.strftime('%Y-%m-%d %H:%M:%S')} {tz_name}"

    # Add datetime info to the system message content
    if hasattr(sys_msg, "content"):
        sys_msg.content = sys_msg.content + datetime_info
        if get_string:
            return sys_msg.content

    elif hasattr(sys_msg, "prompt") and hasattr(sys_msg.prompt, "template"):
        sys_msg.prompt.template = sys_msg.prompt.template + datetime_info
        if get_string:
            return sys_msg.prompt.template

    return sys_msg
