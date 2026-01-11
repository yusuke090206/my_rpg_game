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

# --- 3. グラフィック読み込み関数 ---
def get_image(sheet, frame_x, frame_y, width, height, scale):
  image = pygame.Surface((width, height), pygame.SRCALPHA)
  image.blit(sheet, (0, 0), (frame_x * width,
                             frame_y * height, width, height))
  return pygame.transform.scale(image, (int(width * scale), int(height * scale)))

# 【更新】NPCとプレイヤーの画像読み込み
base_dir = os.path.dirname(os.path.abspath(__file__))
npc_sheets = {}
try:
  # メインキャラ
  chara_path = os.path.join(base_dir, "assets", "images", "main_chara.png")
  sprite_sheet = pygame.image.load(chara_path).convert_alpha()
  HAS_IMAGE = True
  # NPC 3人
  for name in ["john", "monika", "anna"]:
    path = os.path.join(base_dir, "assets", "images", f"{name}_chara.png")
    npc_sheets[name] = pygame.image.load(path).convert_alpha()
except Exception as e:
  print(f"画像読み込みエラー: {e}")
  HAS_IMAGE = False

# --- ゲーム状態・変数 ---
game_state = "TITLE"
player_pos = list(maps.get_spawn_pos())
player_speed = 4
direction = 0
frame = 1
anim_timer = 0

text_timer = 0
visible_char_count = 0
text_speed = 2

# 【更新】ダイアログ描画関数（face_id対応）
def draw_dialogue_ui():
  global visible_char_count
  scene_data = story.get_current_scene_data()
  # face_id があるか確認
  face_id = scene_data.get("face_id")

  # ダイアログ枠
  box_rect = pygame.Rect(40, 420, 720, 150)
  pygame.draw.rect(screen, (20, 20, 20), box_rect)
  pygame.draw.rect(screen, c.WHITE, box_rect, 2)

  # 顔表示（IDを渡して描画）
  if face_id:
    face_manager.draw(screen, face_id)

  # テキスト表示
  full_text = story.get_current_text()
  display_text = full_text[:visible_char_count]

  # 顔があるときは右にずらす(220px)、ないときは(60px)
  text_x = 60 if face_id else 60
  line_limit = 20 if face_id else 25

  lines = [display_text[i:i + line_limit]
           for i in range(0, len(display_text), line_limit)]

  for i, line in enumerate(lines):
    txt_surf = font_main.render(line, True, c.WHITE)
    screen.blit(txt_surf, (text_x, 445 + i * 30))

  if visible_char_count >= len(full_text):
    guide = "[Y/N] で選択" if scene_data["type"] == "choice" else "SPACEで進む"
    g_surf = font_main.render(guide, True, (180, 180, 180))
    screen.blit(g_surf, (60, 535))

# --- 4. メインループ ---
while True:
  # --- A. 更新処理 (Update) ---
  if game_state == "DIALOGUE":
    text_timer += 1
    if text_timer >= text_speed:
      visible_char_count += 1
      text_timer = 0

  # --- B. イベント処理 (Events) ---
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      pygame.quit(); sys.exit()

    if game_state == "TITLE":
      if event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
        game_state = "DIALOGUE"
        visible_char_count = 0

    elif game_state == "DIALOGUE":
      if event.type == pygame.KEYDOWN:
        scene = story.get_current_scene_data()
        full_text = story.get_current_text()
        is_typing = visible_char_count < len(full_text)

        if scene["type"] == "choice":
          if is_typing:
            visible_char_count = len(full_text)
          else:
            if event.key == pygame.K_y:
              story.current_scene = scene["choices"]["Y"]; story.text_index = 0
              visible_char_count = 0
            elif event.key == pygame.K_n:
              story.current_scene = scene["choices"]["N"]; story.text_index = 0
              visible_char_count = 0

        elif scene["type"] == "normal" and event.key == pygame.K_SPACE:
          if is_typing:
            visible_char_count = len(full_text)
          else:
            item_name = scene.get("give_item")
            if item_name and item_name not in story.items:
              story.items.append(item_name)
            if not story.next_step():
              if scene.get("is_ending", False):
                game_state = "ENDING"
              else:
                game_state = "EXPLORING"
            visible_char_count = 0

    elif game_state == "EXPLORING":
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_e:
          game_state = "INVENTORY"
        elif event.key == pygame.K_f:  # Fキーで調査
          # 足元の判定（SCALEに合わせて調整）
          check_x = player_pos[0] + (c.SPRITE_WIDTH * c.SCALE) / 2
          check_y = player_pos[1] + (c.SPRITE_HEIGHT * c.SCALE) * 0.9
          obj = maps.get_object_at(check_x, check_y)
          if obj:
            story.current_scene = obj["target_scene"]
            story.text_index = 0
            game_state = "DIALOGUE"
            visible_char_count = 0

    elif game_state == "INVENTORY":
      if event.type == pygame.KEYDOWN and event.key in [pygame.K_e, pygame.K_ESCAPE]:
        game_state = "EXPLORING"

    elif game_state == "ENDING":
      if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
        game_state = "TITLE"
        story.current_scene = "start_scene"
        story.text_index = 0
        visible_char_count = 0

  # --- C. 移動・マップ処理 (Logic) ---
  if game_state == "EXPLORING":
    keys = pygame.key.get_pressed()
    nx, ny = player_pos[0], player_pos[1]
    moving = False

    # 移動
    if keys[pygame.K_a]: nx -= player_speed; direction = 1; moving = True
    elif keys[pygame.K_d]: nx += player_speed; direction = 2; moving = True
    elif keys[pygame.K_w]: ny -= player_speed; direction = 3; moving = True
    elif keys[pygame.K_s]: ny += player_speed; direction = 0; moving = True

    # 当たり判定（足元2点で判定）
    f_w = (c.SPRITE_WIDTH * c.SCALE)
    f_h = (c.SPRITE_HEIGHT * c.SCALE)
    if not maps.is_wall(nx + f_w * 0.3, ny + f_h * 0.9) and not maps.is_wall(nx + f_w * 0.7, ny + f_h * 0.9):
      player_pos = [nx, ny]

    # マップ移動
    target_map = maps.check_transition(
        player_pos[0] + f_w / 2, player_pos[1] + f_h * 0.9)
    if target_map and target_map in maps.all_maps:
      maps.load_map(target_map)
      player_pos = list(maps.get_spawn_pos())

    if moving:
      anim_timer += 1
      if anim_timer >= 10: frame = (frame + 1) % 3; anim_timer = 0
    else: frame = 1

  # --- D. 描画処理 (Draw) ---
  if game_state == "TITLE":
    title_ui.draw(screen)
  elif game_state == "ENDING":
    screen.fill((0, 0, 0))
    end_text = font_title.render("THE END", True, (200, 0, 0))
    sub_text = font_main.render("真相は誰も知らない", True, c.WHITE)
    restart_text = font_main.render("Press R to Title", True, c.RED)
    screen.blit(end_text, (c.SCREEN_WIDTH // 2 - 100, 200))
    screen.blit(sub_text, (c.SCREEN_WIDTH // 2 - 100, 300))
    screen.blit(restart_text, (c.SCREEN_WIDTH // 2 - 100, 500))
  else:
    maps.draw(screen)
    debug_tool.draw_grid(screen)

    # 【追加】NPCの描画
    current_objects = maps.all_maps[maps.current_map_key].get("objects", [])
    for obj in current_objects:
      cid = obj.get("char_id")
      if cid in npc_sheets:
        npc_img = get_image(
            npc_sheets[cid], 1, 0, c.SPRITE_WIDTH, c.SPRITE_HEIGHT, c.SCALE)
        npc_dir = obj.get("direction", 0)
        # 取得した向き (npc_dir) を使って画像を取得
        npc_img = get_image(
            npc_sheets[cid], 1, npc_dir, c.SPRITE_WIDTH, c.SPRITE_HEIGHT, c.SCALE)
        screen.blit(npc_img, (obj["rect"][0], obj["rect"][1]))

    # プレイヤー
    if HAS_IMAGE:
      curr_s = get_image(sprite_sheet, frame, direction,
                         c.SPRITE_WIDTH, c.SPRITE_HEIGHT, c.SCALE)
      screen.blit(curr_s, player_pos)
    else:
      pygame.draw.rect(
          screen, c.BLUE, (player_pos[0], player_pos[1], 40, 80))

    # UI
    if game_state == "DIALOGUE":
      draw_dialogue_ui()
    elif game_state == "INVENTORY":
      inventory_ui.draw(screen, story.items)

    # 座標表示
    pos_text = f"X: {int(player_pos[0])} Y: {int(player_pos[1])}"
    pos_surf = font_main.render(pos_text, True, (255, 255, 0))
    screen.blit(pos_surf, (c.SCREEN_WIDTH - pos_surf.get_width() - 20, 20))

  pygame.display.flip()
  clock.tick(c.FPS)
