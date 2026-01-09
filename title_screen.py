# title_screen.py
import pygame
import constants as c

class TitleScreen:
  def __init__(self, font_title, font_main):
    self.font_title = font_title
    self.font_main = font_main

  def draw(self, screen):
    """タイトル画面の描画処理"""
    screen.fill(c.BLACK)

    # タイトル名（メイン）
    title_label = self.font_title.render("16世紀の探偵", True, c.WHITE)
    title_rect = title_label.get_rect(center=(c.SCREEN_WIDTH // 2, 200))
    screen.blit(title_label, title_rect)

    # サブタイトル
    subtitle_label = self.font_title.render("～屋敷の調査～", True, c.WHITE)
    subtitle_rect = subtitle_label.get_rect(
        center=(c.SCREEN_WIDTH // 2, 280))
    screen.blit(subtitle_label, subtitle_rect)

    # 操作ガイド
    start_label = self.font_main.render("SPACEキー または クリックで開始", True, c.RED)
    start_rect = start_label.get_rect(center=(c.SCREEN_WIDTH // 2, 450))
    screen.blit(start_label, start_rect)
