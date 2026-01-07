# map_manager.py (完全版)
import pygame
import constants as c
import os
from maps import home_map

class MapManager:
  def __init__(self):
    self.all_maps = {"home": home_map.DATA}
    self.current_map_key = "home"
    self.bg_image = None
    self.load_map(self.current_map_key)

  def load_map(self, map_key):
    self.current_map_key = map_key
    map_data = self.all_maps[map_key]

    # 実行中のスクリプトがあるディレクトリを取得
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # ファイル名を png に固定してパスを作成
    img_path = "assets/images/my_game_home.png"
    full_path = os.path.normpath(os.path.join(base_dir, img_path))

    print(f"DEBUG: 読み込み試行 -> {full_path}")

    if os.path.exists(full_path):
      try:
        self.bg_image = pygame.image.load(full_path).convert()
        self.bg_image = pygame.transform.scale(
            self.bg_image, (c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
        print("DEBUG: ✅ 背景画像の読み込みに成功しました！")
      except Exception as e:
        print(f"DEBUG: ❌ 読み込みエラー: {e}")
        self.bg_image = None
    else:
      print(f"DEBUG: ❌ 指定された場所に画像がありません: {full_path}")
      self.bg_image = None

  def get_spawn_pos(self):
    return self.all_maps[self.current_map_key]["spawn_pos"]

  def is_wall(self, x, y):
    col, row = int(x // c.TILE_SIZE), int(y // c.TILE_SIZE)
    collision = self.all_maps[self.current_map_key]["collision"]
    if 0 <= row < len(collision) and 0 <= col < len(collision[0]):
      return collision[row][col] == 1
    return True

  def draw(self, screen):
    if self.bg_image:
      screen.blit(self.bg_image, (0, 0))
    else:
      screen.fill((100, 100, 100))  # 失敗時は灰色
