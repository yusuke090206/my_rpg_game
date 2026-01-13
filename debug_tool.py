# debug_tool.py
import pygame
import constants as c

def draw_grid(screen):
  """タイルサイズに基づいたグリッド線と座標を表示する"""
  grid_color = (100, 100, 100)  # グレー
  font = pygame.font.SysFont(None, 18)

  # 垂直線の描画
  for x in range(0, c.SCREEN_WIDTH, c.TILE_SIZE):
    pygame.draw.line(screen, grid_color, (x, 0), (x, c.SCREEN_HEIGHT))

  # 水平線の描画
  for y in range(0, c.SCREEN_HEIGHT, c.TILE_SIZE):
    pygame.draw.line(screen, grid_color, (0, y), (c.SCREEN_WIDTH, y))

  # 座標番号の表示 (col, row)
  for row in range(c.SCREEN_HEIGHT // c.TILE_SIZE):
    for col in range(c.SCREEN_WIDTH // c.TILE_SIZE):
      label = font.render(f"{col},{row}", True, (120, 120, 120))
      screen.blit(label, (col * c.TILE_SIZE + 2, row * c.TILE_SIZE + 2))

def draw_debug_info(screen, maps):
  """マップ移動ポイントとオブジェクトの判定範囲を可視化する"""
  # 現在のマップデータを取得
  current_map = maps.all_maps[maps.current_map_key]

  # --- 1. マップ移動ポイント (exits) を赤色で表示 ---
  if "exits" in current_map:
    for trans in current_map["exits"]:
      rect = trans["rect"]
      # 半透明の赤色の面を描画
      overlay = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
      overlay.fill((255, 0, 0, 80))  # (赤, 緑, 青, 透明度)
      screen.blit(overlay, (rect[0], rect[1]))
      # 枠線
      pygame.draw.rect(screen, (255, 0, 0), rect, 2)

  # --- 2. 調査・会話オブジェクト (objects) を水色で表示 ---
  if "objects" in current_map:
    for obj in current_map["objects"]:
      rect = obj["rect"]
      # 枠線のみ表示
      pygame.draw.rect(screen, (0, 255, 255), rect, 2)
