from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import basic_lighting_shader
import csv

#fullscreen
window.size = window.fullscreen_size
window.position = Vec2(0, 0)


app = Ursina()
# Pause the game immediately when it starts
application.paused = True

# Start game function is called when the player clicks the start button, begins the game and disables the menu
def start_game():
    player.name = name_input_field.text
    menu.enabled = False
    player.enabled = True
    enemy.enabled = True
    mouse.locked = True
    application.paused = False
    title.enabled = False
    name_input_field.enabled = False
    start_button.enabled = False
    damage_Text.enabled = True
    damage_text.enabled = True
    description.enabled = False
    description2.enabled = False
    description3.enabled = False
    description4.enabled = False


# Create a menu entity and add a title and description text objects to it
menu = Entity(enabled=True)
title = Text(text="Killer Head", origin=(0, -3), scale=5, color=color.white)
#Add a description of the game
description = Text(text="The goal is to do as much damage as possible without dying! Watch out for the obstacles!", origin=(0, -6), scale=1, color=color.white)
description2 = Text(text="You can pick up damage and speed boosts to help you! They spawn every 15 seconds.", origin=(0, -4), scale=1, color=color.white)
description3 = Text(text="The killer will get increased speed as the game progresses! He gets buffed every 15 seconds.", origin=(0, -2), scale=1, color=color.white)
description4 = Text(text="Press TAB to pause", origin=(0, 0), scale=1, color=color.white)
# Create an input field for the player's name and a start button to begin the game
name_input_field = InputField(position=(0, -0.1), text="Enter your name")
start_button = Button(text="Start", position=(0, -0.2), scale=(0.2, 0.1), color=color.green, on_click=start_game)

# Write the player's name and damage dealt to the scoreboard file
def write_scoreboard(name, damage_dealt):

    with open('UrsinaFPS/scoreboard.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([name, damage_dealt])

# Read the scoreboard from the CSV file and sort it by damage dealt
def read_scoreboard():
    with open('UrsinaFPS/scoreboard.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        scoreboard = []
        for row in reader:
            scoreboard.append(row)
        scoreboard.sort(key=lambda x: int(x[1]), reverse=True)
        return scoreboard

# Formats the scoreboard into a string that can be displayed to the player
def format_scoreboard(scoreboard):
    formatted_scoreboard = ''
    for i, row in enumerate(scoreboard):
        formatted_scoreboard += f'{i+1}. {row[0]} - {row[1]} damage\n'
    return formatted_scoreboard

# Reads the scoreboard from the CSV file, formats it, and displays it to the player
def open_scoreboard():
    scoreboard = read_scoreboard()
    formatted_scoreboard = format_scoreboard(scoreboard)
    scoreboard_panel.enabled = True
    scoreboard_panel.content = Text(text=formatted_scoreboard, origin=(0, -0.5), scale=1)


# Called when the player dies in the game
def on_die():
    global damage_dealt
    # Writes the player's name and damage dealt to the scoreboard file
    write_scoreboard(player.name, damage_dealt)
    damage_dealt = 0
    # Disables the player and enemy objects and unlocks the mouse
    player.enabled = False
    enemy.enabled = False
    mouse.locked = False
    # Pauses the game and displays a "You died!" message to the player
    application.pause()
    print_on_screen("You died!", position=(-0.25,0), scale=5, duration=3)
    # Enables the quit and scoreboard buttons and disables the damage text objects
    quit_button.enabled = True
    scoreboard_button.enabled = True
    damage_text.enabled = False
    damage_Text.enabled = False




#camera

editor_camera = EditorCamera(enabled=False, ignore_paused=True)
# Player class
class Player(FirstPersonController):
    def __init__(self, **kwargs):
        super().__init__(model='cube', position=(20,0,0), z=-10, color=color.light_gray, origin_y=-0.5, speed=8, gun_damage=10, **kwargs)
        self.name = 'Player'

    def on_trigger_enter(self, other):
        if isinstance(other, Pickup):
            # Check if the player is within a certain distance of the pickup
            if distance(self.position, other.position) < 2:
                # Call the on_pickup method of the pickup
                other.on_pickup()
# Initialize the player
player = Player()

player.on_die = on_die

player.enabled = False
damage_Text = Text(text='Damage dealt:', position=(-0.87,0.47))
damage_Text.enabled = False
# Array of pickup objects
pickups = []

# Pickup class
class Pickup(Entity):
    def __init__(self, **kwargs):
        super().__init__(model='cube', texture=None, scale=0.5, collider='box', **kwargs)
        # The type of pickup, either damage or speed
        self.pickup_type = random.choice(['damage', 'speed'])
        # Set the color of the pickup based on its type
        if self.pickup_type == 'damage':
            self.color = color.red
        elif self.pickup_type == 'speed':
            self.color = color.blue
    # Called when the player collides with the pickup
    def on_pickup(self):
        if self.pickup_type == 'damage':
            player.gun_damage += 1
            # Show a pickup text for 2 seconds
            message = Text(text='Picked up damage boost!', position=(0, 0.4), origin=(0, 0), scale=2, color=color.red)
        elif self.pickup_type == 'speed':
            player.speed += 1
            # Show a pickup text for 2 seconds
            message = Text(text='Picked up speed boost!', position=(0, 0.4), origin=(0, 0), scale=2, color=color.blue)
        self.visible = False
        self.disable()
        self.enabled = False
        pickups.remove(self)
        destroy(message, delay=2)

# Spawn a pickup at a random position
def spawn_pickup():
    position = (random.uniform(-20, 20), 0.5, random.uniform(-20, 20))
    pickup = Pickup(position=position)
    pickups.append(pickup)
    
# Spawn a pickup every 15 seconds
def spawn_pickups():
    spawn_pickup()
    invoke(spawn_pickups, delay=15)

# Inital call to spawn_pickups
invoke(spawn_pickups, delay=15)



#gun
playergun = Entity(model="cube", position=(0.25,-0.25,1), parent=camera, scale=(0.1,0.1,1), origin_z=0.5, on_cooldown=False, color=color.light_gray,shader=basic_lighting_shader)
playergun.muzzle_flash = Entity(parent=playergun, z=1, y=-2, x=2, world_scale=.3, model='quad', color=color.yellow, enabled=False)
#variable for the damage dealt that will be used in the scoreboard
damage_dealt = 0
damage_text = Text(text='0', position=(-0.70,0.47))
damage_text.enabled = False
shootables_parent = Entity()

mouse.traverse_target = shootables_parent

#Buttons for the pause menu
quit_button = Button(text="Quit", on_click=application.quit, position=(0,0.4), scale=(0.1,0.05), color=color.red, ignore_paused=True, enabled=False)
scoreboard_button = Button(text="Scoreboard", on_click=open_scoreboard, position=(0,0.3), scale=(0.2,0.05), color=color.green, ignore_paused=True, enabled=False)


#obstacles and ground
ground = Entity(model='plane', collider='box', scale=64, texture='Assets/pexels-stefwithanf-3580088-1920x1080-25fps.mp4',shader=basic_lighting_shader)

# Scoreboard panel(displays the scoreboard)
scoreboard_panel = WindowPanel(title='Scoreboard', content=None, enabled=False, draggable=True, resizable=True, close_button=True, min_size=(400, 300), max_size=(800, 600))

# Spawns 10 obstacles in random positions
for i in range(10):
    Entity(model='cube', origin_y=-.5, scale=3, texture='vertical_gradient',
        x=random.uniform(-24,24),
        z=random.uniform(-24,24),
        collider='box',
        scale_y = random.uniform(4,7),
        shader=basic_lighting_shader,
        )

# Shoot function
def shoot():
    global damage_dealt
    # If the player gun is not on cooldown, the player can shoot
    if not playergun.on_cooldown:
        playergun.on_cooldown = True
        playergun.muzzle_flash.enabled = True
        invoke(playergun.muzzle_flash.disable, delay=.05)
        # Set a cooldown for the player gun
        invoke(setattr, playergun, 'on_cooldown', False, delay=0.3)
        #If the player is looking at the enemy, the enemy will take damage
        if mouse.hovered_entity == enemy:
            damage_dealt += player.gun_damage
            damage_text.text = damage_dealt
            enemy.blink(color.white, duration=.2)

#main update for shooting input and pickups
def update():
    if held_keys['left mouse']:
        shoot()
    #If the player is within a certain distance of a pickup, the pickup will be picked up
    for pickup in pickups:
        if distance(player.position, pickup.position) < 2:
            pickup.on_pickup()
    
#pause function
def pause(key):
    #Tab will be used as a pause button, it will pause the enemy and the player, and unlock the mouse so you can access a menu
    if key =="tab":
        editor_camera.enabled = not editor_camera.enabled

        player.visible_self = editor_camera.enabled
        player.cursor.enabled = not editor_camera.enabled
        playergun.enabled = not editor_camera.enabled
        mouse.locked = not editor_camera.enabled
        editor_camera.position = player.position

        application.paused = editor_camera.enabled

        #enable all the menu/pause buttons
        quit_button.enabled = editor_camera.enabled

# Pause handler
pause_handler = Entity(ignore_paused=True, input=pause)


# Enemy class
class Enemy(Entity):
    def __init__(self, **kwargs):    
        super().__init__(parent=shootables_parent, model='Assets/ToughGuy.obj', scale_y=2,scale_x=2,scale_z=2, origin_y=-0.75, color=color.light_gray, collider='box',shader=basic_lighting_shader, enemyspeed=1, **kwargs)
        self.color = color.red
        self.has_written_to_csv = False

    #Increase enemy speed        
    def increase_speed(self):
        self.enemyspeed += 0.5

    #Enemy movement
    def update(self):
        #If the player is too far away, the enemy will not move
        dist = distance_xz(player.position, self.position)
        if dist > 80:
            return
        #If the player is close enough, the enemy will move towards the player 
        self.look_at_2d(player, "y")
        distance_to_player = distance_xz(self.position, player.position)
        if distance_to_player >= 2.5:
            self.position += self.forward * time.dt * self.enemyspeed
        else:
            #If the enemy is close enough to the player, the player will die
            if not self.has_written_to_csv:
                player.on_die()
                self.has_written_to_csv = True
        hit_info = raycast(self.world_position + Vec3(0,1,0), self.forward, 30, ignore=(self,))
        if hit_info.entity == player:
            if dist > 2:
                self.position += self.forward * time.dt * 5
        
#Increase enemy speed every 15 seconds
def increase_enemy_speed():
    enemy.increase_speed()
    invoke(increase_enemy_speed, delay=15)
#spawn enemy
enemy = Enemy()
enemy.enabled = False
#Increase enemy speed every 15 seconds(inital call)
invoke(increase_enemy_speed, delay=15)

#lighting
sun = DirectionalLight()
sun.look_at(Vec3(1,-1,-1))
Sky()

app.run()