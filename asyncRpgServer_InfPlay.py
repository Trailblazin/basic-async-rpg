import asyncio
import random

MAX_PLAYERS = 4

CLASS_STATS = {
    "Thief": {"hp": 80, "atk": 10, "speed": 15},
    "Warrior": {"hp": 120, "atk": 15, "speed": 8},
    "White Mage": {"hp": 70, "atk": 5, "speed": 10},
    "Black Mage": {"hp": 60, "atk": 20, "speed": 12},
}

AI_NAMES = ["AI_Rikku", "AI_Cecil", "AI_Lulu", "AI_Bartz"]

# Represents a player or AI participant in the game
class Player:
    def __init__(self, name, writer, is_ai=False):
        self.name = name                      # Player's name
        self.class_name = None               # Chosen class name
        self.stats = {}                      # Stats derived from class
        self.ready = False                   # Readiness for battle
        self.writer = writer                 # Writer stream to communicate with client
        self.is_host = False                 # Host flag
        self.is_ai = is_ai                   # AI player flag

    def set_class(self, class_name):
        # Set player's class and corresponding stats
        if class_name in CLASS_STATS:
            self.class_name = class_name
            self.stats = CLASS_STATS[class_name]

    def to_dict(self):
        # Return player data as a dictionary
        return {
            "name": self.name,
            "class": self.class_name,
            "ready": self.ready,
            "is_host": self.is_host,
            "is_ai": self.is_ai
        }

class RPGServer:
    def __init__(self):
        self.players = []
        self.server = None
        self.disconnected_players = {}

    async def start(self):
        self.server = await asyncio.start_server(self.handle_client, '127.0.0.1', 8888)
        print("Server running on 127.0.0.1:8888")
        async with self.server:
            await self.server.serve_forever()

    def get_unused_classes(self):
        return [cls for cls in CLASS_STATS if cls not in [p.class_name for p in self.players if p.class_name]]

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        player = None

        try:
            writer.write(b"Enter your name: \n")
            await writer.drain()
            name = await asyncio.wait_for(reader.readline(), timeout=15.0)
            name = name.decode().strip()

            if name in self.disconnected_players:
                player = self.disconnected_players.pop(name)
                player.writer = writer
                self.players = [p for p in self.players if p.name != name or p.is_ai]
                self.players.append(player)
                await self.send_to_all(f"{name} has rejoined the game.")

            elif len([p for p in self.players if not p.is_ai]) >= MAX_PLAYERS:
                writer.write(b"Server full. Try again later.\n")
                await writer.drain()
                writer.close()
                await writer.wait_closed()
                return

            else:
                player = Player(name, writer)
                if not self.players:
                    player.is_host = True
                    writer.write(b"You are the host.\n")
                self.players.append(player)
                await self.send_to_all(f"{name} has joined the lobby.")

            await self.show_lobby()
            await self.handle_player_session(player, reader)

        except (asyncio.TimeoutError, asyncio.IncompleteReadError, ConnectionResetError):
            print(f"Client {addr} disconnected or failed to respond.")
        finally:
            if player is not None:
                await self.handle_disconnect(player)

    async def handle_player_session(self, player, reader):
        writer = player.writer

        try:
            while True:
                # Step 1: Class selection if not yet chosen
                while not player.class_name:
                    writer.write(b"Choose your class (Thief, Warrior, White Mage, Black Mage): \n")
                    await writer.drain()

                    line = await asyncio.wait_for(reader.readline(), timeout=60.0)
                    if not line:
                        raise ConnectionResetError

                    class_choice = line.decode().strip()

                    # Check if class is valid and not taken
                    taken_classes = [p.class_name for p in self.players if p.class_name]
                    if class_choice in CLASS_STATS and class_choice not in taken_classes:
                        player.set_class(class_choice)
                        writer.write(f"Class set to {class_choice}\n".encode())
                        await writer.drain()
                        await self.show_lobby()
                    else:
                        writer.write(b"Invalid or already taken class. Try again.\n")
                        await writer.drain()

                # Step 2: Wait for player commands when class is set
                writer.write(b"Commands: /ready to ready up, /unready to unready, /class to change class, /start to start (host only)\n")
                await writer.drain()

                line = await asyncio.wait_for(reader.readline(), timeout=180.0)
                if not line:
                    raise ConnectionResetError

                msg = line.decode().strip()

                # Step 3: Process commands
                if msg == "/ready":
                    player.ready = True
                    await self.send_to_all(f"{player.name} is ready.")
                    await self.show_lobby()

                elif msg == "/unready":
                    player.ready = False
                    await self.send_to_all(f"{player.name} is no longer ready.")
                    await self.show_lobby()

                elif msg == "/class":
                    # Allow player to change class; reset class and go back to Step 1
                    player.class_name = None
                    player.ready = False
                    await self.show_lobby()

                elif msg == "/start" and player.is_host:
                    if self.ready_to_start():
                        # Start battle and wait for it to finish
                        await self.start_battle()

                        # After battle, states reset inside start_battle
                        # Lobby is shown; loop continues to allow re-joining and readying
                    else:
                        writer.write(b"Not all players are ready or not enough players.\n")
                        await writer.drain()

                else:
                    writer.write(b"Unknown command. Valid commands: /ready, /unready, /class, /start (host only).\n")
                    await writer.drain()

        except (asyncio.TimeoutError, asyncio.IncompleteReadError, ConnectionResetError):
            # Client disconnected or timed out, handle clean-up
            await self.handle_disconnect(player)
            writer = player.writer
            writer.write(b"Choose your class (Thief, Warrior, White Mage, Black Mage): ")
            await writer.drain()

            try:
                while not player.class_name:
                    line = await asyncio.wait_for(reader.readline(), timeout=60.0)
                    if not line:
                        raise ConnectionResetError
                    class_choice = line.decode().strip()
                    if class_choice in CLASS_STATS and class_choice not in [p.class_name for p in self.players if p.class_name]:
                        player.set_class(class_choice)
                        writer.write(f"Class set to {class_choice}\n".encode())
                    else:
                        writer.write(b"Invalid or already taken class. Try again: ")
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
                await self.handle_disconnect(player)

    async def handle_disconnect(self, player):
        await self.remove_player(player)
        self.disconnected_players[player.name] = player
        await self.substitute_ai(player)
        await self.reassign_host_if_needed(player)
        await self.show_lobby()

    async def remove_player(self, player):
        if player in self.players:
            self.players.remove(player)
            await self.send_to_all(f"{player.name} has disconnected.")

    async def substitute_ai(self, player):
        if player.class_name and AI_NAMES:
            ai_name = AI_NAMES.pop(0)
            ai = Player(ai_name, None, is_ai=True)
            ai.set_class(player.class_name)
            ai.ready = True
            self.players.append(ai)
            await self.send_to_all(f"{ai.name} has replaced {player.name} as an AI.")

    async def reassign_host_if_needed(self, player):
        if player.is_host:
            for p in self.players:
                if not p.is_ai:
                    p.is_host = True
                    await self.send_to_all(f"{p.name} is now the host.")
                    break

    def ready_to_start(self):
        # All players must be ready and player count within max allowed
        return len(self.players) <= MAX_PLAYERS and all(p.ready for p in self.players)

    async def start_battle(self):
        await self.fill_with_ai_if_needed()
        await self.announce_battle_start()
        await self.simulate_battle()
        await self.finish_battle()
        await self.show_lobby()

    async def fill_with_ai_if_needed(self):
        while len(self.players) < MAX_PLAYERS:
            if not AI_NAMES:
                break
            name = AI_NAMES.pop(0)
            ai_player = Player(name, None, is_ai=True)
            available_classes = self.get_unused_classes()
            if not available_classes:
                ai_player.set_class(random.choice(list(CLASS_STATS.keys())))
            else:
                ai_player.set_class(random.choice(available_classes))
            ai_player.ready = True
            self.players.append(ai_player)
        await self.show_lobby(True)

    async def announce_battle_start(self):
        await self.send_to_all("\n--- Battle Started! ---\n")
        await asyncio.sleep(2)

    async def simulate_battle(self):
        await self.send_to_all("[Battle phase placeholder]\n")
        await asyncio.sleep(3)

    async def finish_battle(self):
        await self.send_to_all("\nGame over! Returning to lobby...\n")

        for p in self.players:
            p.ready = False
            if not p.is_ai:
                p.class_name = None
                p.stats = {}

        self.players = [p for p in self.players if not p.is_ai]
        self.disconnected_players.clear()

    async def show_lobby(self, isParty=False):
        status = "\n--- Lobby ---\n"
        if isParty:
            status = "\n--- Battle Party ---\n"
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

if __name__ == "__main__":
    server = RPGServer()
    asyncio.run(server.start())
