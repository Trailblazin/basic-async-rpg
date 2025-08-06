from serverHelpers import reassign_host

async def disconnect_msg(server,player, message=""):
    server.players.remove(player)
    await server.send_to_all(f"{player.name} has disconnected {message}.")

async def exec_disconnect(server,player):
    cleanup_task = asyncio.create_task(schedule_disconnect_cleanup(server, player.name, timeout=300))  # e.g., 5 mins
    server.disconnected_players[player.name] = (player, cleanup_task)

async def handle_disconnect_lobby(server, player):
    # Handle player disconnection in lobby
    disconnect_msg(server,player)
    exec_disconnect(server,player)

    #Set next human player to be host
    if player.is_host:
        reassign_host(server)
    await show_lobby(server)

async def handle_disconnect_in_battle(server, player, boss):

    disconnect_msg(server,player,message="during combat")
    exec_disconnect(server,player)

    # Spawn AI replacement for battle continuity
    if player.class_name:
        if not AI_NAMES:
            ai_name = f"AI_{player.name}"
        else:
            ai_name = AI_NAMES.pop(0)

        ai = Player(ai_name, None, is_ai=True)
        ai.set_class(player.class_name)
        ai.ready = True
        ai.currentHP = player.currentHP
        server.players.append(ai)

        await server.send_to_all(f"{ai.name} has replaced {player.name} as an AI.")
        print(f"[DEBUG] {ai.name} inserted into battle with {ai.currentHP} HP.")

    # Reassign host if needed
    if player.is_host:
        reassign_host(server)


#Async Task
def schedule_disconnect_cleanup(server, player_name):
    async def cleanup():
        await asyncio.sleep(RECONNECT_TIMEOUT)
        # If still disconnected after timeout
        if player_name in server.disconnected_players:
            # _ means we ignore reconnect cleanup task
            player, _ = server.disconnected_players[player_name]
            print(f"[DEBUG] Cleanup: player {player_name} did not reconnect in time.")
            # Remove AI if exists and cleanup player data
            ai_to_remove = None
            for p in server.players:
                if p.is_ai and p.class_name == player.class_name:
                    ai_to_remove = p
                    break
            if ai_to_remove:
                self.players.remove(ai_to_remove)
                print(f"[DEBUG] Removed AI {ai_to_remove.name} after timeout.")

            del self.disconnected_players[player_name]
            # Optionally notify remaining players
            await self.send_to_all(f"Player {player_name} failed to reconnect and has been removed.")

    task = asyncio.create_task(cleanup())
    return task

