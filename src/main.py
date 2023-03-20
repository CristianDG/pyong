import sys
import random
from dataclasses import dataclass
from enum import Enum, auto
from time import sleep
from ctypes import byref, c_uint8, c_int, c_uint32, CFUNCTYPE
from sdl2 import *

WINDOW_WIDTH, WINDOW_HEIGHT  = 1280, 720

FRAMERATE = 75

PADDLE_WIDTH  = 25
PADDLE_HEIGHT = 200

PADDLE_VEL = 200


p1_paddle  = None
p2_paddle  = None
ball       = None
game_state = None

class GameEventType(Enum):
    P1_UP   = auto()
    P1_DOWN = auto()
    P2_UP   = auto()
    P2_DOWN = auto()
    START   = auto()
    RESTART = auto()
    STOP    = auto()



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
        p2_paddle['rect']['x'] = WINDOW_WIDTH - 50
        p2_paddle['rect']['y'] = (WINDOW_HEIGHT // 2) - (PADDLE_HEIGHT//2)
        p2_paddle['rect']['h'] = PADDLE_HEIGHT
        p2_paddle['rect']['w'] = PADDLE_WIDTH
        p2_paddle['physics']['res'] = 1
    initialize_p2_paddle()

    def initialize_ball():
        global ball

        ball = { 'rect': base_rect.copy(), 'physics': base_physics.copy() }
        ball['rect']['h'] = PADDLE_WIDTH
        ball['rect']['w'] = PADDLE_WIDTH
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
        ball['physics']['vel'] = 200 * dt # Mudar


def update(dt = 1/FRAMERATE):

    # physics update
    ball['rect']['x'] = ball['rect']['x'] + ball['physics']['vel'] * ball['physics']['dir'][0]


    if check_collision(p1_paddle, ball) or check_collision(p2_paddle, ball):
        paddle = p1_paddle if ball['rect']['x'] < WINDOW_WIDTH / 2 else p2_paddle

        ball['physics']['dir'][0] *= -1
        pass

def check_collision(paddle, ball):
    paddle_rect = SDL_FRect(**paddle['rect'])
    ball_rect   = SDL_FRect(**ball['rect'])

    return SDL_HasIntersectionF(paddle_rect, ball_rect) == SDL_TRUE



def main():

    SDL_Init(SDL_INIT_VIDEO)
    window = SDL_CreateWindow(b"Pong",
                              SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                              WINDOW_WIDTH, WINDOW_HEIGHT, SDL_WINDOW_SHOWN)

    # SDL_SetHint(SDL_HINT_RENDER_SCALE_QUALITY, b"2");
    renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_SOFTWARE)
    SDL_SetRenderDrawBlendMode(renderer, SDL_BLENDMODE_NONE)


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
    SDL_Quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
