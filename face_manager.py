# face_manager.py
import pygame
import os
import image_manager

# 顔グラフィックの表示サイズと位置
FACE_SIZE = (160, 160)
# 会話ウィンドウの右側に表示する設定（580, 280）
FACE_POS = (580, 280)

# ロードした画像を保持する辞書
_faces = {}

def init():
  """
  image_manager を初期化し、すべてのキャラクターの顔グラフィックを
  あらかじめ FACE_SIZE にリサイズして辞書に保持します。
  """
  image_manager.init()

  # 登録したいキャラクター名のリスト
  char_names = ["main", "john", "monika", "anna"]

  for name in char_names:
    # image_manager から元画像を取得 (例: john_face)
    raw_img = image_manager.get(f"{name}_face")
    if raw_img:
      # あらかじめリサイズして保存（描画時の負荷を減らす）
      _faces[name] = pygame.transform.scale(raw_img, FACE_SIZE)
    else:
      print(f"Warning: {name}_face の読み込みに失敗しました。")

def draw(screen, face_id):
  """
  main.py から渡された face_id に基づいて顔を表示します。
  """
  if face_id in _faces:
    screen.blit(_faces[face_id], FACE_POS)
