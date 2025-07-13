# Database Structure - SyncaraBot

## Overview
SyncaraBot menggunakan MongoDB sebagai database utama dengan Motor (AsyncIOMotorClient) untuk operasi asynchronous. Database ini dirancang untuk menyimpan semua data yang diperlukan untuk operasi bot, pembelajaran AI, dan manajemen user/group.

## Database Configuration
- **Database Name**: `SyncaraBot`
- **Connection**: MongoDB melalui `MONGO_URI` dari config
- **Driver**: Motor (AsyncIOMotorClient) untuk Python async operations

## Collection Structure

### 1. Core Collections

#### `users`
Menyimpan informasi dan data pembelajaran user.
```javascript
{
  _id: ObjectId,
  user_id: Number,           // Telegram user ID
  username: String,          // Telegram username
  first_name: String,        // First name
  last_name: String,         // Last name
  last_interaction: Date,    // Last interaction time
  first_seen: Date,          // First time seen
  interaction_count: Number, // Total interactions
  preferences: {             // User preferences
    communication_style: String,     // "default", "formal", "casual", "friendly"
    response_length: String,         // "short", "medium", "long"
    emoji_usage: Boolean,           // Whether to use emojis
    language_preference: String,    // "id", "en", "mixed"
    topics_of_interest: Array,      // Array of topics
    avoided_topics: Array          // Array of avoided topics
  },
  conversation_history: [{    // Limited to 50 entries
    timestamp: Date,
    message: String,
    response: String,
    context: Object
  }],
  learning_data: {           // AI learning data
    frequently_asked: Array,
    successful_responses: Array,
    user_feedback: Array
  },
  ai_learning_patterns: {    // AI learning patterns
    question_types: Object,
    topics: Object,
    time_patterns: Object,
    response_preferences: Object,
    last_updated: Date
  },
  ai_learning_quality: [{    // Limited to 100 entries
    timestamp: Date,
    message: String,
    response: String,
    response_length: Number,
    has_emoji: Boolean,
    feedback: String
  }],
  notes: String,             // Admin notes
  personality_notes: String  // AI personality notes
}
```

#### `groups`
Menyimpan informasi group/chat.
```javascript
{
  _id: ObjectId,
  chat_id: Number,           // Telegram chat ID
  title: String,             // Group title
  type: String,              // "group", "supergroup", "channel"
  member_count: Number,      // Member count
  created_at: Date,          // First seen
  updated_at: Date,          // Last updated
  settings: {                // Group settings
    welcome_message: String,
    rules: String,
    auto_moderation: Boolean,
    allowed_commands: Array
  }
}
```

### 2. Feature Collections

#### `canvas_files`
Menyimpan virtual files dari Canvas Management.
```javascript
{
  _id: ObjectId,
  filename: String,          // File name
  filetype: String,          // File type (txt, py, js, etc.)
  content: String,           // File content
  chat_id: Number,           // Associated chat ID
  created_at: Date,          // Creation time
  updated_at: Date,          // Last update time
  history: [{                // File history
    content: String,
    timestamp: Date
  }],
  auto_exported: Boolean     // Whether auto-exported
}
```

#### `image_generations`
Menyimpan history image generation.
```javascript
{
  _id: ObjectId,
  user_id: Number,           // User who requested
  chat_id: Number,           // Chat where requested
  prompt: String,            // Image prompt
  advanced_params: {         // Advanced parameters
    image: String,
    mask: String,
    seed: Number,
    resolution: String,
    style_type: String,
    aspect_ratio: String,
    magic_prompt_option: String,
    style_reference_images: Array
  },
  created_at: Date,          // Request time
  completed_at: Date,        // Completion time
  success: Boolean,          // Success status
  image_url: String,         // Generated image URL
  error_message: String,     // Error message if failed
  delivered: Boolean,        // Whether delivered to user
  delivered_at: Date,        // Delivery time
  delivery_error: String     // Delivery error if any
}
```

#### `user_warnings`
Menyimpan user warnings.
```javascript
{
  _id: ObjectId,
  user_id: Number,           // Warned user ID
  chat_id: Number,           // Chat where warned
  warned_by: Number,         // Admin who warned
  reason: String,            // Warning reason
  created_at: Date           // Warning time
}
```

#### `ban_records`
Menyimpan ban records.
```javascript
{
  _id: ObjectId,
  user_id: Number,           // Banned user ID
  chat_id: Number,           // Chat where banned
  banned_by: Number,         // Admin who banned
  reason: String,            // Ban reason
  duration_minutes: Number,  // Ban duration (null for permanent)
  created_at: Date,          // Ban time
  is_active: Boolean,        // Whether ban is active
  unbanned_at: Date,         // Unban time
  unbanned_by: Number        // Admin who unbanned
}
```

#### `mute_records`
Menyimpan mute records.
```javascript
{
  _id: ObjectId,
  user_id: Number,           // Muted user ID
  chat_id: Number,           // Chat where muted
  muted_by: Number,          // Admin who muted
  reason: String,            // Mute reason
  duration_minutes: Number,  // Mute duration
  created_at: Date,          // Mute time
  expires_at: Date,          // Expiration time
  is_active: Boolean,        // Whether mute is active
  unmuted_at: Date,          // Unmute time
  unmuted_by: Number         // Admin who unmuted
}
```

#### `user_permissions`
Menyimpan permission changes (promote/demote).
```javascript
{
  _id: ObjectId,
  user_id: Number,           // User ID
  chat_id: Number,           // Chat ID
  changed_by: Number,        // Admin who made change
  action: String,            // "promote", "demote", "kick", etc.
  title: String,             // Admin title (for promotions)
  created_at: Date,          // Change time
  timestamp: Date,           // Alternative timestamp field
  reason: String,            // Reason for action
  performed_by: Number       // Alternative field for performed_by
}
```

#### `workflow_definitions`
Menyimpan workflow definitions untuk multi-step processing.
```javascript
{
  _id: ObjectId,
  workflow_id: String,       // Unique workflow ID
  name: String,              // Workflow name
  description: String,       // Description
  steps: [{                  // Workflow steps
    id: String,
    name: String,
    handler: String,
    params: Object,
    dependencies: Array,
    timeout: Number,
    retry_count: Number,
    retry_delay: Number,
    condition: String
  }],
  global_timeout: Number,    // Global timeout
  max_parallel_steps: Number, // Max parallel steps
  auto_retry: Boolean,       // Auto retry
  metadata: Object,          // Additional metadata
  created_at: Date,          // Creation time
  updated_at: Date           // Last update time
}
```

#### `workflow_executions`
Menyimpan workflow executions.
```javascript
{
  _id: ObjectId,
  execution_id: String,      // Unique execution ID
  workflow_id: String,       // Associated workflow ID
  status: String,            // "created", "running", "completed", "failed"
  current_step: String,      // Current step ID
  context: Object,           // Shared context
  started_at: Date,          // Start time
  completed_at: Date,        // Completion time
  user_id: Number,           // User who triggered
  chat_id: Number,           // Chat where triggered
  message_id: Number,        // Message ID
  progress: Number,          // Progress percentage (0-100)
  steps: [{                  // Step states
    id: String,
    name: String,
    status: String,
    attempts: Number,
    started_at: Date,
    completed_at: Date,
    result: {
      success: Boolean,
      data: Mixed,
      error: String,
      execution_time: Number,
      metadata: Object
    }
  }]
}
```

#### `todos_{chat_id}`
Menyimpan todo items per chat (dynamic collection name).
```javascript
{
  _id: ObjectId,
  description: String,       // Todo description
  status: String,            // "pending", "completed"
  created_at: Date,          // Creation time
  created_by: Number,        // User who created
  chat_id: Number,           // Chat ID
  completed_at: Date,        // Completion time
  completed_by: Number,      // User who completed
  updated_at: Date,          // Last update time
  updated_by: Number         // User who updated
}
```

### 3. System Collections

#### `system_logs`
Menyimpan system logs.
```javascript
{
  _id: ObjectId,
  timestamp: Date,           // Log timestamp
  level: String,             // "info", "warning", "error"
  module: String,            // Module name
  message: String,           // Log message
  metadata: Object           // Additional metadata
}
```

#### `error_logs`
Menyimpan error logs.
```javascript
{
  _id: ObjectId,
  timestamp: Date,           // Error timestamp
  module: String,            // Module name
  error: String,             // Error message
  traceback: String,         // Error traceback
  user_id: Number,           // Associated user ID
  chat_id: Number            // Associated chat ID
}
```

#### `performance_metrics`
Menyimpan performance metrics.
```javascript
{
  _id: ObjectId,
  timestamp: Date,           // Metric timestamp
  metric_name: String,       // Metric name
  value: Number,             // Metric value
  unit: String,              // Unit (ms, bytes, etc.)
  metadata: Object           // Additional metadata
}
```

### 4. AI & Learning Collections

#### `ai_learning`
Menyimpan AI learning data.
```javascript
{
  _id: ObjectId,
  user_id: Number,           // User ID
  patterns: Object,          // Learning patterns
  created_at: Date,          // Creation time
  updated_at: Date           // Last update time
}
```

#### `assistant_memory`
Menyimpan assistant memory data.
```javascript
{
  _id: ObjectId,
  user_id: Number,           // User ID
  memory_type: String,       // Type of memory
  content: Object,           // Memory content
  created_at: Date,          // Creation time
  expires_at: Date           // Expiration time
}
```

#### `conversation_history`
Menyimpan detailed conversation history.
```javascript
{
  _id: ObjectId,
  user_id: Number,           // User ID
  chat_id: Number,           // Chat ID
  message: String,           // User message
  response: String,          // Bot response
  context: Object,           // Context data
  timestamp: Date,           // Timestamp
  metadata: Object           // Additional metadata
}
```

### 5. Cache & Session Collections

#### `pyrogram_cache`
Menyimpan Pyrogram cache data.
```javascript
{
  _id: ObjectId,
  cache_key: String,         // Cache key
  cache_data: Object,        // Cached data
  created_at: Date,          // Creation time
  expires_at: Date,          // Expiration time
  hit_count: Number          // Hit count
}
```

#### `pyrogram_sessions`
Menyimpan Pyrogram session data.
```javascript
{
  _id: ObjectId,
  session_name: String,      // Session name
  session_data: Object,      // Session data
  created_at: Date,          // Creation time
  last_used: Date,           // Last used time
  is_active: Boolean         // Whether active
}
```

### 6. Autonomous AI Collections

#### `autonomous_tasks`
Menyimpan autonomous AI tasks.
```javascript
{
  _id: ObjectId,
  task_id: String,           // Task ID
  task_type: String,         // Task type
  parameters: Object,        // Task parameters
  status: String,            // Task status
  created_at: Date,          // Creation time
  scheduled_at: Date,        // Scheduled time
  completed_at: Date,        // Completion time
  result: Object             // Task result
}
```

#### `user_patterns`
Menyimpan user behavior patterns.
```javascript
{
  _id: ObjectId,
  user_id: Number,           // User ID
  pattern_type: String,      // Pattern type
  pattern_data: Object,      // Pattern data
  confidence: Number,        // Confidence score
  created_at: Date,          // Creation time
  updated_at: Date           // Last update time
}
```

#### `scheduled_actions`
Menyimpan scheduled actions.
```javascript
{
  _id: ObjectId,
  action_id: String,         // Action ID
  action_type: String,       // Action type
  parameters: Object,        // Action parameters
  scheduled_at: Date,        // Scheduled time
  executed_at: Date,         // Execution time
  status: String,            // Action status
  result: Object             // Action result
}
```

## Database Indexes

### Performance Indexes
- `users.user_id` (unique)
- `users.username`
- `users.last_interaction`
- `groups.chat_id` (unique)
- `groups.group_type`
- `canvas_files.chat_id + canvas_files.filename` (unique compound)
- `canvas_files.created_at`
- `workflow_executions.execution_id` (unique)
- `workflow_executions.user_id + workflow_executions.status` (compound)
- `workflow_executions.created_at`
- `image_generations.user_id`
- `image_generations.created_at`
- `user_permissions.user_id + user_permissions.chat_id` (unique compound)
- `system_logs.timestamp`
- `system_logs.level`
- `system_logs.module`

## Database Operations

### Initialization
```python
from syncara.database import initialize_database
await initialize_database()
```

### Cleanup
```python
from syncara.database import database_manager
await database_manager.cleanup_old_data(days_old=30)
```

### Statistics
```python
from syncara.database import database_manager
stats = await database_manager.get_database_stats()
```

### Backup
```python
from syncara.database import database_manager
await database_manager.backup_collection('users', 'users_backup.json')
```

## Helper Functions

### User Data
```python
from syncara.database import get_user_data
user_data = await get_user_data(user_id)
```

### Group Data
```python
from syncara.database import get_group_data
group_data = await get_group_data(chat_id)
```

### Logging
```python
from syncara.database import log_system_event, log_error, record_performance_metric

await log_system_event("info", "module_name", "Event message")
await log_error("module_name", "Error message", traceback_str)
await record_performance_metric("response_time", 150.5, "ms")
```

## Data Retention Policy

### Automatic Cleanup
- **System Logs**: 30 days retention
- **Error Logs**: 30 days retention
- **Canvas History**: 30 days retention
- **Workflow Executions**: 30 days retention (completed/failed only)
- **Pyrogram Cache**: Based on TTL expiration

### Manual Cleanup
- **Conversation History**: Limited to 50 entries per user
- **AI Learning Quality**: Limited to 100 entries per user
- **User Feedback**: No automatic cleanup (admin managed)

## Security Considerations

### Data Protection
- User IDs are stored as numbers (Telegram user IDs)
- No sensitive personal data stored
- All database operations are logged
- Error handling prevents data leakage

### Access Control
- Database access through centralized modules only
- No direct database access from shortcode handlers
- All operations use proper error handling
- Sensitive operations require admin privileges

## Monitoring & Maintenance

### Performance Monitoring
- Database query performance tracked
- Collection sizes monitored
- Index usage analyzed
- Automatic cleanup scheduled

### Health Checks
- Database connectivity checks
- Collection integrity verification
- Index optimization recommendations
- Storage usage monitoring

## Migration & Backup

### Database Migration
```python
# Future migrations should be handled through database_manager
# with proper versioning and rollback capabilities
```

### Backup Strategy
- Regular automated backups
- Collection-specific backups
- Point-in-time recovery capability
- Data export functionality

## Usage Examples

### Canvas Management
```python
from syncara.modules.canvas_manager import canvas_manager

# Create file with database persistence
file = await canvas_manager.create_file("test.py", "python", "print('Hello')", chat_id=123)

# Get file from database
file = await canvas_manager.get_file("test.py", chat_id=123)

# Update file (automatically saved to database)
await canvas_manager.update_file("test.py", "print('Updated')", chat_id=123)
```

### Image Generation Tracking
```python
from syncara.shortcode.image_generation import image_shortcode

# Generate image (automatically tracked in database)
result = await image_shortcode.image_gen(client, message, "a beautiful sunset")

# Get user's image history
history = await image_shortcode._get_user_image_history(user_id, limit=10)
```

### User Management
```python
from syncara.shortcode.users_management import users_shortcode

# Ban user (automatically recorded in database)
await users_shortcode.ban_user(client, message, "username")

# Get user statistics
stats = await users_shortcode._get_user_stats(user_id, chat_id)
```

## Notes

1. **Asynchronous Operations**: All database operations are asynchronous using Motor
2. **Error Handling**: Comprehensive error handling with logging
3. **Data Consistency**: Proper data validation and consistency checks
4. **Performance**: Optimized with appropriate indexes and query patterns
5. **Scalability**: Designed to handle growing data volumes
6. **Maintenance**: Built-in cleanup and maintenance functions 