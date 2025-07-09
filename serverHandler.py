async def client_init(server):
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

        await server.show_lobby()
        await server.handle_player_session(player, reader)

    except (asyncio.TimeoutError, asyncio.IncompleteReadError, ConnectionResetError):
        print(f"Client {addr} disconnected or failed to respond.")
    finally:
        if player is not None:
            await handle_disconnect(server, player)


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

    await server.show_lobby()


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