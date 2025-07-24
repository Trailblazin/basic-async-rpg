import asyncio
import random
from player import Player
from serverHandler import client_init, handle_disconnect
from playerUtil import get_unused_classes

# Maximum number of players in the game
MAX_PLAYERS = 4

# Default class stats for each class
CLASS_STATS = {
    "Thief": {"hp": 80, "atk": 10, "speed": 15},
    "Warrior": {"hp": 120, "atk": 15, "speed": 8},
    "White Mage": {"hp": 70, "atk": 5, "speed": 10},
    "Black Mage": {"hp": 60, "atk": 20, "speed": 12},
}

# Predefined names for AI players
AI_NAMES = ["AI_Setro", "AI_Firion", "AI_Refia", "AI_Cecil", "AI_Bartz","AI_Terra", "AI_Vincent", "AI_Zell", "AI_Eiko", "AI_Auron","AI_Balthier", "AI_Serah","AI_Noctis_Lucius_Caelum"]

HOST_ADDR = '127.0.0.1'
PORT = 8888

# The main RPG server handling players, lobby, and game state
class RPGServer:
    def __init__(self):
        self.players = []     # List of all current players (real and AI)
        self.server = None    # Server object
        self.disconnected_players = {}  # Store disconnected players for possible rejoin

    async def start(self):
        # Start the asyncio server on localhost:8888
        self.server = await asyncio.start_server(self.handle_client, HOST_ADDR , 8888)
        print(f"Server running on {HOST_ADDR}:{PORT}")
        async with self.server:
            await self.server.serve_forever()

    async def handle_client(self, reader, writer):
        # Handle a new player connection
        addr = writer.get_extra_info('peername')
        # Init temp player object
        player = None
        client_init(self, reader, writer)

    async def handle_player_session(self, player, reader):
        # Handle input commands from a player
        writer = player.writer
        writer.write(b"Choose your class (Thief, Warrior, White Mage, Black Mage): \n")
        await writer.drain()

        try:
            #Await player input for class selection
            while not player.class_name:
                line = await asyncio.wait_for(reader.readline(), timeout=60.0)
                if not line:
                    raise ConnectionResetError
                class_choice = line.decode().strip()
                # Require that players pick unique classes
                if class_choice in CLASS_STATS and class_choice not in [p.class_name for p in self.players if p.class_name]:
                    player.set_class(class_choice)
                    writer.write(f"Class set to {class_choice}\n".encode())
                else:
                    writer.write(b"Invalid or already taken class. Try again: \n")
                await writer.drain()

            await self.show_lobby()

            while True:
                line = await asyncio.wait_for(reader.readline(), timeout=180.0)
                if not line:
                    raise ConnectionResetError
                msg = line.decode().strip()
                if msg == "/ready":
                    player.ready = True
                    await self.send_to_all(f"{player.name} is ready.")
                    await self.show_lobby()
                elif msg == "/start" and player.is_host:
                    if self.ready_to_start():
                        await self.start_battle()
                        break
                    else:
                        writer.write(b"Not all players are ready or not enough players.\n")
                        await writer.drain()
                else:
                    writer.write(b"Unknown command. Type /ready or /start (host only).\n")
                    await writer.drain()
        except (asyncio.TimeoutError, asyncio.IncompleteReadError, ConnectionResetError):
            await handle_disconnect(self, player)

    def ready_to_start(self):
        return len(self.players) <= MAX_PLAYERS and all(p.ready for p in self.players)

    async def start_battle(self):
        #Loop populates AI players into player list
        while len(self.players) < MAX_PLAYERS:
            name = AI_NAMES.pop(0)
            ai_player = Player(name, None, is_ai=True)
            available_classes = get_unused_classes()
            ai_player.set_class(random.choice(available_classes))
            ai_player.ready = True
            self.players.append(ai_player)
        await show_party(self)

        await self.send_to_all("\n--- Battle Started! ---\n")
        await asyncio.sleep(2)
        await self.send_to_all("[Battle phase placeholder]\n")
        await asyncio.sleep(3)
        await self.send_to_all("\nGame over! Returning to lobby...\n")

        #De-ready players and prepare to reset lobby
        for p in self.players:
            p.ready = False
            if not p.is_ai:
                p.class_name = None
                p.stats = {}

        self.players = [p for p in self.players if not p.is_ai]
        self.disconnected_players.clear()

        await self.show_lobby()

    async def show_lobby(self):
        status = "\n--- Lobby ---\n"
        for p in self.players:
            role = "(Host)" if p.is_host else ""
            bot = "[AI]" if p.is_ai else ""
            cls = p.class_name if p.class_name else "(no class)"
            ready = "✓" if p.ready else "✗"
            status += f"{p.name} {bot} {role} | Class: {cls} | Ready: {ready}\n"
        await self.send_to_all(status)

    async def send_to_all(self, message):
        for p in self.players:
            if p.writer:
                try:
                    p.writer.write((message + "\n").encode())
                    await p.writer.drain()
                except:
                    pass

# Entry point
if __name__ == "__main__":
    server = RPGServer()
    asyncio.run(server.start())
