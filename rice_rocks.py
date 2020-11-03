# To run the program, go to 
# http://www.codeskulptor.org/#user47_VeqWIztrW3LK42j.py

# program template for Spaceship
import simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
lives = 3
time = 0
started = False

class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

    
# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.f2014.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
ship_thrust_sound.set_volume(.5)
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

# alternative upbeat soundtrack by composer and former IIPP student Emiel Stopler
# please do not redistribute without permission from Emiel at http://www.filmcomposer.nl
#soundtrack = simplegui.load_sound("https://storage.googleapis.com/codeskulptor-assets/ricerocks_theme.mp3")

# All helper functions
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p,q):
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)

# Collison detection
def process_sprite_group(group, canvas):
    for sprite in set(group):
        sprite.draw(canvas)
        if sprite.update():
            group.remove(sprite)

def group_collide(group, other_object):
    collision = False
    for sprite in set(group):
        if sprite.collide(other_object):
            collision = True
            group.remove(sprite)
            explosion_group.add(Sprite(sprite.pos, [0, 0], 0, 0, explosion_image, explosion_info, explosion_sound))
    return collision

def group_group_collide(group, other_group):
    counter = 0
    for sprite in set(group):
        if group_collide(other_group, sprite):
            group.remove(sprite)
            counter += 1
    return counter 
               

# Ship class
class Ship:
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        
    def draw (self, canvas):
        if self.thrust:
            canvas.draw_image (self.image, [130, 45], self.image_size, self.pos, self.image_size, self.angle)
        else:
            canvas.draw_image (self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)

    def update(self):
        friction = 0.20 / 60
        acceleration_scale = 0.08
        
        self.angle += self.angle_vel
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT
        self.vel[0] *= (1 - friction)
        self.vel[1] *= (1 - friction)
        
        if self.thrust:
            m_forward = angle_to_vector (self.angle)
            self.vel[0] += m_forward[0] * acceleration_scale
            self.vel[1] += m_forward[1] * acceleration_scale

    
    def increase_angle_vel(self):
        self.angle_vel += .04
    
    def decrease_angle_vel(self):
        self.angle_vel -= .04
    
    def thrusting(self, thrust_is_on):
        self.thrust = bool(thrust_is_on)
        
        if self.thrust:
            ship_thrust_sound.rewind()
            ship_thrust_sound.play()
        else:
            ship_thrust_sound.pause()
        
    def shoot_missile (self):
        global missile_group
        
        forward = angle_to_vector(self.angle)
        missile_position = [self.pos[0] + forward[0] * self.radius, self.pos[1] + forward[1] * self.radius]
        missile_velocity = [self.vel[0] + forward[0] * 6, self.vel[1] + forward[1] * 6]
        missile_group.add(Sprite(missile_position, missile_velocity, self.angle, 0, missile_image, missile_info, missile_sound))

        
# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        
        if sound:
            sound.rewind()
            sound.play()
   
    def draw(self, canvas):
        center = list(self.image_center)
        
        if self.animated:
            center[0] = self.image_center[0] + (self.image_size[0] * self.age)
        canvas.draw_image(self.image, center, self.image_size, self.pos, self.image_size, self.angle)

    def update(self):
        self.angle += self.angle_vel
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT
        self.age += 1
        return self.age > self.lifespan
    
    def collide(self, other_object):
        return dist(self.pos, other_object.pos) <= (self.radius + other_object.radius)
        

# Ship key handlers      
def down(key):
    if key == simplegui.KEY_MAP['left']:
        my_ship.decrease_angle_vel()
    elif key == simplegui.KEY_MAP['right']:
        my_ship.increase_angle_vel()
    elif key == simplegui.KEY_MAP['space']:
        my_ship.shoot_missile()
    elif key == simplegui.KEY_MAP['up']:
         my_ship.thrusting(True)

def up(key):
    if key == simplegui.KEY_MAP['left']:
        my_ship.increase_angle_vel()
    elif key == simplegui.KEY_MAP['right']:
        my_ship.decrease_angle_vel()
    elif key == simplegui.KEY_MAP['up']:
         my_ship.thrusting(False)

# mouseclick handlers to reset UI for splash screen
def click(pos):
    global started, soundtrack, lives, score
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and inwidth and inheight:
        started = True
        score = 0
        lives = 3
        soundtrack.rewind()
        soundtrack.play()            
    
def draw(canvas):
    global time, rock_group, lives, score, missile_group, started
    
    # animiate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))

    # draw ship and sprites
    my_ship.draw(canvas)
    process_sprite_group(rock_group, canvas)
    process_sprite_group(missile_group, canvas)
    process_sprite_group(explosion_group, canvas)
    
    # checks if game is over
    if lives == 0:
        rock_group = set()
        started = False
        
    # check for collisions and decrement lives or increment score
    if group_collide(rock_group, my_ship):
        lives -= 1
    score += group_group_collide(missile_group, rock_group) * 10
    
    # update ship and sprites
    my_ship.update()
    
    # draw splash screen if not started
    if not started:
        canvas.draw_image(splash_image, splash_info.get_center(),
                          splash_info.get_size(), [WIDTH / 2, HEIGHT / 2],
                          splash_info.get_size())
    
    # Lives and Score
    canvas.draw_text ('Lives: '+ str(lives), (60, 40), 36, "White")
    canvas.draw_text ('Score: '+ str(score), (605, 40), 36, "White")

# timer handler that spawns a rock    
def rock_spawner():
    global rock_group, started
    
    if len(rock_group) > 12 or not started:
        return
    rock_vel = [random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3]
    rock_avel = random.random() * 0.3 - 0.1
    rock_pos = [random.randrange(0, WIDTH), random.randrange(0, HEIGHT)]
    
    while dist(rock_pos, my_ship.pos) < 120:
        rock_pos = [random.randrange(0, WIDTH), random.randrange(0, HEIGHT)]
    rock_group.add(Sprite(rock_pos, rock_vel, 0, rock_avel, asteroid_image, asteroid_info))
    
    
# initialize frame
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# initialize ship and sprites
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
rock_group = set()
missile_group = set()
explosion_group = set()


# register handlers
frame.set_draw_handler(draw)
frame.set_keydown_handler(down)
frame.set_keyup_handler(up)
frame.set_mouseclick_handler(click)

timer = simplegui.create_timer(1300.0, rock_spawner)

# get things rolling
timer.start()
frame.start()