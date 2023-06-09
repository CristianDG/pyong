import sys
import os
import random
import math
from dataclasses import dataclass
from enum import Enum, auto
from time import sleep
from ctypes import byref, c_uint8, c_int, c_uint32, CFUNCTYPE, c_float, c_long, pointer
from sdl2 import *
from sdl2.sdlttf import *

WINDOW_WIDTH, WINDOW_HEIGHT  = 1280, 720

FRAMERATE = 75

PADDLE_WIDTH  = 25
BALL_WIDTH = 25
BALL_VEL = 1000
PADDLE_HEIGHT = 200

PADDLE_VEL = 200

UPPER_BORDER_Y = 150
UPPER_BORDER = [[0,UPPER_BORDER_Y],[WINDOW_WIDTH,UPPER_BORDER_Y]]

LOWER_BORDER_Y = WINDOW_HEIGHT
LOWER_BORDER = [[0,LOWER_BORDER_Y],[WINDOW_WIDTH, LOWER_BORDER_Y]]

LEFT_BORDER  = [[0,0],[0,WINDOW_HEIGHT]]
RIGHT_BORDER = [[WINDOW_WIDTH,0],[WINDOW_WIDTH,WINDOW_HEIGHT]]

p1_paddle  = None
p2_paddle  = None
ball       = None
game_state = None

font = None

def initialize_p2_paddle_pos():
    global p2_paddle
    p2_paddle['rect']['x'] = WINDOW_WIDTH - 50 - PADDLE_WIDTH
    p2_paddle['rect']['y'] = (WINDOW_HEIGHT + UPPER_BORDER_Y - PADDLE_HEIGHT)//2

def initialize_p1_paddle_pos():
    global p1_paddle
    p1_paddle['rect']['x'] = 50
    p1_paddle['rect']['y'] = (WINDOW_HEIGHT + UPPER_BORDER_Y - PADDLE_HEIGHT)//2

class GameEventType(Enum):
    P1_UP     = auto()
    P1_DOWN   = auto()
    P2_UP     = auto()
    P2_DOWN   = auto()
    P1_SCORED = auto()
    P2_SCORED = auto()
    START     = auto()
    RESTART   = auto()
    PAUSE     = auto()
    UNPAUSE   = auto()

def initialize_ball_pos_and_vel():
    global ball

    ball['rect']['x'] = (WINDOW_WIDTH - ball['rect']['w'])//2
    ball['rect']['y'] = (WINDOW_HEIGHT + UPPER_BORDER_Y - ball['rect']['h'])//2
    ball['physics']['vel'] = BALL_VEL * 0.5

def initialize():

    base_rect = {
        'x': 0,
        'y': 0,
        'w': 0,
        'h': 0,
    }

    base_physics = {
        'vel': 0,
        'dir': [0,0]
    }


    def initialize_game_state():
        global game_state
        game_state = { 'paused': False, 'started': False, 'p1_score': 0, 'p2_score': 0 }
    initialize_game_state()

    def initialize_p1_paddle():
        global p1_paddle

        p1_paddle = { 'rect': base_rect.copy(), 'physics': base_physics.copy() }
        p1_paddle['rect']['h'] = PADDLE_HEIGHT
        p1_paddle['rect']['w'] = PADDLE_WIDTH
        initialize_p1_paddle_pos()
    initialize_p1_paddle()

    def initialize_p2_paddle():
        global p2_paddle

        p2_paddle = { 'rect': base_rect.copy(), 'physics': base_physics.copy() }
        p2_paddle['rect']['h'] = PADDLE_HEIGHT
        p2_paddle['rect']['w'] = PADDLE_WIDTH
        initialize_p2_paddle_pos()
    initialize_p2_paddle()

    def initialize_ball():
        global ball

        ball = { 'rect': base_rect.copy(), 'physics': base_physics.copy() }
        ball['rect']['h'] = BALL_WIDTH
        ball['rect']['w'] = BALL_WIDTH
        initialize_ball_pos_and_vel()

    initialize_ball()


def render(renderer, window):
    p1_rect   = SDL_FRect(**p1_paddle['rect'])
    p2_rect   = SDL_FRect(**p2_paddle['rect'])
    ball_rect = SDL_FRect(**ball['rect'])
    upper_border_rect = SDL_FRect(0, UPPER_BORDER_Y - 2, WINDOW_WIDTH, 1)

    window_rect = SDL_FRect(w=WINDOW_WIDTH, h=WINDOW_HEIGHT)

    SDL_SetRenderDrawColor(renderer,0,0,0, 255)
    SDL_RenderFillRectF(renderer, window_rect)

    SDL_SetRenderDrawColor(renderer,255,255,255, 255)
    SDL_RenderFillRectF(renderer, p1_rect)
    SDL_RenderFillRectF(renderer, p2_rect)
    SDL_RenderFillRectF(renderer, ball_rect)
    SDL_RenderFillRectF(renderer, upper_border_rect)

    # TODO

    p1_score_color = SDL_Color(255,255,255, 255)
    p1_score_surface = TTF_RenderUTF8_Solid(font, str.encode(str(game_state['p1_score'])), p1_score_color)
    p1_score_texture = SDL_CreateTextureFromSurface(renderer, p1_score_surface)
    p1_score_rect = SDL_Rect(50,50,p1_score_surface.contents.w, p1_score_surface.contents.h)
    SDL_RenderCopy(renderer, p1_score_texture, None, p1_score_rect)
    SDL_FreeSurface(p1_score_surface)

    p2_score_color = SDL_Color(255,255,255, 255)
    p2_score_surface = TTF_RenderUTF8_Solid(font, str.encode(str(game_state['p2_score'])), p2_score_color)
    p2_score_texture = SDL_CreateTextureFromSurface(renderer, p2_score_surface)
    p2_score_rect = SDL_Rect(WINDOW_WIDTH - p2_score_surface.contents.w - 50, 50,p2_score_surface.contents.w, p2_score_surface.contents.h)
    SDL_RenderCopy(renderer, p2_score_texture, None, p2_score_rect)
    SDL_FreeSurface(p2_score_surface)

    SDL_RenderPresent(renderer)


def clamp(val):
    def inner( min_val = val, max_val = val):
        if val < min_val:
            return min_val
        elif val > max_val:
            return max_val
        else:
            return val
    return inner

def center(rect):
    return {
        'x': rect['x'] + (rect['w'] / 2),
        'y': rect['y'] + (rect['h'] / 2)
    }


def handle_event(event: GameEventType):
    if not game_state['paused']:
        #TODO: mudar o lugar para não usar dt nessa função

        dt = 1/FRAMERATE
        if event == GameEventType.P1_UP:
            p1_paddle['rect']['y'] = clamp(p1_paddle['rect']['y'] - PADDLE_VEL * dt)(min_val=UPPER_BORDER[0][1])
        elif event == GameEventType.P1_DOWN:
            p1_paddle['rect']['y'] = clamp(p1_paddle['rect']['y'] + PADDLE_VEL * dt)(max_val=LOWER_BORDER[0][1] - p1_paddle['rect']['h'])
        elif event == GameEventType.P2_UP:
            p2_paddle['rect']['y'] = clamp(p2_paddle['rect']['y'] - PADDLE_VEL * dt)(min_val=UPPER_BORDER[0][1])
        elif event == GameEventType.P2_DOWN:
            p2_paddle['rect']['y'] = clamp(p2_paddle['rect']['y'] + PADDLE_VEL * dt)(max_val=LOWER_BORDER[0][1] - p2_paddle['rect']['h'])

    if event == GameEventType.RESTART:
        initialize()


    if event == GameEventType.START and not game_state['started']:
        game_state['started']  = True
        game_state['paused']   = False
        ball['physics']['dir'] = [random.choice([-1,1]) * 1,0] # Randomizar mais

    if event == GameEventType.P1_SCORED:
        game_state['p1_score'] += 1
        ball['physics']['dir'] = [1, 0]
        initialize_ball_pos_and_vel()
        initialize_p1_paddle_pos()
        initialize_p2_paddle_pos()
        handle_event(GameEventType.PAUSE)

    if event == GameEventType.P2_SCORED:
        game_state['p2_score'] += 1
        ball['physics']['dir'] = [-1, 0]
        initialize_ball_pos_and_vel()
        initialize_p1_paddle_pos()
        initialize_p2_paddle_pos()
        handle_event(GameEventType.PAUSE)

    if event == GameEventType.PAUSE:
        game_state['paused'] = True

    if event == GameEventType.UNPAUSE:
        game_state['paused'] = False





def update(dt = 1/FRAMERATE):

    # physics update
    if game_state['paused']:
        return


    if check_border_collision(UPPER_BORDER, ball) \
    or check_border_collision(LOWER_BORDER, ball):
        ball['physics']['dir'][1] *= -1

    ball['rect']['x'] += ball['physics']['vel'] * ball['physics']['dir'][0] * dt
    ball['rect']['y'] += ball['physics']['vel'] * ball['physics']['dir'][1] * dt


    if check_border_collision(LEFT_BORDER, ball):
        handle_event(GameEventType.P2_SCORED)

    if check_border_collision(RIGHT_BORDER, ball):
        handle_event(GameEventType.P1_SCORED)


    if check_paddle_collision(p1_paddle, ball) or check_paddle_collision(p2_paddle, ball):
        is_p1 = ball['rect']['x'] < WINDOW_WIDTH / 2

        paddle, coeff = (p1_paddle, 1) if is_p1 else (p2_paddle, -1)


        paddle_center = center(paddle['rect'])
        ball_center   = center(ball['rect'])


        dir_x, dir_y = abs(paddle_center['x'] - ball_center['x']) * coeff, ball_center['y'] - paddle_center['y']

        if abs(dir_y) < 5: dir_y = 0

        magnitude = math.sqrt(dir_x**2 + dir_y**2)

        ball['physics']['vel'] = clamp(abs(dir_y / magnitude))(min_val=0.5, max_val=1) * BALL_VEL
        ball['physics']['dir'] = [dir_x / magnitude, dir_y / magnitude]

def check_paddle_collision(paddle, ball):
    paddle_rect = SDL_FRect(**paddle['rect'])
    ball_rect   = SDL_FRect(**ball['rect'])

    return SDL_HasIntersectionF(paddle_rect, ball_rect) == SDL_TRUE

def check_border_collision(border, ball):
    ball_rect = SDL_FRect(**ball['rect'])

    return SDL_IntersectFRectAndLine(ball_rect,
                                     c_float(border[0][0]), c_float(border[0][1]),
                                     c_float(border[1][0]), c_float(border[1][1])) == SDL_TRUE


def main():
    global font

    SDL_Init(SDL_INIT_VIDEO)
    TTF_Init()
    window = SDL_CreateWindow(b"Pong",
                              SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                              WINDOW_WIDTH, WINDOW_HEIGHT, SDL_WINDOW_SHOWN)

    # SDL_SetHint(SDL_HINT_RENDER_SCALE_QUALITY, b"2");
    renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_SOFTWARE)
    SDL_SetRenderDrawBlendMode(renderer, SDL_BLENDMODE_NONE)


    font = TTF_OpenFont(str.encode(os.path.join(os.path.dirname(__file__), 'assets', 'font.ttf')), 100)

    initialize()

    running = True
    event = SDL_Event()
    while running:

        keystate = SDL_GetKeyboardState(None)

        while SDL_PollEvent(event) != 0:
            if event.type == SDL_QUIT:
                running = False
                break
            elif keystate[SDL_SCANCODE_SPACE]:
                handle_event(GameEventType.START)
            elif keystate[SDL_SCANCODE_APOSTROPHE]:
                handle_event(GameEventType.STOP)
            elif keystate[SDL_SCANCODE_R]:
                handle_event(GameEventType.RESTART)
            elif keystate[SDL_SCANCODE_P]:
                handle_event(GameEventType.PAUSE)
            elif keystate[SDL_SCANCODE_U]:
                handle_event(GameEventType.UNPAUSE)

        keystate = SDL_GetKeyboardState(None)
        if keystate[SDL_SCANCODE_Q]:
            running = False
            break
        if keystate[SDL_SCANCODE_W]:
            handle_event(GameEventType.P1_UP)
        elif keystate[SDL_SCANCODE_S]:
            handle_event(GameEventType.P1_DOWN)
        if keystate[SDL_SCANCODE_UP]:
            handle_event(GameEventType.P2_UP)
        elif keystate[SDL_SCANCODE_DOWN]:
            handle_event(GameEventType.P2_DOWN)

        update()


        # TODO

        render(renderer,window)
        sleep(1/FRAMERATE)

    SDL_DestroyWindow(window)
    TTF_Quit()
    SDL_Quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
