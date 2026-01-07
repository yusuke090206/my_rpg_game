# inventory.py
import pygame
import constants as c

class InventoryUI:
  def __init__(self, font):
    self.font = font

  def draw(self, screen, items):
    # 背景の半透明レイヤー
    overlay = pygame.Surface(
        (c.SCREEN_WIDTH, c.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # 黒の半透明
    screen.blit(overlay, (0, 0))

    # インベントリの枠
    rect = pygame.Rect(100, 50, 600, 500)
    pygame.draw.rect(screen, c.BLACK, rect)
    pygame.draw.rect(screen, c.WHITE, rect, 3)

    # 見出し
    title_surf = self.font.render("--- 所持品 (E/ESCで閉じる) ---", True, c.WHITE)
    screen.blit(title_surf, (c.SCREEN_WIDTH // 2 -
                title_surf.get_width() // 2, 80))

    # アイテムリストの表示
    if not items:
      empty_surf = self.font.render("何も持っていない...", True, c.GRAY)
      screen.blit(empty_surf, (150, 150))
    else:
      for i, item in enumerate(items):
        item_surf = self.font.render(f"・ {item}", True, c.WHITE)
        screen.blit(item_surf, (150, 150 + i * 40))
