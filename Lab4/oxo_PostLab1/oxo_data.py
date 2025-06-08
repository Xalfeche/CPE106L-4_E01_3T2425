def saveGame(game):
    with open('saved_game.txt', 'w') as f:
        f.write(''.join(game))

def restoreGame():
    try:
        with open('saved_game.txt', 'r') as f:
            game = f.read()
            return list(game)
    except FileNotFoundError:
        return []  # Return an empty list if no saved game exists