import os
import pygame
from random import choice
import neat

pygame.init()

#CONSTANTS
WIDTH, HEIGHT = 400, 600  #Screen height and width
WIN = pygame.display.set_mode((WIDTH, HEIGHT))  #Pygame surface object
P_HEIGHT = 24  #Player height DO NOT CHANGE
P_WIDTH = 34  #Player width DO NOT CHANGE
VELOCITY = 7  #Initial downwards velocity 7 works
FPS = 60  #FPS duh
BG = pygame.image.load("bg.png").convert_alpha()  #Background image
PIPE_TOP = pygame.image.load("pipe2.png").convert_alpha()  #Top pipe
PIPE_BOTTOM = pygame.image.load("pipe1.png").convert_alpha()  #Bottom pipe
PIPE_IMG_HEIGHT = 379
BIRD_SIZE = (P_WIDTH, P_HEIGHT)  #DO NOT CHANGE
BIRD_IMG = pygame.image.load("birb.png").convert_alpha()  #Player image
JUMP_HEIGHT = 8  #Jump height Feel free to experiment though 8 works pretty well
GRAV = 0.8  #Gravity value Feel free to experiment though 0.8 works pretty well
BLOCK_WIDTH = 52  #52
BLOCK_GAP = 150  #150
BLOCK_VEL = 4  #4
my_font = pygame.font.SysFont('Consolas', 20)  #Set font and font size here
RUN = True  #True
GEN = 0  #0


class obstacles:
    """
        #Class for bottom and top pipe
        height1 and rect1 correspond to height and hitbox of top pipe
        height2 and rect2 correspond to height and hitbox of bottom pipe
        
    """

    def __init__(self, width, gap, velocity):
        self.x = WIDTH + width - 20
        self.width = width
        self.velocity = velocity
        self.height1 = choice([80, 120, 160, 200, 240, 280, 320])
        self.height2 = (HEIGHT - gap) - self.height1
        self.rect1 = pygame.Rect(self.x, 0, self.width, self.height1)
        self.rect2 = pygame.Rect(self.x, HEIGHT - self.height2, self.width,
                                 self.height2)

    def move(self):
        self.rect1.x -= self.velocity
        self.rect2.x -= self.velocity

    def draw(self):
        #pygame.draw.rect(WIN, (0, 0, 0), self.rect1)  #To view hitbox of top pipe
        #pygame.draw.rect(WIN, (0, 0, 0), self.rect2)   #To view hitbox of bottom pipe
        WIN.blit(PIPE_TOP, (self.rect1.x, self.rect1.height - PIPE_IMG_HEIGHT))
        WIN.blit(PIPE_BOTTOM, (self.rect2.x, self.rect2.y))


class player:
    """
    #Birdy class
    
    """
    highscore = 0

    def __init__(self, x, y):
        self.jumpcount = JUMP_HEIGHT
        self.isjump = False
        self.velocity = VELOCITY
        self.neg = 1
        self.rect = pygame.Rect(x, y, P_WIDTH, P_HEIGHT)
        self.score = 0
        self.score_updated = False
        self.run = True

    def draw(self):
        #pygame.draw.rect(WIN, (255, 0, 0), self.rect, 1)
        WIN.blit(BIRD_IMG,
                 (self.rect.x, self.rect.y))  #Draw the birdy on screen

    def grav(self):
        self.rect.y += self.velocity  #Move bird down
        self.velocity += GRAV  #Accelerate bird


#All draw function calls
def draw_window(birds, block, GEN):
    WIN.blit(BG, (0, 0))

    for bird in birds:
        bird.draw()
    block.draw()
    text1 = my_font.render("Generation: " + str(GEN), True, (0, 0, 0))
    text3 = my_font.render("Alive birds: " + str(len(birds)), True, (0, 0, 0))
    text4 = my_font.render("Highscore: " + str(player.highscore), True,
                           (0, 0, 0))

    if len(birds) != 0:
        text2 = my_font.render("Score: " + str(birds[0].score), True,
                               (0, 0, 0))
        WIN.blit(text2, dest=(WIDTH - 200, 30))
    WIN.blit(text1, dest=(20, 30))
    WIN.blit(text3, dest=(WIDTH - 200, 70))
    WIN.blit(text4, dest=(WIDTH - 200, 90))

    pygame.display.update()


#Jumping function
def jump_handler(bird):
    if bird.isjump:
        bird.velocity = -10
    else:
        bird.velocity = VELOCITY


#Function that handles collisions and out of bounds. Mess with this to enable noclip :) P.S.: THE SCORING FUNCTION IS IN HERE TOO
def fail_handler(birds, ge, nets, block):
    global RUN
    if block.rect1.x < -block.width:  #If block goes out of screen
        block.__init__(BLOCK_WIDTH, BLOCK_GAP, BLOCK_VEL)
        for bird in birds:
            bird.score_updated = False
        #If score is more than 200
        if birds[0].score > 500:
            RUN = False

    if len(birds) != 0:
        for x, bird in enumerate(birds):
            #If collide with blocks
            if pygame.Rect.colliderect(bird.rect,
                                       block.rect1) or pygame.Rect.colliderect(
                                           bird.rect, block.rect2):
                ge[x].fitness -= 2
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        for x, bird in enumerate(birds):
            #If gone through block
            if bird.rect.x > block.rect1.x + block.width and (
                    not bird.score_updated):
                for g in ge:
                    g.fitness += 3
                bird.score += 1
                bird.score_updated = True
                player.highscore = max(player.highscore, bird.score)

        for x, bird in enumerate(birds):
            #If bird touches the top
            if bird.rect.y < 0:
                bird.rect.y = 0
                ge[x].fitness -= 0.5
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)
            #If bird falls down
            if bird.rect.y > HEIGHT:
                ge[x].fitness -= 20
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)
    else:
        RUN = False


def main(genomes, config):
    global RUN
    global GEN
    GEN += 1
    RUN = True
    #Neural net variables
    nets = []
    ge = []
    birds = []
    block = obstacles(BLOCK_WIDTH, BLOCK_GAP, BLOCK_VEL)

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(player(100, 200))
        g.fitness = 0
        ge.append(g)
    clock = pygame.time.Clock()

    while (RUN):
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUN = False
                pygame.quit()

        fail_handler(birds, ge, nets, block)

        for x, bird in enumerate(birds):
            output = nets[x].activate(
                (bird.rect.y, abs(bird.rect.y - block.height1),
                 abs(bird.rect.y - (HEIGHT - block.height2))))
            bird.grav()

            if (output[0] > 0.5):
                bird.isjump = True
                jump_handler(bird)
            ge[x].fitness += 0.01

        block.move()
        draw_window(birds, block, GEN)
        for bird in birds:
            bird.isjump = False

    print("\n")


def Run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    winner = p.run(main)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    Run(config_path)
