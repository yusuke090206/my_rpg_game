import pygame
import sys
import os
import constants as c
from map_manager import MapManager
from story_data import StoryManager
from title_screen import TitleScreen
from inventory import InventoryUI
import image_manager  # ★ これが重要
import face_manager
import debug_tool

# --- 1. 初期化 ---
pygame.init()
screen = pygame.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
pygame.display.set_caption("16世紀の探偵 RPG")
clock = pygame.time.Clock()

# --- 2. フォント設定 ---
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

# --- 3. 管理クラス・リソースの初期化 ---
image_manager.init()  # 全画像を読み込み
story = StoryManager()
maps = MapManager()
title_ui = TitleScreen(font_title, font_main)
inventory_ui = InventoryUI(font_main)

# 最初は主人公の顔をセット
face_manager.set_face("main")

# --- 4. スプライト切り出し関数 ---
def get_sprite_frame(sheet, frame_x, frame_y, width, height, scale):
  """画像シートから1コマを切り出す。シートがNoneならNoneを返す"""
  if sheet is None:
    return None
  try:
    image = pygame.Surface((width, height), pygame.SRCALPHA)
    # 指定の座標から切り出し
    image.blit(sheet, (0, 0), (frame_x * width,
               frame_y * height, width, height))
    return pygame.transform.scale(image, (int(width * scale), int(height * scale)))
  except:
    return None

# --- 5. ゲーム状態とプレイヤー設定 ---
game_state = "TITLE"
player_pos = list(maps.get_spawn_pos())
player_speed = 4
direction = 0
frame = 1
anim_timer = 0

def draw_dialogue_ui():
  """30文字改行対応の会話UI"""
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

# --- 6. メインループ ---
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

  # 更新ロジック
  if game_state == "EXPLORING":
    keys = pygame.key.get_pressed()
    nx, ny = player_pos[0], player_pos[1]
    moving = False
    if keys[pygame.K_LEFT]: nx -= player_speed; direction = 1; moving = True
    elif keys[pygame.K_RIGHT]: nx += player_speed; direction = 2; moving = True
    elif keys[pygame.K_UP]: ny -= player_speed; direction = 3; moving = True
    elif keys[pygame.K_DOWN]: ny += player_speed; direction = 0; moving = True

    if not maps.is_wall(nx + 20, ny + 70) and not maps.is_wall(nx + 40, ny + 70):
      player_pos = [nx, ny]

    if moving:
      anim_timer += 1
      if anim_timer >= 10: frame = (frame + 1) % 3; anim_timer = 0
    else: frame = 1

  # 描画処理
  if game_state == "TITLE":
    title_ui.draw(screen)
  else:
    maps.draw(screen)
    debug_tool.draw_grid(screen)

    # ★ キャラクター描画部分の修正
    # image_managerのキーを "main_sprite" に統一
    sheet = image_manager.get("main_sprite")
    curr_s = get_sprite_frame(
        sheet, frame, direction, c.SPRITE_WIDTH, c.SPRITE_HEIGHT, c.SCALE)

    if curr_s:
      screen.blit(curr_s, player_pos)
    else:
      # 画像がない場合は青い四角を表示（これでエラー落ちを防ぐ）
      pygame.draw.rect(screen, (0, 0, 255),
                       (player_pos[0], player_pos[1], 40, 80))

    if game_state == "DIALOGUE":
      draw_dialogue_ui()
    elif game_state == "INVENTORY":
      inventory_ui.draw(screen, story.items)

  pygame.display.flip()
  clock.tick(c.FPS)
