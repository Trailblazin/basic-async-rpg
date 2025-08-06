async def cancel_disconnect_task(server):
    player, cleanup_task = server.disconnected_players.pop(name)
    cleanup_task.cancel()

    return player

async def handle_reconnect_in_lobby(server, name, writer):
    player = cancel_disconnect_task(server)

    # No AI to handle in lobby, just update writer and re-add player
    player.writer = writer

    # Remove any old player instance (just in case)
    server.players = [p for p in server.players if p.name != name]
    server.players.append(player)

    await server.send_to_all(f"{name} has rejoined the lobby.")
    await show_lobby(server)

    print(f"[DEBUG] Player {name} reconnected in lobby.")
    return True


async def handle_reconnect_in_battle(server, name, writer):
    player = cancel_disconnect_task(server)

    # Find AI substitute matching class and remove it
    ai_player = None
    for p in server.players:
        if p.is_ai and p.class_name == player.class_name:
            ai_player = p
            break
    if ai_player:
        server.players.remove(ai_player)
        print(f"[DEBUG] Removed AI {ai_player.name} to rebind player {name}.")

    player.writer = writer

    # Remove old player instance, add back human player
    server.players = [p for p in server.players if p.name != name]
    server.players.append(player)

    await server.send_to_all(f"{name} has rejoined the battle.")
    print(f"[DEBUG] Player {name} reconnected in battle.")
    return True