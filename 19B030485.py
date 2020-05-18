import pygame
import pygame_menu
from enum import Enum
import random, time
import threading 
from threading import Thread
import pika, uuid, json

pygame.init()
width = 800 + 180
height = 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Tanks')
font = pygame.font.SysFont("Times New Roman", 20)
shot = pygame.mixer.Sound("Shot.wav")
end = pygame.mixer.Sound("the_end.wav")
music = pygame.mixer.music.load("Music.wav")

def single_player():
    pygame.init()
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

    class Direction(Enum):
        UP = 1
        DOWN = 2
        LEFT = 3
        RIGHT = 4

    class Tank(object):

        def __init__(self, x, y, img, bullets, walls, d_right=pygame.K_RIGHT, d_left=pygame.K_LEFT, d_up=pygame.K_UP, d_down=pygame.K_DOWN):
            self.x = x
            self.y = y
            self.speed = 4
            self.img = img
            self.width = 40
            self.direction = Direction.RIGHT
            self.hp = 3
            self.rect = pygame.Rect(self.x,self.y,self.width,self.width)
            self.bullets = bullets
            self.walls = walls
            self.is_add = False
            self.KEY = {d_right: Direction.RIGHT, d_left: Direction.LEFT,
                        d_up: Direction.UP, d_down: Direction.DOWN}

        def draw(self):
            if self.direction == Direction.RIGHT:
                right = pygame.transform.rotate(self.img, 90)
                screen.blit(right, (self.x, self.y))

            if self.direction == Direction.LEFT:
                left = pygame.transform.rotate(self.img, 270)
                screen.blit(left,  (self.x, self.y))

            if self.direction == Direction.UP:
                up = pygame.transform.rotate(self.img, 180)
                screen.blit(up,  (self.x, self.y))

            if self.direction == Direction.DOWN:
                down = pygame.transform.rotate(self.img, 0)
                screen.blit(down,  (self.x, self.y))


        def change_direction(self, direction):
            self.direction = direction

        def move(self):
            if self.direction == Direction.LEFT:
                self.x -= self.speed
            if self.direction == Direction.RIGHT:
                self.x += self.speed
            if self.direction == Direction.UP:
                self.y -= self.speed
            if self.direction == Direction.DOWN:
                self.y += self.speed
            self.draw()
            self.edge()

        def bullet(self):
            if len(self.bullets) == 0:
                if self.direction == Direction.RIGHT:
                    self.bullets.append(snaryad(self.x + self.width, self.y + int(self.width / 3), 270, 1))
                    pygame.mixer.Sound.play(shot)
                if self.direction == Direction.LEFT:
                    self.bullets.append(snaryad(self.x, self.y + int(self.width / 3), 90, -1))
                    pygame.mixer.Sound.play(shot)
                if self.direction == Direction.UP:
                    self.bullets.append(snaryad(self.x + int(self.width / 3), self.y, 0, -1))
                    pygame.mixer.Sound.play(shot)
                if self.direction == Direction.DOWN:
                    self.bullets.append(snaryad(self.x + int(self.width / 3), self.y + self.width, 180, 1))
                    pygame.mixer.Sound.play(shot)

        def edge(self):
            if self.x > width:
                self.x = 0
                self.x += self.speed
            if self.x < 0:
                self.x = width
                self.x += self.speed
            if self.y > height:
                self.y = 0
                self.y += self.speed
            if self.y < 0:
                self.y = height
                self.y += self.speed

        def decr(self):
            self.speed -= 4
            for bullet in self.bullets:
                bullet.vel -= bullet.vel

        def eat(self):
            if pygame.Rect(self.x, self.y, self.width, self.width).colliderect(pygame.Rect(food.x, food.y, food.width, food.width)):
                self.is_add = True
                food.x = random.randint(80, 520)
                food.y = random.randint(80, 520)
                timer = threading.Timer(5, self.decr)
                timer.start()

            if self.is_add:
                self.speed += 4
                for bullet in self.bullets:
                    bullet.vel += bullet.vel
                self.is_add = False
        
        def wall(self):
            for w in self.walls:
                if pygame.Rect(self.x, self.y, self.width, self.width).colliderect(pygame.Rect(w.x, w.y, w.size, w.size)):
                    self.walls.remove(w)
                    self.hp -= 1

    class snaryad(object):
        
        def __init__(self, x, y, angle, facing):
            self.x = x
            self.y = y
            self.img = pygame.image.load("fire.png")
            self.width = 20
            self.angle = angle
            self.vel = 20 * facing
            self.facing = facing
            self.rect = pygame.Rect(self.x, self.y, 15, 20)
            
        def draw(self):
            new = pygame.transform.rotate(self.img, self.angle)
            screen.blit(new, (self.x, self.y))

        def move(self, bullets, tank):
            if self.x > 0 and self.x < width and self.y > 0 and self.y < height:
                if tank.direction == Direction.RIGHT or tank.direction == Direction.LEFT:
                    self.x += self.vel
                if tank.direction == Direction.UP or tank.direction == Direction.DOWN:
                    self.y += self.vel
            else:
                bullets.pop(bullets.index(bullet))

        def war(self, walls):
            for w in walls:
                if pygame.Rect(self.x, self.y, 15, 20).colliderect(pygame.Rect(w.x, w.y, w.size, w.size)):
                    walls.remove(w)
        
        def spr(self, bullets, tank):
            if pygame.Rect(self.x, self.y, 15, 20).colliderect(pygame.Rect(tank.x, tank.y, tank.width, tank.width)):
                bullets.pop(bullets.index(bullet)) 
                tank.hp -= 1

    class Food(object):

        def __init__(self):
            self.x = random.randint(80, 520)
            self.y = random.randint(80, 520)
            self.width = 35
            self.image = pygame.image.load("1.png")
            self.rect = pygame.Rect(self.x, self.y, self.width, self.width)

        def draw(self):
            screen.blit(self.image, (self.x, self.y))

    class Wall(object):
        def __init__(self):
            self.x = random.randint(40, width - 40)
            self.y = random.randint(40, height - 40)
            self.size = 16
            self.img = pygame.image.load("wall.png")
            self.are = True
            self.rect = pygame.Rect(self.x, self.y, self.size, self.size)

        def draw(self):
            screen.blit(self.img,(self.x,self.y))

    def game_over():
        img = pygame.image.load("gameover.jpg")
        screen.blit(img, (0, 0))
        pygame.mixer.music.pause()
        pygame.mixer.Sound.play(end)
        pygame.display.update()
        time.sleep(5)
        pygame.quit()

    food = Food()
    mainloop = True
    bullets1 = []
    bullets2 = []
    walls = []
    FPS = 30
    clock = pygame.time.Clock()
    img1 = pygame.image.load("tank1.png")
    img2 = pygame.image.load("tank2.png")
    tank1 = Tank(200, 200, img1, bullets1, walls)
    tank2 = Tank(100, 100, img2, bullets2, walls, pygame.K_d, pygame.K_a, pygame.K_w, pygame.K_s)
    tanks = [tank1, tank2]
    walls.append(Wall())
    walls.append(Wall())

    while mainloop:
        mill = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                mainloop = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    mainloop = False
                if event.key == pygame.K_RETURN:
                    tank1.bullet()            
                if event.key == pygame.K_SPACE:
                    tank2.bullet()
                    
                for tank in tanks:
                    if event.key in tank.KEY.keys():
                        tank.change_direction(tank.KEY[event.key])
        for bullet in bullets1:
            bullet.move(bullets1, tank1)
            bullet.spr(bullets1, tank2)
        for bullet in bullets2:
            bullet.move(bullets2, tank2)
            bullet.spr(bullets2, tank1)

        screen.fill((0, 0, 0))
        screen.blit(font.render(f"Hp: {tank2.hp}", 1, (255, 0, 0)),(18, 0))
        screen.blit(font.render(f"Hp: {tank1.hp}", 1, (0, 255, 0)), (920,0))
        tank1.eat()
        tank2.eat()
        tank1.wall()
        tank2.wall()
        if pygame.Rect(tank1.x, tank1.y, tank1.width, tank1.width).colliderect(pygame.Rect(tank2.x, tank2.y, tank2.width, tank2.width)):
            tank1.x += tank1.speed
            tank2.x -= tank2.speed
        for bullet in bullets1:
            bullet.war(walls)
        for bullet in bullets2:
            bullet.war(walls)    
        if tank1.hp == 0 or tank2.hp == 0:
            game_over()
        for tank in tanks:
            tank.move()
        for bullet in bullets1:
            bullet.draw()
        for bullet in bullets2:
            bullet.draw()
        for wall in walls:
            wall.draw()
        food.draw()
        pygame.display.flip()

def multiplayer_mode():
    IP = '34.254.177.17'
    PORT = 5672
    VIRTUAL_HOST = 'dar-tanks'
    USERNAME = 'dar-tanks'
    PASSWORD = '5orPLExUYnyVYZg48caMpX'
    pygame.init()
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
    class TankRpcClient:
        def __init__(self):
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host = IP,
                    port = PORT,
                    virtual_host = VIRTUAL_HOST,
                    credentials = pika.PlainCredentials(
                        username = USERNAME,
                        password = PASSWORD
                    )
                )
            )
            self.channel = self.connection.channel()
            queue = self.channel.queue_declare(queue='',
                                            auto_delete=True,
                                            exclusive= True)
            self.callback_queue = queue.method.queue
            self.channel.queue_bind(
                exchange = 'X:routing.topic',
                queue = self.callback_queue
            )

            self.channel.basic_consume(
                queue = self.callback_queue,
                on_message_callback=self.on_response,
                auto_ack = True
            )
            self.token = None
            self.tank_id = None
            self.room_id = None

        def on_response(self, ch, method, props, body):#Принимает запрос
            if self.corr_id == props.correlation_id:
                self.response = json.loads(body)

        def call(self, key, message):
            self.response = None
            self.corr_id = str(uuid.uuid4())
            self.channel.basic_publish(
                exchange = 'X:routing.topic',
                routing_key = key,
                properties=pika.BasicProperties(
                    reply_to =self.callback_queue,
                    correlation_id = self.corr_id
                ),
                body = json.dumps(message)
            )
            while self.response is None:
                self.connection.process_data_events()

        def check_server(self): #Healthcheck
            self.call('tank.request.healthcheck','')
            return self.response['status'] == '200'

        def obtain_token(self, room_id): #Register
            message = {
                'roomId':room_id
            }
            self.call('tank.request.register', message)
            if 'token' in self.response:
                self.token = self.response['token']
                self.tank_id = self.response['tankId']
                self.room_id = self.response['roomId']
                return True
            return False

        def turn_tank(self, token, direction):
            message = {
                'token': token,
                'direction': direction
            }
            self.call('tank.request.turn', message)

        def fire_bullet(self, token):
            message = {
                'token': token
            }
            self.call('tank.request.fire', message)


    class TankConsumerClient(Thread):
        def __init__(self, roomId):
            super().__init__()
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host = IP,
                    port = PORT,
                    virtual_host = VIRTUAL_HOST,
                    credentials = pika.PlainCredentials(
                        username = USERNAME,
                        password = PASSWORD
                    )
                )
            )
            self.channel = self.connection.channel()
            queue = self.channel.queue_declare(queue='',
                                            auto_delete=True,
                                            exclusive= True
                                            )
            event_listener = queue.method.queue
            self.channel.queue_bind(exchange='X:routing.topic',
                                    queue=event_listener,
                                    routing_key='event.state.'+roomId
                                    )
            self.channel.basic_consume(
                queue=event_listener,
                on_message_callback=self.on_response,
                auto_ack=True
            )
            self.response = None

        def on_response(self, ch, method, props, body):
            self.response = json.loads(body)
            print(self.response)

        def run(self):
            self.channel.start_consuming()

    UP = 'UP'
    DOWN = 'DOWN'
    LEFT = 'LEFT'
    RIGHT = 'RIGHT'

    MOVE_KEYS = {
        pygame.K_w: UP,
        pygame.K_s: DOWN,
        pygame.K_d: RIGHT,
        pygame.K_a: LEFT
    }

    client = TankRpcClient()
    event_client = TankConsumerClient('room-1')
    event_client.daemon = True

    def draw_tank(id, x, y, width, height, direction, health, score, img):
        if direction == RIGHT:
            right = pygame.transform.rotate(img, 90)
            screen.blit(right, (x, y))
        if direction == LEFT:
            left = pygame.transform.rotate(img, 270)
            screen.blit(left, (x, y))
        if direction == UP:
            up = pygame.transform.rotate(img, 180)
            screen.blit(up, (x, y))
        if direction == DOWN:
            down = pygame.transform.rotate(img, 0)
            screen.blit(down, (x, y))

    def draw_bullets(owner, x, y, width, height, direction, fire):
        if direction == RIGHT:
            right = pygame.transform.rotate(fire, 270)
            screen.blit(right, (x, y))
        if direction == LEFT:
            left = pygame.transform.rotate(fire, 90)
            screen.blit(left, (x, y))
        if direction == UP:
            up = pygame.transform.rotate(fire, 0)
            screen.blit(up, (x, y))
        if direction == DOWN:
            down = pygame.transform.rotate(fire, 180)
            screen.blit(down, (x, y))

    def information_panel(remaining_time):
        surface = pygame.Surface((200, 600))
        surface.fill((0, 51, 0))
        first_line = font.render('ID     | Health | Score ', True, (255, 255, 255))
        text = font.render('Remaining Time: {}'.format(remaining_time), True, (255, 255, 255))
        screen.blit(surface, (width-180, 0))
        screen.blit(text, (width-180, 0))
        screen.blit(first_line, (width-180, 30))

    def game_over():
        screen.fill((128, 128, 128))
        text = font.render('If you want to replay press R', True, (0, 90, 255))
        over = font.render('GAME  OVER!', True, (0, 90, 255))
        screen.blit(over, (150,150))
        screen.blit(text, (150, 170))
        pygame.mixer.music.pause()
        pygame.mixer.Sound.play(end)

    def game_start():
        mainloop = True
        win = False
        kick = False
        lose = False
        while mainloop:
            screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    mainloop = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        mainloop = False
                    elif event.key == pygame.K_SPACE:
                        client.fire_bullet(client.token)
                    elif event.key in MOVE_KEYS:
                        client.turn_tank(client.token, MOVE_KEYS[event.key])
                    elif event.key == pygame.K_r:
                        menu.mainloop(screen)
            try:
                remaining_time = event_client.response["remainingTime"]
            except:
                pass
            bullets = event_client.response['gameField']['bullets']
            tanks = event_client.response['gameField']['tanks']
            hits = event_client.response['hits']
            winners = event_client.response['winners']
            losers = event_client.response['losers']
            kicked = event_client.response['kicked']

            img1 = pygame.image.load("tank1m.png")
            img2 = pygame.image.load("tank2m.png")
            fire1 = pygame.image.load("fire1.png")
            fire2 = pygame.image.load("fire2.png")

            for tank in tanks:
                if tank['id'] == client.tank_id:
                    draw_tank(tank['id'], tank['x'], tank['y'], tank['width'], tank['height'], tank['direction'], tank['health'], tank['score'], img1)
                else:
                    draw_tank(tank['id'], tank['x'], tank['y'], tank['width'], tank['height'], tank['direction'], tank['health'], tank['score'], img2)
                
            for bullet in bullets:
                if bullet['owner'] == client.tank_id:
                    draw_bullets(bullet['owner'], bullet['x'], bullet['y'], bullet['width'], bullet['height'], bullet['direction'], fire1)
                else:
                    draw_bullets(bullet['owner'], bullet['x'], bullet['y'], bullet['width'], bullet['height'], bullet['direction'], fire2)
            
            try:
                information_panel(remaining_time)
            except:
                pass
            j = 50
            t = {}
            for tank in tanks:      
                t[tank['id']] = [tank['health'],tank['score']]
            t_sorted = {a: b for a, b in sorted(t.items(), key=lambda item: item[1][1], reverse = True)}
            for i,s in t_sorted.items():
                lines = font.render('{}   | {} | {}'.format(i, s[0], s[1]), True, (255, 255, 255))
                screen.blit(lines, (width-180, j))
                j += 20
            score_kick = 0
            score_lose = 0
            score_win = 0
            if kicked:
                for e in kicked:
                    if client.tank_id == e['tankId']:
                        kick = True
                        score_kick = e['score']
                    
            elif losers:
                for e in losers:
                    if client.tank_id == e['tankId']:
                        lose = True
                        score_lose = e['score']

            elif winners:
                for e in winners:
                    if client.tank_id == e['tankId']:
                        win = True
                        score_win = e['score']    
                        
            if kick == True:
                game_over()
                reason = font.render('You are kicked. Your score: {}'.format(score_kick), True, (0, 90, 255))
                screen.blit(reason, (150, 190))
            elif win == True:
                game_over()
                reason = font.render('You are winner. Your score: {}'.format(score_win), True, (0, 90, 255))
                screen.blit(reason, (150, 190))    
            elif lose == True:
                game_over()
                reason = font.render('You are loser. Your score: {}'.format(score_lose), True, (0, 90, 255))
                screen.blit(reason, (150, 190))
            
            pygame.display.flip()
        
        client.connection.close()

    client.check_server()
    print(client.obtain_token('room-1'))
    event_client.start()
    game_start()

def ai():
    IP = '34.254.177.17'
    PORT = 5672
    VIRTUAL_HOST = 'dar-tanks'
    USERNAME = 'dar-tanks'
    PASSWORD = '5orPLExUYnyVYZg48caMpX'
    pygame.init()
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
    class TankRpcClient:
        def __init__(self):
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host = IP,
                    port = PORT,
                    virtual_host = VIRTUAL_HOST,
                    credentials = pika.PlainCredentials(
                        username = USERNAME,
                        password = PASSWORD
                    )
                )
            )
            self.channel = self.connection.channel()
            queue = self.channel.queue_declare(queue='',
                                            auto_delete=True,
                                            exclusive= True)
            self.callback_queue = queue.method.queue
            self.channel.queue_bind(
                exchange = 'X:routing.topic',
                queue = self.callback_queue
            )

            self.channel.basic_consume(
                queue = self.callback_queue,
                on_message_callback=self.on_response,
                auto_ack = True
            )
            self.token = None
            self.tank_id = None
            self.room_id = None

        def on_response(self, ch, method, props, body):#Принимает запрос
            if self.corr_id == props.correlation_id:
                self.response = json.loads(body)

        def call(self, key, message):
            self.response = None
            self.corr_id = str(uuid.uuid4())
            self.channel.basic_publish(
                exchange = 'X:routing.topic',
                routing_key = key,
                properties=pika.BasicProperties(
                    reply_to =self.callback_queue,
                    correlation_id = self.corr_id
                ),
                body = json.dumps(message)
            )
            while self.response is None:
                self.connection.process_data_events()

        def check_server(self): #Healthcheck
            self.call('tank.request.healthcheck','')
            return self.response['status'] == '200'

        def obtain_token(self, room_id): #Register
            message = {
                'roomId':room_id
            }
            self.call('tank.request.register', message)
            if 'token' in self.response:
                self.token = self.response['token']
                self.tank_id = self.response['tankId']
                self.room_id = self.response['roomId']
                return True
            return False

        def turn_tank(self, token, direction):
            message = {
                'token': token,
                'direction': direction
            }
            self.call('tank.request.turn', message)

        def fire_bullet(self, token):
            message = {
                'token': token
            }
            self.call('tank.request.fire', message)


    class TankConsumerClient(Thread):
        def __init__(self, roomId):
            super().__init__()
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host = IP,
                    port = PORT,
                    virtual_host = VIRTUAL_HOST,
                    credentials = pika.PlainCredentials(
                        username = USERNAME,
                        password = PASSWORD
                    )
                )
            )
            self.channel = self.connection.channel()
            queue = self.channel.queue_declare(queue='',
                                            auto_delete=True,
                                            exclusive= True
                                            )
            event_listener = queue.method.queue
            self.channel.queue_bind(exchange='X:routing.topic',
                                    queue=event_listener,
                                    routing_key='event.state.'+roomId
                                    )
            self.channel.basic_consume(
                queue=event_listener,
                on_message_callback=self.on_response,
                auto_ack=True
            )
            self.response = None

        def on_response(self, ch, method, props, body):
            self.response = json.loads(body)
            print(self.response)

        def run(self):
            self.channel.start_consuming()

    client = TankRpcClient()
    event_client = TankConsumerClient('room-1')
    event_client.daemon = True

    UP = 'UP'
    DOWN = 'DOWN'
    LEFT = 'LEFT'
    RIGHT = 'RIGHT'

    def draw_tank(id, x, y, width, height, direction, health, score, img):
        if direction == RIGHT:
            right = pygame.transform.rotate(img, 90)
            screen.blit(right, (x, y))
        if direction == LEFT:
            left = pygame.transform.rotate(img, 270)
            screen.blit(left, (x, y))
        if direction == UP:
            up = pygame.transform.rotate(img, 180)
            screen.blit(up, (x, y))
        if direction == DOWN:
            down = pygame.transform.rotate(img, 0)
            screen.blit(down, (x, y))

    def draw_bullets(owner, x, y, width, height, direction, fire):
        if direction == RIGHT:
            right = pygame.transform.rotate(fire, 270)
            screen.blit(right, (x, y))
        if direction == LEFT:
            left = pygame.transform.rotate(fire, 90)
            screen.blit(left, (x, y))
        if direction == UP:
            up = pygame.transform.rotate(fire, 0)
            screen.blit(up, (x, y))
        if direction == DOWN:
            down = pygame.transform.rotate(fire, 180)
            screen.blit(down, (x, y))

    def information_panel(remaining_time):
        surface = pygame.Surface((200, 600))
        surface.fill((0, 51, 0))
        first_line = font.render('ID     | Health | Score ', True, (255, 255, 255))
        text = font.render('Remaining Time: {}'.format(remaining_time), True, (255, 255, 255))
        screen.blit(surface, (width-180, 0))
        screen.blit(text, (width-180, 0))
        screen.blit(first_line, (width-180, 30))

    def game_over():
        screen.fill((128, 128, 128))
        text = font.render('If you want to replay press R', True, (0, 90, 255))
        over = font.render('GAME  OVER!', True, (0, 90, 255))
        screen.blit(over, (150,150))
        screen.blit(text, (150, 170))
        pygame.mixer.music.pause()
        pygame.mixer.Sound.play(end)

    def game_start():
        mainloop = True
        win = False
        kick = False
        lose = False
        client.turn_tank(client.token, UP)
        while mainloop:
            screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    mainloop = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        mainloop = False
                    elif event.key == pygame.K_r:
                        menu.mainloop(screen)
                    
            try:
                remaining_time = event_client.response["remainingTime"]
            except:
                pass
            bullets = event_client.response['gameField']['bullets']
            tanks = event_client.response['gameField']['tanks']
            hits = event_client.response['hits']
            winners = event_client.response['winners']
            losers = event_client.response['losers']
            kicked = event_client.response['kicked']

            img1 = pygame.image.load("tank1m.png")
            img2 = pygame.image.load("tank2m.png")
            fire1 = pygame.image.load("fire1.png")
            fire2 = pygame.image.load("fire2.png")

            tankx = 0
            tanky = 0
            tankw = 0
            tankh = 0
            tankd = ''
            enemyx = 0
            enemyy = 0
            enemyw = 0
            enemyh = 0
            enemyd = ''
            bulletx = 0
            bullety = 0
            bulletw = 0
            bulleth = 0
            bulletd = ''
            ebulletx = 0
            ebullety = 0
            ebulletw = 0
            ebulleth = 0
            ebulletd = ''
            
            for tank in tanks:
                if tank['id'] == client.tank_id:
                    tankx = tank['x']
                    tanky = tank['y']
                    tankw = tank['width']
                    tankh = tank['height']
                    tankd = tank['direction']
                    draw_tank(tank['id'], tankx, tanky, tankw, tankh, tankd, tank['health'], tank['score'], img1)
                else:
                    enemyx = tank['x']
                    enemyy = tank['y']
                    enemyw = tank['width']
                    enemyh = tank['height']
                    enemyd = tank['direction']
                    draw_tank(tank['id'], enemyx, enemyy, enemyw, enemyh, enemyd, tank['health'], tank['score'], img2)    

            for bullet in bullets:
                if bullet['owner'] == client.tank_id:
                    bulletx = bullet['x']
                    bullety = bullet['y']
                    bulletw = bullet['width']
                    bulleth = bullet['height']
                    bulletd = bullet['direction']
                    draw_bullets(bullet['owner'], bulletx, bullety, bulletw, bulleth, bulletd, fire1)
                else:
                    ebulletx = bullet['x']
                    ebullety = bullet['y']
                    ebulletw = bullet['width']
                    ebulleth = bullet['height']
                    ebulletd = bullet['direction']
                    draw_bullets(bullet['owner'], ebulletx, ebullety, ebulletw, ebulleth, ebulletd, fire2)     
            
            #если стреляют с правой или с левой стороны
            if (0 <= ebulletx + ebulletw <= tankx or tankx <= ebulletx + ebulletw <= 800) and tanky <= ebullety <= tanky + tankh:
                client.turn_tank(client.token, UP)
            elif (0 <= ebullety + ebulleth <= tanky or tanky <= ebullety + ebulleth <= 600) and tankx <= ebulletx <= tankx + tankw:
                client.turn_tank(client.token, RIGHT)
            #если другие танки находятся справа или слева - стрелять в них
            if 35 < enemyx - tankx <= 100 and enemyy <= tanky + tankh//2 <= enemyy + enemyh:
                client.turn_tank(client.token, RIGHT)
                client.fire_bullet(client.token)
            elif 35 < tankx - enemyx <= 100 and enemyy <= tanky + tankh//2 <= enemyy + enemyh:
                client.turn_tank(client.token, LEFT)
                client.fire_bullet(client.token)
            #если другой танк сверху или снизу
            if 35 < enemyy - tanky <= 100 and enemyx <= tankx + tankw//2 <= enemyx + enemyw:
                client.turn_tank(client.token, DOWN)
                client.fire_bullet(client.token)
            elif 35 < tanky - enemyy <= 100 and enemyx <= tankx + tankw//2 <= enemyx + enemyw:
                client.turn_tank(client.token, UP)
                client.fire_bullet(client.token)    
            
            try:
                information_panel(remaining_time)
            except:
                pass
                
            j = 50
            t = {}
            for tank in tanks:      
                t[tank['id']] = [tank['health'],tank['score']]
            t_sorted = {a: b for a, b in sorted(t.items(), key=lambda item: item[1][1], reverse = True)}
            for i,s in t_sorted.items():
                lines = font.render('{}   | {} | {}'.format(i, s[0], s[1]), True, (255, 255, 255))
                screen.blit(lines, (width-180, j))
                j += 20

            if kicked:
                for e in kicked:
                    if client.tank_id == e['tankId']:
                        kick = True
                    
            elif losers:
                for e in losers:
                    if client.tank_id == e['tankId']:
                        lose = True

            elif winners:
                for e in winners:
                    if client.tank_id == e['tankId']:
                        win = True    
                        
            if kick == True:
                game_over()
                reason = font.render('You are kicked', True, (0, 90, 255))
                screen.blit(reason, (150, 190))
            if win == True:
                game_over()
                reason = font.render('You are winner', True, (0, 90, 255))
                screen.blit(reason, (150, 190))    
            if lose == True:
                game_over()
                reason = font.render('You are loser', True, (0, 90, 255))
                screen.blit(reason, (150, 190))
            
            pygame.display.flip()
        
        client.connection.close()

    client.check_server()
    print(client.obtain_token('room-1'))
    event_client.start()
    game_start()

menu = pygame_menu.Menu(300, 400, 'Welcome',
                       theme=pygame_menu.themes.THEME_BLUE)

menu.add_button('Single Player mode', single_player)
menu.add_button('Multiplayer mode', multiplayer_mode)
menu.add_button('Multiplayer AI mode', ai)
menu.add_button('Quit', pygame_menu.events.EXIT)

menu.mainloop(screen)