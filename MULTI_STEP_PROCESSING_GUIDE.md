# 🚀 Multi-Step Processing System Guide

Sistem Multi-Step Processing memungkinkan Anda membuat workflow kompleks dengan langkah-langkah yang saling terkait, eksekusi paralel, state management, dan error handling yang robust.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Basic Concepts](#basic-concepts)
3. [Getting Started](#getting-started)
4. [Workflow Creation](#workflow-creation)
5. [Step Types](#step-types)
6. [Built-in Handlers](#built-in-handlers)
7. [Shortcode Usage](#shortcode-usage)
8. [Advanced Features](#advanced-features)
9. [Error Handling](#error-handling)
10. [Best Practices](#best-practices)
11. [Examples](#examples)

## 🎯 Overview

Multi-Step Processing System adalah framework untuk membuat dan menjalankan workflow yang kompleks dengan fitur-fitur canggih:

### ✨ Key Features

- **🔄 Sequential & Parallel Execution**: Jalankan step secara berurutan atau paralel
- **📊 State Management**: Shared context antar steps
- **🔁 Retry Mechanism**: Automatic retry dengan backoff
- **⏱️ Timeout Handling**: Timeout per step dan global
- **🎯 Conditional Steps**: Step yang berjalan berdasarkan kondisi
- **📈 Progress Tracking**: Real-time progress monitoring
- **🗃️ Persistent Storage**: State disimpan ke database
- **🔧 Custom Handlers**: Buat handler custom untuk kebutuhan spesifik
- **📝 Shortcode Integration**: Mudah digunakan dari AI response

## 📚 Basic Concepts

### Workflow
Workflow adalah kumpulan steps yang saling terkait untuk mencapai tujuan tertentu.

### Step
Step adalah unit terkecil dalam workflow yang menjalankan satu tugas spesifik.

### Handler
Handler adalah function yang mengeksekusi logic dari sebuah step.

### Context
Context adalah shared state yang bisa diakses oleh semua steps dalam workflow.

### Dependencies
Dependencies menentukan urutan eksekusi steps.

## 🚀 Getting Started

### Import Module

```python
from syncara.modules.multi_step_processor import multi_step_processor
```

### Create Simple Workflow

```python
# Create workflow
workflow_id = multi_step_processor.create_workflow(
    name="My First Workflow",
    description="Simple workflow example"
)

# Add steps
step1 = multi_step_processor.add_step(
    workflow_id=workflow_id,
    name="Log Message",
    handler="log",
    params={"message": "Hello World!", "level": "info"}
)

step2 = multi_step_processor.add_step(
    workflow_id=workflow_id,
    name="Wait 2 seconds",
    handler="delay",
    params={"seconds": 2},
    dependencies=[step1]
)

# Execute workflow
execution_id = await multi_step_processor.execute_workflow(
    workflow_id=workflow_id
)
```

## 🔧 Workflow Creation

### Create Workflow

```python
workflow_id = multi_step_processor.create_workflow(
    name="Data Processing Pipeline",
    description="Process user data and send notifications",
    global_timeout=1800,  # 30 minutes
    max_parallel_steps=5,
    auto_retry=True,
    metadata={"version": "1.0", "author": "AERIS"}
)
```

### Add Steps

```python
step_id = multi_step_processor.add_step(
    workflow_id=workflow_id,
    name="Process Data",
    handler="database_operation",
    params={
        "operation": "find",
        "collection": "users",
        "query": {"active": True}
    },
    dependencies=["previous_step_id"],
    timeout=300,  # 5 minutes
    retry_count=3,
    retry_delay=5,
    condition="context.get('should_process') == True"
)
```

## 🎯 Step Types

### 1. Sequential Steps
Steps yang berjalan berurutan dengan dependencies.

```python
step1 = multi_step_processor.add_step(
    workflow_id=workflow_id,
    name="Step 1",
    handler="log",
    params={"message": "First step"}
)

step2 = multi_step_processor.add_step(
    workflow_id=workflow_id,
    name="Step 2",
    handler="log",
    params={"message": "Second step"},
    dependencies=[step1]  # Depends on step1
)
```

### 2. Parallel Steps
Steps yang berjalan bersamaan.

```python
# All these steps will run in parallel
for i in range(3):
    multi_step_processor.add_step(
        workflow_id=workflow_id,
        name=f"Parallel Task {i+1}",
        handler="delay",
        params={"seconds": 1}
        # No dependencies = parallel execution
    )
```

### 3. Conditional Steps
Steps yang berjalan berdasarkan kondisi.

```python
multi_step_processor.add_step(
    workflow_id=workflow_id,
    name="Conditional Step",
    handler="send_message",
    params={"text": "Condition met!"},
    condition="context.get('user_count') > 10"
)
```

## 🔨 Built-in Handlers

### 1. Basic Handlers

#### `delay`
```python
params = {"seconds": 5}
```

#### `log`
```python
params = {
    "message": "Log message",
    "level": "info"  # info, warning, error
}
```

#### `notification`
```python
params = {
    "message": "Notification message",
    "type": "success"  # info, warning, error, success
}
```

### 2. Context Handlers

#### `set_context`
```python
params = {
    "key": "user_name",
    "value": "AERIS"
}
```

#### `get_context`
```python
params = {
    "key": "user_name"
}
```

#### `condition_check`
```python
params = {
    "condition": "context.get('count') > 5"
}
```

### 3. Communication Handlers

#### `send_message`
```python
params = {
    "text": "Hello {context.user_name}!",
    "chat_id": 123456789  # Optional, uses execution chat_id if not provided
}
```

#### `execute_shortcode`
```python
params = {
    "shortcode": "GROUP:PIN_MESSAGE",
    "params": "message_id"
}
```

### 4. Data Handlers

#### `database_operation`
```python
# Find
params = {
    "operation": "find",
    "collection": "users",
    "query": {"active": True}
}

# Insert
params = {
    "operation": "insert",
    "collection": "logs",
    "data": {"message": "Log entry", "timestamp": "2024-01-01"}
}

# Update
params = {
    "operation": "update",
    "collection": "users",
    "query": {"id": 123},
    "data": {"last_seen": "2024-01-01"}
}

# Delete
params = {
    "operation": "delete",
    "collection": "temp_data",
    "query": {"expired": True}
}
```

#### `file_operation`
```python
# Read file
params = {
    "operation": "read",
    "file_path": "/path/to/file.txt"
}

# Write file
params = {
    "operation": "write",
    "file_path": "/path/to/output.txt",
    "content": "File content"
}

# Append to file
params = {
    "operation": "append",
    "file_path": "/path/to/log.txt",
    "content": "New log entry\n"
}

# Delete file
params = {
    "operation": "delete",
    "file_path": "/path/to/temp.txt"
}
```

#### `api_call`
```python
params = {
    "url": "https://api.example.com/data",
    "method": "POST",
    "headers": {"Authorization": "Bearer token"},
    "data": {"key": "value"}
}
```

### 5. Advanced Handlers

#### `parallel_group`
```python
params = {
    "tasks": [
        {
            "name": "Task 1",
            "handler": "log",
            "params": {"message": "Parallel task 1"}
        },
        {
            "name": "Task 2",
            "handler": "delay",
            "params": {"seconds": 2}
        }
    ]
}
```

## 📝 Shortcode Usage

### Basic Shortcodes

#### Create Workflow
```
[MULTISTEP:CREATE_WORKFLOW:My Workflow:Description:1800:5]
```

#### Add Step
```
[MULTISTEP:ADD_STEP:workflow_id:Step Name:handler:{"param":"value"}:dependency1,dependency2:300]
```

#### Execute Workflow
```
[MULTISTEP:EXECUTE:workflow_id:{"context_key":"context_value"}]
```

#### Check Status
```
[MULTISTEP:STATUS:execution_id]
```

#### Get Progress
```
[MULTISTEP:PROGRESS:execution_id]
```

### Management Shortcodes

#### List Workflows
```
[MULTISTEP:LIST_WORKFLOWS:]
```

#### List Executions
```
[MULTISTEP:LIST_EXECUTIONS:running]
```

#### Cancel Execution
```
[MULTISTEP:CANCEL:execution_id]
```

#### Pause/Resume
```
[MULTISTEP:PAUSE:execution_id]
[MULTISTEP:RESUME:execution_id]
```

### Advanced Shortcodes

#### Quick Workflow
```
[MULTISTEP:QUICK_WORKFLOW:Quick Test:[{"name":"Log","handler":"log","params":{"message":"Quick test"}}]]
```

#### Batch Process
```
[MULTISTEP:BATCH_PROCESS:log:[{"message":"Item 1"},{"message":"Item 2"}]:3]
```

#### Scheduled Workflow
```
[MULTISTEP:SCHEDULED_WORKFLOW:workflow_id:300:{"delay":"5 minutes"}]
```

#### Template Workflow
```
[MULTISTEP:TEMPLATE_WORKFLOW:message_sequence:{"welcome_text":"Welcome!","delay":3}]
```

## 🔧 Advanced Features

### 1. Custom Handlers

```python
async def custom_handler(step, execution):
    """Custom step handler"""
    params = step.params
    context = execution.context
    
    # Your custom logic here
    result = f"Processed {params.get('data')}"
    
    # Update context
    context['custom_result'] = result
    
    return StepResult(success=True, data=result)

# Register handler
multi_step_processor.register_handler("custom_handler", custom_handler)
```

### 2. Context Variables in Text

```python
# Context variables will be replaced in text
params = {
    "text": "Hello {context.user_name}! You have {context.message_count} messages."
}
```

### 3. Progress Monitoring

```python
# Get real-time progress
progress = multi_step_processor.get_execution_progress(execution_id)
print(f"Progress: {progress['progress']:.1f}%")
print(f"Current step: {progress['current_step']}")
```

### 4. Workflow Templates

```python
# Pre-defined templates
templates = {
    'message_sequence': 'Send welcome -> delay -> send follow-up',
    'data_processing': 'Load data -> process -> save results',
    'notification_flow': 'Send notification -> log event'
}
```

## 🚨 Error Handling

### Automatic Retry

```python
multi_step_processor.add_step(
    workflow_id=workflow_id,
    name="Retry Step",
    handler="api_call",
    params={"url": "https://api.example.com"},
    retry_count=3,      # Retry 3 times
    retry_delay=5       # Wait 5 seconds between retries
)
```

### Timeout Handling

```python
multi_step_processor.add_step(
    workflow_id=workflow_id,
    name="Long Running Task",
    handler="file_operation",
    params={"operation": "read", "file_path": "large_file.txt"},
    timeout=60          # 60 seconds timeout
)
```

### Error Recovery

```python
# Add error recovery step
multi_step_processor.add_step(
    workflow_id=workflow_id,
    name="Error Recovery",
    handler="log",
    params={"message": "Recovering from error", "level": "warning"},
    condition="context.get('error_occurred') == True"
)
```

## 💡 Best Practices

### 1. Workflow Design

- **Keep steps atomic**: Each step should do one thing well
- **Use meaningful names**: Clear step names help debugging
- **Set appropriate timeouts**: Prevent hanging workflows
- **Handle errors gracefully**: Always plan for failure scenarios

### 2. Performance Optimization

- **Use parallel execution**: For independent tasks
- **Limit parallel steps**: Don't overwhelm the system
- **Set reasonable timeouts**: Balance between patience and efficiency
- **Clean up resources**: Remove completed executions periodically

### 3. State Management

- **Use context wisely**: Share data between steps efficiently
- **Avoid large context**: Keep context data lightweight
- **Validate context**: Check context values before using them

### 4. Error Handling

- **Set retry policies**: Configure appropriate retry counts
- **Use exponential backoff**: Increase delay between retries
- **Log errors properly**: Help with debugging and monitoring
- **Plan for partial failures**: Handle scenarios where some steps fail

## 📖 Examples

### Example 1: User Onboarding Workflow

```python
# Create onboarding workflow
workflow_id = multi_step_processor.create_workflow(
    name="User Onboarding",
    description="Complete user onboarding process"
)

# Welcome message
step1 = multi_step_processor.add_step(
    workflow_id=workflow_id,
    name="Send Welcome",
    handler="send_message",
    params={"text": "Welcome to SyncaraBot! 🎉"}
)

# Wait for user to settle
step2 = multi_step_processor.add_step(
    workflow_id=workflow_id,
    name="Wait",
    handler="delay",
    params={"seconds": 5},
    dependencies=[step1]
)

# Send tutorial
step3 = multi_step_processor.add_step(
    workflow_id=workflow_id,
    name="Send Tutorial",
    handler="send_message",
    params={"text": "Let me show you how to use the bot..."},
    dependencies=[step2]
)

# Update user status
step4 = multi_step_processor.add_step(
    workflow_id=workflow_id,
    name="Update Status",
    handler="database_operation",
    params={
        "operation": "update",
        "collection": "users",
        "query": {"id": "{context.user_id}"},
        "data": {"onboarded": True}
    },
    dependencies=[step3]
)

# Execute for specific user
execution_id = await multi_step_processor.execute_workflow(
    workflow_id=workflow_id,
    context={"user_id": 123456789},
    user_id=123456789,
    chat_id=123456789
)
```

### Example 2: Data Processing Pipeline

```python
# Create data processing workflow
workflow_id = multi_step_processor.create_workflow(
    name="Data Processing Pipeline",
    description="Process and analyze user data",
    max_parallel_steps=3
)

# Load data
step1 = multi_step_processor.add_step(
    workflow_id=workflow_id,
    name="Load User Data",
    handler="database_operation",
    params={
        "operation": "find",
        "collection": "users",
        "query": {"active": True}
    }
)

# Process data in parallel
processing_steps = []
for i in range(3):
    step_id = multi_step_processor.add_step(
        workflow_id=workflow_id,
        name=f"Process Batch {i+1}",
        handler="log",
        params={"message": f"Processing batch {i+1}..."},
        dependencies=[step1]
    )
    processing_steps.append(step_id)

# Aggregate results
step_final = multi_step_processor.add_step(
    workflow_id=workflow_id,
    name="Aggregate Results",
    handler="database_operation",
    params={
        "operation": "insert",
        "collection": "analytics",
        "data": {"processed_at": "2024-01-01", "status": "completed"}
    },
    dependencies=processing_steps
)

# Send notification
step_notify = multi_step_processor.add_step(
    workflow_id=workflow_id,
    name="Send Notification",
    handler="notification",
    params={
        "message": "Data processing completed successfully!",
        "type": "success"
    },
    dependencies=[step_final]
)

# Execute pipeline
execution_id = await multi_step_processor.execute_workflow(
    workflow_id=workflow_id
)
```

### Example 3: Scheduled Maintenance

```python
# Create maintenance workflow
workflow_id = multi_step_processor.create_workflow(
    name="Daily Maintenance",
    description="Perform daily system maintenance"
)

# Backup database
step1 = multi_step_processor.add_step(
    workflow_id=workflow_id,
    name="Backup Database",
    handler="log",
    params={"message": "Starting database backup..."}
)

# Clean temporary files
step2 = multi_step_processor.add_step(
    workflow_id=workflow_id,
    name="Clean Temp Files",
    handler="file_operation",
    params={
        "operation": "delete",
        "file_path": "/tmp/syncara_temp.log"
    },
    dependencies=[step1]
)

# Update statistics
step3 = multi_step_processor.add_step(
    workflow_id=workflow_id,
    name="Update Statistics",
    handler="database_operation",
    params={
        "operation": "insert",
        "collection": "maintenance_logs",
        "data": {"date": "2024-01-01", "type": "daily_maintenance"}
    },
    dependencies=[step2]
)

# Send report
step4 = multi_step_processor.add_step(
    workflow_id=workflow_id,
    name="Send Report",
    handler="send_message",
    params={"text": "Daily maintenance completed successfully! ✅"},
    dependencies=[step3]
)

# Execute maintenance
execution_id = await multi_step_processor.execute_workflow(
    workflow_id=workflow_id
)
```

## 🎯 AI Integration Examples

### Example: AI Response dengan Multi-Step

```
Baik! Saya akan membuat workflow untuk memproses data user dan mengirim notifikasi.

[MULTISTEP:CREATE_WORKFLOW:User Data Processing:Process user data and send notifications:1800:3]

Workflow berhasil dibuat! Sekarang saya akan menambahkan langkah-langkahnya:

[MULTISTEP:ADD_STEP:workflow_id:Load Users:database_operation:{"operation":"find","collection":"users","query":{"active":true}}::300]

[MULTISTEP:ADD_STEP:workflow_id:Process Data:log:{"message":"Processing user data...","level":"info"}:step1_id:300]

[MULTISTEP:ADD_STEP:workflow_id:Send Notifications:send_message:{"text":"Data processing completed!"}:step2_id:300]

[MULTISTEP:EXECUTE:workflow_id:{"started_by":"AERIS","timestamp":"2024-01-01"}]

Workflow sudah dijalankan! Gunakan [MULTISTEP:STATUS:execution_id] untuk melihat progress.
```

---

## 🚀 Ready to Use!

Multi-Step Processing System sekarang sudah siap digunakan! Sistem ini memberikan fleksibilitas tinggi untuk membuat workflow kompleks dengan error handling yang robust dan monitoring yang real-time.

**Key Benefits:**
- ✅ **Scalable**: Handle workflow kompleks dengan mudah
- ✅ **Reliable**: Built-in retry dan error handling
- ✅ **Flexible**: Custom handlers dan conditional steps
- ✅ **Monitorable**: Real-time progress tracking
- ✅ **Persistent**: State disimpan ke database
- ✅ **User-friendly**: Mudah digunakan via shortcode

Mulai buat workflow pertama Anda sekarang! 🎉 