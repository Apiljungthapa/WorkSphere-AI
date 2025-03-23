import asyncio

async def task1():
    print("Task 1 started")
    await asyncio.sleep(2)  # Simulate a delay
    print("Task 1 completed")
    return "Result from Task 1"

async def task2():
    print("Task 2 started")
    await asyncio.sleep(3)  # Simulate a longer delay
    print("Task 2 completed")
    return "Result from Task 2"

async def run_parallel():
    result1, result2 = await asyncio.gather(task1(), task2())
    print("Both tasks completed")
    return result1, result2

# Run the async function
if __name__ == "__main__":
    asyncio.run(run_parallel())
