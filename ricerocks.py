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
explosion_group = set([])

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
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p,q):
    return math.sqrt((p[0] - q[0]) ** 2+(p[1] - q[1]) ** 2)


# Ship class
class Ship:
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0.0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        
    def draw(self,canvas):
        if self.thrust:
            canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)
        else:
            canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)

    def update(self):
        self.angle += self.angle_vel
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT
        self.vel[0] *= 0.99
        self.vel[1] *= 0.99
        if self.thrust:
            self.vel[0] += 0.1*angle_to_vector(self.angle)[0]
            self.vel[1] += 0.1*angle_to_vector(self.angle)[1]
            
    def angle_vel_inc(self, angle_acc):
        self.angle_vel += angle_acc
    
    def angle_vel_dec(self):
        self.angle_vel = 0
    
    def thrusters_on(self):
        self.thrust = True
        self.image_center = [135, 45]
        ship_thrust_sound.rewind()
        ship_thrust_sound.play()
        
    def thrusters_off(self):
        self.thrust = False
        self.image_center = [45, 45]
        ship_thrust_sound.pause()
    
    def shoot(self):
        global a_missile
        missile_pos = [self.pos[0]+self.radius*angle_to_vector(self.angle)[0], self.pos[1]+self.radius*angle_to_vector(self.angle)[1]]
        missile_vel = [self.vel[0]+6*angle_to_vector(self.angle)[0], self.vel[1]+6*angle_to_vector(self.angle)[1]]
        a_missile = Sprite(missile_pos, missile_vel, 0, 0, missile_image, missile_info, missile_sound)
        missile_group.add(a_missile)
    
    def get_position(self):
        return self.pos
    
    def get_radius(self):
        return self.radius
    
    
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
        if self.animated:
            center = [self.age * self.image_size[0] + self.image_center[0], self.image_center[1]]
            canvas.draw_image(self.image, center, self.image_size, self.pos, self.image_size, self.angle)
        else:
            canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)
    
    def update(self):
        self.angle += self.angle_vel
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT
        self.age += 1
        if self.age < self.lifespan:
            return False
        return True
    
    def collide(self, other_object):
        if dist(self.get_position(),other_object.get_position()) <= self.get_radius() + other_object.get_radius():
            return True
        return False
        
    def get_position(self):
        return self.pos
    
    def get_radius(self):
        return self.radius

           
def draw(canvas):
    global time, lives, score, started, my_ship
    global rock_group, missile_group, explosion_group
    
    # animiate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))

    #draw & update ship
    my_ship.draw(canvas)
    my_ship.update()
    
    if started:
        soundtrack.play()
        #draw grouped objects
        process_sprite_group(rock_group, canvas)
        process_sprite_group(missile_group, canvas)
        process_sprite_group(explosion_group, canvas)
        
        #check for collides
        score += 10 * group_group_collide(rock_group, missile_group)
        if group_collide(rock_group, my_ship):
            lives -= 1
        if lives == 0:
            started = False
            rock_group = set([])
            missile_group = set([])
            explosion_group = set([])
            soundtrack.pause()
            ship_thrust_sound.pause()
            my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
    else:
        canvas.draw_image(splash_image, splash_info.get_center(), splash_info.get_size(), (WIDTH / 2, HEIGHT / 2), splash_info.get_size())
        
        
    # draw text
    canvas.draw_text("Lives: " + str(lives), (30, 30), 22, 'White', 'sans-serif')
    str1_width = frame.get_canvas_textwidth("Score", 22, 'sans-serif')
    canvas.draw_text("Score", (WIDTH - (str1_width + 30), 30), 22, 'White', 'sans-serif')
    str2_width = frame.get_canvas_textwidth(str(score), 22, 'sans-serif')
    canvas.draw_text(str(score), (WIDTH - (str2_width + 30), 52), 22, 'White', 'sans-serif')
            
def keydown(key):
    global started
    if started:
        if key == simplegui.KEY_MAP["right"]:
            my_ship.angle_vel_inc(0.05)
        elif key == simplegui.KEY_MAP["left"]:
            my_ship.angle_vel_inc(-0.05)
        elif key == simplegui.KEY_MAP["up"]:
            my_ship.thrusters_on()
        elif key == simplegui.KEY_MAP["space"]:
            my_ship.shoot()

def keyup(key):
    global started
    if started:
        if key == simplegui.KEY_MAP["right"]:
            my_ship.angle_vel_dec()
        elif key == simplegui.KEY_MAP["left"]:
            my_ship.angle_vel_dec()
        elif key == simplegui.KEY_MAP["up"]:
            my_ship.thrusters_off()

def click(pos):
    global started, lives, score, my_ship
    if not started:
        started = True
        lives = 3
        score = 0
        soundtrack.rewind()
        my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)

# timer handler that spawns a rock    
def rock_spawner():
    global started, rock_group, tot_rocks
    if started and len( list(rock_group) ) < 12:
        a_rock = Sprite([random.randrange(0, WIDTH), random.randrange(0, HEIGHT)], [random.randint(-10, 10)/10, random.randint(-10, 10)/10], random.random()*random.choice([-1, 1]), (random.random()*random.choice([-1, 1]))/10, asteroid_image, asteroid_info)
        rock_group.add(a_rock)
        
def process_sprite_group(group, canvas):
    objs_to_rmv = set([])
    for obj in group:
        obj.draw(canvas)
        if obj.update():
            objs_to_rmv.add(obj)
    group.difference_update(objs_to_rmv)

def group_collide(group, other_obj):
    objs_to_rmv = set([])
    for obj in group:
        if obj.collide(other_obj):
            objs_to_rmv.add(obj)
            explosion_anime(other_obj)
    group.difference_update(objs_to_rmv)
    if len( list(objs_to_rmv) ) == 0:
        return False
    return True

def group_group_collide(group, other_group):
    group_elm = 0
    for obj in group:
        if group_collide(other_group, obj):
            group_elm += 1
            group.discard(obj)
            explosion_anime(obj)
    return group_elm
    
def explosion_anime(obj):
    global explosion_group
    an_explosion = Sprite(obj.get_position(), [0,0], 0, 0, explosion_image, explosion_info, explosion_sound)
    explosion_group.add(an_explosion)
    
# initialize frame
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# initialize ship and two sprites
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
rock_group = set([])
missile_group = set([])

# register handlers
frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)
frame.set_mouseclick_handler(click)
timer = simplegui.create_timer(1000.0, rock_spawner)

# get things rolling
timer.start()
frame.start()
