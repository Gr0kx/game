
Skip to content
Pull requests
Issues
Marketplace
Explore
@Gr0kx
Gr0kx /
game
Public

Code
Issues
Pull requests
Actions
Projects
Wiki
Security
Insights

    Settings

game/
in
main

1

import pygame

2

from pygame import mixer

3

import os

4

import random

5

import csv

6

import button

7

​

8

mixer.init()

9

pygame.init()

10

​

11

SCREEN_WIDTH = 1200

12

SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

13

​

14

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

15

pygame.display.set_caption('Shooter')

16

​

17

# set framerate

18

clock = pygame.time.Clock()

19

FPS = 60

20

​

21

# define game variables

22

GRAVITY = 0.75

23

SCROLL_THRESH = 200

24

ROWS = 16

25

COLS = 150

26

TILE_SIZE = SCREEN_HEIGHT // ROWS

27

TILE_TYPES = 22

28

MAX_LEVELS = 3

29

screen_scroll = 0

30

bg_scroll = 0

31

level = 1

32

start_game = False

33

start_intro = False

34

​

35

bomb_start_time = None

36

defuser_start = None

37

​

38

# define player action variables

39

moving_left = False

40

moving_right = False

41

moving_up = False

42

moving_down = False

43

shoot_active = False

44

shoot = False

45

grenade = False

46

grenade_thrown = False

@Gr0kx
Commit changes
Commit summary
Optional extended description
Commit directly to the main branch.
Create a new branch for this commit and start a pull request. Learn more about pull requests.
Footer
© 2022 GitHub, Inc.
Footer navigation

    Terms
    Privacy
    Security
    Status
    Docs
    Contact GitHub
    Pricing
    API
    Training
    Blog
    About

You have no unread notifications
