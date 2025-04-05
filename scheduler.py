import asyncio
import platform
from datetime import datetime

from src import processor

# Scheduler class
class TaskScheduler:
    def __init__(self, interval_seconds):
        self.interval = interval_seconds
        self.running = False
        
    async def run_task(self, task):
        self.running = True
        while self.running:
            task()
            await asyncio.sleep(self.interval)
            
    def stop(self):
        self.running = False

# Main execution
async def main():
    scheduler = TaskScheduler(interval_seconds=5)
    print("Scheduler started. Running task every 5 seconds...")
    print("Press Ctrl+C to stop")
    try:
        print(processor.process_unprocessed_note)
        await scheduler.run_task(processor.process_unprocessed_note)
    except KeyboardInterrupt:
        scheduler.stop()
        print("\nScheduler stopped")

# Platform-specific execution
if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
