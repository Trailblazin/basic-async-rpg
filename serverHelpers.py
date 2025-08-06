async def reassign_host(server):    # Reassign host if needed
    for p in server.players:
        if not p.is_ai:
            p.is_host = True
            await server.send_to_all(f"{p.name} is now the host.")
            break