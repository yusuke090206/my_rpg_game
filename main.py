import pygame
import sys
import os
import constants as c
from map_manager import MapManager
from story_data import StoryManager
from title_screen import TitleScreen
from inventory import InventoryUI
import face_manager
import debug_tool

# --- 1. 初期化 ---
pygame.init()
screen = pygame.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
pygame.display.set_caption("16世紀の探偵 RPG")
clock = pygame.time.Clock()

def get_font(size, bold=False):
  fonts = ["msgothic", "msmincho", "hiraginosans-w3", "notosanscjkjp"]
  available = pygame.font.get_fonts()
  for f in fonts:
    if f in available:
      font = pygame.font.SysFont(f, size)
      if bold: font.set_bold(True)
      return font
  return pygame.font.SysFont(None, size)

font_main = get_font(24)
font_title = get_font(48, bold=True)

# --- 2. 管理クラスの初期化 ---
story = StoryManager()
maps = MapManager()
title_ui = TitleScreen(font_title, font_main)
inventory_ui = InventoryUI(font_main)
face_manager.init()

# --- 3. プレイヤーグラフィック読み込み ---
def get_image(sheet, frame_x, frame_y, width, height, scale):
  image = pygame.Surface((width, height), pygame.SRCALPHA)
  image.blit(sheet, (0, 0), (frame_x * width,
             frame_y * height, width, height))
  return pygame.transform.scale(image, (int(width * scale), int(height * scale)))

try:
  base_dir = os.path.dirname(os.path.abspath(__file__))
  chara_path = os.path.join(base_dir, "assets", "images", "main_chara.png")
  sprite_sheet = pygame.image.load(chara_path).convert_alpha()
  HAS_IMAGE = True
except:
  HAS_IMAGE = False

game_state = "TITLE"
player_pos = list(maps.get_spawn_pos())
player_speed = 4
direction = 0
frame = 1
anim_timer = 0

def draw_dialogue_ui():
  box_rect = pygame.Rect(40, 420, 720, 150)
  pygame.draw.rect(screen, (20, 20, 20), box_rect)
  pygame.draw.rect(screen, c.WHITE, box_rect, 2)
  face_manager.draw(screen)

  current_text = story.get_current_text()
  scene_data = story.get_current_scene_data()
  line_limit = 30
  lines = [current_text[i:i + line_limit]
           for i in range(0, len(current_text), line_limit)]

  for i, line in enumerate(lines):
    txt_surf = font_main.render(line, True, c.WHITE)
    screen.blit(txt_surf, (60, 445 + i * 30))

  guide = "[Y/N] で選択" if scene_data["type"] == "choice" else "SPACEで進む"
  g_surf = font_main.render(guide, True, (180, 180, 180))
  screen.blit(g_surf, (60, 535))

# --- 4. メインループ ---
while True:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      pygame.quit(); sys.exit()

    if game_state == "TITLE":
      if event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
        game_state = "DIALOGUE"
    elif game_state == "DIALOGUE":
      if event.type == pygame.KEYDOWN:
        scene = story.get_current_scene_data()
        if scene["type"] == "choice":
          if event.key == pygame.K_y:
            story.current_scene = scene["choices"]["Y"]; story.text_index = 0
          elif event.key == pygame.K_n:
            story.current_scene = scene["choices"]["N"]; story.text_index = 0
        elif scene["type"] == "normal" and event.key == pygame.K_SPACE:
          if not story.next_step():
            game_state = "EXPLORING"
    elif game_state == "EXPLORING":
      if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
        game_state = "INVENTORY"
    elif game_state == "INVENTORY":
      if event.type == pygame.KEYDOWN and event.key in [pygame.K_e, pygame.K_ESCAPE]:
        game_state = "EXPLORING"

  if game_state == "EXPLORING":
    keys = pygame.key.get_pressed()
    nx, ny = player_pos[0], player_pos[1]
    moving = False
    if keys[pygame.K_a]: nx -= player_speed; direction = 1; moving = True
    elif keys[pygame.K_d]: nx += player_speed; direction = 2; moving = True
    elif keys[pygame.K_w]: ny -= player_speed; direction = 3; moving = True
    elif keys[pygame.K_s]: ny += player_speed; direction = 0; moving = True

    if not maps.is_wall(nx + 20, ny + 70) and not maps.is_wall(nx + 40, ny + 70):
      player_pos = [nx, ny]

    target_map = maps.check_transition(
        player_pos[0] + 30, player_pos[1] + 70)
    if target_map:
      if target_map in maps.all_maps:
        maps.load_map(target_map)
        player_pos = list(maps.get_spawn_pos())

    if moving:
      anim_timer += 1
      if anim_timer >= 10: frame = (frame + 1) % 3; anim_timer = 0
    else: frame = 1

  if game_state == "TITLE":
    title_ui.draw(screen)
  else:
    maps.draw(screen)
    # もし debug_tool でエラーが出るなら下の行を消してください
    try: debug_tool.draw_grid(screen)
    except: pass

    if HAS_IMAGE:
      curr_s = get_image(sprite_sheet, frame, direction,
                         c.SPRITE_WIDTH, c.SPRITE_HEIGHT, c.SCALE)
      screen.blit(curr_s, player_pos)
    else:
      pygame.draw.rect(
          screen, c.BLUE, (player_pos[0], player_pos[1], 40, 80))

    if game_state == "DIALOGUE":
      draw_dialogue_ui()
    elif game_state == "INVENTORY":
      inventory_ui.draw(screen, story.items)

  pygame.display.flip()
  clock.tick(c.FPS)
