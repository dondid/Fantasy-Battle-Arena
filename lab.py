import pygame
import sys
import random
import math
import os

# Initialize pygame
pygame.init()
pygame.font.init()

# Screen setup
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fantasy Battle Arena")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
GOLD = (255, 215, 0)
DARK_GREEN = (0, 100, 0)
GRAY = (100, 100, 100)
LIGHT_BLUE = (173, 216, 230)

# Fonts
font_small = pygame.font.SysFont('Arial', 16)
font_medium = pygame.font.SysFont('Arial', 24)
font_large = pygame.font.SysFont('Arial', 32)
font_title = pygame.font.SysFont('Arial', 48, bold=True)

# Game clock
clock = pygame.time.Clock()
FPS = 60

# Create an "images" folder if it doesn't exist
if not os.path.exists("images"):
    os.makedirs("images")
    print("Created 'images' folder. Please add character sprites to this folder.")


# Load images (now with placeholders that suggest adding real images)
def load_image(name, scale=1.0):
    image_path = os.path.join("images", f"{name}.png")

    # Try to load the actual image
    try:
        image = pygame.image.load(image_path)
        print(f"Loaded image: {image_path}")
    except:
        # If the image doesn't exist, create a placeholder with text prompting to add real images
        print(f"Image not found: {image_path}")
        size = (100, 150)
        image = pygame.Surface(size)

        if name == "player":
            image.fill(BLUE)
            text = "Add hero.png"
            color = WHITE
        elif name == "goblin":
            image.fill(GREEN)
            text = "Add goblin.png"
            color = BLACK
        elif name == "orc":
            image.fill(RED)
            text = "Add orc.png"
            color = WHITE
        elif name == "elf":
            image.fill(LIGHT_BLUE)
            text = "Add elf.png"
            color = BLACK
        else:
            image.fill(GRAY)
            text = f"Add {name}.png"
            color = WHITE

        # Add text to the placeholder
        font = pygame.font.SysFont('Arial', 14)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(size[0] // 2, size[1] // 2))
        image.blit(text_surface, text_rect)

    # Scale the image if needed
    if scale != 1.0:
        original_size = image.get_size()
        new_size = (int(original_size[0] * scale), int(original_size[1] * scale))
        image = pygame.transform.scale(image, new_size)

    return image


# Button class for UI
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.is_hovered = False
        self.font = font_medium

    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)

        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def update(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
            self.is_hovered = True
        else:
            self.current_color = self.color
            self.is_hovered = False

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False


# Game character classes
class Character:
    def __init__(self, name, char_type, health, attack, defense, x, y):
        self.name = name
        self.char_type = char_type
        self.max_health = health
        self.health = health
        self.attack = attack
        self.defense = defense
        self.level = 1
        self.experience = 0
        self.is_alive = True
        self.stunned = False

        # Position and animation
        self.x = x
        self.y = y
        self.original_x = x
        self.original_y = y
        self.image = load_image(char_type)
        self.rect = self.image.get_rect(center=(x, y))

        # Animation state
        self.animating = False
        self.animation_frames = 0
        self.animation_type = None
        self.animation_target = None

        # Load attack animation frames if they exist
        self.attack_frames = []
        for i in range(1, 4):  # Try to load 3 attack frames
            try:
                frame = load_image(f"{char_type}_attack{i}", scale=1.0)
                self.attack_frames.append(frame)
            except:
                # If we can't load an attack frame, just use the regular image
                pass

        # Load hit animation frames
        self.hit_frames = []
        try:
            self.hit_frames.append(load_image(f"{char_type}_hit", scale=1.0))
        except:
            # If we can't load a hit frame, just use the regular image
            pass

    def draw(self, surface):
        if not self.is_alive:
            # Draw character lying down if dead
            try:
                dead_image = load_image(f"{self.char_type}_dead")
                dead_rect = dead_image.get_rect(center=(self.x, self.y))
                surface.blit(dead_image, dead_rect)
            except:
                # Fall back to rotation if no specific dead image
                rotated_image = pygame.transform.rotate(self.image, 90)
                rotated_rect = rotated_image.get_rect(center=(self.x, self.y + 20))
                surface.blit(rotated_image, rotated_rect)
        else:
            # If character is attacking and we have attack frames
            if self.animating and self.animation_type == "attack" and self.attack_frames:
                # Choose appropriate attack frame based on animation progress
                frame_index = min(len(self.attack_frames) - 1, self.animation_frames // 5)
                attack_image = self.attack_frames[frame_index]
                attack_rect = attack_image.get_rect(center=(self.x, self.y))
                surface.blit(attack_image, attack_rect)
            # If character is being hit and we have hit frames
            elif self.animating and self.animation_type == "hit" and self.hit_frames:
                hit_image = self.hit_frames[0]
                hit_rect = hit_image.get_rect(center=(self.x, self.y))
                surface.blit(hit_image, hit_rect)
            # Otherwise use the default image
            else:
                surface.blit(self.image, self.rect)

        # Draw health bar
        health_bar_width = 100
        health_bar_height = 10
        health_ratio = self.health / self.max_health

        # Background (empty health)
        pygame.draw.rect(surface, RED,
                         (self.x - health_bar_width // 2,
                          self.y - 80,
                          health_bar_width,
                          health_bar_height))

        # Foreground (filled health)
        if health_ratio > 0:
            pygame.draw.rect(surface, GREEN,
                             (self.x - health_bar_width // 2,
                              self.y - 80,
                              int(health_bar_width * health_ratio),
                              health_bar_height))

        # Border
        pygame.draw.rect(surface, BLACK,
                         (self.x - health_bar_width // 2,
                          self.y - 80,
                          health_bar_width,
                          health_bar_height), 1)

        # Name and level
        name_text = font_small.render(f"{self.name} (Lvl {self.level})", True, BLACK)
        surface.blit(name_text, (self.x - name_text.get_width() // 2, self.y - 100))

        # Status effects
        if self.stunned:
            stun_text = font_small.render("STUNNED", True, RED)
            surface.blit(stun_text, (self.x - stun_text.get_width() // 2, self.y - 60))

        # Draw special effects
        if self.animation_type == "heal" and self.animating:
            draw_heal_effect(screen, self)

    def update_animation(self):
        if not self.animating:
            return

        if self.animation_type == "attack":
            if self.animation_frames < 10:  # Moving forward
                self.x += (self.animation_target.x - self.original_x) / 20
                self.animation_frames += 1
            elif self.animation_frames < 20:  # Moving back
                self.x -= (self.animation_target.x - self.original_x) / 20
                self.animation_frames += 1
            else:  # Animation finished
                self.animating = False
                self.animation_frames = 0
                self.x = self.original_x

        elif self.animation_type == "hit":
            if self.animation_frames < 5:  # Shake right
                self.x += 2
                self.animation_frames += 1
            elif self.animation_frames < 10:  # Shake left
                self.x -= 4
                self.animation_frames += 1
            elif self.animation_frames < 15:  # Back to center
                self.x += 2
                self.animation_frames += 1
            else:  # Animation finished
                self.animating = False
                self.animation_frames = 0
                self.x = self.original_x

        elif self.animation_type == "heal":
            if self.animation_frames < 15:
                self.animation_frames += 1
            else:
                self.animating = False
                self.animation_frames = 0

        # Update rectangle position
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def attack_target(self, target):
        if not self.is_alive:
            return f"{self.name} is dead and cannot attack!"

        if not target.is_alive:
            return f"{target.name} is already dead!"

        # Start attack animation
        self.animating = True
        self.animation_frames = 0
        self.animation_type = "attack"
        self.animation_target = target

        # Start hit animation for target
        target.animating = True
        target.animation_frames = 0
        target.animation_type = "hit"

        # Calculate damage
        damage = max(1, self.attack - target.defense // 2)
        damage += random.randint(-2, 2)  # Add some randomness
        damage = max(1, damage)  # Ensure at least 1 damage

        target.health -= damage

        if target.health <= 0:
            target.health = 0
            target.is_alive = False
            self.gain_experience(target.level * 10)
            return f"{self.name} attacked {target.name} for {damage} damage and killed them!"

        return f"{self.name} attacked {target.name} for {damage} damage!"

    def gain_experience(self, amount):
        self.experience += amount
        level_up_threshold = self.level * 20

        if self.experience >= level_up_threshold:
            self.level_up()
            return True
        return False

    def level_up(self):
        self.level += 1
        self.max_health += 5
        self.health = self.max_health
        self.attack += 2
        self.defense += 1

    def heal(self, amount):
        if not self.is_alive:
            return f"{self.name} is dead and cannot be healed!"

        self.animating = True
        self.animation_frames = 0
        self.animation_type = "heal"

        old_health = self.health
        self.health = min(self.max_health, self.health + amount)
        actual_heal = self.health - old_health

        return f"{self.name} was healed for {actual_heal} health points!"

    def special_ability(self, target):
        return f"{self.name} has no special ability!"


class Player(Character):
    def __init__(self, name, x, y):
        super().__init__(name, "player", health=25, attack=8, defense=5, x=x, y=y)
        self.potions = 3

    def use_potion(self):
        if not self.is_alive:
            return "You cannot use potions while dead!"

        if self.potions <= 0:
            return "You have no potions left!"

        self.potions -= 1
        heal_amount = self.max_health // 2
        result = self.heal(heal_amount)

        return f"You used a potion! {result} Potions left: {self.potions}"

    def special_ability(self, target):
        if not self.is_alive or not target.is_alive:
            return "Cannot use special ability now!"

        # Start special animation
        self.animating = True
        self.animation_frames = 0
        self.animation_type = "attack"  # Reuse attack animation for now
        self.animation_target = target

        # Start hit animation for target
        target.animating = True
        target.animation_frames = 0
        target.animation_type = "hit"

        # Critical strike - double damage with a chance to stun
        damage = self.attack * 2 - target.defense // 3
        damage = max(1, damage)
        target.health -= damage

        message = f"You use CRITICAL STRIKE on {target.name} for {damage} damage!"

        if random.random() < 0.3:  # 30% chance to stun
            message += f" {target.name} is stunned and will miss their next turn!"
            target.stunned = True

        if target.health <= 0:
            target.health = 0
            target.is_alive = False
            self.gain_experience(target.level * 10)
            message += f" You defeated {target.name}!"

        return message


class Goblin(Character):
    def __init__(self, name, x, y):
        super().__init__(name, "goblin", health=15, attack=5, defense=3, x=x, y=y)

    def special_ability(self, target):
        if not self.is_alive or not target.is_alive:
            return f"{self.name} cannot use special ability now!"

        # Start special animation
        self.animating = True
        self.animation_frames = 0
        self.animation_type = "attack"
        self.animation_target = target

        # Start hit animation for target
        target.animating = True
        target.animation_frames = 0
        target.animation_type = "hit"

        # Frenzy - multiple quick strikes
        hits = random.randint(2, 4)
        total_damage = 0

        for i in range(hits):
            damage = max(1, self.attack // 2 - target.defense // 4)
            target.health -= damage
            total_damage += damage

        message = f"{self.name} goes into a FRENZY and strikes {hits} times for {total_damage} total damage!"

        if target.health <= 0:
            target.health = 0
            target.is_alive = False
            message += f" {self.name} defeated {target.name}!"

        return message


class Orc(Character):
    def __init__(self, name, x, y):
        super().__init__(name, "orc", health=30, attack=7, defense=6, x=x, y=y)

    def special_ability(self, target):
        if not self.is_alive or not target.is_alive:
            return f"{self.name} cannot use special ability now!"

        # Start special animation
        self.animating = True
        self.animation_frames = 0
        self.animation_type = "attack"
        self.animation_target = target

        # Start hit animation for target
        target.animating = True
        target.animation_frames = 0
        target.animation_type = "hit"

        # Crushing blow - high damage with defense reduction
        damage = self.attack * 1.5 - target.defense // 4
        damage = max(1, int(damage))
        target.health -= damage

        old_defense = target.defense
        target.defense = max(0, target.defense - 2)
        defense_reduction = old_defense - target.defense

        message = f"{self.name} uses CRUSHING BLOW on {target.name} for {damage} damage and reduces defense by {defense_reduction}!"

        if target.health <= 0:
            target.health = 0
            target.is_alive = False
            message += f" {self.name} defeated {target.name}!"

        return message


class Elf(Character):
    def __init__(self, name, x, y):
        super().__init__(name, "elf", health=18, attack=6, defense=4, x=x, y=y)

    def special_ability(self, target):
        if not self.is_alive or not target.is_alive:
            return f"{self.name} cannot use special ability now!"

        # Start special animation
        self.animating = True
        self.animation_frames = 0
        self.animation_type = "attack"
        self.animation_target = target

        # Start hit animation for target
        target.animating = True
        target.animation_frames = 0
        target.animation_type = "hit"

        # Nature's blessing - deal damage and heal self
        damage = self.attack - target.defense // 3
        damage = max(1, damage)
        target.health -= damage

        heal_amount = damage // 2
        self.health = min(self.max_health, self.health + heal_amount)

        message = f"{self.name} uses NATURE'S BLESSING on {target.name} for {damage} damage and heals for {heal_amount}!"

        if target.health <= 0:
            target.health = 0
            target.is_alive = False
            message += f" {self.name} defeated {target.name}!"

        return message


# Battle class to manage the game
class Battle:
    def __init__(self):
        self.game_state = "main_menu"  # main_menu, battle, game_over, victory

        # Load background images
        self.menu_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.menu_bg.fill((100, 100, 150))
        self.battle_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.battle_bg.fill((220, 220, 220))

        try:
            self.menu_bg = pygame.image.load(os.path.join("images", "menu_bg.png"))
            self.menu_bg = pygame.transform.scale(self.menu_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            print("Menu background image not found, using default color")

        try:
            self.battle_bg = pygame.image.load(os.path.join("images", "battle_bg.png"))
            self.battle_bg = pygame.transform.scale(self.battle_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            print("Battle background image not found, using default color")

        # Create player character
        self.player = Player("Hero", 250, 300)

        # Create enemies
        self.goblin = Goblin("Gobbly", 750, 200)
        self.orc = Orc("Grog", 750, 300)
        self.elf = Elf("Elindril", 750, 400)

        self.enemies = [self.goblin, self.orc, self.elf]
        self.current_enemy_index = 0
        self.current_enemy = self.enemies[self.current_enemy_index]

        # Create UI buttons
        button_width = 150
        button_height = 50
        button_y = 500
        button_spacing = 20

        self.attack_button = Button(
            100, button_y, button_width, button_height,
            "Attack", WHITE, LIGHT_BLUE
        )

        self.special_button = Button(
            100 + button_width + button_spacing, button_y,
            button_width, button_height,
            "Special", WHITE, LIGHT_BLUE
        )

        self.potion_button = Button(
            100 + (button_width + button_spacing) * 2, button_y,
            button_width, button_height,
            f"Potion ({self.player.potions})", WHITE, LIGHT_BLUE
        )

        self.next_enemy_button = Button(
            100 + (button_width + button_spacing) * 3, button_y,
            button_width, button_height,
            "Next Enemy", WHITE, LIGHT_BLUE
        )

        self.buttons = [
            self.attack_button,
            self.special_button,
            self.potion_button,
            self.next_enemy_button
        ]

        # Battle state
        self.player_turn = True
        self.battle_active = True
        self.battle_message = "Battle begins! Your turn!"
        self.message_timer = 180  # Frames to display a message

        # Main menu button
        self.start_button = Button(
            SCREEN_WIDTH // 2 - 100, 400,
            200, 50,
            "Start Battle", WHITE, LIGHT_BLUE
        )

        # Game over / victory buttons
        self.restart_button = Button(
            SCREEN_WIDTH // 2 - 100, 400,
            200, 50,
            "Play Again", WHITE, LIGHT_BLUE
        )

    def draw_battle_scene(self):
        # Draw background
        screen.blit(self.battle_bg, (0, 0))

        # Draw battle area
        pygame.draw.rect(screen, (200, 200, 200, 150), (50, 50, SCREEN_WIDTH - 100, 400), border_radius=5)
        pygame.draw.rect(screen, BLACK, (50, 50, SCREEN_WIDTH - 100, 400), 2, border_radius=5)

        # Draw characters
        self.player.draw(screen)
        self.current_enemy.draw(screen)

        # Draw UI buttons
        for button in self.buttons:
            button.draw(screen)

        # Update potion button text
        self.potion_button.text = f"Potion ({self.player.potions})"

        # Draw battle message
        if self.message_timer > 0:
            message_bg = pygame.Rect(SCREEN_WIDTH // 2 - 250, 10, 500, 40)
            pygame.draw.rect(screen, (0, 0, 0, 150), message_bg, border_radius=10)
            pygame.draw.rect(screen, BLACK, message_bg, 2, border_radius=10)

            message_surface = font_medium.render(self.battle_message, True, WHITE)
            screen.blit(message_surface, (SCREEN_WIDTH // 2 - message_surface.get_width() // 2, 20))
            self.message_timer -= 1

        # Draw turn indicator
        turn_text = "Player's Turn" if self.player_turn else "Enemy's Turn"
        turn_color = BLUE if self.player_turn else RED
        turn_surface = font_medium.render(turn_text, True, turn_color)
        screen.blit(turn_surface, (SCREEN_WIDTH - turn_surface.get_width() - 20, 20))

        # Draw player stats
        stat_x = 20
        stat_y = 20

        # Draw stat background
        stat_bg = pygame.Rect(stat_x - 5, stat_y - 5, 150, 105)
        pygame.draw.rect(screen, (0, 0, 0, 150), stat_bg, border_radius=5)
        pygame.draw.rect(screen, BLACK, stat_bg, 2, border_radius=5)

        stats = [
            f"Level: {self.player.level}",
            f"EXP: {self.player.experience}/{self.player.level * 20}",
            f"Attack: {self.player.attack}",
            f"Defense: {self.player.defense}"
        ]

        for stat in stats:
            stat_surface = font_small.render(stat, True, WHITE)
            screen.blit(stat_surface, (stat_x, stat_y))
            stat_y += 20

    def draw_main_menu(self):
        # Draw background
        screen.blit(self.menu_bg, (0, 0))

        # Draw title
        title_shadow = font_title.render("Fantasy Battle Arena", True, BLACK)
        screen.blit(title_shadow, (SCREEN_WIDTH // 2 - title_shadow.get_width() // 2 + 2, 102))

        title_surface = font_title.render("Fantasy Battle Arena", True, GOLD)
        screen.blit(title_surface, (SCREEN_WIDTH // 2 - title_surface.get_width() // 2, 100))

        # Draw subtitle
        subtitle_bg = pygame.Rect(SCREEN_WIDTH // 2 - 250, 180, 500, 50)
        pygame.draw.rect(screen, (0, 0, 0, 150), subtitle_bg, border_radius=10)

        subtitle_surface = font_medium.render("Face off against fearsome fantasy creatures!", True, WHITE)
        screen.blit(subtitle_surface, (SCREEN_WIDTH // 2 - subtitle_surface.get_width() // 2, 195))

        # Draw character previews
        char_spacing = 200
        start_x = SCREEN_WIDTH // 2 - (3 * char_spacing) // 2 + char_spacing // 2

        # Draw player preview
        player_image = self.player.image
        player_rect = player_image.get_rect(center=(start_x - char_spacing, 300))
        screen.blit(player_image, player_rect)

        # Draw enemy previews
        for i, enemy in enumerate(self.enemies):
            enemy_image = enemy.image
            enemy_rect = enemy_image.get_rect(center=(start_x + i * char_spacing, 300))
            screen.blit(enemy_image, enemy_rect)

        # Draw start button
        self.start_button.draw(screen)

    def draw_game_over(self):
        # Draw background (red tint)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((255, 0, 0))
        overlay.set_alpha(100)

        screen.blit(self.battle_bg, (0, 0))
        screen.blit(overlay, (0, 0))

        # Draw title
        title_surface = font_title.render("Game Over", True, WHITE)
        screen.blit(title_surface, (SCREEN_WIDTH // 2 - title_surface.get_width() // 2, 150))

        # Draw message
        message_surface = font_medium.render("You have been defeated!", True, WHITE)
        screen.blit(message_surface, (SCREEN_WIDTH // 2 - message_surface.get_width() // 2, 250))

        # Draw restart button
        self.restart_button.draw(screen)

    def draw_victory(self):
        # Draw background (green tint)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 255, 0))
        overlay.set_alpha(100)

        screen.blit(self.battle_bg, (0, 0))
        screen.blit(overlay, (0, 0))

        # Draw title
        title_surface = font_title.render("Victory!", True, GOLD)
        screen.blit(title_surface, (SCREEN_WIDTH // 2 - title_surface.get_width() // 2, 150))

        # Draw message
        message_surface = font_medium.render("You have defeated all enemies!", True, WHITE)
        screen.blit(message_surface, (SCREEN_WIDTH // 2 - message_surface.get_width() // 2, 250))

        # Draw player's final stats
        stats_bg = pygame.Rect(SCREEN_WIDTH // 2 - 100, 300, 200, 80)
        pygame.draw.rect(screen, (0, 0, 0, 150), stats_bg, border_radius=10)

        stats = [
            f"Final Level: {self.player.level}",
            f"Monsters Defeated: {len([enemy for enemy in self.enemies if not enemy.is_alive])}",
            f"Potions Remaining: {self.player.potions}"
        ]

        for i, stat in enumerate(stats):
            stat_surface = font_small.render(stat, True, WHITE)
            screen.blit(stat_surface, (SCREEN_WIDTH // 2 - stat_surface.get_width() // 2, 310 + i * 20))

        # Draw restart button
        self.restart_button.draw(screen)

    def update_battle(self):
        # Update character animations
        self.player.update_animation()
        self.current_enemy.update_animation()

        # Check if the enemy is dead and make the next enemy current
        if not self.current_enemy.is_alive:
            all_dead = True
            for enemy in self.enemies:
                if enemy.is_alive:
                    all_dead = False
                    break

            if all_dead:
                self.game_state = "victory"

        # Check if player is dead
        if not self.player.is_alive:
            self.game_state = "game_over"

        # If it's the enemy's turn and no animations are playing, make the enemy act
        if not self.player_turn and not self.player.animating and not self.current_enemy.animating:
            self.enemy_action()

    def enemy_action(self):
        if not self.current_enemy.is_alive:
            # Find next alive enemy
            alive_enemies = [enemy for enemy in self.enemies if enemy.is_alive]
            if alive_enemies:
                self.current_enemy = alive_enemies[0]
            else:
                self.game_state = "victory"
                return

        if self.current_enemy.stunned:
            self.battle_message = f"{self.current_enemy.name} is stunned and misses their turn!"
            self.message_timer = 180
            self.current_enemy.stunned = False
        else:
            # Decide what the enemy will do
            action = random.random()

            if action < 0.7:  # 70% chance to use normal attack
                result = self.current_enemy.attack_target(self.player)
            else:  # 30% chance to use special ability
                result = self.current_enemy.special_ability(self.player)

            self.battle_message = result
            self.message_timer = 180

        # End enemy turn after a delay
        pygame.time.delay(500)  # Small delay for readability
        self.player_turn = True

    def change_enemy(self):
        # Cycle to the next enemy
        alive_enemies = [enemy for enemy in self.enemies if enemy.is_alive]

        if not alive_enemies:
            self.game_state = "victory"
            return

        if self.current_enemy in alive_enemies:
            current_index = alive_enemies.index(self.current_enemy)
            next_index = (current_index + 1) % len(alive_enemies)
            self.current_enemy = alive_enemies[next_index]
        else:
            self.current_enemy = alive_enemies[0]

        self.battle_message = f"You are now facing {self.current_enemy.name}!"
        self.message_timer = 180

    def reset_game(self):
        # Reset player
        self.player = Player("Hero", 250, 300)

        # Reset enemies
        self.goblin = Goblin("Gobbly", 750, 200)
        self.orc = Orc("Grog", 750, 300)
        self.elf = Elf("Elindril", 750, 400)

        self.enemies = [self.goblin, self.orc, self.elf]
        self.current_enemy_index = 0
        self.current_enemy = self.enemies[self.current_enemy_index]

        # Reset battle state
        self.player_turn = True
        self.battle_active = True
        self.battle_message = "Battle begins! Your turn!"
        self.message_timer = 180

        # Return to main menu
        self.game_state = "main_menu"

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if self.game_state == "main_menu":
                self.start_button.update(mouse_pos)
                if self.start_button.is_clicked(event):
                    self.game_state = "battle"

            elif self.game_state == "battle":
                # Only process button clicks during player's turn and when no animations are active
                if self.player_turn and not self.player.animating and not self.current_enemy.animating:
                    # Update all buttons
                    for button in self.buttons:
                        button.update(mouse_pos)

                    # Check for button clicks
                    if self.attack_button.is_clicked(event):
                        result = self.player.attack_target(self.current_enemy)
                        self.battle_message = result
                        self.message_timer = 180
                        self.player_turn = False

                    elif self.special_button.is_clicked(event):
                        result = self.player.special_ability(self.current_enemy)
                        self.battle_message = result
                        self.message_timer = 180
                        self.player_turn = False

                    elif self.potion_button.is_clicked(event):
                        result = self.player.use_potion()
                        self.battle_message = result
                        self.message_timer = 180
                        if "Potions left" in result:  # If potion was successfully used
                            self.player_turn = False

                    elif self.next_enemy_button.is_clicked(event):
                        self.change_enemy()

            elif self.game_state == "game_over" or self.game_state == "victory":
                self.restart_button.update(mouse_pos)
                if self.restart_button.is_clicked(event):
                    self.reset_game()

    def run(self):
        while True:
            self.handle_events()

            if self.game_state == "main_menu":
                self.draw_main_menu()
            elif self.game_state == "battle":
                self.update_battle()
                self.draw_battle_scene()
            elif self.game_state == "game_over":
                self.draw_game_over()
            elif self.game_state == "victory":
                self.draw_victory()

            pygame.display.flip()
            clock.tick(FPS)


# Draw special effects
def draw_particle_effect(surface, x, y, color, size, count):
    for _ in range(count):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1, 3)
        particle_x = x + math.cos(angle) * random.uniform(0, 20)
        particle_y = y + math.sin(angle) * random.uniform(0, 20)
        particle_size = random.uniform(size / 2, size)

        pygame.draw.circle(surface, color, (int(particle_x), int(particle_y)), int(particle_size))


def draw_heal_effect(surface, character):
    if character.animation_type == "heal" and character.animating:
        particles = int(character.animation_frames)
        draw_particle_effect(surface, character.x, character.y, GREEN, 5, particles)


def main():
    # Print instructions for adding images
    print("\nFantasy Battle Arena")
    print("--------------------")
    print("To use custom character sprites, add the following PNG files to the 'images' folder:")
    print("- player.png - Your hero character")
    print("- player_attack1.png, player_attack2.png, player_attack3.png - Hero attack animations")
    print("- player_hit.png - Hero getting hit animation")
    print("- player_dead.png - Hero defeated animation")
    print("\nRepeat the same pattern for other characters:")
    print("- goblin.png, goblin_attack1.png, etc.")
    print("- orc.png, orc_attack1.png, etc.")
    print("- elf.png, elf_attack1.png, etc.")
    print("\nBackground images:")
    print("- menu_bg.png - Main menu background")
    print("- battle_bg.png - Battle scene background")

    # Start the game
    game = Battle()
    game.run()


if __name__ == "__main__":
    main()
