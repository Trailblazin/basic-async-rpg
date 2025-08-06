import asyncio
from player import Player
from boss import Boss
from serverDisconnectHandler import handle_disconnect, schedule_disconnect_cleanup

# Maximum number of players in the game
MAX_PLAYERS = 4

#TODO: Move to config class at least - use well formatted config file
# Default class stats for each class
CLASS_STATS = {
    "Thief": {"hp": 80, "atk": 10, "speed": 15},
    "Warrior": {"hp": 120, "atk": 15, "speed": 8},
    "White Mage": {"hp": 70, "atk": 5, "speed": 10},
    "Black Mage": {"hp": 60, "atk": 20, "speed": 12},
}

# Predefined names for AI players
AI_NAMES = ["AI_Setro", "AI_Firion", "AI_Refia", "AI_Cecil", "AI_Bartz","AI_Terra", "AI_Vincent", "AI_Zell", "AI_Eiko", "AI_Auron","AI_Balthier", "AI_Serah","AI_Noctis_Lucius_Caelum"]

#TODO: Refactor further to have serverCombatHandler, serverChatHandler, 
# serverLobbyHandler (Inherits from server chat handler), 
# serverCombatEventHandler

async def client_init(server,reader,writer,player):
    try:
        writer.write(b"Enter your name: \n")
        await writer.drain()
        name = await asyncio.wait_for(reader.readline(), timeout=60.0)
        name = name.decode().strip()

        # Rejoining scenario
        if name in self.disconnected_players:
            if self.in_battle:
                reconnected = await handle_reconnect_in_battle(self, name, writer)
            else:
                reconnected = await handle_reconnect_in_lobby(self, name, writer)
            if reconnected:
                # Proceed with whatever post-reconnect flow you want, e.g. skip class select
                return
        # Server is full, reject player connection
        elif len([p for p in server.players if not p.is_ai]) == MAX_PLAYERS:
            writer.write(b"Server full. Try again later.\n")
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            return
        # Valid first Join, create instant of Player at address
        else:
            player = Player(name, writer)
            #If server list of players is empty, init player as host player
            if not server.players:
                player.is_host = True
                writer.write(b"You are the host.\n")
            server.players.append(player)
            await server.send_to_all(f"{name} has joined the lobby.")

        await show_lobby(server)
        await server.handle_player_session(player, reader)

    except (asyncio.TimeoutError, asyncio.IncompleteReadError, ConnectionResetError):
        #TODO: Consider usage of this "extra info"
        print(f"Client {writer.get_extra_info('peername')} disconnected or failed to respond.")
    finally:
        if player is not None:
            await handle_disconnect(server, player)
        
async def class_selection(player, reader, writer, players):
    try:
        while not player.class_name:
            line = await asyncio.wait_for(reader.readline(), timeout=60.0)
            if not line:
                raise ConnectionResetError
            class_choice = line.decode().strip()

            # Require that players pick unique classes
            taken_classes = [p.class_name for p in players if p.class_name]
            if class_choice in CLASS_STATS and class_choice not in taken_classes:
                player.set_class(class_choice)
                writer.write(f"Class set to {class_choice}\n".encode())
            else:
                writer.write(b"Invalid or already taken class. Try again: \n")
            await writer.drain()
        return True
    except (asyncio.TimeoutError, asyncio.IncompleteReadError, ConnectionResetError):
        return False

async def lobby_cmds(server, player, reader, writer, show_lobby, handle_disconnect):
    try:
        while True:
            line = await asyncio.wait_for(reader.readline(), timeout=180.0)
            if not line:
                raise ConnectionResetError
            msg = line.decode().strip()
            if msg == "/ready":
                player.ready = True
                await server.send_to_all(f"{player.name} is ready.")
                await show_lobby()
            elif msg == "/start" and player.is_host:
                if server.ready_to_start():
                    await server.start_battle()
                    break
                else:
                    writer.write(b"Not all players are ready or not enough players.\n")
                    await writer.drain()
            else:
                writer.write(b"Unknown command. Type /ready or /start (host only).\n")
                await writer.drain()
        return True
    except (asyncio.TimeoutError, asyncio.IncompleteReadError, ConnectionResetError):
        await handle_disconnect(player)
        return False
    
async def battle_loop(server,players):
    #TODO: Once sufficiently complex improvements are made: add method to init 
    # Both enemy side and player side
    boss = Boss(server.rng_pool)
    for p in players:
        p.currentHP = p.hp   
    while boss.is_alive() and any(p.currentHP > 0 for p in players):
        combatants = players + [boss]
        combatants.sort(key=lambda x: x.speed, reverse=True)
        await show_encounter(server,combatants)
        for combatant in combatants:
            await asyncio.sleep(1.5)
            if combatant.type == "Player":
                await handle_player_combat(server, combatant,boss)
            else:
                await handle_enemy_combat(server,combatant,players)

    await asyncio.sleep(2)
    outcome = "Victory!" if not boss.is_alive() else "Defeat!"
    await server.send_to_all(f"\n--- {outcome} ---\n")
    await asyncio.sleep(2)

async def handle_enemy_combat(server, enemy,players):
    target = enemy.select_target(players)
    damage = enemy.atk
    target.currentHP -= damage
    await server.send_to_all(f"{enemy.name} attacks {target.name} for {damage} damage!")
    if target.currentHP <= 0:
        await server.send_to_all(f"{target.name} has fallen!")
    return 0

async def handle_player_combat(server,player, enemy):
    #TODO: Change to get/sets
    target = enemy
    if player.currentHP <= 0:
        return
    target.currentHP -= player.atk
    await server.send_to_all(f"{player.name} attacks {target.name} for {player.atk} damage!")

async def show_lobby(server):
    status = "\n--- Lobby ---\n"
    for p in server.players:
        role = "[AI]" if p.is_ai else "[PC]"
        job = p.class_name
        ready = "✓" if p.ready else "✗"
        status += f"{p.name} {role} | Class: {job} | Ready: {ready}\n"
    await server.send_to_all(status)

async def show_party(server):
    status = "\n--- Party Overview ---\n"
    for p in server.players:
        role = "[AI]" if p.is_ai else "[PC]"
        job = p.class_name
        ready = "✓" if p.ready else "✗"
        status += f"{p.name} {role} | Class: {job} \n"
    await server.send_to_all(status)

async def show_encounter(server,combatants):
    status = "\n--- Encounter Info ---\n"
    for c in combatants:
        role = "[BOSS]" if c.type == "Boss" else "[PARTY]"
        hp = c.currentHP
        status += f"{role} {c.name} | HP: {hp} \n"
    await server.send_to_all(status)