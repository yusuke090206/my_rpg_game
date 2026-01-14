# image_manager.py
import pygame
import os

assets = {}

def load_image(key, file_name):
  # 実行ファイルの場所を基準に assets/images を探す
  base_dir = os.path.dirname(os.path.abspath(__file__))
  path = os.path.join(base_dir, "assets", "images", file_name)

  if os.path.exists(path):
    try:
      img = pygame.image.load(path).convert_alpha()
      assets[key] = img
      return img
    except Exception as e:
      print(f"ERROR: {file_name} の読み込みに失敗: {e}")
  else:
    print(f"WARNING: ファイルが見つかりません: {path}")
  assets[key] = None
  return None

def get(key):
  return assets.get(key)

def init():
  """
  あなたの main.py が使うキー "main_sprite"
  および face_manager が使う "main_face" 等を読み込む
  """
  # 1. 操作キャラクタースプライト
  load_image("main_sprite", "main_sprite.png")

  # 2. 顔グラフィック
  load_image("main_face", "main_chara_face.png")
  load_image("john_face", "john_chara_face.png")
  load_image("anna_face", "anna_chara_face.png")
  load_image("monika_face", "monika_chara_face.png")
  load_image("witch_face", "witch_chara_face.png")
  load_image("erena_face", "erena_chara_face.png")
