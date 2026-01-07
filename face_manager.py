# face_manager.py
import pygame
import image_manager

FACE_SIZE = (160, 160)
FACE_POS = (580, 280)

# 現在表示中の画像オブジェクトを保持
_current_img = None

def set_face(char_name):
  """
  引数に 'main', 'john', 'anna' などを渡すと顔を切り替えます
  """
  global _current_img
  raw_img = image_manager.get(f"{char_name}_face")
  if raw_img:
    _current_img = pygame.transform.scale(raw_img, FACE_SIZE)
  else:
    _current_img = None

def draw(screen):
  if _current_img:
    screen.blit(_current_img, FACE_POS)
