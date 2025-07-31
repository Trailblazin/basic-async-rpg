import asyncio
from player import Player
from boss import Boss

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


async def client_init(server,reader,writer,player):
    try:
        writer.write(b"Enter your name: \n")
        await writer.drain()
        name = await asyncio.wait_for(reader.readline(), timeout=60.0)
        name = name.decode().strip()

        # Rejoining scenario
        if name in server.disconnected_players:
            player = server.disconnected_players.pop(name)
            player.writer = writer
            server.players = [p for p in server.players if p.name != name or p.is_ai]
            server.players.append(player)
            await server.send_to_all(f"{name} has rejoined the game.")
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
        print(f"Client {addr} disconnected or failed to respond.")
    finally:
        if player is not None:
            await handle_disconnect(server, player)
        
async def battle_loop(players):
    #TODO: Once sufficiently complex improvements are made: add method to init enemy side
    boss = Boss()
    while boss.is_alive() and any(p.currentHP > 0 for p in players):
        combatants = players + [boss]
        combatants.sort(key=lambda x: x.speed, reverse=True)
        for combatant in combatants:
            await asyncio.sleep(1.5)
            if combatant.type == "player":
                handle_player_combat(combatant,boss)
            else:
                handle_enemy_combat(combatant,players)

    await asyncio.sleep(2)
    outcome = "Victory!" if boss.hp <= 0 else "Defeat!"
    await self.send_to_all(f"\n--- {outcome} ---\n")
    await asyncio.sleep(2)

async def handle_enemy_combat(enemy,players):
    target = enemy.select_target(self.players)
    damage = combatant.atk
    target.currentHP -= damage
    await s.send_to_all(f"{combatant.name} attacks {target.name} for {damage} damage!")
    if target.currentHP <= 0:
        await self.send_to_all(f"{target.name} has fallen!")
    return 0

async def handle_player_combat(player, enemy):
    #TODO: Change to get/sets
    target = enemy
    if player.current_hp <= 0:
        return
    target.hp -= player.atk
    await self.send_to_all(f"{player.name} attacks {tagrget.name} for {player.atk} damage!")


async def handle_disconnect(server, player):
    # Handle player disconnection and substitution with AI
    # TODO: Extend to maintain expected functionality if player disconnects mid combat
    if player in server.players:
        server.players.remove(player)
        await server.send_to_all(f"{player.name} has disconnected.")

    server.disconnected_players[player.name] = player

    # Create new AI using existing player class
    # FIXME: Make sure once extended for midcombat, AI char is not healed
    if player.class_name:
        ai_name = AI_NAMES.pop(0)
        ai = Player(ai_name, None, is_ai=True)
        ai.set_class(player.class_name)
        ai.ready = True
        server.players.append(ai)
        await server.send_to_all(f"{ai.name} has replaced {player.name} as an AI.")

    #Set next human player to be host
    if player.is_host:
        for p in server.players:
            if not p.is_ai:
                p.is_host = True
                await server.send_to_all(f"{p.name} is now the host.")
                break
    await show_lobby(server)


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