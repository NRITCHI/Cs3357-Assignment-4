import pygame
import socket
import rsa


rgb_colors = [
    (255, 0, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 165, 0),
] 
# Initialize Pygame
pygame.init()


# create rsa keys
publicKey, clientKey = rsa.newkeys(1024)


# Set up the display
width, height = 500, 500
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Client")

# Global variables
client_number = 0

# Connect to the server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 5555))
sock.send(publicKey.save_pkcs1("PEM"))
serverKey = rsa.PublicKey.load_pkcs1(sock.recv(4096), "PEM")

sock.settimeout(0.1)

# draw the game state
def draw_game_state(game_statee):
    # Reset screen to black before drawing
    win.fill((0, 0, 0))

    try:
        Message = rsa.decrypt(game_state, clientKey).decode()
        if "z" in Message:
            print("Congratulations!")
        elif "x" in Message:
            print("It works!")
        elif "c" in Message:
            print("Ready?")

    except:
        pass

    try:
        game_state = game_statee.decode()





        # When game states are concatonated split them
        if ')(' in game_state:
            # Find the last occurrence of ')(' which is likely where the split should occur
            split_index = game_state.rfind(')(')
            # Add a split character '|' to separate the two game states
            game_state = game_state[:split_index+1] + '|' + game_state[split_index+1:]


        #print('gamestate: ' + game_state)

        # Split game state into snake positions and snack positions and discard the previously concatonated game state
        if '|' in game_state:
            snake_pos_str, snacks_pos_str = game_state.split('|', 2)[slice(2)]
            
            #snake_pos_str, snacks_pos_str = game_state.split('|')
            #snake_pos_str, snacks_pos_str = game_state.split('|', 1)
            snake_positions = snake_pos_str.split('**')
            #print("test" + snacks_pos_str)

            # Draw each snake
            for snake_str in snake_positions:
                snake_body = snake_str.split('*')
                #i = snake_positions[snake_str]
                i = snake_positions.index(snake_str)
                color = rgb_colors[i % len(rgb_colors)]
                for pos_str in snake_body:
                    if pos_str:  # Ensure the position is not empty
                        x, y = map(int, pos_str.strip('()').split(','))
                        pygame.draw.rect(win, color, (x * 20, y * 20, 20, 20))

            # Draw the snacks
            snack_positions = snacks_pos_str.split('**')
            for snack_pos_str in snack_positions:
                if snack_pos_str:  # Ensure the position is not empty
                    #print("post split:" + snack_pos_str)
                    x, y = map(int, snack_pos_str.strip('()').split(','))
                    pygame.draw.rect(win, (0, 255, 0), (x * 20, y * 20, 20, 20))

        # Update display
        pygame.display.update()
    except:
        pass

# Main loop
def main():
    keyboard_event = False
    

    run = True
    while run:
        #keyboard_event = False
        pygame.time.delay(50)
        #keyboard_event = False
        #send quit command if needed
        getstate = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            # Send movement commands to the server
            if event.type == pygame.KEYDOWN:
                #input = True
                if event.key == pygame.K_LEFT:
                    #sock.send("left".encode())
                    sock.send(rsa.encrypt("left".encode(), serverKey))
                    getstate = False
                if event.key == pygame.K_RIGHT:
                    #sock.send("right".encode())
                    sock.send(rsa.encrypt("right".encode(), serverKey))
                    getstate = False
                if event.key == pygame.K_UP:
                    #sock.send("up".encode())
                    sock.send(rsa.encrypt("up".encode(), serverKey))
                    getstate = False
                if event.key == pygame.K_DOWN:
                    #sock.send("down".encode())
                    sock.send(rsa.encrypt("down".encode(), serverKey))
                    getstate = False
                if event.key == pygame.K_z:
                    print("z pressed")
                    getstate = False
                    sock.send(rsa.encrypt("z".encode(), serverKey))
                if event.key == pygame.K_x:
                    sock.send(rsa.encrypt("x".encode(), serverKey))
                if event.key == pygame.K_c:
                    sock.send(rsa.encrypt("c".encode(), serverKey))
            
        if getstate:
            sock.send(rsa.encrypt("get".encode(), serverKey))
            #getstate = True

        try:
            #game_state = sock.recv(2048).decode()
            game_state = sock.recv(2048)
        except:
            pass

        # Draw the game state
        draw_game_state(game_state)

    sock.close()

if __name__ == "__main__":
    main()