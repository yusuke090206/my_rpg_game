# story_data.py
class StoryManager:
  def __init__(self):
    self.scenes = {
        "start_scene": {
            "text": [
                "少し昔のとある世界のとある街。",
                "あなたは５年前事故で記憶を失ってしまい生き別れた妻を探すために探偵業を始めた。",
            ],
            "face_id": "main",
            "type": "normal",
            "next": "intro"
        },
        "intro": {
            "text": [
                "記憶を失ってから長いこと立ったけど探偵業も板についてきたな",
                "まだ妻は見つけられてないんだけど…",
                "新しい依頼だ。",
                "？この依頼書…",
                "送り主が書かれてないな。",
                "報酬は前払いされているけど",
                "受けるも受けないもあなた次第…か",
            ],
            "face_id": "main",
            "type": "normal",
            "next": "choice_scene"
        },
        "choice_scene": {
            "text": ["この依頼、引き受けて屋敷へ向かうか？"],
            "type": "choice",
            "choices": {"Y": "accept", "N": "stay"}
        },
        "accept": {
            "text": ["……よし、屋敷へ向かうとしよう。準備を整えるか。"],
            "type": "normal",
            "face_id": "main",
            "next": None
        },
        "stay": {
            "text": ["怪しい依頼は断ろう。この依頼は受けない。"],
            "type": "normal",
            "next": None,
            "face_id": "main",
            "is_ending": True,
        },

        "desk_investigation": {
            "text": [
                "机の上に、一枚の写真が置かれている。",
                "妻との写真だ…。",
            ],
            "face_id": "main",
            "type": "normal",
            "next": "photo_choice",
            "is_ending": False
        },
        "photo_choice": {
            "text": ["この写真を持っていきますか？"],
            "face_id": "main",
            "type": "choice",
            "choices": {"Y": "get_photo", "N": "leave_photo"}
        },
        "get_photo": {
            "text": ["何か妻の手がかりがあるかもしれないしな。持っていこう。"],
            "face_id": "main",
            "type": "normal",
            "next": None,
            "give_item": "夫婦写真"
        },
        "leave_photo": {
            "text": ["今回は必要ないだろう"],
            "face_id": "main",
            "type": "normal",
            "next": None
        },
        "bakery": {
            "text": [
                "おなかもすいたしパンを買っていこうかな。",
                "店員さん。これお願いします。",
                "……",
                "もぐもぐ…おいしい!",
                "でもこの味…どこかで食べたことある気がするな。",
            ],
            "face_id": "main",
            "type": "normal",
            "next": None,
            "give_item": "懐かしいパン"
        },
        "forest": {
            "text": [
                "こんなところに指輪の落とし物だ。一度持っていこうか？"
            ],
            "face_id": "main",
            "type": "choice",
            "choices": {"Y": "get_ring", "N": "leave_ring"}
        },
        "get_ring": {
            "text": ["こんなところに指輪がある。後で持ち主を探そう。"],
            "face_id": "main",
            "type": "normal",
            "next": None,
            "give_item": "指輪"
        },
        "leave_ring": {
            "text": ["指輪はそのままにしておこう。"],
            "face_id": "main",
            "type": "normal",
            "next": None
        },
        # --- story_data.py 50行目付近 ---
        "npc_guard": {  # これをジョン（門番）にします
            "text": ["ジョン：貴様、何用だ。ここは許可なき者は通さん。", "（……厳重に警備されているようだ）"],
            "face_id": "john",  # face_managerに登録した名前
            "type": "normal",
            "next": None
        },
        "npc_gardener": {  # これをモニカ（庭師）にします
            "text": ["モニカ：この屋敷のバラは、主人の誇りでしてね。", "……おや、あんた、どこかで見た顔だな？"],
            "face_id": "monika",
            "type": "normal",
            "next": None
        },
        "npc_stranger": {  # これをアンナ（怪しい女）にします
            "text": ["アンナ：フフフ……。あんたも『真実』を探しに来たのかい？", "あの中には、触れてはならぬ過去が眠っておるぞ。"],
            "face_id": "anna",
            "type": "normal",
            "next": None
        }

    }

    self.current_scene = "start_scene"
    self.text_index = 0
    self.items = []

  # story_data.py の 135行目付近

  def get_current_scene_data(self):
      # もし current_scene が空、または scenes に存在しない名前なら
    if not self.current_scene or self.current_scene not in self.scenes:
      # 安全のために最初のシーンを返す、もしくはダミーを返す
      print(
          f"Warning: Scene '{self.current_scene}' not found. Redirecting to start.")
      self.current_scene = "start_scene"

    return self.scenes[self.current_scene]

  def get_current_text(self):
    return self.scenes[self.current_scene]["text"][self.text_index]

  def next_step(self):
    scene = self.scenes[self.current_scene]
    self.text_index += 1
    if self.text_index >= len(scene["text"]):
      if scene.get("next"):
        self.current_scene = scene["next"]
        self.text_index = 0
        return True
      else:
        return False
    return True
