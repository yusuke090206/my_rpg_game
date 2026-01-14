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
font_huge = get_font(64, bold=True)  # エンディング用の特大フォント

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

base_dir = os.path.dirname(os.path.abspath(__file__))
npc_sheets = {}
try:
  chara_path = os.path.join(base_dir, "assets", "images", "main_chara.png")
  sprite_sheet = pygame.image.load(chara_path).convert_alpha()
  HAS_IMAGE = True
  for name in ["john", "monika", "anna", "witch", "erena"]:
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

  text_x = 60 if face_id else 60
  line_limit = 25 if face_id else 25

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
  # 会話中の文字送りタイマー
  if game_state == "DIALOGUE":
    text_timer += 1
    if text_timer >= text_speed:
      visible_char_count += 1
      text_timer = 0

    # ▼▼▼ 5つのエンディング分岐処理 ▼▼▼
    def check_items_complete():
      required_items = ["夫婦写真", "懐かしいパン", "指輪", "美しい花", "同じ夫婦写真", "楽譜"]
      return all(item in story.items for item in required_items)

    current = story.current_scene
    target_scene = None

    # パターンA: 銃なし判定
    if current == "witch_check_no_gun":
      if check_items_complete():
        target_scene = "end_2_pure_peace"
      else:
        target_scene = "end_1_bad_helpless"

    # パターンB: 銃あり・撃つ(Y)
    elif current == "witch_check_shoot":
      if check_items_complete():
        target_scene = "end_4_tragic_kill"
      else:
        target_scene = "end_3_ruthless_kill"

    # パターンC: 銃あり・撃たない(N)
    elif current == "witch_check_spare":
      if check_items_complete():
        target_scene = "end_5_true_peace"
      else:
        target_scene = "end_1_bad_helpless"

    if target_scene:
      story.current_scene = target_scene
      story.text_index = 0
      visible_char_count = 0
    # ▲▲▲ 分岐処理ここまで ▲▲▲

  # ▼ イベント処理ループ ▼
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      pygame.quit(); sys.exit()

    # --- タイトル画面 ---
    if game_state == "TITLE":
      if event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
        story.current_scene = "start_scene"
        story.text_index = 0
        game_state = "DIALOGUE"
        visible_char_count = 0

    # --- 会話画面 ---
    elif game_state == "DIALOGUE":
      if event.type == pygame.KEYDOWN:
        scene = story.get_current_scene_data()
        full_text = story.get_current_text()
        is_typing = visible_char_count < len(full_text)

        # 選択肢
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

        # 通常会話
        elif scene["type"] == "normal" and event.key == pygame.K_SPACE:
          if is_typing:
            visible_char_count = len(full_text)
          else:
            # アイテム入手
            item_name = scene.get("give_item")
            if item_name and item_name not in story.items:
              story.items.append(item_name)

            # 次へ
            current_scene_id = story.current_scene
            if not story.next_step():
              # 特殊イベント
              if current_scene_id == "door_open":
                maps.load_map("mansion_inside")
                player_pos = list(maps.get_spawn_pos())

              # 状態遷移 (エンディングかどうか)
              if scene.get("is_ending", False):
                game_state = "ENDING"
              else:
                game_state = "EXPLORING"

            visible_char_count = 0

    # --- ポーズ画面 ---
    elif game_state == "PAUSE":
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
          game_state = "EXPLORING"
        elif event.key == pygame.K_t:
          game_state = "TITLE"
        elif event.key == pygame.K_q:
          pygame.quit(); sys.exit()

    # --- 探索画面 ---
    elif game_state == "EXPLORING":
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_e:
          game_state = "INVENTORY"
        elif event.key == pygame.K_ESCAPE:
          game_state = "PAUSE"
        elif event.key == pygame.K_f:
          check_x = player_pos[0] + (c.SPRITE_WIDTH * c.SCALE) / 2
          check_y = player_pos[1] + (c.SPRITE_HEIGHT * c.SCALE) * 0.9
          obj = maps.get_object_at(check_x, check_y)
          if obj:
            target = obj.get("target_scene")
            # 魔女イベント入り口
            if obj.get("char_id") == "witch":
              if "新式の拳銃" in story.items:
                target = "witch_gun_choice"
              else:
                target = "witch_check_no_gun"
            elif obj.get("char_id") == "anna":
              if "古びた鍵" in story.items:
                target = "anna_after"
              else:
                target = "npc_anna"
            elif target == "door_locked":
              if "古びた鍵" in story.items:
                target = "door_open"

            if target:
              story.current_scene = target
              story.text_index = 0
              game_state = "DIALOGUE"
              visible_char_count = 0

    # --- インベントリ ---
    elif game_state == "INVENTORY":
      if event.type == pygame.KEYDOWN and event.key in [pygame.K_e, pygame.K_ESCAPE]:
        game_state = "EXPLORING"

    # --- エンディング画面 ---
    elif game_state == "ENDING":
      # Rキーでタイトルへ
      if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
        game_state = "TITLE"
        story.current_scene = "start_scene"
        story.text_index = 0
        visible_char_count = 0
        # アイテムリセット等はStoryManagerのinitが必要だが簡易的に
        story.items = []
        maps.load_map("town")
        player_pos = list(maps.get_spawn_pos())

  # ▼ ゲームロジック更新 ▼
  if game_state == "EXPLORING":
    keys = pygame.key.get_pressed()
    nx, ny = player_pos[0], player_pos[1]
    moving = False
    if keys[pygame.K_a]: nx -= player_speed; direction = 1; moving = True
    elif keys[pygame.K_d]: nx += player_speed; direction = 2; moving = True
    elif keys[pygame.K_w]: ny -= player_speed; direction = 3; moving = True
    elif keys[pygame.K_s]: ny += player_speed; direction = 0; moving = True

    f_w = (c.SPRITE_WIDTH * c.SCALE)
    f_h = (c.SPRITE_HEIGHT * c.SCALE)
    if not maps.is_wall(nx + f_w * 0.3, ny + f_h * 0.9) and not maps.is_wall(nx + f_w * 0.7, ny + f_h * 0.9):
      player_pos = [nx, ny]

    target_map = maps.check_transition(
        player_pos[0] + f_w / 2, player_pos[1] + f_h * 0.9)
    if target_map and target_map in maps.all_maps:
      maps.load_map(target_map)
      player_pos = list(maps.get_spawn_pos())

    if moving:
      anim_timer += 1
      if anim_timer >= 10: frame = (frame + 1) % 3; anim_timer = 0
    else: frame = 1

  # ▼ 描画処理 ▼
  if game_state == "TITLE":
    title_ui.draw(screen)

  elif game_state == "ENDING":
    screen.fill((0, 0, 0))  # 背景は黒

    # エンディングごとの設定
    # シーンID: {タイトル, サブタイトル, 色}
    ending_config = {
        "end_1_bad_helpless": {
            "title": "BAD ENDING",
            "sub": "無力な最期",
            "color": (200, 50, 50)  # 赤
        },
        "end_2_pure_peace": {
            "title": "TRUE ENDING A",
            "sub": "純粋な和解",
            "color": (150, 255, 255)  # 水色
        },
        "end_3_ruthless_kill": {
            "title": "NORMAL ENDING",
            "sub": "冷徹な仕事",
            "color": (180, 180, 180)  # グレー
        },
        "end_4_tragic_kill": {
            "title": "BAD ENDING",
            "sub": "拭えない後悔",
            "color": (150, 100, 200)  # 紫
        },
        "end_5_true_peace": {
            "title": "TRUE ENDING B",
            "sub": "真の探偵",
            "color": (255, 215, 0)  # 金色
        }
    }

    # 現在のシーンIDから設定を取得
    current_end = ending_config.get(story.current_scene, {
        "title": "THE END",
        "sub": "...",
        "color": c.WHITE
    })

    # タイトル描画
    title_surf = font_huge.render(
        current_end["title"], True, current_end["color"])
    screen.blit(title_surf, (c.SCREEN_WIDTH // 2 -
                title_surf.get_width() // 2, 200))

    # サブタイトル描画
    sub_surf = font_title.render(f"- {current_end['sub']} -", True, c.WHITE)
    screen.blit(sub_surf, (c.SCREEN_WIDTH // 2 -
                sub_surf.get_width() // 2, 320))

    # リスタート案内
    restart_text = font_main.render(
        "Press R to Title", True, (100, 100, 100))
    screen.blit(restart_text, (c.SCREEN_WIDTH // 2 -
                restart_text.get_width() // 2, 500))

  else:
    # 暗転演出 (銃殺エンドの会話中のみ)
    if story.current_scene in ["end_3_ruthless_kill", "end_4_tragic_kill"]:
      screen.fill((0, 0, 0))
    else:
      # 通常描画
      maps.draw(screen)
      debug_tool.draw_debug_info(screen, maps)
      debug_tool.draw_grid(screen)
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

    # UI描画
    if game_state == "DIALOGUE":
      draw_dialogue_ui()
    elif game_state == "INVENTORY":
      inventory_ui.draw(screen, story.items)
    elif game_state == "PAUSE":
      overlay = pygame.Surface(
          (c.SCREEN_WIDTH, c.SCREEN_HEIGHT), pygame.SRCALPHA)
      overlay.fill((0, 0, 0, 150))
      screen.blit(overlay, (0, 0))
      # ...ポーズメニューの描画...
      # (省略せずに描画するため既存コードを維持)
      menu_rect = pygame.Rect(
          c.SCREEN_WIDTH // 2 - 150, c.SCREEN_HEIGHT // 2 - 100, 300, 200)
      pygame.draw.rect(screen, (30, 30, 30), menu_rect)
      pygame.draw.rect(screen, (255, 255, 255), menu_rect, 3)
      title_text = font_title.render("PAUSE", True, c.WHITE)
      screen.blit(title_text, (c.SCREEN_WIDTH // 2 -
                  title_text.get_width() // 2, menu_rect.y + 20))
      txt_resume = font_main.render("[ESC] ゲームに戻る", True, c.WHITE)
      txt_title_p = font_main.render("[ T ] タイトルへ", True, c.WHITE)
      txt_quit = font_main.render("[ Q ] 終了する", True, c.RED)
      cx = c.SCREEN_WIDTH // 2
      sy = menu_rect.y + 80
      screen.blit(txt_resume, (cx - txt_resume.get_width() // 2, sy))
      screen.blit(
          txt_title_p, (cx - txt_title_p.get_width() // 2, sy + 40))
      screen.blit(txt_quit, (cx - txt_quit.get_width() // 2, sy + 80))

    # 座標表示
    pos_surf = font_main.render(
        f"X: {int(player_pos[0])} Y: {int(player_pos[1])}", True, (255, 255, 0))
    screen.blit(pos_surf, (c.SCREEN_WIDTH - pos_surf.get_width() - 20, 20))

  pygame.display.flip()
  clock.tick(c.FPS)
