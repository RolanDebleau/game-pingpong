import pygame
import random
import math

# Resolusi rendah internal untuk efek pixel art
LOW_RES_WIDTH = 320
LOW_RES_HEIGHT = 240

# Warna Cozy Pixel (RGB)
COLOR_BACKGROUND_DARK = (40, 30, 45)    # Ungu tua hangat
COLOR_BACKGROUND_LIGHT = (65, 50, 70)   # Ungu sedikit lebih terang
COLOR_PADDLE = (230, 200, 170)         # Krem hangat
COLOR_BALL = (255, 160, 122)           # Oranye salmon muda (LightSalmon)
COLOR_TEXT = (240, 230, 220)           # Putih gading
COLOR_ACCENT = (255, 180, 100)         # Oranye aksen
COLOR_SHADOW = (30, 20, 35)            # Bayangan tipis
COLOR_SELECTED = (255, 220, 150)       # Warna untuk opsi yang dipilih
COLOR_AI_PADDLE = (180, 220, 255)      # Biru muda untuk paddle AI

# Konstanta Game
PADDLE_WIDTH = 4
PADDLE_HEIGHT = 40  
BALL_RADIUS = 4     
PADDLE_SPEED = 2.5  
BALL_SPEED_X_INITIAL = 1.5
BALL_SPEED_Y_INITIAL = 1.5
WINNING_SCORE = 5

# Konstanta AI yang diperbaiki
AI_SPEED = 2.2  # Kecepatan AI sedikit lebih cepat
AI_PREDICTION_ERROR = 0.12  # Tingkat kesalahan prediksi AI
AI_REACTION_TIME = 0.15  # Waktu reaksi AI dalam detik
AI_DIFFICULTY_ADAPTIVE = True  # AI menyesuaikan tingkat kesulitan

# Konstanta untuk peningkatan kecepatan
SPEED_INCREASE_INTERVAL = 3.0  # Detik
SPEED_INCREASE_AMOUNT = 0.15   # Multiplier peningkatan kecepatan
MAX_SPEED_MULTIPLIER = 2.5     # Batas maksimum kecepatan

# Game States
STATE_MAIN_MENU = 0
STATE_START = 1
STATE_PLAY = 2
STATE_SCORE_SCREEN = 3
STATE_GAME_OVER = 4
STATE_DIFFICULTY_SELECT = 5

# Game Modes
MODE_TWO_PLAYER = 0
MODE_VS_COMPUTER = 1

# AI Difficulty Levels
DIFFICULTY_EASY = 0
DIFFICULTY_MEDIUM = 1
DIFFICULTY_HARD = 2

def draw_dashed_line(surface, color, start_pos, end_pos, width=1, dash_length=5, space_length=3):
    """ Helper function to draw a dashed line. """
    x1, y1 = start_pos
    x2, y2 = end_pos
    dx = x2 - x1
    dy = y2 - y1
    distance = max(abs(dx), abs(dy))
    
    if distance == 0:
        return
    
    segment_length = dash_length + space_length
    num_dashes = int(distance / segment_length)

    for i in range(num_dashes):
        start = i * segment_length
        end = start + dash_length
        if y1 == y2:  # Horizontal line
            pygame.draw.line(surface, color, (x1 + start, y1), (x1 + end, y1), width)
        else:  # Vertical line
            pygame.draw.line(surface, color, (x1, y1 + start), (x1, y1 + end), width)

def draw_text_with_shadow(surface, text, font, color, shadow_color, x, y, centered=True):
    """Helper function to draw text with shadow effect"""
    shadow_text = font.render(text, True, shadow_color)
    main_text = font.render(text, True, color)
    
    if centered:
        shadow_rect = shadow_text.get_rect(center=(x + 1, y + 1))
        main_rect = main_text.get_rect(center=(x, y))
    else:
        shadow_rect = (x + 1, y + 1)
        main_rect = (x, y)
    
    surface.blit(shadow_text, shadow_rect)
    surface.blit(main_text, main_rect)

def wrap_text(text, font, max_width):
    """Helper function to wrap text to fit within max_width"""
    words = text.split(' ')
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line.strip())
                current_line = word + " "
            else:
                lines.append(word)
    
    if current_line:
        lines.append(current_line.strip())
    
    return lines

def main():
    pygame.init()

    # === SETUP FULLSCREEN ===
    # Mendapatkan info display
    display_info = pygame.display.Info()
    SCREEN_WIDTH = display_info.current_w
    SCREEN_HEIGHT = display_info.current_h
    
    # Buat screen fullscreen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
    
    # Hitung scale factor untuk maintain aspect ratio
    scale_x = SCREEN_WIDTH / LOW_RES_WIDTH
    scale_y = SCREEN_HEIGHT / LOW_RES_HEIGHT
    scale_factor = min(scale_x, scale_y)  # Gunakan yang terkecil untuk maintain aspect ratio
    
    # Hitung posisi untuk center game
    scaled_width = int(LOW_RES_WIDTH * scale_factor)
    scaled_height = int(LOW_RES_HEIGHT * scale_factor)
    offset_x = (SCREEN_WIDTH - scaled_width) // 2
    offset_y = (SCREEN_HEIGHT - scaled_height) // 2
    
    # Surface untuk game dengan resolusi rendah
    game_surface = pygame.Surface((LOW_RES_WIDTH, LOW_RES_HEIGHT))
    pygame.display.set_caption('Cozy Pixel Pong')
    clock = pygame.time.Clock()

    # Font - gunakan font sistem dengan ukuran yang lebih kecil untuk mencegah terpotong
    try:
        small_font = pygame.font.Font("fonts/VT323-Regular.ttf", 14)
        medium_font = pygame.font.Font("fonts/VT323-Regular.ttf", 18)
        large_font = pygame.font.Font("fonts/PressStart2P-Regular.ttf", 16)
        title_font = pygame.font.Font("fonts/PressStart2P-Regular.ttf", 20)
    except pygame.error:
        print("Font kustom tidak ditemukan, menggunakan font sistem.")
        small_font = pygame.font.SysFont('Consolas', 12)
        medium_font = pygame.font.SysFont('Consolas', 16)
        large_font = pygame.font.SysFont('Consolas', 18)
        title_font = pygame.font.SysFont('Consolas', 20)

    # Posisi dan pergerakan paddle
    paddle_1_rect = pygame.Rect(15, LOW_RES_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    paddle_2_rect = pygame.Rect(LOW_RES_WIDTH - 15 - PADDLE_WIDTH, LOW_RES_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    paddle_1_move = 0
    paddle_2_move = 0

    # Bola
    ball_rect = pygame.Rect(LOW_RES_WIDTH // 2 - BALL_RADIUS, LOW_RES_HEIGHT // 2 - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)
    ball_vel_x = 0
    ball_vel_y = 0
    
    # Variabel untuk sistem peningkatan kecepatan
    round_start_time = 0
    current_speed_multiplier = 1.0
    base_speed_x = BALL_SPEED_X_INITIAL
    base_speed_y = BALL_SPEED_Y_INITIAL

    # Skor
    score_1 = 0
    score_2 = 0

    # Game state dan mode
    current_game_state = STATE_MAIN_MENU
    game_mode = MODE_TWO_PLAYER
    ai_difficulty = DIFFICULTY_MEDIUM
    winner = None
    
    # Menu variables
    menu_selected = 0  # 0 = 2 Player, 1 = VS Computer, 2 = Quit
    menu_options = ["2 PLAYER", "VS COMPUTER", "QUIT"]
    
    # Difficulty menu variables
    difficulty_selected = 1  # Default medium
    difficulty_options = ["MUDAH", "SEDANG", "SULIT"]

    # Variabel untuk efek getar
    screen_shake_timer = 0
    
    # Variabel untuk efek bola
    ball_trail = []  # Menyimpan posisi bola untuk efek trail
    ball_glow_timer = 0  # Timer untuk efek glow berdenyut
    
    # Variabel untuk efek speed up
    speed_up_effect_timer = 0
    last_speed_increase_time = 0
    
    # Variabel AI yang diperbaiki
    ai_target_y = LOW_RES_HEIGHT // 2
    ai_reaction_delay = 0
    ai_error_offset = 0
    ai_last_ball_x = 0
    ai_prediction_timer = 0
    ai_difficulty_adjustment = 0
    
    # Statistik untuk adaptive AI
    player_wins = 0
    ai_wins = 0
    total_games = 0

    def get_ai_settings(difficulty):
        """Mendapatkan setting AI berdasarkan tingkat kesulitan"""
        if difficulty == DIFFICULTY_EASY:
            return {
                'speed': 1.8,
                'prediction_error': 0.25,
                'reaction_time': 0.25,
                'accuracy': 0.7
            }
        elif difficulty == DIFFICULTY_MEDIUM:
            return {
                'speed': 2.2,
                'prediction_error': 0.12,
                'reaction_time': 0.15,
                'accuracy': 0.85
            }
        else:  # HARD
            return {
                'speed': 2.6,
                'prediction_error': 0.05,
                'reaction_time': 0.08,
                'accuracy': 0.95
            }

    def reset_ball(direction_to_loser=1):
        ball_rect.center = (LOW_RES_WIDTH // 2, LOW_RES_HEIGHT // 2)
        nonlocal ball_vel_x, ball_vel_y, round_start_time, current_speed_multiplier
        nonlocal base_speed_x, base_speed_y, last_speed_increase_time
        
        # Reset kecepatan ke nilai awal
        current_speed_multiplier = 1.0
        base_speed_x = BALL_SPEED_X_INITIAL
        base_speed_y = BALL_SPEED_Y_INITIAL
        
        ball_vel_x = base_speed_x * direction_to_loser * random.choice([-1, 1])
        ball_vel_y = base_speed_y * random.choice([-1, 1])
        
        # Reset timer
        round_start_time = pygame.time.get_ticks() / 1000.0
        last_speed_increase_time = round_start_time
        
        # Reset trail dan efek
        ball_trail.clear()
        nonlocal ball_glow_timer
        ball_glow_timer = 0

    def start_new_game(mode, difficulty=DIFFICULTY_MEDIUM):
        nonlocal score_1, score_2, winner, current_game_state, game_mode, ai_difficulty
        score_1 = 0
        score_2 = 0
        winner = None
        game_mode = mode
        ai_difficulty = difficulty
        reset_ball(random.choice([-1,1]))
        current_game_state = STATE_PLAY

    def update_ai():
        nonlocal ai_target_y, ai_reaction_delay, ai_error_offset, ai_last_ball_x
        nonlocal ai_prediction_timer, ai_difficulty_adjustment, paddle_2_move
        """Update AI paddle movement dengan logika yang diperbaiki"""
        nonlocal paddle_2_move
        
        if game_mode == MODE_VS_COMPUTER:
            ai_settings = get_ai_settings(ai_difficulty)
            
            # Adaptive difficulty berdasarkan performa pemain
            if AI_DIFFICULTY_ADAPTIVE and total_games > 0:
                win_ratio = player_wins / total_games
                if win_ratio > 0.7:  # Pemain menang terlalu sering
                    ai_difficulty_adjustment = min(ai_difficulty_adjustment + 0.1, 0.5)
                elif win_ratio < 0.3:  # AI menang terlalu sering
                    ai_difficulty_adjustment = max(ai_difficulty_adjustment - 0.1, -0.5)
            
            # AI hanya bereaksi jika bola bergerak ke arahnya
            if ball_vel_x > 0:
                # Hitung waktu sampai bola mencapai paddle
                time_to_paddle = (paddle_2_rect.x - ball_rect.centerx) / ball_vel_x
                
                if time_to_paddle > 0:
                    # Prediksi posisi bola dengan mempertimbangkan pantulan
                    predicted_y = ball_rect.centery + (ball_vel_y * time_to_paddle)
                    
                    # Simulasi pantulan dari dinding atas/bawah
                    bounces = 0
                    temp_y = predicted_y
                    temp_vel_y = ball_vel_y
                    
                    while bounces < 3:  # Maksimal 3 pantulan
                        if temp_y <= 0:
                            temp_y = -temp_y
                            temp_vel_y = -temp_vel_y
                            bounces += 1
                        elif temp_y >= LOW_RES_HEIGHT:
                            temp_y = 2 * LOW_RES_HEIGHT - temp_y
                            temp_vel_y = -temp_vel_y
                            bounces += 1
                        else:
                            break
                    
                    predicted_y = temp_y
                    
                    # Tambahkan error berdasarkan tingkat kesulitan
                    if ai_reaction_delay <= 0:
                        error_range = PADDLE_HEIGHT * (ai_settings['prediction_error'] - ai_difficulty_adjustment)
                        ai_error_offset = random.uniform(-error_range, error_range)
                        
                        # Waktu reaksi berdasarkan tingkat kesulitan
                        reaction_frames = int(ai_settings['reaction_time'] * 60)  # Convert to frames
                        ai_reaction_delay = random.randint(reaction_frames - 2, reaction_frames + 2)
                    
                    ai_target_y = predicted_y + ai_error_offset
                    
                    # Batasi target dalam area bermain
                    ai_target_y = max(PADDLE_HEIGHT // 2, 
                                    min(LOW_RES_HEIGHT - PADDLE_HEIGHT // 2, ai_target_y))
                    
                    # Kadang-kadang AI "mengantuk" untuk menambah variasi
                    if random.random() > ai_settings['accuracy']:
                        ai_target_y += random.uniform(-PADDLE_HEIGHT, PADDLE_HEIGHT)
            
            # Kurangi delay reaksi
            if ai_reaction_delay > 0:
                ai_reaction_delay -= 1
            
            # Gerakkan paddle AI menuju target
            paddle_center_y = paddle_2_rect.centery
            distance_to_target = ai_target_y - paddle_center_y
            
            # Kecepatan AI berdasarkan tingkat kesulitan
            ai_speed = ai_settings['speed'] + ai_difficulty_adjustment
            
            # Dead zone untuk menghindari jitter
            dead_zone = 3
            if abs(distance_to_target) > dead_zone:
                if distance_to_target > 0:
                    paddle_2_move = min(ai_speed, distance_to_target / 10)
                else:
                    paddle_2_move = max(-ai_speed, distance_to_target / 10)
            else:
                paddle_2_move = 0
            
            # Simpan posisi bola untuk tracking
            ai_last_ball_x = ball_rect.centerx

    def update_ball_speed():
        nonlocal current_speed_multiplier, ball_vel_x, ball_vel_y, last_speed_increase_time
        nonlocal speed_up_effect_timer
        
        current_time = pygame.time.get_ticks() / 1000.0
        time_since_round_start = current_time - round_start_time
        
        # Hitung berapa kali kecepatan harus ditingkatkan
        speed_increases = int(time_since_round_start / SPEED_INCREASE_INTERVAL)
        new_speed_multiplier = min(1.0 + (speed_increases * SPEED_INCREASE_AMOUNT), MAX_SPEED_MULTIPLIER)
        
        # Jika ada peningkatan kecepatan
        if new_speed_multiplier > current_speed_multiplier:
            current_speed_multiplier = new_speed_multiplier
            
            # Terapkan multiplier ke kecepatan bola
            speed_direction_x = 1 if ball_vel_x > 0 else -1
            speed_direction_y = 1 if ball_vel_y > 0 else -1
            
            ball_vel_x = base_speed_x * current_speed_multiplier * speed_direction_x
            ball_vel_y = base_speed_y * current_speed_multiplier * speed_direction_y
            
            # Aktifkan efek visual
            speed_up_effect_timer = 30  # 30 frame efek
            last_speed_increase_time = current_time
            
            # Tambahkan sedikit screen shake
            nonlocal screen_shake_timer
            screen_shake_timer = max(screen_shake_timer, 3)

    # GAME LOOP
    running = True
    while running:
        delta_time = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Tambahkan kontrol untuk keluar dari fullscreen
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            if current_game_state == STATE_MAIN_MENU:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        menu_selected = (menu_selected - 1) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        menu_selected = (menu_selected + 1) % len(menu_options)
                    elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        if menu_selected == 0:  # 2 Player
                            start_new_game(MODE_TWO_PLAYER)
                        elif menu_selected == 1:  # VS Computer
                            current_game_state = STATE_DIFFICULTY_SELECT
                        elif menu_selected == 2:  # Quit
                            running = False
            
            elif current_game_state == STATE_DIFFICULTY_SELECT:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        difficulty_selected = (difficulty_selected - 1) % len(difficulty_options)
                    elif event.key == pygame.K_DOWN:
                        difficulty_selected = (difficulty_selected + 1) % len(difficulty_options)
                    elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        start_new_game(MODE_VS_COMPUTER, difficulty_selected)
                    elif event.key == pygame.K_BACKSPACE:
                        current_game_state = STATE_MAIN_MENU
            
            elif current_game_state == STATE_START:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        start_new_game(game_mode)
            
            elif current_game_state == STATE_PLAY:
                # Kontrol paddle
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        paddle_1_move = -PADDLE_SPEED
                    if event.key == pygame.K_s:
                        paddle_1_move = PADDLE_SPEED
                    # Kontrol paddle 2 hanya untuk mode 2 player
                    if game_mode == MODE_TWO_PLAYER:
                        if event.key == pygame.K_UP:
                            paddle_2_move = -PADDLE_SPEED
                        if event.key == pygame.K_DOWN:
                            paddle_2_move = PADDLE_SPEED
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_w or event.key == pygame.K_s:
                        paddle_1_move = 0
                    # Kontrol paddle 2 hanya untuk mode 2 player
                    if game_mode == MODE_TWO_PLAYER:
                        if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                            paddle_2_move = 0
            
            elif current_game_state == STATE_SCORE_SCREEN:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if winner:
                            current_game_state = STATE_GAME_OVER
                        else:
                            reset_ball(1 if ball_vel_x < 0 else -1)
                            current_game_state = STATE_PLAY
            
            elif current_game_state == STATE_GAME_OVER:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Update statistik
                        if game_mode == MODE_VS_COMPUTER:
                            total_games += 1
                            if winner == "Player 1":
                                player_wins += 1
                            else:
                                ai_wins += 1
                        
                        current_game_state = STATE_MAIN_MENU
                        menu_selected = 0  # Reset menu selection

        # === LOGIKA GAME ===
        if current_game_state == STATE_PLAY:
            # Update kecepatan bola secara bertahap
            update_ball_speed()
            
            # Update AI jika dalam mode VS Computer
            if game_mode == MODE_VS_COMPUTER:
                update_ai()
            
            # Pergerakan paddle
            paddle_1_rect.y += paddle_1_move * 60 * delta_time
            paddle_2_rect.y += paddle_2_move * 60 * delta_time

            # Batas paddle
            if paddle_1_rect.top < 0: paddle_1_rect.top = 0
            if paddle_1_rect.bottom > LOW_RES_HEIGHT: paddle_1_rect.bottom = LOW_RES_HEIGHT
            if paddle_2_rect.top < 0: paddle_2_rect.top = 0
            if paddle_2_rect.bottom > LOW_RES_HEIGHT: paddle_2_rect.bottom = LOW_RES_HEIGHT

            # Pergerakan bola
            ball_rect.x += ball_vel_x * 60 * delta_time
            ball_rect.y += ball_vel_y * 60 * delta_time
            
            # Update trail bola untuk efek visual
            ball_trail.append((ball_rect.centerx, ball_rect.centery))
            if len(ball_trail) > int(8 + current_speed_multiplier * 2):  # Trail lebih panjang untuk kecepatan tinggi
                ball_trail.pop(0)

            # Kolisi bola dengan dinding atas/bawah
            if ball_rect.top <= 0:
                ball_rect.top = 0
                ball_vel_y *= -1
            if ball_rect.bottom >= LOW_RES_HEIGHT:
                ball_rect.bottom = LOW_RES_HEIGHT
                ball_vel_y *= -1

            # Kolisi bola dengan paddle
            collided_paddle_1 = paddle_1_rect.colliderect(ball_rect)
            collided_paddle_2 = paddle_2_rect.colliderect(ball_rect)

            if collided_paddle_1 and ball_vel_x < 0:
                # Pertahankan kecepatan yang sudah ditingkatkan
                speed_sign = 1 if ball_vel_x > 0 else -1
                ball_vel_x = abs(ball_vel_x) * -1.05 * speed_sign
                ball_rect.left = paddle_1_rect.right + 1
                relative_intersect_y = (paddle_1_rect.centery - ball_rect.centery) / (PADDLE_HEIGHT / 2)
                ball_vel_y -= relative_intersect_y * 0.5 * current_speed_multiplier
                screen_shake_timer = max(5, int(3 * current_speed_multiplier))
                ball_glow_timer = max(15, int(10 * current_speed_multiplier))

            if collided_paddle_2 and ball_vel_x > 0:
                # Pertahankan kecepatan yang sudah ditingkatkan
                speed_sign = 1 if ball_vel_x > 0 else -1
                ball_vel_x = abs(ball_vel_x) * -1.05 * speed_sign
                ball_rect.right = paddle_2_rect.left - 1
                relative_intersect_y = (paddle_2_rect.centery - ball_rect.centery) / (PADDLE_HEIGHT / 2)
                ball_vel_y -= relative_intersect_y * 0.5 * current_speed_multiplier
                screen_shake_timer = max(5, int(3 * current_speed_multiplier))
                ball_glow_timer = max(15, int(10 * current_speed_multiplier))

            # Cek skor
            point_scored_by_player = None
            if ball_rect.left <= 0:
                score_2 += 1
                point_scored_by_player = 2
                current_game_state = STATE_SCORE_SCREEN
                if score_2 >= WINNING_SCORE: 
                    winner = "Computer" if game_mode == MODE_VS_COMPUTER else "Player 2"
            if ball_rect.right >= LOW_RES_WIDTH:
                score_1 += 1
                point_scored_by_player = 1
                current_game_state = STATE_SCORE_SCREEN
                if score_1 >= WINNING_SCORE: winner = "Player 1"
            
            if point_scored_by_player:
                if winner:
                    current_game_state = STATE_GAME_OVER
                else:
                    current_game_state = STATE_SCORE_SCREEN

        # Update timer efek
        if ball_glow_timer > 0:
            ball_glow_timer -= 1
        if speed_up_effect_timer > 0:
            speed_up_effect_timer -= 1

        # Efek getar layar
        render_offset_x, render_offset_y = 0, 0
        if screen_shake_timer > 0:
            screen_shake_timer -= 1
            intensity = max(1, int(current_speed_multiplier))
            render_offset_x = random.randint(-intensity, intensity)
            render_offset_y = random.randint(-intensity, intensity)

        # === RENDER ===
        # Bersihkan layar dengan warna hitam
        screen.fill((0, 0, 0))
        
        # Latar belakang game
        game_surface.fill(COLOR_BACKGROUND_DARK)
        center_rect_width = LOW_RES_WIDTH // 1.5
        center_rect_height = LOW_RES_HEIGHT
        center_rect_x = (LOW_RES_WIDTH - center_rect_width) // 2
        pygame.draw.rect(game_surface, COLOR_BACKGROUND_LIGHT, 
                        (center_rect_x, 0, center_rect_width, center_rect_height))

        if current_game_state == STATE_MAIN_MENU:
            # Judul game
            draw_text_with_shadow(game_surface, 'COZY PONG', title_font, COLOR_TEXT, COLOR_SHADOW, 
                                LOW_RES_WIDTH // 2, 40)
            
            # Menu options
            menu_start_y = 100
            menu_spacing = 25
            
            for i, option in enumerate(menu_options):
                color = COLOR_SELECTED if i == menu_selected else COLOR_TEXT
                draw_text_with_shadow(game_surface, option, medium_font, color, COLOR_SHADOW,
                                    LOW_RES_WIDTH // 2, menu_start_y + i * menu_spacing)
                
                # Indicator untuk opsi yang dipilih
                if i == menu_selected:
                    draw_text_with_shadow(game_surface, '>', medium_font, COLOR_SELECTED, COLOR_SHADOW,
                                        LOW_RES_WIDTH // 2 - 80, menu_start_y + i * menu_spacing)
            
            # Instruksi dengan text wrapping
            instructions = [
                "UP/DOWN: navigasi",
                "SPACE: pilih",
                "ESC: keluar"
            ]
            
            instruction_y = 190
            for instruction in instructions:
                draw_text_with_shadow(game_surface, instruction, small_font, COLOR_ACCENT, COLOR_SHADOW,
                                    LOW_RES_WIDTH // 2, instruction_y)
                instruction_y += 15

        elif current_game_state == STATE_DIFFICULTY_SELECT:
            # Judul
            draw_text_with_shadow(game_surface, 'PILIH TINGKAT KESULITAN', medium_font, COLOR_TEXT, COLOR_SHADOW,
                                LOW_RES_WIDTH // 2, 60)
            
            # Difficulty options
            difficulty_start_y = 100
            difficulty_spacing = 25
            
            for i, option in enumerate(difficulty_options):
                color = COLOR_SELECTED if i == difficulty_selected else COLOR_TEXT
                draw_text_with_shadow(game_surface, option, medium_font, color, COLOR_SHADOW,
                                    LOW_RES_WIDTH // 2, difficulty_start_y + i * difficulty_spacing)
                
                # Indicator untuk opsi yang dipilih
                if i == difficulty_selected:
                    draw_text_with_shadow(game_surface, '>', medium_font, COLOR_SELECTED, COLOR_SHADOW,
                                        LOW_RES_WIDTH // 2 - 80, difficulty_start_y + i * difficulty_spacing)
            # Instruksi untuk kembali ke menu utama
            draw_text_with_shadow(game_surface, 'BACKSPACE: kembali', small_font, COLOR_ACCENT, COLOR_SHADOW,
                                LOW_RES_WIDTH // 2, 190)
        elif current_game_state == STATE_PLAY:
            # Gambar paddle dengan bayangan setelah efek bola
            pygame.draw.rect(game_surface, COLOR_SHADOW, (paddle_1_rect.x + 1, paddle_1_rect.y + 1, paddle_1_rect.width, paddle_1_rect.height))
            pygame.draw.rect(game_surface, COLOR_PADDLE, paddle_1_rect)
            pygame.draw.rect(game_surface, COLOR_SHADOW, (paddle_2_rect.x + 1, paddle_2_rect.y + 1, paddle_2_rect.width, paddle_2_rect.height))
            pygame.draw.rect(game_surface, COLOR_AI_PADDLE if game_mode == MODE_VS_COMPUTER else COLOR_PADDLE, paddle_2_rect)
            # Garis tengah putus-putus (selalu muncul saat main)
            draw_dashed_line(game_surface, COLOR_PADDLE, 
                             (LOW_RES_WIDTH // 2, 5), (LOW_RES_WIDTH // 2, LOW_RES_HEIGHT - 5), 
                             width=2, dash_length=6, space_length=4)

            # Efek trail bola dengan alpha/transparansi (efek api/terbakar)
            if len(ball_trail) > 1:
                ball_speed = abs(ball_vel_x) + abs(ball_vel_y)
                speed_factor = min(ball_speed / 3.0, 3.0)
                for i, (trail_x, trail_y) in enumerate(ball_trail[:-1]):
                    alpha = int(255 * (i + 1) / len(ball_trail) * 0.8)
                    trail_size = max(1, int(BALL_RADIUS * (0.3 + 0.7 * (i + 1) / len(ball_trail))))
                    if current_speed_multiplier > 2.0:
                        trail_color = (255, int(80 + 60 * (i + 1) / len(ball_trail)), 40)
                    elif current_speed_multiplier > 1.5:
                        trail_color = (255, int(120 + 40 * (i + 1) / len(ball_trail)), 60)
                    elif current_speed_multiplier > 1.0:
                        trail_color = (255, int(160 + 40 * (i + 1) / len(ball_trail)), 100)
                    else:
                        trail_color = COLOR_BALL
                    trail_surf = pygame.Surface((trail_size*2, trail_size*2), pygame.SRCALPHA)
                    trail_surf.set_alpha(alpha)
                    pygame.draw.ellipse(trail_surf, trail_color, (0, 0, trail_size*2, trail_size*2))
                    game_surface.blit(trail_surf, (trail_x - trail_size, trail_y - trail_size))

            # Efek glow bola (layer glow menyala/fire effect)
            glow_intensity = max(current_speed_multiplier - 1.0, ball_glow_timer / 15.0)
            if glow_intensity > 0:
                glow_size = int(BALL_RADIUS * (2 + glow_intensity * 1.5))
                # Jika glow timer aktif, gunakan warna "api" dan alpha lebih tinggi
                if ball_glow_timer > 0:
                    # Warna transisi dari kuning ke oranye ke merah
                    glow_colors = [
                        (255, 200, 80),   # kuning
                        (255, 140, 40),   # oranye
                        (255, 80, 40),    # merah
                    ]
                    for i in range(int(6 + glow_intensity*2)):
                        layer_size = glow_size - i * 2
                        if layer_size > 0:
                            color_idx = min(i // 2, len(glow_colors)-1)
                            glow_color = glow_colors[color_idx]
                            alpha = 120 - i*15
                            glow_surf = pygame.Surface((layer_size*2, layer_size*2), pygame.SRCALPHA)
                            pygame.draw.ellipse(glow_surf, glow_color + (max(30, alpha),), (0, 0, layer_size*2, layer_size*2))
                            game_surface.blit(glow_surf, (ball_rect.centerx - layer_size, ball_rect.centery - layer_size))
                else:
                    # Glow normal berdasarkan speed
                    if current_speed_multiplier > 2.0:
                        glow_color = (255, 80, 40)
                    elif current_speed_multiplier > 1.5:
                        glow_color = (255, 120, 60)
                    elif current_speed_multiplier > 1.0:
                        glow_color = (255, 140, 80)
                    else:
                        glow_color = COLOR_ACCENT
                    for i in range(int(4 + glow_intensity*1.5)):
                        layer_size = glow_size - i * 2
                        if layer_size > 0:
                            glow_surf = pygame.Surface((layer_size*2, layer_size*2), pygame.SRCALPHA)
                            pygame.draw.ellipse(glow_surf, glow_color + (60,), (0, 0, layer_size*2, layer_size*2))
                            game_surface.blit(glow_surf, (ball_rect.centerx - layer_size, ball_rect.centery - layer_size))

            # Gambar bayangan bola
            pygame.draw.rect(game_surface, COLOR_SHADOW, (ball_rect.x + 1, ball_rect.y + 1, ball_rect.width, ball_rect.height))

            # Gambar bola utama dengan warna berubah sesuai kecepatan
            if current_speed_multiplier > 2.0:
                ball_color = (255, 100, 100)
            elif current_speed_multiplier > 1.5:
                ball_color = (255, 120, 80)
            elif current_speed_multiplier > 1.0:
                ball_color = (255, 140, 100)
            else:
                ball_color = COLOR_BALL
            pygame.draw.ellipse(game_surface, ball_color, ball_rect)

            # Efek berkedip untuk kecepatan sangat tinggi
            if current_speed_multiplier > 2.0 and int(pygame.time.get_ticks() / 80) % 2:
                pygame.draw.ellipse(game_surface, (255, 255, 255), ball_rect, 1)

            # --- Render skor dan efek speed up di atas elemen lain ---
            score_1_text = medium_font.render(str(score_1), True, COLOR_TEXT)
            score_1_rect = score_1_text.get_rect(center=(LOW_RES_WIDTH // 4, 20))
            game_surface.blit(score_1_text, score_1_rect)

            score_2_text = medium_font.render(str(score_2), True, COLOR_TEXT)
            score_2_rect = score_2_text.get_rect(center=(LOW_RES_WIDTH * 3 // 4, 20))
            game_surface.blit(score_2_text, score_2_rect)

            speed_text = f"Speed: {current_speed_multiplier:.1f}x"
            speed_display = small_font.render(speed_text, True, COLOR_ACCENT)
            speed_rect = speed_display.get_rect(center=(LOW_RES_WIDTH // 2, 40))
            game_surface.blit(speed_display, speed_rect)

            if speed_up_effect_timer > 0:
                flash_intensity = int(255 * (speed_up_effect_timer / 30.0))
                flash_color = (255, 255 - flash_intensity, 255 - flash_intensity)
                speed_up_text = small_font.render("SPEED UP!", True, flash_color)
                speed_up_rect = speed_up_text.get_rect(center=(LOW_RES_WIDTH // 2, 55))
                game_surface.blit(speed_up_text, speed_up_rect)

            # Info keluar (pojok bawah)
            exit_text = small_font.render('ESC untuk Keluar', True, COLOR_TEXT)
            exit_rect = exit_text.get_rect(center=(LOW_RES_WIDTH // 2, LOW_RES_HEIGHT - 20))
            game_surface.blit(exit_text, exit_rect)

        elif current_game_state == STATE_START:
            title_text = large_font.render('COZY PONG', True, COLOR_TEXT)
            title_rect = title_text.get_rect(center=(LOW_RES_WIDTH // 2, LOW_RES_HEIGHT // 3))
            game_surface.blit(title_text, title_rect)

            prompt_text = small_font.render('Tekan SPACE untuk Mulai', True, COLOR_ACCENT)
            prompt_rect = prompt_text.get_rect(center=(LOW_RES_WIDTH // 2, LOW_RES_HEIGHT // 1.5))
            game_surface.blit(prompt_text, prompt_rect)
            
            # Tampilkan mode game
            mode_text = "Mode: " + ("2 Player" if game_mode == MODE_TWO_PLAYER else "VS Computer")
            mode_display = small_font.render(mode_text, True, COLOR_TEXT)
            mode_rect = mode_display.get_rect(center=(LOW_RES_WIDTH // 2, LOW_RES_HEIGHT // 1.5 + 20))
            game_surface.blit(mode_display, mode_rect)
            
            # Tambahkan info kecepatan progresif
            speed_info = small_font.render('Kecepatan meningkat tiap 3 detik!', True, COLOR_TEXT)
            speed_info_rect = speed_info.get_rect(center=(LOW_RES_WIDTH // 2, LOW_RES_HEIGHT // 1.5 + 40))
            game_surface.blit(speed_info, speed_info_rect)

        elif current_game_state == STATE_PLAY or current_game_state == STATE_SCORE_SCREEN:
            # Garis tengah putus-putus (selalu di bawah skor, di atas background)
            draw_dashed_line(game_surface, COLOR_PADDLE, 
                             (LOW_RES_WIDTH // 2, 5), (LOW_RES_WIDTH // 2, LOW_RES_HEIGHT - 5), 
                             width=2, dash_length=6, space_length=4)

            # Gambar paddle dengan bayangan
            pygame.draw.rect(game_surface, COLOR_SHADOW, (paddle_1_rect.x + 1, paddle_1_rect.y + 1, paddle_1_rect.width, paddle_1_rect.height))
            pygame.draw.rect(game_surface, COLOR_PADDLE, paddle_1_rect)
            pygame.draw.rect(game_surface, COLOR_SHADOW, (paddle_2_rect.x + 1, paddle_2_rect.y + 1, paddle_2_rect.width, paddle_2_rect.height))
            pygame.draw.rect(game_surface, COLOR_PADDLE, paddle_2_rect)

            # Efek trail bola dengan alpha/transparansi (efek api/terbakar)
            if current_game_state == STATE_PLAY and len(ball_trail) > 1:
                ball_speed = abs(ball_vel_x) + abs(ball_vel_y)
                speed_factor = min(ball_speed / 3.0, 3.0)
                for i, (trail_x, trail_y) in enumerate(ball_trail[:-1]):
                    alpha = int(255 * (i + 1) / len(ball_trail) * 0.8)
                    trail_size = max(1, int(BALL_RADIUS * (0.3 + 0.7 * (i + 1) / len(ball_trail))))
                    if current_speed_multiplier > 2.0:
                        trail_color = (255, int(80 + 60 * (i + 1) / len(ball_trail)), 40)
                    elif current_speed_multiplier > 1.5:
                        trail_color = (255, int(120 + 40 * (i + 1) / len(ball_trail)), 60)
                    elif current_speed_multiplier > 1.0:
                        trail_color = (255, int(160 + 40 * (i + 1) / len(ball_trail)), 100)
                    else:
                        trail_color = COLOR_BALL
                    # Surface sementara untuk alpha
                    trail_surf = pygame.Surface((trail_size*2, trail_size*2), pygame.SRCALPHA)
                    trail_surf.set_alpha(alpha)
                    pygame.draw.ellipse(trail_surf, trail_color, (0, 0, trail_size*2, trail_size*2))
                    game_surface.blit(trail_surf, (trail_x - trail_size, trail_y - trail_size))

            # Gambar bola dengan efek kecepatan
            ball_speed = abs(ball_vel_x) + abs(ball_vel_y)
            speed_factor = min(ball_speed / 3.0, 3.0)
            
            # Efek glow berdasarkan kecepatan multiplier
            glow_intensity = max(current_speed_multiplier - 1.0, ball_glow_timer / 15.0)
            if glow_intensity > 0:
                glow_size = int(BALL_RADIUS * (2 + glow_intensity * 1.5))
                
                # Warna glow berubah sesuai speed multiplier
                if current_speed_multiplier > 2.0:
                    glow_color = (255, 80, 40)  # Merah untuk kecepatan sangat tinggi
                elif current_speed_multiplier > 1.5:
                    glow_color = (255, 120, 60)  # Oranye kemerahan untuk kecepatan tinggi
                elif current_speed_multiplier > 1.0:
                    glow_color = (255, 140, 80)  # Oranye untuk kecepatan sedang
                else:
                    glow_color = COLOR_ACCENT
                
                # Gambar multiple layer glow
                for i in range(int(3 + glow_intensity)):
                    layer_size = glow_size - i * 2
                    if layer_size > 0:
                        glow_rect = pygame.Rect(ball_rect.centerx - layer_size, ball_rect.centery - layer_size, 
                                              layer_size * 2, layer_size * 2)
                        pygame.draw.ellipse(game_surface, glow_color, glow_rect)

            # Gambar bayangan bola
            pygame.draw.rect(game_surface, COLOR_SHADOW, (ball_rect.x + 1, ball_rect.y + 1, ball_rect.width, ball_rect.height))
            
            # Gambar bola utama dengan warna berubah sesuai kecepatan
            if current_speed_multiplier > 2.0:
                ball_color = (255, 100, 100)  # Merah terang untuk kecepatan sangat tinggi
            elif current_speed_multiplier > 1.5:
                ball_color = (255, 120, 80)   # Oranye kemerahan untuk kecepatan tinggi
            elif current_speed_multiplier > 1.0:
                ball_color = (255, 140, 100)  # Oranye terang untuk kecepatan sedang
            else:
                ball_color = COLOR_BALL
            
            pygame.draw.ellipse(game_surface, ball_color, ball_rect)
            
            # Efek berkedip untuk kecepatan sangat tinggi
            if current_speed_multiplier > 2.0 and int(pygame.time.get_ticks() / 80) % 2:
                pygame.draw.ellipse(game_surface, (255, 255, 255), ball_rect, 1)

            # Tampilkan Skor
            score_1_text = medium_font.render(str(score_1), True, COLOR_TEXT)
            score_1_rect = score_1_text.get_rect(center=(LOW_RES_WIDTH // 4, 20))
            game_surface.blit(score_1_text, score_1_rect)

            score_2_text = medium_font.render(str(score_2), True, COLOR_TEXT)
            score_2_rect = score_2_text.get_rect(center=(LOW_RES_WIDTH * 3 // 4, 20))
            game_surface.blit(score_2_text, score_2_rect)
            
            # Tampilkan indikator kecepatan saat bermain
            if current_game_state == STATE_PLAY:
                speed_text = f"Speed: {current_speed_multiplier:.1f}x"
                speed_display = small_font.render(speed_text, True, COLOR_ACCENT)
                speed_rect = speed_display.get_rect(center=(LOW_RES_WIDTH // 2, 40))
                game_surface.blit(speed_display, speed_rect)
                
                # Efek khusus saat kecepatan meningkat
                if speed_up_effect_timer > 0:
                    flash_intensity = int(255 * (speed_up_effect_timer / 30.0))
                    flash_color = (255, 255 - flash_intensity, 255 - flash_intensity)
                    speed_up_text = small_font.render("SPEED UP!", True, flash_color)
                    speed_up_rect = speed_up_text.get_rect(center=(LOW_RES_WIDTH // 2, 55))
                    game_surface.blit(speed_up_text, speed_up_rect)

            if current_game_state == STATE_SCORE_SCREEN and not winner:
                prompt_text = small_font.render('Tekan SPACE untuk Lanjut', True, COLOR_ACCENT)
                prompt_rect = prompt_text.get_rect(center=(LOW_RES_WIDTH // 2, LOW_RES_HEIGHT - 30))
                game_surface.blit(prompt_text, prompt_rect)

        if current_game_state == STATE_GAME_OVER:
            if winner:
                win_text_content = f"{winner} MENANG!"
            else:
                win_text_content = "GAME OVER"
            
            win_text = large_font.render(win_text_content, True, COLOR_ACCENT)
            win_rect = win_text.get_rect(center=(LOW_RES_WIDTH // 2, LOW_RES_HEIGHT // 3))
            game_surface.blit(win_text, win_rect)

            restart_text = small_font.render('Tekan SPACE untuk Main Lagi', True, COLOR_TEXT)
            restart_rect = restart_text.get_rect(center=(LOW_RES_WIDTH // 2, LOW_RES_HEIGHT // 1.5))
            game_surface.blit(restart_text, restart_rect)
            
            final_score_text_1 = medium_font.render(f"P1: {score_1}", True, COLOR_TEXT)
            game_surface.blit(final_score_text_1, final_score_text_1.get_rect(center=(LOW_RES_WIDTH // 2, LOW_RES_HEIGHT // 2 + 10)))
            final_score_text_2 = medium_font.render(f"P2: {score_2}", True, COLOR_TEXT)
            game_surface.blit(final_score_text_2, final_score_text_2.get_rect(center=(LOW_RES_WIDTH // 2, LOW_RES_HEIGHT // 2 + 35)))

        scaled_surface = pygame.transform.scale(game_surface, (scaled_width, scaled_height))
        final_x = offset_x + (render_offset_x * int(scale_factor))
        final_y = offset_y + (render_offset_y * int(scale_factor))
        screen.blit(scaled_surface, (final_x, final_y))
        
        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()