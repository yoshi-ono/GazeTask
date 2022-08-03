import random
import sys
import pygame
from pygame.locals import *
import time

# 定数扱い
SURFACE = Rect(0, 0, 660, 660) # 画面サイズ(X軸,Y軸,横,縦)
F_RATE  = 60                   # フレームレート
RGB_WHITE = (255, 255, 255)

class BasicSprite(pygame.sprite.Sprite):
    """基本スプライト
    """
    def __init__(self, filename, x, y, size):
        pygame.sprite.Sprite.__init__(self)

        img = pygame.image.load(filename).convert_alpha()

        self.image = pygame.transform.scale(img, size)
        self.rect = Rect(x - self.w * 0.5, y - self.h * 0.5, self.w, self.h)

    @property
    def w(self):
        return self.image.get_width()

    @property
    def h(self):
        return self.image.get_height()

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect)

    def move(self, surface: pygame.Surface, pos):
        surface.blit(self.image, (pos[0] - self.w * 0.5, pos[1] - self.h * 0.5))
    
    def collide_pos(self, pos) -> bool:
        return self.rect.collidepoint(pos)

class TargetSprite(pygame.sprite.Sprite):
    """ターゲットスプライト

    手掛かり刺激

    ディスプレイを9等分した大きさ
    手掛かり刺激の表示はその中心
    """
    def __init__(self, filename, size, display_size):
        pygame.sprite.Sprite.__init__(self)
        
        self.target_rect = Rect(0, 0, display_size[0] / 3, display_size[1] / 3)

        img = pygame.image.load(filename).convert_alpha()

        self.image = pygame.transform.scale(img, size)
        self.image_rect = Rect(0, 0, self.iw, self.ih)

        self.direct_dic = { 1: (0, 0), 2: (220, 0), 3: (440, 0),
                            4: (0, 220), 5: (440, 220),
                            6: (0, 440), 7: (220, 440), 8: (440, 440) }
        self.direction = 1

    @property
    def iw(self):
        return self.image.get_width()

    @property
    def ih(self):
        return self.image.get_height()

    def set_direction(self):
        self.direction = random.randint(1, 8)

    def random_draw(self, surface: pygame.Surface):
        self.target_rect.x = self.direct_dic[self.direction][0]
        self.target_rect.y = self.direct_dic[self.direction][1]
        self.image_rect.x = self.target_rect.centerx - self.iw * 0.5
        self.image_rect.y = self.target_rect.centery - self.ih * 0.5
        surface.blit(self.image, self.image_rect)

    def collide_pos(self, pos) -> bool:
        return self.target_rect.collidepoint(pos)

############################
### メイン関数 
############################
def main():

    ### 画面初期化
    pygame.init()
    surface = pygame.display.set_mode(SURFACE.size)
    pygame.display.set_caption("GAZE TASK")              # タイトルバーに表示する文字

    ### スプライトを作成
    start_point = BasicSprite("blue.png", SURFACE.centerx, SURFACE.centery, (30, 30))
    gaze = BasicSprite("eye.png", 200, 200, (100, 50))
    target = TargetSprite("white.png", (20, 20), SURFACE.size)

    font = pygame.font.Font('IPAexfont00401\ipaexg.ttf', 20)               # フォントの設定

    ### 時間オブジェクト生成
    clock = pygame.time.Clock()

    reward = 0
    (x, y) = (0, 0)
    game_start = False
    time_past = 0.0
    pause_time = 0.0
    assist = False

    ### 無限ループ
    while True:

        ### フレームレート設定
        clock.tick(F_RATE)

        ### 背景色設定
        surface.fill((0,0,0))

        if (game_start):
            time_past = time.perf_counter() - time_start
        elif (start_point.collide_pos((x, y))):
            game_start = True
            time_start = time.perf_counter()
            target.set_direction()
        else:
            txt_start = font.render("視線（マウスカーソル）を注視点に合わせたらスタートです。", True, RGB_WHITE)
            surface.blit(txt_start, [SURFACE.centerx - txt_start.get_width() * 0.5, SURFACE.centery - 50])

        # 注視期間 (0.0 ~ 1.0)

        # 手がかり刺激期間 (1.0 ~ 1.5)
        if (1.0 <= time_past and time_past <= 1.5):
            target.random_draw(surface)

        # 遅延期間 (1.5 ~ 4.5)

        # 注視点表示 (~ 4.5)
        if (time_past < 4.5):
            start_point.draw(surface)

            if (game_start and not start_point.collide_pos((x, y))):
                txt_over = font.render("目を逸らしました", True, RGB_WHITE)
                surface.blit(txt_over, [SURFACE.centerx - txt_over.get_width() * 0.5, SURFACE.centery - 50])
                pause_time = 2.5
                
        # 終了
        elif (time_past > 5.0):
            txt_over = font.render("タイムオーバー", True, RGB_WHITE)
            surface.blit(txt_over, [SURFACE.centerx - txt_over.get_width() * 0.5, SURFACE.centery - 50])
            pause_time = 2.5

        # 反応期間 (4.5 ~ 5.0)
        else:
            if (target.collide_pos((x, y))):
                txt_reward = font.render("報酬 +1", True, RGB_WHITE)
                surface.blit(txt_reward, [SURFACE.centerx - txt_reward.get_width() * 0.5, SURFACE.centery - 50])
                reward += 1
                pause_time = 2.5

        # 視線
        gaze.move(surface, (x, y))

        txt_score = font.render("SCORE: " + str(reward), True, RGB_WHITE)
        surface.blit(txt_score, [440, 0])

        if (assist):
            txt_time = font.render("{:.1f}".format(time_past), True, RGB_WHITE)
            surface.blit(txt_time, [0, 0])

            pygame.draw.line(surface, RGB_WHITE, (0, 220), (660, 220), 1)
            pygame.draw.line(surface, RGB_WHITE, (0, 440), (660, 440), 1)
            pygame.draw.line(surface, RGB_WHITE, (220, 0), (220, 660), 1)
            pygame.draw.line(surface, RGB_WHITE, (440, 0), (440, 660), 1)

        ### 画面更新
        pygame.display.update()

        # 次のゲーム
        if (pause_time > 0.0):
            time.sleep(pause_time)

            (x, y) = (0, 0)
            game_start = False
            time_past = 0.0
            pause_time = 0.0

        ### イベント処理
        for event in pygame.event.get():
            if (event.type == MOUSEMOTION):
                x, y = event.pos
            ### 終了処理
            if event.type == QUIT:
                exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    exit()
                elif event.key == K_a:
                    if (assist):
                        assist = False
                    else:
                        assist = True

############################
### 終了関数
############################
def exit():
    pygame.quit()
    sys.exit()

############################
### メイン関数呼び出し
############################
if __name__ == "__main__":

    ### 処理開始
    main()
