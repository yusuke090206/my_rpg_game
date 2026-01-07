# image_manager.py
import pygame
import os

# 読み込んだ画像を保存する辞書
assets = {}

def load_image(key, file_name):
  """
  画像を読み込んで辞書に保存する。
  失敗してもプログラムが止まらないようにエラーハンドリングを行う。
  """
  base_dir = os.path.dirname(os.path.abspath(__file__))
  # 画像ファイルへのフルパスを作成
  path = os.path.join(base_dir, "assets", "images", file_name)

  if os.path.exists(path):
    try:
      # convert_alpha() で透明度を有効にして読み込み
      img = pygame.image.load(path).convert_alpha()
      assets[key] = img
      print(f"DEBUG: [成功] {file_name} を '{key}' として読み込みました")
    except Exception as e:
      print(f"DEBUG: [失敗] {file_name} の読み込み中にエラー: {e}")
      assets[key] = None
  else:
    # ファイルが存在しない場合
    print(f"DEBUG: [未検出] {path} が見つかりません")
    assets[key] = None

def init():
  """
  ゲーム開始時に全てのキャラクター画像を一度に読み込む。
  """
  print("--- 画像リソースの初期化開始 ---")

  # キャラクター名のリスト（ここに追加すれば自動で読み込まれます）
  # あなたが指定した名前に合わせています
  characters = [
      "main",   # 探偵
      "john",   # ジョン
      "anna",   # アンナ
      "erena",  # エレナ
      "monika",  # モニカ
      "witch"   # 魔女
  ]

  for char in characters:
    # 1. 歩行グラフィックの読み込み (例: main_chara.png)
    # main.py で使う "main_sprite" という名前に合わせます
    load_image(f"{char}_sprite", f"{char}_chara.png")

    # 2. 顔グラフィックの読み込み (例: main_chara_face.png)
    # face_manager.py で使う "main_face" という名前に合わせます
    load_image(f"{char}_face", f"{char}_chara_face.png")

  print("--- 画像リソースの初期化完了 ---")

def get(key):
  """
  保存された画像をキー名で取得する。
  画像がない場合は None を返す。
  """
  return assets.get(key)
