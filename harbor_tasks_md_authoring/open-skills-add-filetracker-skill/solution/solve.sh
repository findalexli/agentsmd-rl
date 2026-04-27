#!/usr/bin/env bash
set -euo pipefail

cd /workspace/open-skills

# Idempotency guard
if grep -qF "Automatically logs all incoming and outgoing chat messages to a SQLite database." "skills/chat-logger/SKILL.md" && grep -qF "description: Log all file changes (write, edit, delete) to a SQLite database for" "skills/file-tracker/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/chat-logger/SKILL.md b/skills/chat-logger/SKILL.md
@@ -0,0 +1,309 @@
+---
+name: chat-logger
+description: Log all chat messages (user and assistant) from all channels to a SQLite database for verbatim recall.
+---
+
+# Chat Logger
+
+Automatically logs all incoming and outgoing chat messages to a SQLite database. Essential for building a searchable chat history and auditing conversations.
+
+## When to use
+
+- When you need to remember exact wording of past conversations
+- Building a searchable chat history
+- Auditing conversations
+- The user asks to log chats
+
+## Required tools / APIs
+
+- Python standard library (sqlite3, datetime, json)
+- nanobot agent framework
+
+No external APIs required.
+
+## Installation
+
+```bash
+# Create the logging directory
+mkdir -p ~/.nanobot
+
+# Create the agent.py file with logging code
+cat > ~/.nanobot/agent.py << 'EOF'
+"""Custom agent with logging hooks for chat and file tracking."""
+
+import json
+import sqlite3
+from pathlib import Path
+from datetime import datetime
+from typing import Any
+
+from nanobot.agent.loop import AgentLoop
+from nanobot.bus.events import InboundMessage, OutboundMessage
+
+
+# Database setup
+DB_PATH = Path.home() / ".nanobot" / "chat_logs.db"
+
+
+def _get_db():
+    """Get database connection."""
+    conn = sqlite3.connect(str(DB_PATH))
+    conn.row_factory = sqlite3.Row
+    return conn
+
+
+def _init_db():
+    """Initialize database tables if they don't exist."""
+    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
+    conn = _get_db()
+    try:
+        # Chat messages table
+        conn.execute("""
+            CREATE TABLE IF NOT EXISTS messages (
+                id INTEGER PRIMARY KEY AUTOINCREMENT,
+                timestamp TEXT NOT NULL,
+                channel TEXT NOT NULL,
+                chat_id TEXT NOT NULL,
+                sender TEXT NOT NULL,
+                content TEXT,
+                message_type TEXT NOT NULL,
+                tools_used TEXT
+            )
+        """)
+        
+        # File changes table
+        conn.execute("""
+            CREATE TABLE IF NOT EXISTS file_changes (
+                id INTEGER PRIMARY KEY AUTOINCREMENT,
+                timestamp TEXT NOT NULL,
+                operation TEXT NOT NULL,
+                file_path TEXT NOT NULL,
+                content_preview TEXT,
+                user TEXT DEFAULT 'assistant'
+            )
+        """)
+        
+        conn.commit()
+    finally:
+        conn.close()
+
+
+# Initialize on import
+_init_db()
+
+
+class LoggingAgentLoop(AgentLoop):
+    """
+    Extended AgentLoop with automatic logging of:
+    - All chat messages (inbound and outbound)
+    - All file modifications (via tool execution hooks)
+    """
+    
+    def __init__(self, *args, **kwargs):
+        super().__init__(*args, **kwargs)
+        # Override the tools registry with a logging wrapper
+        self._original_tools = self.tools
+        self.tools = LoggingToolRegistry(self.tools, self._log_file_change)
+    
+    def _log_message(self, msg: InboundMessage | OutboundMessage, msg_type: str, tools_used: list | None = None):
+        """Log a message to the database."""
+        conn = _get_db()
+        try:
+            sender = msg.sender_id if isinstance(msg, InboundMessage) else "assistant"
+            conn.execute(
+                """INSERT INTO messages (timestamp, channel, chat_id, sender, content, message_type, tools_used)
+                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
+                (
+                    datetime.now().isoformat(),
+                    msg.channel,
+                    msg.chat_id,
+                    sender,
+                    msg.content[:5000] if msg.content else None,
+                    msg_type,
+                    json.dumps(tools_used) if tools_used else None,
+                )
+            )
+            conn.commit()
+        finally:
+            conn.close()
+    
+    def _log_file_change(self, operation: str, file_path: str, content_preview: str | None = None):
+        """Log a file change to the database."""
+        conn = _get_db()
+        try:
+            conn.execute(
+                """INSERT INTO file_changes (timestamp, operation, file_path, content_preview, user)
+                   VALUES (?, ?, ?, ?, ?)""",
+                (
+                    datetime.now().isoformat(),
+                    operation,
+                    file_path,
+                    content_preview[:500] if content_preview else None,
+                    "assistant",
+                )
+            )
+            conn.commit()
+        finally:
+            conn.close()
+    
+    async def _process_message(self, msg: InboundMessage, session_key: str | None = None):
+        """Override to log inbound messages before processing."""
+        # Log inbound message
+        self._log_message(msg, "inbound")
+        
+        # Call parent processing
+        response = await super()._process_message(msg, session_key)
+        
+        # Log outbound message (response)
+        if response:
+            self._log_message(response, "outbound")
+        
+        return response
+
+
+class LoggingToolRegistry:
+    """Wrapper around ToolRegistry that logs file operations."""
+    
+    def __init__(self, wrapped, file_callback):
+        self._wrapped = wrapped
+        self._file_callback = file_callback
+    
+    def __getattr__(self, name):
+        return getattr(self._wrapped, name)
+    
+    async def execute(self, tool_name: str, arguments: dict) -> Any:
+        """Execute a tool and log file operations."""
+        # Log file operations before execution
+        if tool_name in ("write_file", "edit_file"):
+            file_path = arguments.get("path", "")
+            if tool_name == "write_file":
+                self._file_callback("write", file_path, arguments.get("content", ""))
+            elif tool_name == "edit_file":
+                self._file_callback("edit", file_path, arguments.get("old_text", ""))
+        
+        # Execute the tool
+        result = await self._wrapped.execute(tool_name, arguments)
+        
+        return result
+
+
+def get_custom_agent():
+    """Return the custom agent class for use by nanobot."""
+    return LoggingAgentLoop
+EOF
+
+# Create the bootstrap runner
+cat > ~/.nanobot/run.py << 'EOF'
+#!/usr/bin/env python3
+"""
+Bootstrap script that patches nanobot with custom logging before running.
+Run this instead of 'nanobot' to enable logging.
+"""
+
+import os
+import sys
+from pathlib import Path
+
+# Change to ~/.nanobot so 'from agent import X' works
+NANOBOT_DIR = Path.home() / ".nanobot"
+os.chdir(NANOBOT_DIR)
+
+# Add custom agent to path
+sys.path.insert(0, str(NANOBOT_DIR))
+
+# Patch the module BEFORE nanobot.cli.commands is imported
+import nanobot.agent.loop
+
+# Import our custom logging agent
+from agent import LoggingAgentLoop
+
+# Replace in the module's namespace
+nanobot.agent.loop.AgentLoop = LoggingAgentLoop
+
+# Now run the actual CLI
+from nanobot.cli.commands import app
+
+if __name__ == "__main__":
+    app()
+EOF
+
+chmod +x ~/.nanobot/run.py
+```
+
+## Usage
+
+Instead of running `nanobot agent`, run:
+
+```bash
+python ~/.nanobot/run.py agent -m "Your message"
+python ~/.nanobot/run.py gateway
+```
+
+## Querying Logs
+
+```python
+import sqlite3
+
+conn = sqlite3.connect('/root/.nanobot/chat_logs.db')
+conn.row_factory = sqlite3.Row
+
+# Get all messages
+cursor = conn.execute('SELECT * FROM messages ORDER BY timestamp DESC')
+
+# Get messages from a specific channel
+cursor = conn.execute(
+    'SELECT * FROM messages WHERE channel = ? ORDER BY timestamp DESC',
+    ('telegram',)
+)
+
+# Get conversation history for a specific chat
+cursor = conn.execute(
+    'SELECT * FROM messages WHERE channel = ? AND chat_id = ? ORDER BY timestamp',
+    ('telegram', '123456789')
+)
+
+for row in cursor:
+    print(f"[{row['timestamp']}] {row['sender']}: {row['content'][:100]}...")
+
+conn.close()
+```
+
+## Database Schema
+
+**messages table:**
+- `id` - Primary key
+- `timestamp` - ISO format datetime
+- `channel` - Source channel (cli, telegram, discord, etc.)
+- `chat_id` - Chat identifier
+- `sender` - user or assistant
+- `content` - Message text (truncated to 5000 chars)
+- `message_type` - inbound or outbound
+- `tools_used` - JSON array of tool names used (if any)
+
+## Agent prompt
+
+```text
+You have chat logging capability. When the user asks to:
+- Search past conversations
+- Find a specific message
+- Review chat history
+
+Use the SQLite database at ~/.nanobot/chat_logs.db to query message history.
+Tables: messages (columns: timestamp, channel, chat_id, sender, content, message_type, tools_used).
+
+Always use python with sqlite3 to query, then present relevant results to the user.
+```
+
+## Troubleshooting
+
+**No messages being logged:**
+- Ensure you're using `python ~/.nanobot/run.py` instead of `nanobot`
+- Check that the database file exists: `ls -la ~/.nanobot/chat_logs.db`
+
+**Database errors:**
+- Check file permissions: `chmod 755 ~/.nanobot/`
+
+## See also
+
+- [file-tracker.md](file-tracker.md) — Track file modifications
+- [memory.md](../memory/SKILL.md) — Long-term memory management
diff --git a/skills/file-tracker/SKILL.md b/skills/file-tracker/SKILL.md
@@ -0,0 +1,100 @@
+---
+name: file-tracker
+description: Log all file changes (write, edit, delete) to a SQLite database for debugging and audit. Use when: (1) Tracking code changes, (2) Debugging issues, (3) Auditing file modifications, or (4) The user asks to track file changes.
+---
+
+# File Tracker
+
+Log every file change (write, edit, delete) to a SQLite database for debugging and audit trail.
+
+## Database
+
+**Location:** `/root/.nanobot/workspace/chat_logs.db`
+
+**Schema:**
+```sql
+CREATE TABLE file_changes (
+  id INTEGER PRIMARY KEY AUTOINCREMENT,
+  timestamp TEXT NOT NULL,
+  channel TEXT,
+  chat_id TEXT,
+  action TEXT NOT NULL,  -- 'write', 'edit', 'delete'
+  file_path TEXT NOT NULL,
+  old_content TEXT,      -- for edits/deletes
+  new_content TEXT       -- for writes/edits
+);
+
+CREATE INDEX idx_file_path ON file_changes(file_path);
+CREATE INDEX idx_timestamp ON file_changes(timestamp);
+```
+
+## Usage
+
+After each file operation, log the change:
+
+```python
+import sqlite3
+from datetime import datetime
+
+def log_file_change(channel: str, chat_id: str, action: str, file_path: str, old_content: str = None, new_content: str = None):
+    conn = sqlite3.connect('/root/.nanobot/workspace/chat_logs.db')
+    conn.execute(
+        "INSERT INTO file_changes (timestamp, channel, chat_id, action, file_path, old_content, new_content) VALUES (?, ?, ?, ?, ?, ?, ?)",
+        (datetime.utcnow().isoformat(), channel, chat_id, action, file_path, old_content, new_content)
+    )
+    conn.commit()
+    conn.close()
+
+# Log a write operation
+log_file_change("telegram", "7676486207", "write", "/path/to/file.md", None, "# New content")
+
+# Log an edit operation
+log_file_change("telegram", "7676486207", "edit", "/path/to/file.md", "old text", "new text")
+
+# Log a delete operation
+log_file_change("telegram", "7676486207", "delete", "/path/to/file.md", "deleted content", None)
+```
+
+## When to Log
+
+Log after every:
+1. `write_file` operation - action: "write"
+2. `edit_file` operation - action: "edit" (capture old and new content)
+3. `delete_file` operation - action: "delete"
+
+## Query Examples
+
+```python
+# Get recent changes to a file
+def get_file_history(file_path: str, limit: int = 20):
+    conn = sqlite3.connect('/root/.nanobot/workspace/chat_logs.db')
+    cursor = conn.execute(
+        "SELECT timestamp, action, old_content, new_content FROM file_changes WHERE file_path=? ORDER BY id DESC LIMIT ?",
+        (file_path, limit)
+    )
+    results = cursor.fetchall()
+    conn.close()
+    return results
+
+# Get all changes from a session/channel
+def get_session_changes(channel: str, chat_id: str):
+    conn = sqlite3.connect('/root/.nanobot/workspace/chat_logs.db')
+    cursor = conn.execute(
+        "SELECT timestamp, action, file_path, new_content FROM file_changes WHERE channel=? AND chat_id=? ORDER BY id DESC",
+        (channel, chat_id)
+    )
+    results = cursor.fetchall()
+    conn.close()
+    return results
+
+# Search for changes to files matching a pattern
+def search_file_changes(pattern: str):
+    conn = sqlite3.connect('/root/.nanobot/workspace/chat_logs.db')
+    cursor = conn.execute(
+        "SELECT timestamp, channel, chat_id, action, file_path FROM file_changes WHERE file_path LIKE ? ORDER BY id DESC",
+        (f'%{pattern}%',)
+    )
+    results = cursor.fetchall()
+    conn.close()
+    return results
+```
PATCH

echo "Gold patch applied."
