import pygame
import sys
import os
import asyncio
import constants as c
from map_manager import MapManager
from story_data import StoryManager
from title_screen import TitleScreen
from inventory import InventoryUI
import face_manager

# --- 1. 初期化 ---
pygame.init()
# Web動作安定のためウィンドウモード推奨ですが、元のフルスクリーン設定に戻します
screen = pygame.display.set_mode(
    (c.SCREEN_WIDTH, c.SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("16世紀の探偵 RPG")
clock = pygame.time.Clock()

# ★ここだけ修正：exe化対応のためのパス設定★
# exe化されている(frozen)か、開発中かで基準フォルダを自動で切り替えます
if getattr(sys, 'frozen', False):
  base_dir = os.path.dirname(sys.executable)
else:
  base_dir = os.path.dirname(os.path.abspath(__file__))


# --- フォント読み込み ---
def get_font(size, bold=False):
  # 手順1: base_dir を基準に assets フォルダを探す
  font_path = os.path.join(base_dir, "assets", "font.ttf")

  if os.path.exists(font_path):
    try:
      font = pygame.font.Font(font_path, size)
      if bold: font.set_bold(True)
      return font
    except:
      pass

  # 手順2: なければPCのシステムフォント
  fonts = ["msgothic", "msmincho",
           "hiraginosans-w3", "notosanscjkjp", "yugothic"]
  available = pygame.font.get_fonts()
  for f in fonts:
    if f in available:
      font = pygame.font.SysFont(f, size)
      if bold: font.set_bold(True)
      return font

  # 手順3: デフォルト
  return pygame.font.SysFont(None, size)

font_main = get_font(24)
font_title = get_font(48, bold=True)
font_huge = get_font(64, bold=True)

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

npc_sheets = {}
HAS_IMAGE = False
sprite_sheet = None

try:
  # パスを base_dir 基準に変更
  chara_path = os.path.join(base_dir, "assets", "images", "main_chara.png")
  if os.path.exists(chara_path):
    sprite_sheet = pygame.image.load(chara_path).convert_alpha()
    HAS_IMAGE = True

  for name in ["john", "monika", "anna", "witch", "erena"]:
    path = os.path.join(base_dir, "assets", "images", f"{name}_chara.png")
    if os.path.exists(path):
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

# ダイアログ描画関数
def draw_dialogue_ui():
  global visible_char_count
  scene_data = story.get_current_scene_data()
  face_id = scene_data.get("face_id")

  box_rect = pygame.Rect(40, 420, 720, 150)
  pygame.draw.rect(screen, (20, 20, 20), box_rect)
  pygame.draw.rect(screen, c.WHITE, box_rect, 2)

  if face_id:
    face_manager.draw(screen, face_id)

  full_text = story.get_current_text()
  display_text = full_text[:visible_char_count]

  text_x = 160 if face_id else 60
  line_limit = 25

  lines = [display_text[i:i + line_limit]
           for i in range(0, len(display_text), line_limit)]
  for i, line in enumerate(lines):
    txt_surf = font_main.render(line, True, c.WHITE)
    screen.blit(txt_surf, (text_x, 445 + i * 30))

  if visible_char_count >= len(full_text):
    guide = "[Y/N] で選択" if scene_data["type"] == "choice" else "SPACEで進む"
    g_surf = font_main.render(guide, True, (180, 180, 180))
    screen.blit(g_surf, (60, 535))

# --- 4. メインループ (非同期対応) ---
async def main():
  global game_state, player_pos, direction, frame, anim_timer, text_timer, visible_char_count

  while True:
    # --- 会話ロジック ---
    if game_state == "DIALOGUE":
      text_timer += 1
      if text_timer >= text_speed:
        visible_char_count += 1
        text_timer = 0

      # アイテムコンプリートチェック関数
      def check_items_complete():
        required_items = ["夫婦写真", "懐かしいパン",
                          "指輪", "美しい花", "同じ夫婦写真", "楽譜"]
        for item in required_items:
          if item not in story.items:
            return False
        return True

      current = story.current_scene
      target_scene = None

      if current == "witch_check_no_gun":
        target_scene = "end_2_pure_peace" if check_items_complete() else "end_1_bad_helpless"
      elif current == "witch_check_shoot":
        target_scene = "end_4_tragic_kill" if check_items_complete() else "end_3_ruthless_kill"
      elif current == "witch_check_spare":
        target_scene = "end_5_true_peace" if check_items_complete() else "end_1_bad_helpless"

      if target_scene:
        story.current_scene = target_scene
        story.text_index = 0
        visible_char_count = 0

    # ▼ イベント処理 ▼
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit(); sys.exit()

      if game_state == "TITLE":
        if event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
          story.current_scene = "start_scene"
          story.text_index = 0
          game_state = "DIALOGUE"
          visible_char_count = 0

      elif game_state == "DIALOGUE":
        if event.type == pygame.KEYDOWN:
          scene = story.get_current_scene_data()
          full_text = story.get_current_text()
          is_typing = visible_char_count < len(full_text)

          if scene["type"] == "choice":
            if is_typing: visible_char_count = len(full_text)
            else:
              if event.key == pygame.K_y:
                story.current_scene = scene["choices"]["Y"]; story.text_index = 0; visible_char_count = 0
              elif event.key == pygame.K_n:
                story.current_scene = scene["choices"]["N"]; story.text_index = 0; visible_char_count = 0

          elif scene["type"] == "normal" and event.key == pygame.K_SPACE:
            if is_typing: visible_char_count = len(full_text)
            else:
              item_name = scene.get("give_item")
              if item_name and item_name not in story.items: story.items.append(
                  item_name)

              last_scene_id = story.current_scene
              if not story.next_step():
                # エンディング・移動処理
                if "door_open" in last_scene_id:
                  maps.load_map("mansion_inside")
                  player_pos = list(maps.get_spawn_pos())
                  game_state = "EXPLORING"
                elif "end_0" in last_scene_id: game_state = "ENDING_0"
                elif "end_1" in last_scene_id: game_state = "ENDING_1"
                elif "end_2" in last_scene_id: game_state = "ENDING_2"
                elif "end_3" in last_scene_id: game_state = "ENDING_3"
                elif "end_4" in last_scene_id: game_state = "ENDING_4"
                elif "end_5" in last_scene_id: game_state = "ENDING_5"
                else: game_state = "EXPLORING"
              visible_char_count = 0

      elif game_state == "PAUSE":
        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_ESCAPE: game_state = "EXPLORING"
          elif event.key == pygame.K_t: game_state = "TITLE"
          elif event.key == pygame.K_q: pygame.quit(); sys.exit()

      elif game_state == "EXPLORING":
        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_e: game_state = "INVENTORY"
          elif event.key == pygame.K_ESCAPE: game_state = "PAUSE"
          elif event.key == pygame.K_f:
            check_x = player_pos[0] + (c.SPRITE_WIDTH * c.SCALE) / 2
            check_y = player_pos[1] + \
                (c.SPRITE_HEIGHT * c.SCALE) * 0.9
            obj = maps.get_object_at(check_x, check_y)
            if obj:
              target = obj.get("target_scene")
              if obj.get("char_id") == "witch":
                target = "witch_gun_choice" if "新式の拳銃" in story.items else "witch_check_no_gun"
              elif obj.get("char_id") == "anna":
                target = "anna_after" if "古びた鍵" in story.items else "npc_anna"
              elif target == "door_locked":
                if "古びた鍵" in story.items: target = "door_open"

              if target:
                story.current_scene = target; story.text_index = 0; game_state = "DIALOGUE"; visible_char_count = 0

      elif game_state == "INVENTORY":
        if event.type == pygame.KEYDOWN and event.key in [pygame.K_e, pygame.K_ESCAPE]:
          game_state = "EXPLORING"

      elif game_state.startswith("ENDING"):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
          game_state = "TITLE"
          story.current_scene = "start_scene"
          story.text_index = 0
          visible_char_count = 0
          story.items = []
          maps.load_map("town")
          player_pos = list(maps.get_spawn_pos())

    # ▼ ロジック更新 ▼
    if game_state == "EXPLORING":
      keys = pygame.key.get_pressed()
      nx, ny = player_pos[0], player_pos[1]
      moving = False
      if keys[pygame.K_a]: nx -= player_speed; direction = 1; moving = True
      elif keys[pygame.K_d]: nx += player_speed; direction = 2; moving = True
      elif keys[pygame.K_w]: ny -= player_speed; direction = 3; moving = True
      elif keys[pygame.K_s]: ny += player_speed; direction = 0; moving = True

      f_w, f_h = c.SPRITE_WIDTH * c.SCALE, c.SPRITE_HEIGHT * c.SCALE
      if not maps.is_wall(nx + f_w * 0.3, ny + f_h * 0.9) and not maps.is_wall(nx + f_w * 0.7, ny + f_h * 0.9):
        player_pos = [nx, ny]

      target_map = maps.check_transition(
          player_pos[0] + f_w / 2, player_pos[1] + f_h * 0.9)
      if target_map:
        maps.load_map(target_map)
        player_pos = list(maps.get_spawn_pos())

      if moving:
        anim_timer += 1
        if anim_timer >= 10: frame = (frame + 1) % 3; anim_timer = 0
      else: frame = 1

    # ▼ 描画処理 ▼
    if game_state == "TITLE":
      title_ui.draw(screen)

    elif game_state == "ENDING_0":
      screen.fill((0, 0, 0))
      title_surf = font_huge.render("GAME OVER", True, (100, 100, 100))
      sub_surf = font_title.render("- 物語は始まらなかった -", True, c.WHITE)
      screen.blit(title_surf, (c.SCREEN_WIDTH // 2 -
                               title_surf.get_width() // 2, 200))
      screen.blit(sub_surf, (c.SCREEN_WIDTH // 2 -
                             sub_surf.get_width() // 2, 320))

    elif game_state == "ENDING_1":
      screen.fill((50, 0, 0))
      title_surf = font_huge.render("BAD ENDING", True, (255, 100, 100))
      sub_surf = font_title.render("- 真相は？ -", True, c.WHITE)
      screen.blit(title_surf, (250, 200))
      screen.blit(sub_surf, (280, 320))

    elif game_state == "ENDING_2":
      screen.fill((0, 20, 50))
      title_surf = font_huge.render(
          "TRUE ENDING A", True, (100, 255, 255))
      sub_surf = font_title.render("- 永遠の別れ -", True, c.WHITE)
      screen.blit(title_surf, (200, 200))
      screen.blit(sub_surf, (300, 320))

    elif game_state == "ENDING_3":
      screen.fill((20, 20, 20))
      title_surf = font_huge.render(
          "NORMAL ENDING", True, (180, 180, 180))
      sub_surf = font_title.render("- これでお別れ？ -", True, c.WHITE)
      screen.blit(title_surf, (200, 200))
      screen.blit(sub_surf, (280, 320))

    elif game_state == "ENDING_4":
      screen.fill((30, 0, 30))
      title_surf = font_huge.render("BAD ENDING", True, (200, 100, 200))
      sub_surf = font_title.render("- 君を愛してる -", True, c.WHITE)
      screen.blit(title_surf, (250, 200))
      screen.blit(sub_surf, (300, 320))

    elif game_state == "ENDING_5":
      screen.fill((80, 60, 0))
      title_surf = font_huge.render("TRUE ENDING B", True, (255, 215, 0))
      sub_surf = font_title.render("- もう一度始めから -", True, c.WHITE)
      screen.blit(title_surf, (200, 200))
      screen.blit(sub_surf, (280, 320))

    if game_state.startswith("ENDING"):
      restart_text = font_main.render(
          "Press R to Title", True, (200, 200, 200))
      screen.blit(restart_text, (350, 500))

    else:
      if story.current_scene in ["end_3_ruthless_kill", "end_4_tragic_kill"]:
        screen.fill((0, 0, 0))
      else:
        maps.draw(screen)
        for obj in maps.all_maps[maps.current_map_key].get("objects", []):
          cid = obj.get("char_id")
          if cid in npc_sheets:
            img = get_image(npc_sheets[cid], 1, obj.get(
                "direction", 0), c.SPRITE_WIDTH, c.SPRITE_HEIGHT, c.SCALE)
            screen.blit(img, obj["rect"][:2])
        if HAS_IMAGE:
          screen.blit(get_image(sprite_sheet, frame, direction,
                                c.SPRITE_WIDTH, c.SPRITE_HEIGHT, c.SCALE), player_pos)
        else:
          pygame.draw.rect(screen, c.BLUE, (*player_pos, 40, 80))

      if game_state == "DIALOGUE":
        draw_dialogue_ui()
      elif game_state == "INVENTORY":
        inventory_ui.draw(screen, story.items)
      elif game_state == "PAUSE":
        overlay = pygame.Surface(
            (c.SCREEN_WIDTH, c.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        # ポーズメニュー
        title_text = font_title.render("PAUSE", True, c.WHITE)
        screen.blit(title_text, (350, 200))
        txt_resume = font_main.render("[ESC] ゲームに戻る", True, c.WHITE)
        txt_title_p = font_main.render("[ T ] タイトルへ", True, c.WHITE)
        txt_quit = font_main.render("[ Q ] 終了する", True, c.RED)
        screen.blit(txt_resume, (300, 280))
        screen.blit(txt_title_p, (300, 320))
        screen.blit(txt_quit, (300, 360))

    pygame.display.flip()
    clock.tick(c.FPS)
    await asyncio.sleep(0)

if __name__ == "__main__":
  asyncio.run(main())
