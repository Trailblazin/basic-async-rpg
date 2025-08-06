import asyncio
import random
from player import Player
from serverHandler import await_class_selection, await_lobby_commands, client_init, handle_disconnect, show_lobby, show_party, battle_loop
from playerUtil import get_unused_classes
from serverRngPool import RNGPool

# Maximum number of players in the game
MAX_PLAYERS = 4

#TODO: Move to config class at least - use well formatted config file; GET RID OF THIS SHIT AND IT'S USAGE - USE JUST THE LIST OF NAMES BRO

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

combat

# The main RPG server handling players, lobby, and game state
class RPGServer:
    def __init__(self):
        self.players = []     # List of all current players (real and AI)
        self.server = None    # Server object
        self.disconnected_players = {}  # Store disconnected players for possible rejoin
        self.rng_pool = RNGPool(pool_size=5, base_seed=935115)
        #TODO: Find better means to do this such as enum equival
        # Initialize flag: -1 means init, 0 means no, 1 means rebuild
        self.combatants_need_rebuild = -1

    async def start(self):
        # Start the asyncio server on localhost:8888
        self.server = await asyncio.start_server(self.handle_client_init, HOST_ADDR , 8888)
        print(f"Server running on {HOST_ADDR}:{PORT}")
        async with self.server:
            await self.server.serve_forever()

    async def handle_client_init(self, reader, writer):
        # Init temp player object
        player = Player(None,None)
        await client_init(self, reader, writer,player)

    async def handle_player_session(self, player, reader):
        
        is_valid_class = await class_selection(player, reader, writer, self.players)
        if not is_valid_class:
            await self.handle_disconnect(player)
            return
        
        await show_lobby(self)
        
        lobby_commands_success = await lobby_cmds(self, player, reader, writer, show_lobby=lambda: show_lobby(self), handle_disconnect=lambda p=player: self.handle_disconnect(p))
        if not lobby_commands_success:
            return

    def ready_to_start(self):
        return len(self.players) <= MAX_PLAYERS and all(p.ready for p in self.players)

    async def start_battle(self):
        #Loop populates AI players into player list
        while len(self.players) < MAX_PLAYERS:
            name = AI_NAMES.pop(0)
            ai_player = Player(name, None, is_ai=True)
            available_classes = get_unused_classes(self.players)
            ai_player.set_class(random.choice(available_classes))
            ai_player.ready = True
            self.players.append(ai_player)
        await show_party(self)
        await self.send_to_all("\n--- Battle Starting! ---\n")
        await asyncio.sleep(2)
        await self.send_to_all("\n--- [Battle phase: Begins!] ---\n")
        await battle_loop(self, self.players)
        await self.send_to_all("\nGame over! Returning to lobby...\n")

        #De-ready players and prepare to reset lobby
        for p in self.players:
            p.ready = False
            if not p.is_ai:
                #TODO: Verify that stat reset is not needed
                p.class_name = None

        self.players = [p for p in self.players if not p.is_ai]
        self.disconnected_players.clear()
        await show_lobby(self)

    #TODO: Consider moving to serverHandler 

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
