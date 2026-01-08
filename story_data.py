# story_data.py
class StoryManager:
  def __init__(self):
    self.scenes = {
        "intro": {
            "text": [
                "暖かい春の日だ。机には一通の依頼状が届いている。",
                "送り主は不明だ。"
            ],
            "type": "normal",
            "next": "choice_scene"
        },
        "choice_scene": {
            "text": ["この依頼、引き受けて屋敷へ向かうか？"],
            "type": "choice",
            "choices": {"Y": "accept", "N": "stay"}
        },
        "accept": {
            "text": ["「……よし、屋敷へ向かうとしよう。準備を整えるか。」"],
            "type": "normal",
            "next": None
        },
        "stay": {
            "text": ["「今はもう少し、この部屋で考えを整理したい……。」"],
            "type": "normal",
            "next": None
        }
    }
    self.current_scene = "intro"
    self.text_index = 0
    self.items = []

  def get_current_scene_data(self):
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
