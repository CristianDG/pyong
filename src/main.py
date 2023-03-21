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
PADDLE_HEIGHT = 200

PADDLE_VEL = 200


p1_paddle  = None
p2_paddle  = None
ball       = None
game_state = None

font = None

class GameEventType(Enum):
    P1_UP     = auto()
    P1_DOWN   = auto()
    P2_UP     = auto()
    P2_DOWN   = auto()
    P1_SCORED = auto()
    P2_SCORED = auto()
    START     = auto()
    RESTART   = auto()
    STOP      = auto()



def initialize():

    base_rect = {
        'x': 0,
        'y': 0,
        'w': 0,
        'h': 0,
    }

    base_physics = {
        'acc': 0,
        'res': 0,
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
        p1_paddle['rect']['x'] = 50
        p1_paddle['rect']['y'] = (WINDOW_HEIGHT // 2) - (PADDLE_HEIGHT//2)
        p1_paddle['rect']['h'] = PADDLE_HEIGHT
        p1_paddle['rect']['w'] = PADDLE_WIDTH
        p1_paddle['physics']['res'] = 1
    initialize_p1_paddle()

    def initialize_p2_paddle():
        global p2_paddle

        p2_paddle = { 'rect': base_rect.copy(), 'physics': base_physics.copy() }
        p2_paddle['rect']['x'] = WINDOW_WIDTH - 50 - PADDLE_WIDTH
        p2_paddle['rect']['y'] = (WINDOW_HEIGHT // 2) - (PADDLE_HEIGHT//2)
        p2_paddle['rect']['h'] = PADDLE_HEIGHT
        p2_paddle['rect']['w'] = PADDLE_WIDTH
        p2_paddle['physics']['res'] = 1
    initialize_p2_paddle()

    def initialize_ball():
        global ball

        ball = { 'rect': base_rect.copy(), 'physics': base_physics.copy() }
        ball['rect']['h'] = BALL_WIDTH
        ball['rect']['w'] = BALL_WIDTH
        ball['rect']['x'] = (WINDOW_WIDTH // 2) - (ball['rect']['w']//2)
        ball['rect']['y'] = (WINDOW_HEIGHT // 2) - (ball['rect']['h']//2)
    initialize_ball()


def render(renderer, window):
    p1_rect   = SDL_FRect(**p1_paddle['rect'])
    p2_rect   = SDL_FRect(**p2_paddle['rect'])
    ball_rect = SDL_FRect(**ball['rect'])

    window_rect = SDL_FRect(w=WINDOW_WIDTH, h=WINDOW_HEIGHT)

    SDL_SetRenderDrawColor(renderer,0,0,0, 255)
    SDL_RenderFillRectF(renderer, window_rect)

    SDL_SetRenderDrawColor(renderer,255,255,255, 255)
    SDL_RenderFillRectF(renderer, p1_rect)
    SDL_RenderFillRectF(renderer, p2_rect)
    SDL_RenderFillRectF(renderer, ball_rect)

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


def handle_event(event: GameEventType, dt = 1/FRAMERATE):
    if event == GameEventType.P1_UP:
        p1_paddle['rect']['y'] = clamp(p1_paddle['rect']['y'] - PADDLE_VEL * dt)(min_val=0)
    elif event == GameEventType.P1_DOWN:
        p1_paddle['rect']['y'] = clamp(p1_paddle['rect']['y'] + PADDLE_VEL * dt)(max_val=WINDOW_HEIGHT - PADDLE_HEIGHT)
    elif event == GameEventType.P2_UP:
        p2_paddle['rect']['y'] = clamp(p2_paddle['rect']['y'] - PADDLE_VEL * dt)(min_val=0)
    elif event == GameEventType.P2_DOWN:
        p2_paddle['rect']['y'] = clamp(p2_paddle['rect']['y'] + PADDLE_VEL * dt)(max_val=WINDOW_HEIGHT - PADDLE_HEIGHT)

    if event == GameEventType.RESTART:
        initialize()

    if event == GameEventType.START and not game_state['started']:
        game_state['started'] = True
        ball['physics']['dir'] = [random.choice([-1,1]) * 1,0] # Randomizar mais
        ball['physics']['vel'] = 300 * dt # Mudar


def update(dt = 1/FRAMERATE):

    # physics update

    if check_border_collision([[0,0],[WINDOW_WIDTH,0]], ball) \
    or check_border_collision([[0,WINDOW_HEIGHT],[WINDOW_WIDTH, WINDOW_HEIGHT]], ball):
        ball['physics']['dir'][1] *= -1
        print('???')

    ball['rect']['x'] = ball['rect']['x'] + ball['physics']['vel'] * ball['physics']['dir'][0]
    ball['rect']['y'] = ball['rect']['y'] + ball['physics']['vel'] * ball['physics']['dir'][1]



    if check_border_collision([[0,0],[0,WINDOW_HEIGHT]], ball):
        handle_event(GameEventType.P2_SCORED)
        pass


    if check_paddle_collision(p1_paddle, ball) or check_paddle_collision(p2_paddle, ball):
        paddle = p1_paddle if ball['rect']['x'] < WINDOW_WIDTH / 2 else p2_paddle

        paddle_midpos = paddle['rect']['y'] + (PADDLE_HEIGHT / 2)
        ball_midpos = ball['rect']['y'] + (BALL_WIDTH / 2)

        ball['physics']['dir'][1] = .5 * (1 if (ball_midpos - paddle_midpos) > 0 else -1)
        ball['physics']['dir'][0] *= -1

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

        update(None)


        # TODO

        render(renderer,window)
        sleep(1/FRAMERATE)

    SDL_DestroyWindow(window)
    TTF_Quit()
    SDL_Quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
