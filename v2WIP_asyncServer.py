import asyncio
import random

# Maximum number of players allowed in the game
MAX_PLAYERS = 4
TICK_INTERVAL = 0.1  # Seconds per tick for the real-time loop

# Default stats for each player class
CLASS_STATS = {
    "Thief": {"hp": 80, "atk": 10, "speed": 15},
    "Warrior": {"hp": 120, "atk": 15, "speed": 8},
    "White Mage": {"hp": 70, "atk": 5, "speed": 10},
    "Black Mage": {"hp": 60, "atk": 20, "speed": 12},
}

# Predefined names to assign to AI players
AI_NAMES = ["AI_Rikku", "AI_Cecil", "AI_Lulu", "AI_Bartz"]

class Player:
    def __init__(self, name, writer, is_ai=False):
        self.name = name
        self.class_name = None
        self.stats = {}
        self.ready = False
        self.writer = writer
        self.is_host = False
        self.is_ai = is_ai
        self.wait_time = 0.0  # Time until next turn

    def set_class(self, class_name):
        # Assign class and calculate initial wait time based on speed
        if class_name in CLASS_STATS:
            self.class_name = class_name
            self.stats = CLASS_STATS[class_name].copy()
            self.stats["current_hp"] = self.stats["hp"]
            self.wait_time = 1000 / self.stats["speed"]

    def to_dict(self):
        # For debugging or export, not currently used in battle
        return {
            "name": self.name,
            "class": self.class_name,
            "ready": self.ready,
            "is_host": self.is_host,
            "is_ai": self.is_ai
        }

    def get_speed(self):
        return self.stats.get("speed", 0)

    def is_alive(self):
        return self.stats.get("current_hp", 0) > 0

class Boss:
    def __init__(self):
        self.name = "Chaos"
        self.hp = 300
        self.atk = 18
        self.speed = 10
        self.wait_time = 1000 / self.speed

    def is_alive(self):
        return self.hp > 0

    def get_speed(self):
        return self.speed

    def select_target(self, players):
        # Select a random living player as the attack target
        living = [p for p in players if p.is_alive()]
        return random.choice(living) if living else None

class RPGServer:
    def __init__(self):
        self.players = []
        self.server = None
        self.disconnected_players = {}  # For rejoining support
        self.ai_substitutes = {}        # AI replacements for disconnected players

    async def start(self):
        # Start listening for incoming client connections
        self.server = await asyncio.start_server(self.handle_client, '127.0.0.1', 8888)
        print("Server running on 127.0.0.1:8888")
        async with self.server:
            await self.server.serve_forever()

    def get_unused_classes(self):
        # Return list of available classes not yet picked
        return [cls for cls in CLASS_STATS if cls not in [p.class_name for p in self.players if p.class_name]]

    async def handle_client(self, reader, writer):
        # Main client handler
        addr = writer.get_extra_info('peername')
        player = None
        try:
            # Request player name
            writer.write(b"Enter your name: ")
            await writer.drain()
            name = await asyncio.wait_for(reader.readline(), timeout=15.0)
            name = name.decode().strip()

            if name in self.disconnected_players:
                # Reconnect existing player and restore state
                player = self.disconnected_players.pop(name)
                player.writer = writer
                self.players = [p for p in self.players if p.name != name or p.is_ai]

                # Remove AI that replaced this player
                if name in self.ai_substitutes:
                    ai_player = self.ai_substitutes.pop(name)
                    self.players.remove(ai_player)
                    AI_NAMES.insert(0, ai_player.name)

                self.players.append(player)
                await self.send_to_all(f"{name} has rejoined the game.")

            elif len([p for p in self.players if not p.is_ai]) >= MAX_PLAYERS:
                # Reject player if lobby is full
                writer.write(b"Server full. Try again later.\n")
                await writer.drain()
                writer.close()
                await writer.wait_closed()
                return

            else:
                # New player joins
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
        # Session loop for lobby phase
        writer = player.writer
        writer.write(b"Choose your class (Thief, Warrior, White Mage, Black Mage): ")
        await writer.drain()
        try:
            # Class selection
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

            # Lobby commands (/ready, /start)
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
        # Handle player disconnection
        if player in self.players:
            self.players.remove(player)
            await self.send_to_all(f"{player.name} has disconnected.")

        self.disconnected_players[player.name] = player

        # Substitute disconnected player with an AI
        if player.class_name:
            ai_name = AI_NAMES.pop(0)
            ai = Player(ai_name, None, is_ai=True)
            ai.set_class(player.class_name)
            ai.ready = True
            self.players.append(ai)
            self.ai_substitutes[player.name] = ai
            await self.send_to_all(f"{ai.name} has replaced {player.name} as an AI.")

        # Reassign host if host disconnected
        if player.is_host:
            for p in self.players:
                if not p.is_ai:
                    p.is_host = True
                    await self.send_to_all(f"{p.name} is now the host.")
                    break

        await self.show_lobby()

    def ready_to_start(self):
        return len(self.players) <= MAX_PLAYERS and all(p.ready for p in self.players)

    async def start_battle(self):
        # Fill remaining slots with AIs
        while len(self.players) < MAX_PLAYERS:
            name = AI_NAMES.pop(0)
            ai_player = Player(name, None, is_ai=True)
            available_classes = self.get_unused_classes()
            ai_player.set_class(random.choice(available_classes))
            ai_player.ready = True
            self.players.append(ai_player)

        boss = Boss()
        await self.send_to_all("\n--- Battle Started! ---\n")
        await asyncio.sleep(2)

        # Begin real-time turn-based loop
        while boss.is_alive() and any(p.is_alive() for p in self.players):
            for combatant in [*self.players, boss]:
                if not combatant.is_alive():
                    continue
                combatant.wait_time -= TICK_INTERVAL * 1000
                if combatant.wait_time <= 0:
                    if isinstance(combatant, Boss):
                        await self.boss_turn(combatant)
                    else:
                        await self.player_turn(combatant, boss)
                    combatant.wait_time = 1000 / combatant.get_speed()

            await self.send_wait_times(boss)
            await asyncio.sleep(TICK_INTERVAL)

        await self.end_battle(boss)

    async def send_wait_times(self, boss):
        # Broadcast wait timers for all alive players and boss
        updates = "\n-- Turn Timers --\n"
        all_combatants = [p for p in self.players if p.is_alive()] + ([boss] if boss.is_alive() else [])
        for c in sorted(all_combatants, key=lambda c: c.wait_time):
            name = c.name if isinstance(c, Player) else "Boss"
            wait = max(0, int(c.wait_time))
            bar = "#" * (10 - min(10, wait // 100)) + "-" * min(10, wait // 100)
            updates += f"{name:12} [{bar}] {wait}ms\n"
        await self.send_to_all(updates)

    async def player_turn(self, player, boss):
        # Handle a player's attack on the boss
        if not player.is_alive():
            return
        boss.hp -= player.stats["atk"]
        await self.send_to_all(f"{player.name} attacks {boss.name} for {player.stats['atk']} damage!")
        if boss.hp <= 0:
            await self.send_to_all(f"{boss.name} has been defeated!")

    async def boss_turn(self, boss):
        # Boss selects and attacks a player
        target = boss.select_target(self.players)
        if not target:
            return
        target.stats["current_hp"] -= boss.atk
        await self.send_to_all(f"{boss.name} attacks {target.name} for {boss.atk} damage!")
        if target.stats["current_hp"] <= 0:
            await self.send_to_all(f"{target.name} has fallen!")

    async def end_battle(self, boss):
        # Cleanup after battle ends
        await asyncio.sleep(2)
        outcome = "Victory!" if not boss.is_alive() else "Defeat!"
        await self.send_to_all(f"\n--- {outcome} ---\n")
        await asyncio.sleep(2)
        await self.send_to_all("\nGame over! Returning to lobby...\n")

        for p in self.players:
            p.ready = False
            if not p.is_ai:
                p.class_name = None
                p.stats = {}

        self.players = [p for p in self.players if not p.is_ai]
        self.disconnected_players.clear()
        self.ai_substitutes.clear()

        await self.show_lobby()

    async def show_lobby(self):
        # Send lobby state to all players
        status = "\n--- Lobby ---\n"
        for p in self.players:
            role = "(Host)" if p.is_host else ""
            bot = "[AI]" if p.is_ai else ""
            cls = p.class_name if p.class_name else "(no class)"
            ready = "✓" if p.ready else "✗"
            status += f"{p.name} {bot} {role} | Class: {cls} | Ready: {ready}\n"
        await self.send_to_all(status)

    async def send_to_all(self, message):
        # Broadcast message to all connected players
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
