#!/usr/bin/env python2
# std
import argparse
import sys
# user
import risk
import risk.logger
import risk.game_master
from risk import board
from risk.game_master import GameMaster

# exit codes
_EXIT_BAD_ARGS = -1

###############################################################################
## CLI option parsing
#
def app_setup():
    parser = argparse.ArgumentParser(description='Risk game with Python')
    # dev build defaults to debug for now
    parser.add_argument('--verbose', '-v', action='count',
                        help='extra output', default=risk.logger.LEVEL_DEBUG)
    parser.add_argument('--gui', '-g', action='store_true',
                        help='graphical display', default=False)
    settings = parser.parse_args()
    risk.logger.LOG_LEVEL = settings.verbose
    return settings

###############################################################################
## CLI functions
#
def print_banner():
    print \
"""
    --==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==--
    ||                              PyRisk                             ||
    ||-----------------------------------------------------------------||
    || Risk is a turn-based game for two to six players. The standard  ||
    || version is played on a board depicting a political map of the   ||
    || Earth, divided into forty-two territories, which are grouped    ||
    || into six continents. The primary object of the game is "world   ||
    || domination," or "to occupy every territory on the board and in  ||
    || so doing, eliminate all other players." Players control         ||
    || armies with which they attempt to capture territories from      ||
    || other players, with results determined by dice rolls.           ||
    ||-----------------------------------------------------------------||
    ||                     By: CMPT106 Group Beta                      ||
    --==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==--
"""


###############################################################################
## Debug functions
#
def end_turn_debug_print(game_master):
    risk.logger.debug('Ending turn...')

###############################################################################
## Main game functions
#
def game_setup(settings):
    _DEV_HUMAN_PLAYERS = 1
    game_board = board.generate_empty_board()
    #game_board = board.generate_mini_board()
    game_master = risk.game_master.GameMaster(game_board, settings)
    game_master.generate_players(_DEV_HUMAN_PLAYERS)
    game_master.add_end_turn_callback(end_turn_debug_print)
    # dev
    board.dev_random_assign_owners(game_master)
    return game_master

def run_game(game_master):
    print_banner()
    risk.logger.debug('Starting risk game...')
    try:
        #game_master.choose_territories()
        #game_master.deploy_troops()
        while not game_master.ended:
            run_turn(game_master)
    except (risk.errors.input.UserQuitInput, KeyboardInterrupt):
        game_master.end_game()
    risk.logger.debug('User quit the game!') 

def graphical_run_game(game_master):
    import pygame
    from pygame.locals import *
    pygame.init()
    window = pygame.display.set_mode((640, 480))
    pygame.display.set_caption('RiskPy')

    board = pygame.image.load('resources/risk_board.png').convert()
    board = pygame.transform.scale(board, (640, 480))

    rgb_codes = [
        (255, 0, 0), # red
        (0, 255, 0), # green
        (0, 0, 255), # blue
        (255, 255, 0), # yellow
        (160, 32, 240), # purple
        (165, 42, 42), # brown
    ]
    player_colour_mapping = {None: (255, 255, 255)}
    for player in  game_master.players:
        player_colour_mapping[player] = rgb_codes.pop()
    
    display_refresh.mapping = player_colour_mapping
    display_refresh.board = board
    display_refresh.window = window   

    game_master.add_end_turn_callback(display_refresh)
    game_master.add_end_action_callback(display_refresh)
    game_master.add_end_action_callback(refresh_delay)
    display_refresh(game_master)
    run_game(game_master)
    #while True:
    #    window.blit(board, (0, 0))
    #    pygame.display.flip()

def refresh_delay(game_master, event_type, result):
    import time
    risk.logger.debug("delaying refresh...")
    time.sleep(1/2)

def display_refresh(game_master, event_type=None, result=None):
    import pygame
    if not hasattr(display_refresh, 'coordinates'):
        display_refresh.coordinates = {
            # North America
            'alaska' : (60, 75),
            'northwest_territory': (120, 75),
            'alberta': (110, 110),
            'ontario': (150, 120),
            'greenland': (230, 50),
            'eastern_canada': (190, 120),
            'western_united_states': (115, 155),
            'eastern_united_states': (170, 160),
            'central_america': (115, 210),
            ## Central America
            'venezuela': (160, 260),
            'brazil': (200, 300),
            'peru': (165, 320),
            'argentina': (175, 360),
            ## Africa
            'north_africa': (300, 280),
            'egypt': (345, 270),
            'east_africa': (370, 320),
            'central_africa': (345, 340),
            'south_africa': (355, 400),
            'madagascar': (400, 410),
            ## Europe
            'iceland': (280, 100),
            'great_britain': (265, 145),
            'western_europe': (275, 220),
            'northern_europe': (320, 160),
            'southern_europe': (320, 195),
            'scandinavia': (320, 100),
            'russia': (380, 120),
            ## Asia
            'kamchatka': (560, 70),
            'yakutsk': (510, 70),
            'siberia': (470, 90),
            'ural': (440, 120),
            'afghanistan': (425, 180),
            'middle_east': (390, 240),
            'india': (460, 240),
            'southern_asia': (505, 260),
            'china': (500, 210),
            'mongolia': (510, 160),
            'irkutsk': (510, 115),
            'japan': (575, 165),
            ## Australia
            'indonesia': (520, 340),
            'new_guinea': (570, 320),
            'western_australia': (540, 400),
            'eastern_australia': (590, 390),
        }
    display_refresh.window.blit(display_refresh.board, (0, 0))    
    for name, coordinate in display_refresh.coordinates.iteritems():
        risk.logger.debug("drawing %s!" % name)
        pygame.draw.circle(display_refresh.window, display_refresh.mapping[game_master.board[name].owner], coordinate, 10)
    pygame.display.flip()

def run_turn(game_master):
    risk.logger.debug('Current player is: %s' % 
                      game_master.current_player().name)
    game_master.player_take_turn()
    game_master.call_end_turn_callbacks()
    game_master.end_turn()

if __name__ == '__main__':
    settings = app_setup()
    risk.logger.debug(settings)
    master = game_setup(settings)
    if not settings.gui:
        run_game(master)
    else:
        graphical_run_game(master)
