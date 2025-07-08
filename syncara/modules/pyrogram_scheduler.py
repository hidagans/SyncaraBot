"""
Scheduler untuk automated tasks dan fitur advanced.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable, Union
from syncara.console import console
from dataclasses import dataclass
import json
import os
from croniter import croniter

@dataclass
class ScheduledTask:
    """
    Representasi task yang dijadwalkan.
    """
    id: str
    name: str
    func: Callable
    args: tuple
    kwargs: dict
    cron_expression: Optional[str] = None
    interval_seconds: Optional[int] = None
    next_run: Optional[datetime] = None
    last_run: Optional[datetime] = None
    enabled: bool = True
    max_runs: Optional[int] = None
    current_runs: int = 0
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: Optional[int] = None
    metadata: Dict[str, Any] = None

class PyrogramScheduler:
    """
    Scheduler untuk menjalankan task secara otomatis.
    """
    
    def __init__(self, persistent_file: str = "scheduled_tasks.json"):
        self.tasks: Dict[str, ScheduledTask] = {}
        self.running = False
        self.persistent_file = persistent_file
        self.loop_task = None
        
        # Load persistent tasks
        self.load_persistent_tasks()
    
    def add_task(self, 
                task_id: str,
                name: str,
                func: Callable,
                args: tuple = (),
                kwargs: dict = None,
                cron_expression: str = None,
                interval_seconds: int = None,
                enabled: bool = True,
                max_runs: int = None,
                max_retries: int = 3,
                timeout_seconds: int = None,
                metadata: dict = None) -> bool:
        """
        Menambahkan task ke scheduler.
        """
        if kwargs is None:
            kwargs = {}
        
        if metadata is None:
            metadata = {}
        
        # Validate parameters
        if not cron_expression and not interval_seconds:
            raise ValueError("Either cron_expression or interval_seconds must be provided")
        
        # Calculate next run time
        next_run = None
        if cron_expression:
            cron = croniter(cron_expression, datetime.now())
            next_run = cron.get_next(datetime)
        elif interval_seconds:
            next_run = datetime.now() + timedelta(seconds=interval_seconds)
        
        task = ScheduledTask(
            id=task_id,
            name=name,
            func=func,
            args=args,
            kwargs=kwargs,
            cron_expression=cron_expression,
            interval_seconds=interval_seconds,
            next_run=next_run,
            enabled=enabled,
            max_runs=max_runs,
            max_retries=max_retries,
            timeout_seconds=timeout_seconds,
            metadata=metadata
        )
        
        self.tasks[task_id] = task
        self.save_persistent_tasks()
        
        console.info(f"✅ Task '{name}' ({task_id}) added to scheduler")
        return True
    
    def remove_task(self, task_id: str) -> bool:
        """
        Menghapus task dari scheduler.
        """
        if task_id in self.tasks:
            task_name = self.tasks[task_id].name
            del self.tasks[task_id]
            self.save_persistent_tasks()
            console.info(f"🗑️ Task '{task_name}' ({task_id}) removed from scheduler")
            return True
        return False
    
    def enable_task(self, task_id: str) -> bool:
        """
        Mengaktifkan task.
        """
        if task_id in self.tasks:
            self.tasks[task_id].enabled = True
            self.save_persistent_tasks()
            console.info(f"✅ Task '{self.tasks[task_id].name}' enabled")
            return True
        return False
    
    def disable_task(self, task_id: str) -> bool:
        """
        Menonaktifkan task.
        """
        if task_id in self.tasks:
            self.tasks[task_id].enabled = False
            self.save_persistent_tasks()
            console.info(f"⏸️ Task '{self.tasks[task_id].name}' disabled")
            return True
        return False
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan status task.
        """
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        return {
            'id': task.id,
            'name': task.name,
            'enabled': task.enabled,
            'next_run': task.next_run.isoformat() if task.next_run else None,
            'last_run': task.last_run.isoformat() if task.last_run else None,
            'current_runs': task.current_runs,
            'max_runs': task.max_runs,
            'retry_count': task.retry_count,
            'max_retries': task.max_retries,
            'cron_expression': task.cron_expression,
            'interval_seconds': task.interval_seconds,
            'metadata': task.metadata
        }
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """
        Mendapatkan semua task.
        """
        return [self.get_task_status(task_id) for task_id in self.tasks.keys()]
    
    async def start(self):
        """
        Memulai scheduler.
        """
        if self.running:
            return
        
        self.running = True
        self.loop_task = asyncio.create_task(self._scheduler_loop())
        console.info("🚀 Pyrogram Scheduler started")
    
    async def stop(self):
        """
        Menghentikan scheduler.
        """
        if not self.running:
            return
        
        self.running = False
        
        if self.loop_task:
            self.loop_task.cancel()
            try:
                await self.loop_task
            except asyncio.CancelledError:
                pass
        
        console.info("🛑 Pyrogram Scheduler stopped")
    
    async def _scheduler_loop(self):
        """
        Main loop scheduler.
        """
        while self.running:
            try:
                current_time = datetime.now()
                
                for task_id, task in list(self.tasks.items()):
                    if not task.enabled:
                        continue
                    
                    # Check if task should run
                    if task.next_run and current_time >= task.next_run:
                        await self._execute_task(task)
                
                # Sleep for 1 second
                await asyncio.sleep(1)
                
            except Exception as e:
                console.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(5)
    
    async def _execute_task(self, task: ScheduledTask):
        """
        Menjalankan task.
        """
        try:
            console.info(f"🔄 Running task: {task.name} ({task.id})")
            
            # Check max runs
            if task.max_runs and task.current_runs >= task.max_runs:
                console.info(f"⏹️ Task {task.name} reached max runs ({task.max_runs})")
                task.enabled = False
                self.save_persistent_tasks()
                return
            
            # Execute task with timeout
            if task.timeout_seconds:
                await asyncio.wait_for(
                    task.func(*task.args, **task.kwargs),
                    timeout=task.timeout_seconds
                )
            else:
                await task.func(*task.args, **task.kwargs)
            
            # Update task statistics
            task.current_runs += 1
            task.last_run = datetime.now()
            task.retry_count = 0
            
            # Calculate next run
            self._calculate_next_run(task)
            
            console.info(f"✅ Task {task.name} completed successfully")
            
        except asyncio.TimeoutError:
            console.error(f"⏰ Task {task.name} timed out")
            await self._handle_task_failure(task)
        except Exception as e:
            console.error(f"❌ Task {task.name} failed: {e}")
            await self._handle_task_failure(task)
        
        finally:
            self.save_persistent_tasks()
    
    async def _handle_task_failure(self, task: ScheduledTask):
        """
        Handle task failure dengan retry logic.
        """
        task.retry_count += 1
        
        if task.retry_count <= task.max_retries:
            # Retry dengan exponential backoff
            retry_delay = 2 ** task.retry_count
            task.next_run = datetime.now() + timedelta(seconds=retry_delay)
            console.info(f"🔄 Retrying task {task.name} in {retry_delay} seconds (attempt {task.retry_count}/{task.max_retries})")
        else:
            # Max retries reached
            console.error(f"💀 Task {task.name} failed after {task.max_retries} retries")
            if task.cron_expression:
                # If cron task, schedule next run
                self._calculate_next_run(task)
                task.retry_count = 0
            else:
                # If interval task, disable
                task.enabled = False
    
    def _calculate_next_run(self, task: ScheduledTask):
        """
        Menghitung waktu run selanjutnya.
        """
        if task.cron_expression:
            cron = croniter(task.cron_expression, datetime.now())
            task.next_run = cron.get_next(datetime)
        elif task.interval_seconds:
            task.next_run = datetime.now() + timedelta(seconds=task.interval_seconds)
    
    def save_persistent_tasks(self):
        """
        Menyimpan task ke file persistent.
        """
        try:
            persistent_data = {}
            for task_id, task in self.tasks.items():
                # Only save serializable data
                persistent_data[task_id] = {
                    'name': task.name,
                    'args': task.args,
                    'kwargs': task.kwargs,
                    'cron_expression': task.cron_expression,
                    'interval_seconds': task.interval_seconds,
                    'enabled': task.enabled,
                    'max_runs': task.max_runs,
                    'current_runs': task.current_runs,
                    'max_retries': task.max_retries,
                    'timeout_seconds': task.timeout_seconds,
                    'metadata': task.metadata,
                    'next_run': task.next_run.isoformat() if task.next_run else None,
                    'last_run': task.last_run.isoformat() if task.last_run else None
                }
            
            with open(self.persistent_file, 'w') as f:
                json.dump(persistent_data, f, indent=2)
                
        except Exception as e:
            console.error(f"Error saving persistent tasks: {e}")
    
    def load_persistent_tasks(self):
        """
        Memuat task dari file persistent.
        """
        try:
            if not os.path.exists(self.persistent_file):
                return
            
            with open(self.persistent_file, 'r') as f:
                persistent_data = json.load(f)
            
            for task_id, data in persistent_data.items():
                # Create task (without func, needs to be re-registered)
                task = ScheduledTask(
                    id=task_id,
                    name=data['name'],
                    func=None,  # Will be set when re-registered
                    args=tuple(data['args']),
                    kwargs=data['kwargs'],
                    cron_expression=data.get('cron_expression'),
                    interval_seconds=data.get('interval_seconds'),
                    enabled=data.get('enabled', True),
                    max_runs=data.get('max_runs'),
                    current_runs=data.get('current_runs', 0),
                    max_retries=data.get('max_retries', 3),
                    timeout_seconds=data.get('timeout_seconds'),
                    metadata=data.get('metadata', {}),
                    next_run=datetime.fromisoformat(data['next_run']) if data.get('next_run') else None,
                    last_run=datetime.fromisoformat(data['last_run']) if data.get('last_run') else None
                )
                
                # Note: func will be None until re-registered
                # This is intentional - functions can't be serialized
                self.tasks[task_id] = task
            
            console.info(f"📂 Loaded {len(persistent_data)} persistent tasks")
            
        except Exception as e:
            console.error(f"Error loading persistent tasks: {e}")
    
    # ==================== PRE-DEFINED SCHEDULED TASKS ====================
    
    async def schedule_message(self, 
                             client,
                             chat_id: Union[int, str],
                             text: str,
                             send_time: datetime,
                             task_id: str = None,
                             **kwargs):
        """
        Jadwalkan pengiriman pesan.
        """
        if task_id is None:
            task_id = f"scheduled_message_{int(time.time())}"
        
        delay_seconds = (send_time - datetime.now()).total_seconds()
        
        if delay_seconds <= 0:
            raise ValueError("Send time must be in the future")
        
        async def send_message():
            await client.kirim_pesan(chat_id=chat_id, text=text, **kwargs)
        
        return self.add_task(
            task_id=task_id,
            name=f"Scheduled Message to {chat_id}",
            func=send_message,
            interval_seconds=int(delay_seconds),
            max_runs=1
        )
    
    async def schedule_backup(self,
                            client,
                            chat_id: Union[int, str],
                            backup_interval_hours: int = 24,
                            task_id: str = None):
        """
        Jadwalkan backup chat otomatis.
        """
        if task_id is None:
            task_id = f"backup_chat_{chat_id}"
        
        async def backup_chat():
            await client.backup_lengkap_chat(chat_id=chat_id, limit=1000)
        
        return self.add_task(
            task_id=task_id,
            name=f"Auto Backup Chat {chat_id}",
            func=backup_chat,
            interval_seconds=backup_interval_hours * 3600
        )
    
    async def schedule_cleanup(self,
                             client,
                             chat_id: Union[int, str],
                             cleanup_interval_hours: int = 168,  # 1 week
                             max_age_days: int = 30,
                             task_id: str = None):
        """
        Jadwalkan cleanup pesan lama.
        """
        if task_id is None:
            task_id = f"cleanup_chat_{chat_id}"
        
        async def cleanup_old_messages():
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            # Implementation would need to iterate through messages
            # This is a placeholder
            console.info(f"Cleaning up messages older than {max_age_days} days in {chat_id}")
        
        return self.add_task(
            task_id=task_id,
            name=f"Cleanup Chat {chat_id}",
            func=cleanup_old_messages,
            interval_seconds=cleanup_interval_hours * 3600
        )
    
    async def schedule_status_check(self,
                                  client,
                                  check_interval_minutes: int = 30,
                                  task_id: str = None):
        """
        Jadwalkan pengecekan status bot.
        """
        if task_id is None:
            task_id = "status_check"
        
        async def check_status():
            try:
                me = await client.get_me()
                console.info(f"✅ Bot status check: {me.first_name} is online")
            except Exception as e:
                console.error(f"❌ Bot status check failed: {e}")
        
        return self.add_task(
            task_id=task_id,
            name="Bot Status Check",
            func=check_status,
            interval_seconds=check_interval_minutes * 60
        )
    
    async def schedule_analytics_report(self,
                                      client,
                                      report_chat_id: Union[int, str],
                                      report_interval_hours: int = 24,
                                      task_id: str = None):
        """
        Jadwalkan laporan analytics.
        """
        if task_id is None:
            task_id = "analytics_report"
        
        async def send_analytics_report():
            try:
                # Get statistics from helpers
                cache_stats = client.helpers.get_cache_stats()
                
                report = f"📊 **Analytics Report**\n\n"
                report += f"🧠 **Cache Stats:**\n"
                report += f"• Memory entries: {cache_stats['memory_cache']['total_entries']}\n"
                report += f"• Cache size: {cache_stats['memory_cache']['total_size_bytes']} bytes\n"
                report += f"• Performance calls: {cache_stats['performance_stats']['total_calls']}\n"
                report += f"• Success rate: {cache_stats['performance_stats']['success_rate']:.2%}\n"
                
                await client.kirim_pesan(chat_id=report_chat_id, text=report)
            except Exception as e:
                console.error(f"Error sending analytics report: {e}")
        
        return self.add_task(
            task_id=task_id,
            name="Analytics Report",
            func=send_analytics_report,
            interval_seconds=report_interval_hours * 3600
        )

# Global instance
pyrogram_scheduler = PyrogramScheduler() 