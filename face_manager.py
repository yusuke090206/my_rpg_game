# face_manager.py
import pygame
import image_manager

FACE_SIZE = (160, 160)
FACE_POS = (580, 280)

# 現在表示中の画像オブジェクトを保持
_current_img = None

def init():
  """
  image_manager を初期化して顔グラフィックをロードし、
  最初の顔をセットします。
  """
  image_manager.init()  # ここで顔グラフィック（face_main.png等）をロード
  set_face("main")      # 最初は主人公の顔を表示するよう予約

def set_face(char_name):
  """
  引数に 'main', 'john', 'anna' などを渡すと顔を切り替えます
  """
  global _current_img
  # image_manager が保持している辞書から画像を取得
  raw_img = image_manager.get(f"{char_name}_face")
  if raw_img:
    _current_img = pygame.transform.scale(raw_img, FACE_SIZE)
  else:
    _current_img = None

def draw(screen):
  if _current_img:
    screen.blit(_current_img, FACE_POS)
