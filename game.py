import os
import pygame
from random import choice
import neat

pygame.init()

#CONSTANTS
WIDTH, HEIGHT = 400, 600  #Screen height and width
PIPE_IMG_HEIGHT = 379
P_HEIGHT = 24  #Player height DO NOT CHANGE
P_WIDTH = 34  #Player width DO NOT CHANGE
BIRD_SIZE = (P_WIDTH, P_HEIGHT)  #DO NOT CHANGE
BLOCK_WIDTH = 52  #Pipe width (52)
BLOCK_GAP = 150  #Pipe height (150)

WIN = pygame.display.set_mode((WIDTH, HEIGHT))  #Pygame surface object
my_font = pygame.font.SysFont('Consolas', 20)  #Set font and font size here

BG = pygame.image.load("bg.png").convert_alpha()  #Background image
PIPE_TOP = pygame.image.load("pipe2.png").convert_alpha()  #Top pipe
PIPE_BOTTOM = pygame.image.load("pipe1.png").convert_alpha()  #Bottom pipe
BIRD_IMG = pygame.image.load("birb.png").convert_alpha()  #Bird image

VELOCITY = 7  #Initial downwards velocity (7)
JUMP_HEIGHT = 8  #Jump height Feel free to experiment though (8)
BLOCK_VEL = 4  # Horizontal velocity of block (4)
GRAV = 0.8  #Gravity value Feel free to experiment though (0.8)

FPS = 65  #FPS duh
RUN = True  #True
GEN = 0  #0


class obstacles:
    """
        #Class for bottom and top pipe
        height1 and rect1 correspond to height and hitbox of top pipe
        height2 and rect2 correspond to height and hitbox of bottom pipe
        
    """

    def __init__(self, width, gap, velocity):
        self.x = WIDTH + width - 20  #To start the pipe outside the screen (+20 so its a little inside)
        self.width = width
        self.velocity = velocity
        self.height1 = choice([80, 120, 160, 200, 240, 280,
                               320])  #Predefined heights of top pipe
        self.height2 = (HEIGHT -
                        gap) - self.height1  #Predefined height of bottom pipe
        self.rect1 = pygame.Rect(self.x, 0, self.width, self.height1)
        self.rect2 = pygame.Rect(self.x, HEIGHT - self.height2, self.width,
                                 self.height2)

    def move(self):
        ''' Moves the pipes'''
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
        self.velocity = VELOCITY
        self.rect = pygame.Rect(x, y, P_WIDTH, P_HEIGHT)
        self.score = 0
        self.score_updated = False

    def draw(self):
        '''Moves the birds'''
        #pygame.draw.rect(WIN, (255, 0, 0), self.rect, 1)
        WIN.blit(BIRD_IMG,
                 (self.rect.x, self.rect.y))  #Draw the birdy on screen

    def grav(self):
        self.rect.y += self.velocity  #Move bird down
        self.velocity += GRAV  #Accelerate bird


#All draw function calls
def draw_window(birds, block, GEN):
    WIN.blit(BG, (0, 0))  #Draws background

    #Draws all birds in generation
    for bird in birds:
        bird.draw()

    block.draw()  #Draws pipes
    text1 = my_font.render("Generation: " + str(GEN), True,
                           (0, 0, 0))  #Prints generation on screen
    text3 = my_font.render("Alive birds: " + str(len(birds)), True,
                           (0, 0, 0))  #Prints alive birds on screen
    text4 = my_font.render("Highscore: " + str(player.highscore), True,
                           (0, 0, 0))  #Prints highscore on screen

    if len(birds) != 0:  #If generation still has birds
        text2 = my_font.render("Score: " + str(birds[0].score), True,
                               (0, 0, 0))
        WIN.blit(text2, dest=(WIDTH - 200, 30))

    WIN.blit(text1, dest=(20, 30))
    WIN.blit(text3, dest=(WIDTH - 200, 70))
    WIN.blit(text4, dest=(WIDTH - 200, 90))

    pygame.display.update()


#Jumping function
def jump_handler(bird):
    bird.velocity = -10


def fail_handler(birds, ge, nets, block):
    """
    Function that handles collisions and out of bounds. Mess with this to enable noclip :) P.S.: THE SCORING FUNCTION IS IN HERE TOO

    """
    global RUN
    global FPS

    if block.rect1.x < -block.width:  #If block goes out of screen
        block.__init__(BLOCK_WIDTH, BLOCK_GAP, BLOCK_VEL)
        for bird in birds:
            bird.score_updated = False
        if birds[0].score > 20:  #To quit the game if any bird reaches certain score
            FPS = 200

    if len(birds) != 0:
        for x, bird in enumerate(birds):
            #If collide with pipes
            if pygame.Rect.colliderect(bird.rect,
                                       block.rect1) or pygame.Rect.colliderect(
                                           bird.rect, block.rect2):
                ge[x].fitness -= 2
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        for x, bird in enumerate(birds):
            #If gone past a pipe
            if bird.rect.x > block.rect1.x + block.width and (
                    not bird.score_updated):
                for g in ge:
                    g.fitness += 5
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
                ge[x].fitness -= 3
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)
    else:
        RUN = False


def main(genomes, config):
    global RUN
    global GEN

    GEN += 1  #Increment generation count
    RUN = True

    #Neural net variables
    nets = []
    ge = []
    birds = []
    block = obstacles(BLOCK_WIDTH, BLOCK_GAP, BLOCK_VEL)

    #Create generations of nerual net variables
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(player(100, 200))
        g.fitness = 0
        ge.append(g)
    clock = pygame.time.Clock()

    while (RUN):
        clock.tick(FPS)  #Set the game speed

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUN = False
                pygame.quit()

        fail_handler(birds, ge, nets, block)

        for x, bird in enumerate(birds):
            output = nets[x].activate(
                (bird.rect.y, (bird.rect.y - block.height1),
                 (bird.rect.y - (HEIGHT - block.height2)
                  )))  #Calculate output (probability of jump)

            bird.grav()

            if (
                    output[0] > 0.5
            ):  #If probability if jumo is greater than certain value then jump all birds
                jump_handler(bird)
            ge[x].fitness += 0.01

        block.move()  #Move pipes
        draw_window(birds, block, GEN)  #Draw everything


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
