import pygame
import os
import constants as c
from maps import home_map, mansion_inside, mansion_out, town_map, forest_map, piano_room, syokutaku, monooki, sinsitu

class MapManager:
  def __init__(self):
    # マップデータの登録
    self.all_maps = {
        "home": getattr(home_map, 'DATA', {}),
        "town": getattr(town_map, 'DATA', {}),
        "forest": getattr(forest_map, 'DATA', {}),
        "mansion_out": getattr(mansion_out, 'DATA', {}),
        "mansion_inside": getattr(mansion_inside, 'DATA', {}),
        "piano_room": getattr(piano_room, 'DATA', {}),
        "syokutaku": getattr(syokutaku, 'DATA', {}),
        "monooki": getattr(monooki, 'DATA', {}),
        "sinsitu": getattr(sinsitu, 'DATA', {}),
    }
    self.current_map_key = "home"
    self.bg_image = None
    self.load_map("home")

  def load_map(self, map_key):
    if map_key not in self.all_maps:
      return

    self.current_map_key = map_key
    data = self.all_maps[map_key]

    # ファイル名だけを取り出す（パスの二重化防止）
    img_name = os.path.basename(data.get("img_path", ""))

    base_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(base_dir, "assets", "images", img_name)

    if os.path.exists(img_path):
      try:
        raw_img = pygame.image.load(img_path).convert()
        self.bg_image = pygame.transform.scale(
            raw_img, (c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
      except:
        self.bg_image = None
    else:
      self.bg_image = None

  def get_spawn_pos(self):
    map_data = self.all_maps.get(self.current_map_key, {})
    return map_data.get("spawn_pos", [400, 300])

  def is_wall(self, x, y):
    col, row = int(x // c.TILE_SIZE), int(y // c.TILE_SIZE)
    collision = self.all_maps[self.current_map_key].get("collision", [])
    if 0 <= row < len(collision) and 0 <= col < len(collision[0]):
      return collision[row][col] == 1
    return False

  def check_transition(self, x, y):
    exits = self.all_maps[self.current_map_key].get("exits", [])
    for ex in exits:
      if pygame.Rect(ex["rect"]).collidepoint(x, y):
        return ex["target"]
    return None

  def draw(self, screen):
    if self.bg_image:
      screen.blit(self.bg_image, (0, 0))
    else:
      screen.fill((100, 0, 0))  # 背景がない時は暗い赤

  def get_object_at(self, x, y):
    data = self.all_maps.get(self.current_map_key, {})
    objects = data.get("objects", [])
    for obj in objects:
      # 判定を少し広め(inflate)にして調べやすくする
      rect = pygame.Rect(obj["rect"]).inflate(20, 20)
      if rect.collidepoint(x, y):
        return obj
    return None
