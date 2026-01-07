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
  # これがあると home_map.py の配列のどこがどこか一目でわかります
  for row in range(c.SCREEN_HEIGHT // c.TILE_SIZE):
    for col in range(c.SCREEN_WIDTH // c.TILE_SIZE):
      label = font.render(f"{col},{row}", True, (120, 120, 120))
      screen.blit(label, (col * c.TILE_SIZE + 2, row * c.TILE_SIZE + 2))
