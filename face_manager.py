import pygame
import os
import sys

# 顔グラフィックの表示サイズと位置
FACE_SIZE = (160, 160)
FACE_POS = (580, 280)

# ロードした画像を保持する辞書
_faces = {}

def init():
  """
  画像を直接読み込んで、すべてのキャラクターの顔グラフィックを
  あらかじめ FACE_SIZE にリサイズして辞書に保持します。
  """

  # exe化対応のパス取得
  if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
  else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

  # 登録したいキャラクター名
  char_names = ["main", "john", "monika", "anna", "witch", "erena"]

  for name in char_names:
    # ★修正: ファイル名のパターンを「○○_chara_face.png」に変更しました
    # 例: assets/images/john_chara_face.png
    filename = f"{name}_chara_face.png"
    img_path = os.path.join(base_dir, "assets", "images", filename)

    if os.path.exists(img_path):
      try:
        raw_img = pygame.image.load(img_path).convert_alpha()
        _faces[name] = pygame.transform.scale(raw_img, FACE_SIZE)
      except Exception as e:
        print(f"Error loading {name}: {e}")
    else:
      # 見つからない場合はログを出す
      print(f"顔画像が見つかりません: {filename}")

def draw(screen, face_id):
  if face_id in _faces:
    screen.blit(_faces[face_id], FACE_POS)
