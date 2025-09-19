import pygame, sys, random
from screeninfo import get_monitors
monitors = get_monitors()
random_pipe_position=500 #biến này là vị trí của ống

# Game mode settings
GAME_MODES = {
    'single': {
        'name': '1 PLAYER',
        'description': 'Control blue bird with SPACEBAR'
    },
    'multiplayer': {
        'name': '2 PLAYERS', 
        'description': 'Blue bird: SPACEBAR, Yellow bird: UP ARROW'
    }
}

current_game_mode = 'single'  # Chế độ mặc định

# Difficulty settings
DIFFICULTIES = {
    'easy': {
        'name': 'EASY',
        'pipe_gap': 320,
        'spawn_time': 2000,
        'speed_range': [3, 7],
        'gravity': 0.4,
        'jump_strength': 10
    },
    'medium': {
        'name': 'MEDIUM', 
        'pipe_gap': 270,
        'spawn_time': 1600,
        'speed_range': [3, 10],
        'gravity': 0.6,
        'jump_strength': 12
    },
    'hard': {
        'name': 'HARD',
        'pipe_gap': 220,
        'spawn_time': 1200,
        'speed_range': [5, 12],
        'gravity': 0.8,
        'jump_strength': 14
    }
}

current_difficulty = 'medium'  # Độ khó mặc định

# Global variables for tracking scored pipes
scored_pipes = set()  # Set to track which pipes have been scored

def draw_floor():
	screen.blit(floor_surface,(floor_x_position,900))
	screen.blit(floor_surface,(floor_x_position + 576,900))

def create_pipe(): #hàm này để sinh các chướng ngại vật (ống)
	global random_pipe_position
	random_pipe_position = random.randint(400, 800) #mỗi lần tạo ra ống mới tại 1 vị trí ngẫu nhiên
	#sinh ra 2 ống trên và dưới và return chúng 
	pipe_gap = DIFFICULTIES[current_difficulty]['pipe_gap']
	bottom_pipe = pipe_surface.get_rect(midtop = (900,random_pipe_position)) 
	top_pipe = pipe_surface.get_rect(midbottom = (900,random_pipe_position-pipe_gap))
	return bottom_pipe, top_pipe
 
def create_powerup(): #hàm này tạo ra các powerup là tăng tốc và giảm tốc
	random_number =random.randint(1, 10)
	#lấy 1 số ngẫu nhiên từ 1 đến 10
	#nếu là số 2 thì tạo ra powerup tăng tốc
	#nếu là 3 thì tạo ra speedup giảm tốc
	#còn là những số khác thì không tạo powerup
	#return vị trí của powerup và mô tả của chúng: 'fast' hoặc 'slow' hoặc return 0 nếu không tạo powerup
	if random_number == 2:
		speedup = arrow_speedup_surface.get_rect(center = (900, random_pipe_position - 20))
		return [speedup, 'fast']
	# else: 
	elif random_number==3: 
		speedup = arrow_slow_surface.get_rect(center = (900, random_pipe_position - 20))
		return [speedup, 'slow']
	return 0

def move_pipes(pipes):
	# print(pipes)
	#di chuyển tất cả các ống trên mỗi khung hình với tốc độ được thể hiện bằng biến speed và return về list các ống đó để in ra
	#speed mặc định là 5  #với mỗi powerup tăng tốc thì speed tăng lên 1 đơn vị, tối đa là 
	for pipe in pipes:
		pipe.centerx -= speed
	
	# Remove pipes that are completely off screen and clean up scored_pipes set
	visible_pipes = []
	for pipe in pipes:
		if pipe.centerx > -52:  # Keep pipe if still visible
			visible_pipes.append(pipe)
		else:
			# Remove from scored_pipes set when pipe is off screen
			if id(pipe) in scored_pipes:
				scored_pipes.remove(id(pipe))
	
	return visible_pipes

def move_pws(pws):
	#cũng tương tự hàm move_pipes(), di chuyển các powerup với cùng tốc độ
	for powerup in pws:
		powerup[0].centerx -= speed
	return pws

def draw_pipes_powerup(pipes, pws):
	#vẽ lên màn hình list các ống và list các powerup bằng screen.blit()
	for pipe in pipes:
		if pipe.bottom >= 1024:
			screen.blit(pipe_surface, pipe)
		else:
			flip_pipe = pygame.transform.flip(pipe_surface, False, True)
			screen.blit(flip_pipe, pipe)
	for power in pws:
		if power[1]=='slow':
			screen.blit(arrow_slow_surface, power[0])
		else:
			screen.blit(arrow_speedup_surface, power[0])

def check_collision(pipes):
	global score, scored_pipes
	'''
	hàm này để kiểm tra sự va chạm của bird với các chướng ngại vật (bản chất là các hình chữ nhật) bằng hàm colliderect
	duyệt tất cả các ống trong list và kiểm tra sự va chạm giữa các con chim và các ống đó
	ngoài ra cũng cần kiểm tra xem có con chim nào đã bay lên quá cao hoặc đã rơi xuống đất chưa (tức là chạm vào rìa trên hoặc rìa dưới)
	nếu có va chạm, game kết thúc
	'''
	
	# Tính điểm dựa trên chế độ chơi - Fixed logic
	for pipe in pipes:
		pipe_id = id(pipe)
		
		if current_game_mode == 'single':
			# Chế độ 1 player: tính 1 điểm khi bird qua mỗi cặp ống
			# Kiểm tra nếu bird đã qua ống và chưa được tính điểm
			if (bird1_rectangle.centerx > pipe.centerx + 26 and 
				pipe_id not in scored_pipes and 
				pipe.bottom >= 1024):  # Chỉ tính điểm cho ống dưới
				score_sound.play()
				score += 1
				scored_pipes.add(pipe_id)
		else:
			# Chế độ 2 players: chỉ tính điểm khi CẢ 2 birds cùng vượt qua ống
			if (bird1_rectangle.centerx > pipe.centerx + 26 and 
				bird2_rectangle.centerx > pipe.centerx + 26 and
				pipe_id not in scored_pipes and 
				pipe.bottom >= 1024):  # Chỉ tính điểm cho ống dưới
				score_sound.play()
				score += 1
				scored_pipes.add(pipe_id)
	
	# Kiểm tra va chạm với ống cho bird1
	for pipe in pipes:
		if bird1_rectangle.colliderect(pipe):
			death_sound.play()
			return False
	
	# Chỉ kiểm tra va chạm cho bird2 nếu đang ở chế độ 2 players
	if current_game_mode == 'multiplayer':
		for pipe in pipes:
			if bird2_rectangle.colliderect(pipe):
				death_sound.play()
				return False
		
		# Kiểm tra bird2 có chạm rìa màn hình không
		if bird2_rectangle.top <= -100 or bird2_rectangle.bottom >= 900:
			death_sound.play()
			return False
		
	# Kiểm tra bird1 có chạm rìa màn hình không
	if bird1_rectangle.top <= -100 or bird1_rectangle.bottom >= 900:
		death_sound.play()
		return False
	
	return True

def check_collision_powerups(pws):
	'''
	hàm này để kiểm tra xem các con chim có chạm vào được các powerups
	nguyên lý hoạt động tương tự hàm kiểm tra va chạm với ống check_collision():
	là duyệt qua tất cả các powerups có trong list các powerups được truyền vào hàm này và kiểm tra xem chim có va chạm với chúng không
	'''
	global speed 
	speed_range = DIFFICULTIES[current_difficulty]['speed_range']
	i=0
	while i < len(pws):
		collision = False
		
		# Kiểm tra va chạm với bird1
		if bird1_rectangle.colliderect(pws[i][0]):
			collision = True
		
		# Chỉ kiểm tra va chạm với bird2 nếu đang ở chế độ 2 players
		if current_game_mode == 'multiplayer' and bird2_rectangle.colliderect(pws[i][0]):
			collision = True
		
		if collision:
			if pws[i][1]=='fast': #nếu có sự va chạm với powerup tăng tốc, tốc độ (speed) sẽ tăng 1 đơn vị
				speed = min(speed+1, speed_range[1])
				powerup_faster_sound.play()
				pws.pop(i)
			else: #nếu có sự va chạm với powerup giảm tốc, tốc độ (speed) sẽ giảm 1 đơn vị
				speed = max(speed-1, speed_range[0])
				powerup_slower_sound.play()
				pws.pop(i)
		else:
			i+=1

def rotate_bird(bird, index):
	'''
	hàm này trả về hình ảnh con chim bị xoay trong lúc di chuyển
	'''
	if index==1:
		new_bird = pygame.transform.rotate(bird, -bird1_speed*3)
		return new_bird
	else: 
		new_bird = pygame.transform.rotate(bird, -bird2_speed*3)
		return new_bird
        
def score_display(game_state):
	'''
	game_state là biến lưu trạng thái hiện tại của trò chơi
	'main_game' tương ứng với đang chơi, 'game_over' tương ứng với lúc game đã kết thúc và đang trong trạng thái chờ kích hoạt game mới
	'''
	#tạo số điểm bằng font chữ của game và in ra màn hình
	if game_state == 'main_game':
		score_surface = font.render(str(int(score)), True, (255,255,255))
		screen.blit(score_surface, (width_game//2, 100))
		
		# Display current difficulty and game mode
		difficulty_surface = small_font.render(f'Difficulty: {DIFFICULTIES[current_difficulty]["name"]}', True, (255,255,255))
		screen.blit(difficulty_surface, (20, 20))
		
		mode_surface = small_font.render(f'Mode: {GAME_MODES[current_game_mode]["name"]}', True, (255,255,255))
		screen.blit(mode_surface, (20, 45))
		
	#nếu game đã kết thúc, in ra điểm đã đạt được và cả high_score ở phía dưới của điểm hiện tại nữa
	if game_state == 'game_over':
		score_surface = font.render(f'Score: {int(score)}', True, (255,255,255))
		screen.blit(score_surface, (width_game//3, 100))

		high_score_surface = font.render(f'High Score: {int(high_score)}', True, (255,255,255))
		screen.blit(high_score_surface, (width_game//3, 185))

def draw_game_mode_menu():
	"""Draw game mode selection menu"""
	# Semi-transparent background
	overlay = pygame.Surface((width_game, height_game))
	overlay.set_alpha(128)
	overlay.fill((0, 0, 0))
	screen.blit(overlay, (0, 0))
	
	# Title
	title_surface = font.render('SELECT GAME MODE', True, (255, 255, 255))
	title_rect = title_surface.get_rect(center=(width_game//2, 200))
	screen.blit(title_surface, title_rect)
	
	# Game mode options
	y_start = 300
	for i, (key, mode) in enumerate(GAME_MODES.items()):
		color = (255, 255, 0) if key == current_game_mode else (255, 255, 255)
		mode_surface = font.render(f'{i+1}. {mode["name"]}', True, color)
		mode_rect = mode_surface.get_rect(center=(width_game//2, y_start + i*80))
		screen.blit(mode_surface, mode_rect)
		
		# Description
		desc_surface = small_font.render(mode["description"], True, (200, 200, 200))
		desc_rect = desc_surface.get_rect(center=(width_game//2, y_start + i*80 + 25))
		screen.blit(desc_surface, desc_rect)
	
	# Instructions
	instruction_surface = small_font.render('Press 1 or 2 to select | SPACE to continue', True, (255, 255, 255))
	instruction_rect = instruction_surface.get_rect(center=(width_game//2, 600))
	screen.blit(instruction_surface, instruction_rect)

def draw_difficulty_menu():
	"""Draw difficulty selection menu"""
	# Semi-transparent background
	overlay = pygame.Surface((width_game, height_game))
	overlay.set_alpha(128)
	overlay.fill((0, 0, 0))
	screen.blit(overlay, (0, 0))
	
	# Title
	title_surface = font.render('SELECT DIFFICULTY', True, (255, 255, 255))
	title_rect = title_surface.get_rect(center=(width_game//2, 200))
	screen.blit(title_surface, title_rect)
	
	# Difficulty options
	y_start = 300
	for i, (key, diff) in enumerate(DIFFICULTIES.items()):
		color = (255, 255, 0) if key == current_difficulty else (255, 255, 255)
		diff_surface = font.render(f'{i+1}. {diff["name"]}', True, color)
		diff_rect = diff_surface.get_rect(center=(width_game//2, y_start + i*80))
		screen.blit(diff_surface, diff_rect)
	
	# Instructions
	instruction_surface = small_font.render('Press 1, 2, 3 to select | SPACE to start', True, (255, 255, 255))
	instruction_rect = instruction_surface.get_rect(center=(width_game//2, 600))
	screen.blit(instruction_surface, instruction_rect)
	
	# Current difficulty details
	details = DIFFICULTIES[current_difficulty]
	detail_text = [
		f"Pipe Gap: {details['pipe_gap']}px",
		f"Spawn Time: {details['spawn_time']/1000}s",
		f"Gravity: {details['gravity']}",
		f"Jump Power: {details['jump_strength']}"
	]
	
	for i, text in enumerate(detail_text):
		detail_surface = small_font.render(text, True, (200, 200, 200))
		detail_rect = detail_surface.get_rect(center=(width_game//2, 700 + i*25))
		screen.blit(detail_surface, detail_rect)

def update_score(score, high_score): #cập nhật kỷ lục mới
	high_score = max(high_score, score)
	return high_score

def reset_spawn_timer():
	"""Reset spawn timer according to current difficulty"""
	spawn_time = DIFFICULTIES[current_difficulty]['spawn_time']
	pygame.time.set_timer(SPAWN, spawn_time)

def reset_game():
	"""Reset game state for new game"""
	global bird1_speed, bird2_speed, score, speed, scored_pipes
	pipe_list.clear()
	powerup_list.clear()
	scored_pipes.clear()  # Clear scored pipes tracking
	bird1_rectangle.center = (100, height_game//2)
	bird1_speed = 0
	
	if current_game_mode == 'multiplayer':
		bird2_rectangle.center = (200, height_game//2)
		bird2_speed = 0
	else:
		# Ẩn bird2 khi chơi single player
		bird2_rectangle.center = (-100, -100)  # Di chuyển ra khỏi màn hình
		bird2_speed = 0
	
	score = 0
	# Reset speed according to difficulty
	speed_range = DIFFICULTIES[current_difficulty]['speed_range']
	speed = (speed_range[0] + speed_range[1]) // 2

'''
khởi tạo cửa sổ trò chơi
chiều rộng 800px, dài 1024px
'''
width_game=800
height_game=1024
pygame.init()
screen = pygame.display.set_mode((800,1024))        #màn hình chính của game
clock = pygame.time.Clock()                         #tạo 1 clock để quản lý tốc độ khung hình (fps) 

# Try to load custom font, fallback to default if not found
try:
    font = pygame.font.Font('assets/04B_19.TTF',40)   #font chữ cho game
    small_font = pygame.font.Font('assets/04B_19.TTF',20)   #font chữ nhỏ hơn
except:
    font = pygame.font.Font(None, 40)   # Use default font
    small_font = pygame.font.Font(None, 20)   # Use default font

gravity = DIFFICULTIES[current_difficulty]['gravity']		#gravity from difficulty settings
bird1_speed = 0			#speed of bird 1
bird2_speed = 0			#speed of bird 2
game_active = False		#indicates whether game is being played, initialized as False means not playing yet
show_game_mode_menu = True  #show game mode selection menu
show_difficulty_menu = False  #show difficulty selection menu
score = 0				#score starts from 0
high_score = 0			#save highest record
speed=5					#initial speed is 5

# Try to load images, use fallback if not found
try:
	background_list=[]		#list các background để chọn

	background_list.append(pygame.image.load('assets/background-day_main.png'))

	pipes_image_list=[pygame.image.load('assets/pipe-green2x.png'), pygame.image.load('assets/pipe-red2x.png')	]

	background_surface = background_list[0]

	#một vài hình ảnh các vật trong game

	floor_surface = pygame.image.load('assets/base2x.png')						#nền đất
	floor_x_position = 0														#vị trí ban đầu của nền đất
	bird1_surface = pygame.image.load('assets/bluebird-midflap2x.png')			#hình con chim số 1
	bird1_rectangle = bird1_surface.get_rect(center = (100,height_game//2))		#vị trí chim số 1
	bird2_surface = pygame.image.load('assets/yellowbird-midflap2x.png')		#hình con chim số 2
	bird2_rectangle = bird2_surface.get_rect(center = (200, height_game//2))	#vị trí chim số 2
	arrow_slow_surface=pygame.image.load('assets/arrow_reverse.png')			#hình powerup giảm tốc
	arrow_speedup_surface=pygame.image.load('assets/arrow.png')					#hình powerup tăng tốc
	pipe_surface = pygame.image.load('assets/pipe-green2x.png')					#hình cái ống
	get_ready_surface = pygame.transform.scale2x(pygame.image.load('assets/message.png'))	#màn hình get_ready
	get_ready_rectangle = get_ready_surface.get_rect(center = (width_game//2, height_game//2)) 
except:
	# Create simple colored rectangles as fallback
	background_surface = pygame.Surface((width_game, height_game))
	background_surface.fill((135, 206, 235))  # Sky blue
	
	floor_surface = pygame.Surface((576, 112))
	floor_surface.fill((222, 184, 135))  # Tan color
	floor_x_position = 0
	
	bird1_surface = pygame.Surface((34, 24))
	bird1_surface.fill((0, 0, 255))  # Blue bird
	bird1_rectangle = bird1_surface.get_rect(center = (100,height_game//2))
	
	bird2_surface = pygame.Surface((34, 24))
	bird2_surface.fill((255, 255, 0))  # Yellow bird
	bird2_rectangle = bird2_surface.get_rect(center = (200, height_game//2))
	
	arrow_slow_surface = pygame.Surface((20, 20))
	arrow_slow_surface.fill((255, 0, 0))  # Red arrow
	
	arrow_speedup_surface = pygame.Surface((20, 20))
	arrow_speedup_surface.fill((0, 255, 0))  # Green arrow
	
	pipe_surface = pygame.Surface((52, 320))
	pipe_surface.fill((0, 128, 0))  # Green pipe
	pipes_image_list = [pipe_surface]
	
	get_ready_surface = pygame.Surface((184, 267))
	get_ready_surface.fill((255, 255, 255))  # White rectangle
	get_ready_rectangle = get_ready_surface.get_rect(center = (width_game//2, height_game//2)) 

#2 list chứa các ống và các powerups
pipe_list = []																
powerup_list=[]

#tạo USEREVENT mới là SPAWN
#dùng hàm set_timer để kích hoạt chúng theo độ khó
SPAWN = pygame.USEREVENT
reset_spawn_timer()

# Try to load sounds, use fallback if not found
try:
	flap_sound = pygame.mixer.Sound('assets/wing.wav')
	death_sound = pygame.mixer.Sound('assets/hit.wav')
	score_sound = pygame.mixer.Sound('assets/point.wav')
	powerup_faster_sound = pygame.mixer.Sound('assets/faster.mp3')
	powerup_slower_sound = pygame.mixer.Sound('assets/slower.mp3')
except:
	# Create empty sound objects if files not found
	flap_sound = pygame.mixer.Sound(buffer=b'')
	death_sound = pygame.mixer.Sound(buffer=b'')
	score_sound = pygame.mixer.Sound(buffer=b'')
	powerup_faster_sound = pygame.mixer.Sound(buffer=b'')
	powerup_slower_sound = pygame.mixer.Sound(buffer=b'')

#vòng lặp chính của game
while True:
	for event in pygame.event.get():

		if event.type == pygame.QUIT:
			pygame.quit() #cài đặt tắt trò chơi khi bấm dấu X trên góc cửa sổ trò chơi
			sys.exit()

		#nếu có phím được bấm, chạy đoạn code này để xử lý với từng phím được ấn
		if event.type == pygame.KEYDOWN:     
			if event.key == pygame.K_ESCAPE: #cũng có thể thoát game bằng cách ấn phím Esc
				pygame.quit()
				sys.exit()
			
			# Handle game mode selection menu
			if show_game_mode_menu:
				if event.key == pygame.K_1:
					current_game_mode = 'single'
				elif event.key == pygame.K_2:
					current_game_mode = 'multiplayer'
				elif event.key == pygame.K_SPACE:
					show_game_mode_menu = False
					show_difficulty_menu = True
			
			# Handle difficulty selection menu
			elif show_difficulty_menu:
				if event.key == pygame.K_1:
					current_difficulty = 'easy'
					gravity = DIFFICULTIES[current_difficulty]['gravity']
					reset_spawn_timer()
				elif event.key == pygame.K_2:
					current_difficulty = 'medium'
					gravity = DIFFICULTIES[current_difficulty]['gravity']
					reset_spawn_timer()
				elif event.key == pygame.K_3:
					current_difficulty = 'hard'
					gravity = DIFFICULTIES[current_difficulty]['gravity']
					reset_spawn_timer()
				elif event.key == pygame.K_SPACE:
					show_difficulty_menu = False
			
			# Handle game controls when not in menus
			elif not show_game_mode_menu and not show_difficulty_menu:
				if event.key == pygame.K_SPACE and game_active:  
					# SPACE key to control bird 1
					jump_strength = DIFFICULTIES[current_difficulty]['jump_strength']
					bird1_speed = 0
					bird1_speed -= jump_strength  
					flap_sound.play()
				
				if event.key == pygame.K_UP and game_active and current_game_mode == 'multiplayer':
					# UP key to control bird 2 (only in multiplayer mode)
					jump_strength = DIFFICULTIES[current_difficulty]['jump_strength']
					flap_sound.play()
					bird2_speed = 0
					bird2_speed -= jump_strength
	
				if event.key == pygame.K_SPACE and not game_active:
					# If game hasn't started yet, press SPACE to start new game
					pipe_surface=random.choice(pipes_image_list)
					game_active = True
					reset_game()

				if event.key == pygame.K_m and not game_active:
					# Press M to return to game mode selection menu
					show_game_mode_menu = True

		#If current event is SPAWN (generated according to difficulty timing) then call function to create new pipes and powerups
		if event.type == SPAWN and game_active:
			pipe_list.extend(create_pipe())
			tmp = create_powerup()
			if tmp!=0:
				powerup_list.append(tmp)

	#Display section
	#Display background first
	screen.blit(background_surface,(0,0))

	if show_game_mode_menu:
		# Display game mode selection menu
		draw_game_mode_menu()
	elif show_difficulty_menu:
		# Display difficulty selection menu
		draw_difficulty_menu()
	elif game_active:
		# bird movement
		#Each frame the birds must bear additional gravity force added to their falling speed bird_speed
		bird1_speed += gravity
		
		# Only update bird2 if in multiplayer mode
		if current_game_mode == 'multiplayer':
			bird2_speed += gravity

		#rotate birds
		rotated_bird1 = rotate_bird(bird1_surface, 1)
		
		#position (on y-axis) will change according to their falling speed by adding falling speed to their current y position
		bird1_rectangle.centery += bird1_speed

		#draw bird1 on screen with newly updated positions
		screen.blit(rotated_bird1, bird1_rectangle)
		
		# Only draw and update bird2 if in multiplayer mode
		if current_game_mode == 'multiplayer':
			rotated_bird2 = rotate_bird(bird2_surface, 2)
			bird2_rectangle.centery += bird2_speed
			screen.blit(rotated_bird2, bird2_rectangle)

		#call collision detection function with objects
		game_active = check_collision(pipe_list)
		check_collision_powerups(powerup_list)

		# move pipes and powerups each frame, then display on screen
		pipe_list = move_pipes(pipe_list)
		powerup_list = move_pws(powerup_list)
		draw_pipes_powerup(pipe_list, powerup_list)
	
		# display current score on screen
		score_display('main_game')

	else: #update and display game over message, current score, high score
		screen.blit(get_ready_surface, get_ready_rectangle)
		high_score = update_score(score, high_score)
		score_display('game_over')
		
		# Instructions to return to game mode menu
		back_surface = small_font.render('Press M to change game mode', True, (255, 255, 255))
		back_rect = back_surface.get_rect(center=(width_game//2, height_game//2 + 200))
		screen.blit(back_surface, back_rect)

	# each frame the ground will move back 1 pixel
	# if ground has moved too far back (about to go off screen) then reset to initial position and continue moving
	floor_x_position -= 1
	draw_floor()
	if floor_x_position <= -376:
		floor_x_position = 0

	#update what appears on screen and control frame rate at 60 FPS
	pygame.display.update()
	clock.tick(60)