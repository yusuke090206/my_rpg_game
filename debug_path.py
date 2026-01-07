# debug_path.py
import os

print("--- 診断開始 ---")
print(f"1. 現在の作業フォルダ (CWD): {os.getcwd()}")

# assetsフォルダがあるか確認
if os.path.exists("assets"):
  print("2. ✅ assets フォルダが見つかりました。")
  if os.path.exists("assets/images"):
    print("3. ✅ assets/images フォルダが見つかりました。")
    files = os.listdir("assets/images")
    print(f"4. images内のファイル一覧: {files}")

    target = "my_game_home.png"
    if target in files:
      print(f"5. ✨ 成功! '{target}' は正しい場所にあります。")
    else:
      print(f"5. ❌ 失敗! '{target}' が見つかりません。ファイル名を確認してください。")
  else:
    print("3. ❌ assets/images フォルダが見つかりません。")
else:
  print("2. ❌ assets フォルダ自体が見つかりません。")

print("--- 診断終了 ---")
