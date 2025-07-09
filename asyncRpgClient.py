# rpg_client.py

import asyncio

async def handle_input(writer):
    while True:
        # Take user input and send it to the server
        msg = await asyncio.get_event_loop().run_in_executor(None, input, "")
        writer.write((msg + "\n").encode())
        await writer.drain()

async def handle_server(reader):
    while True:
        # Read and print data from the server
        data = await reader.readline()
        if not data:
            print("Disconnected from server.")
            break
        print(data.decode().rstrip())

async def main():
    # Connect to the server
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    print("Connected to RPG server.")

    # Start concurrent tasks to handle input and server messages
    await asyncio.gather(
        handle_input(writer),
        handle_server(reader),
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nClient exited.")