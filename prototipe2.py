import pygame
import random
import math

# Resolusi rendah untuk efek pixel art
LOW_RES_WIDTH = 320
LOW_RES_HEIGHT = 240

# Warna
COLOR_BG = (40, 30, 45)
COLOR_PADDLE = (230, 200, 170)
COLOR_BALL = (255, 160, 122)
COLOR_TEXT = (240, 230, 220)
COLOR_AI_PADDLE = (180, 220, 255)

# Konstanta Game
PADDLE_WIDTH = 4
PADDLE_HEIGHT = 40  
BALL_RADIUS = 4     
PADDLE_SPEED = 2.5  
BALL_SPEED = 1.5
WINNING_SCORE = 5

class PongGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((LOW_RES_WIDTH, LOW_RES_HEIGHT))
        pygame.display.set_caption('Cozy Pixel Pong')
        self.clock = pygame.time.Clock()
        
        # Font
        self.font = pygame.font.Font(None, 16)
        
        # Objek game
        self.player = pygame.Rect(15, LOW_RES_HEIGHT//2 - PADDLE_HEIGHT//2, 
                                PADDLE_WIDTH, PADDLE_HEIGHT)
        self.ai = pygame.Rect(LOW_RES_WIDTH - 15 - PADDLE_WIDTH, 
                            LOW_RES_HEIGHT//2 - PADDLE_HEIGHT//2,
                            PADDLE_WIDTH, PADDLE_HEIGHT)
        self.ball = pygame.Rect(LOW_RES_WIDTH//2 - BALL_RADIUS, 
                              LOW_RES_HEIGHT//2 - BALL_RADIUS,
                              BALL_RADIUS*2, BALL_RADIUS*2)
        
        # Variabel game
        self.ball_vel = [0, 0]
        self.player_score = 0
        self.ai_score = 0
        self.difficulty = 2  # 1-3 (easy-hard)
        self.reset_ball()
    
    def reset_ball(self):
        self.ball.center = (LOW_RES_WIDTH//2, LOW_RES_HEIGHT//2)
        self.ball_vel = [random.choice([-1, 1]) * BALL_SPEED, 
                        random.uniform(-1, 1) * BALL_SPEED]
    
    def move_ai(self):
        # AI canggih dengan prediksi pantulan
        if self.ball_vel[0] > 0:  # Hanya gerak jika bola menuju AI
            # Prediksi posisi y saat bola sampai ke paddle
            predict_x = self.ai.left
            time_to_reach = (predict_x - self.ball.centerx) / self.ball_vel[0]
            predict_y = self.ball.centery + (self.ball_vel[1] * time_to_reach)
            
            # Simulasi pantulan di dinding
            while predict_y < 0 or predict_y > LOW_RES_HEIGHT:
                if predict_y < 0:
                    predict_y = -predict_y
                else:
                    predict_y = 2 * LOW_RES_HEIGHT - predict_y
            
            # Error berdasarkan difficulty
            error = (4 - self.difficulty) * 10
            predict_y += random.uniform(-error, error)
            
            # Gerakkan paddle dengan smoothing
            target = max(PADDLE_HEIGHT//2, 
                         min(LOW_RES_HEIGHT - PADDLE_HEIGHT//2, predict_y))
            self.ai.centery += (target - self.ai.centery) * 0.1 * self.difficulty
    
    def handle_collision(self):
        # Pantulan di dinding
        if self.ball.top <= 0 or self.ball.bottom >= LOW_RES_HEIGHT:
            self.ball_vel[1] *= -1
        
        # Tumbukan dengan paddle
        if self.ball.colliderect(self.player) and self.ball_vel[0] < 0:
            self.ball_vel[0] *= -1.05
            # Hitung sudut berdasarkan posisi tumbukan
            rel_intersect = (self.player.centery - self.ball.centery) / (PADDLE_HEIGHT/2)
            self.ball_vel[1] = -rel_intersect * BALL_SPEED
        
        if self.ball.colliderect(self.ai) and self.ball_vel[0] > 0:
            self.ball_vel[0] *= -1.05
            rel_intersect = (self.ai.centery - self.ball.centery) / (PADDLE_HEIGHT/2)
            self.ball_vel[1] = -rel_intersect * BALL_SPEED
    
    def run(self):
        running = True
        while running:
            # Input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running =False
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP] and self.player.top > 0:
                self.player.y -= PADDLE_SPEED
            if keys[pygame.K_DOWN] and self.player.bottom < LOW_RES_HEIGHT:
                self.player.y += PADDLE_SPEED
            
            # Update AI
            self.move_ai()
            
            # Update bola
            self.ball.x += self.ball_vel[0]
            self.ball.y += self.ball_vel[1]
            
            # Deteksi skor
            if self.ball.left <= 0:
                self.ai_score += 1
                self.reset_ball()
            elif self.ball.right >= LOW_RES_WIDTH:
                self.player_score += 1
                self.reset_ball()
            
            # Deteksi tumbukan
            self.handle_collision()
            
            # Render
            self.screen.fill(COLOR_BG)
            
            # Gambar objek
            pygame.draw.rect(self.screen, COLOR_PADDLE, self.player)
            pygame.draw.rect(self.screen, COLOR_AI_PADDLE, self.ai)
            pygame.draw.ellipse(self.screen, COLOR_BALL, self.ball)
            
            # Garis tengah putus-putus
            for y in range(0, LOW_RES_HEIGHT, 10):
                pygame.draw.rect(self.screen, COLOR_PADDLE, 
                                (LOW_RES_WIDTH//2 - 1, y, 2, 5))
            
            # Skor
            score_text = self.font.render(f"{self.player_score} : {self.ai_score}", 
                                        True, COLOR_TEXT)
            self.screen.blit(score_text, (LOW_RES_WIDTH//2 - score_text.get_width()//2, 10))
            
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    game = PongGame()
    game.run()
    pygame.quit()