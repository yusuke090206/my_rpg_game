import pygame

class StoryManager:
  def __init__(self):
    self.current_scene = "start_scene"
    self.text_index = 0
    self.items = []  # 所持アイテムリスト

    self.scenes = {
        # --- オープニング ---
        "start_scene": {
            "text": [
                "少し昔のとある世界のとある街。",
                "あなたは５年前事故で記憶を失ってしまい生き別れた妻、エレナを探すために探偵業を始めた。",
            ],
            "face_id": None,
            "type": "normal",
            "next": "intro"
        },
        "intro": {
            "text": [
                "記憶を失ってから長いこと経ったけど探偵業も板についてきたな",
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
            "text": ["この依頼、引き受けようか？"],
            "type": "choice",
            "choices": {"Y": "accept", "N": "stay"}
        },
        "accept": {
            "text": [
                "……よし、屋敷へ向かうとしよう。準備を整えるか。",
                "行方不明の人もいるらしいね",
                "気を付けよう。"
            ],
            "type": "normal",
            "face_id": "main",
            "next": None  # マップへ
        },
        "stay": {
            "text": ["怪しい依頼は断ろう。この依頼は受けない。"],
            "type": "normal",
            "next": None,
            "face_id": "main",
            "is_ending": True,  # ゲームオーバー扱い
        },

        # --- 探索イベント ---
        "desk_investigation": {
            "text": [
                "机の上に、一枚の写真が置かれている。",
                "妻との写真だ…。",
            ],
            "face_id": "main",
            "type": "normal",
            "next": "photo_choice",
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
            "text": [
                "こんなところに指輪がある。後で持ち主を探そう。",
                "彼女にも似たような指輪をあげたような気がするな"
            ],
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

        # --- NPCイベント ---
        "npc_guard": {
            "text": [
                "あんたも屋敷の調査に来たのか？",
                "俺はジョン。よろしくな。",
                "鍵が欲しいなら、あの娘らに頼んでみるといいぞ。",
                "中に入ったら左下の部屋から順に反時計回りに見てみるといい。",
                "そして最後に右下の部屋を見ればいい。",
                "俺はまだ庭を見て回るからな。",
                "中から出てこなかった連中もいる気をつけろよ。",
            ],
            "face_id": "john",
            "type": "normal",
            "next": "john_after"
        },
        "john_after": {
            "text": ["ありがとうございます",],
            "face_id": "main",
            "type": "normal",
            "next": None
        },
        "npc_anna": {
            "text": [
                "あなたも屋敷の調査に来たの？",
                "あたしはアンナ。よろしくね。",
                "その子はモニカっていうらしいわ。",
            ],
            "face_id": "anna",
            "type": "normal",
            "next": "monika_intro"
        },
        "monika_intro": {
            "text": [
                "お、おねがします。",
            ],
            "face_id": "monika",
            "type": "normal",
            "next": "anna_give_key"
        },
        "anna_give_key": {
            "text": [
                "鍵がいるんでしょ？",
                "これ、使って。"
            ],
            "face_id": "anna",
            "type": "normal",
            "give_item": "古びた鍵",
            "next": None
        },
        "anna_after": {
            "text": ["頑張って何か探しましょう。"],
            "face_id": "anna",
            "type": "normal",
            "next": None
        },

        # --- 屋敷内のイベント ---
        "npc_erena": {
            "type": "normal",
            "text": [
                "あら、見ない顔ね。",
                "この屋敷、夜になると不思議な音がするのよ..."
            ],
            "face_id": "erena",
            "next": None
        },
        "door_locked": {
            "text": ["（扉は固く閉ざされている。鍵が必要なようだ……。）"],
            "face_id": None,
            "type": "normal",
            "next": None
        },
        "door_open": {
            "text": ["（鍵を使った！ 扉が開いた。）"],
            "face_id": None,
            "type": "normal",
            "next": None,
            "is_door_open": True
        },
        "mansion_flower": {
            "text": [
                "この花は…",
                "彼女が好きだった花だ。摘んでいこう。",
                "……？",
                "なんだか彼女についての記憶が戻ってきた気がする。",
            ],
            "face_id": "main",
            "type": "normal",
            "next": None,
            "give_item": "美しい花"
        },
        "pistol": {
            "text": [
                "こんなところに拳銃？",
                "必要になることがあるかもしれない。持っていこう。",
            ],
            "face_id": "main",
            "type": "normal",
            "next": None,
            "give_item": "新式の拳銃"  # スペースを削除しました
        },
        "huhu_picture": {
            "text": [
                "この写真…",
                "家にあるのと同じ夫婦写真だ。",
                "なんでここに…？",
                "大事な何かが思い出せそうな気がする。",
            ],
            "face_id": "main",
            "type": "normal",
            "next": None,
            "give_item": "同じ夫婦写真"
        },
        "piano_sheet_music": {
            "text": [
                "この楽譜…",
                "妻がよく弾いていた曲だ。",
                "思い出が蘇ってくる。",
            ],
            "face_id": "main",
            "type": "normal",
            "next": None,
            "give_item": "楽譜"
        },
        "john_inside": {
            "text": [
                "この先は荷物があって通れないみたいだ。",
                "おとなしく４つの部屋を調べよう。"
            ],
            "face_id": "john",
            "type": "normal",
            "next": None
        },
        "anna_inside": {
            "text": [
                "思ってたより広いのね…",
                "あたし、頑張って調べてみるわ。",
                "あんたもこの隣の部屋から順に調べていくのよ。"
            ],
            "face_id": "anna",
            "type": "normal",
            "next": None
        },
        "monika_inside": {
            "text": [
                "役に立たないけど…が、頑張ります",
            ],
            "face_id": "monika",
            "type": "normal",
            "next": "monika_after"
        },
        "monika_after": {
            "text": [
                "うん。気を付けてね。",
            ],
            "face_id": "main",
            "type": "normal",
            "next": None
        },

        # --- 魔女イベント制御用 ---
        "witch_check_no_gun": {"type": "normal", "text": ["..."]},
        "witch_check_shoot": {"type": "normal", "text": ["..."]},
        "witch_check_spare": {"type": "normal", "text": ["..."]},

        "witch_gun_choice": {
            "type": "choice",
            "text": [
                "魔女はあなたをじっと見つめている。"
                "懐には「新式の拳銃」がある..."
                "撃ちますか？",
            ],
            "choices": {
                "Y": "witch_check_shoot",
                "N": "witch_check_spare"
            },
            "face_id": None,
        },

        # --- エンディング 1: 持ち物なし・銃なし（殺される） ---
        "end_1_bad_helpless": {
            "type": "normal",
            "text": [
                "今更何しに来たの？",
            ],
            "face_id": "witch",
            "next": "end_1_bad_helpless_2"
        },
        "end_1_bad_helpless_2": {
            "type": "normal",
            "text": [
                "魔女は冷たくそう言うと、あなたに近づいてきた。",
                "魔女の手があなたの喉元に伸びる。",
            ],
            "face_id": None,
            "next": "end_1_bad_helpless_3"
        },
        "end_1_bad_helpless_3": {
            "type": "normal",
            "text": [
                "君は誰なんだい？"
            ],
            "is_ending": True,
            "face_id": "main",
            "next": None
        },

        # --- エンディング 2: 持ち物あり・銃なし（助かる） ---
        "end_2_pure_peace": {
            "type": "normal",
            "text": [
                "君なんだろう？",
                "ねぇエレナ",
                "すべて思い出せたよ。",
            ],
            "is_ending": True,  # ここからエンディング演出開始
            "face_id": "main",
            "next": "end_2_pure_peace_2"
        },
        "end_2_pure_peace_2": {
            "type": "normal",
            "text": [
                "やっと思い出してくれたのね。",
                "ありがとう……あなた。",
                "でも私はもう人として生きていけないわ。",
                "さよなら、あなた。",
            ],
            "face_id": "witch",
            "next": "end_2_pure_peace_3"
        },
        "end_2_pure_peace_3": {
            "type": "normal",
            "text": [
                "………",
                "彼女は静かに微笑んで、あなたの手を握った。",
            ],
            "face_id": None,
            "next": "end_2_pure_peace_4"
        },
        "end_2_pure_peace_4": {
            "type": "normal",
            "text": [
                "僕のせいだね。",
            ],
            "face_id": "main",
            "next": "end_2_pure_peace_5"
        },
        "end_2_pure_peace_5": {
            "type": "normal",
            "text": [
                "いいえ、違うわ。",
                "私たちのせいよ。",
                "来世ではきっと幸せになりましょうね。",
            ],
            "face_id": "erena",
            "next": "end_2_pure_peace_6"
        },
        "end_2_pure_peace_6": {
            "type": "normal",
            "text": [
                "あぁ、そうだね。",
                "必ず君を迎えに行くよ。",
                "どれだけかかってもね。",
            ],
            "face_id": "main",
            "next": "end_2_pure_peace_7"
        },
        "end_2_pure_peace_7": {
            "type": "normal",
            "text": [
                "ふふっ、楽しみに待ってるわ。",
            ],
            "face_id": "erena",
            "next": "end_2_pure_peace_8"
        },
        "end_2_pure_peace_8": {
            "type": "normal",
            "text": [
                "彼女は息を引き取った。",
            ],
            "is_ending": True,
            "face_id": None,
            "next": None
        },

        # --- エンディング 3: 持ち物なし・銃で撃つ（殺害） ---
        "end_3_ruthless_kill": {
            "type": "normal",
            "text": [
                "引き金を引いた。",
                "BAN!",
                "銃声が響き渡る。",
            ],
            "is_ending": True,
            "next": "end_3_ruthless_kill_2",
        },
        "end_3_ruthless_kill_2": {
            "type": "normal",
            "text": [
                "あなたならそうすると思ってたわ"
            ],
            "face_id": "witch",
            "next": "end_3_ruthless_kill_3"
        },
        "end_3_ruthless_kill_3": {
            "type": "normal",
            "text": [
                "あなたならってどういうことだ？"
            ],
            "face_id": "main",
            "is_ending": True,
            "next": None,
        },

        # --- エンディング 4: 持ち物あり・銃で撃つ（後悔） ---
        "end_4_tragic_kill": {
            "type": "normal",
            "text": [
                "BAN!",
                "銃声が響き渡る。",
            ],
            "is_ending": True,
            "face_id": None,
            "next": "end_4_tragic_kill_2"
        },
        "end_4_tragic_kill_2": {
            "type": "normal",
            "text": [
                "あぁ……撃ったのね",
                "あなたならそうすると思ってたわ。"
            ],
            "face_id": "witch",
            "next": "end_4_tragic_kill_3"
        },
        "end_4_tragic_kill_3": {
            "type": "normal",
            "text": [
                "君を魔女として生かしておくつもりはないよ",
                "僕は誰より君を愛しているのだから",
            ],
            "face_id": "main",
            "next": "end_4_tragic_kill_4"
        },
        "end_4_tragic_kill_4": {
            "type": "normal",
            "text": [
                "5年ぶりに愛してるって言ってくれたわね……",
                "すごく……うれしい"
            ],
            "face_id": "erena",
            "next": "end_4_tragic_kill_5"
        },
        "end_4_tragic_kill_5": {
            "type": "normal",
            "text": [
                "君のためなら……",
                "何度でも言ってあげるさ。",
            ],
            "is_ending": True,
            "face_id": "main",
            "next": None,
        },

        # --- エンディング 5: 持ち物あり・銃を持ちつつ撃たない（完全和解） ---
        "end_5_true_peace": {
            "type": "normal",
            "text": [
                "君なんだろう？",
                "ねぇエレナ",
                "やっと思い出せたよ。",
            ],
            "is_ending": True,
            "face_id": "main",
            "next": "end_5_true_peace_2"
        },
        "end_5_true_peace_2": {
            "type": "normal",
            "text": [
                "やっと思い出してくれたのね。",
                "ありがとう……あなた。",
                "何度迎えに来てくれることを願ったかしれない。",
                "でも私はもう表では生きていけないわ。",
                "さよなら、愛しい人。",
            ],
            "face_id": "witch",
            "next": "end_5_true_peace_3"
        },
        "end_5_true_peace_3": {
            "type": "normal",
            "text": [
                "関係ない",
                "僕たちならやり直せるさ。",
                "さあ、帰ろう。",
            ],
            "face_id": "main",
            "next": "end_5_true_peace_4"
        },
        "end_5_true_peace_4": {
            "type": "normal",
            "text": [
                "………",
                "そうね…ありがとう、あなた。",
                "さあ、行きましょう。",
            ],
            "face_id": "erena",
            "next": "end_5_true_peace_5"
        },
        "end_5_true_peace_5": {
            "type": "normal",
            "text": [
                "あぁ、行こう。"
            ],
            "is_ending": True,
            "face_id": "main",
            "next": None
        },
    }

  def get_current_scene_data(self):
    if not self.current_scene or self.current_scene not in self.scenes:
      # エラー防止用のダミー
      return {
          "text": ["（ここには特に何もなさそうだ……）"],
          "face_id": None,
          "type": "normal",
          "next": None
      }
    return self.scenes[self.current_scene]

  def get_current_text(self):
    data = self.get_current_scene_data()
    if self.text_index < len(data["text"]):
      return data["text"][self.text_index]
    return ""

  def next_step(self):
    scene = self.get_current_scene_data()
    self.text_index += 1

    # 現在のセリフがまだ残っている場合
    if self.text_index < len(scene["text"]):
      return True

    # セリフが終わった場合 -> next があれば次のシーンへ自動遷移
    if scene.get("next"):
      self.current_scene = scene["next"]
      self.text_index = 0
      return True

    # next が None の場合 -> 会話終了（マップに戻る or エンディング画面へ）
    return False
