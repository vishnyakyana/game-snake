import random
from typing import Optional, Tuple

import pygame
from pygame.locals import KEYDOWN, K_DOWN, K_ESCAPE, K_LEFT, K_RIGHT, K_UP, QUIT

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвета
BOARD_BACKGROUND_COLOR = (0, 0, 0)  # черный
SNAKE_COLOR = (0, 255, 0)  # зеленый
APPLE_COLOR = (255, 0, 0)  # красный


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(
        self,
        position: Optional[Tuple[int, int]] = None,
        body_color: Optional[Tuple[int, int, int]] = None,
    ) -> None:
        """
        Инициализирует игровой объект.

        Args:
            position: Начальная позиция объекта (x, y)
            body_color: Цвет объекта (R, G, B)
        """
        if position is None:
            position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.position = position

        if body_color is None:
            body_color = (255, 255, 255)  # белый по умолчанию
        self.body_color = body_color

    def draw(self, surface: pygame.Surface) -> None:
        """
        Абстрактный метод для отрисовки объекта.

        Args:
            surface: Поверхность для отрисовки
        """
        pass


class Apple(GameObject):
    """Класс яблока."""

    def __init__(self) -> None:
        """Инициализирует яблоко со случайной позицией."""
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position()

    def randomize_position(self) -> None:
        """Устанавливает случайное положение яблока на игровом поле."""
        x = random.randint(0, GRID_WIDTH - 1) * GRID_SIZE
        y = random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        self.position = (x, y)

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает яблоко на игровом поле."""
        rect = pygame.Rect(
            (self.position[0], self.position[1]),
            (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, (255, 255, 255), rect, 1)


class Snake(GameObject):
    """Класс змейки."""

    def __init__(self) -> None:
        """Инициализирует змейку в начальном состоянии."""
        super().__init__(body_color=SNAKE_COLOR)
        self.reset()
        self.last: Optional[Tuple[int, int]] = None

    def reset(self) -> None:
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))]
        self.direction = RIGHT
        self.next_direction: Optional[Tuple[int, int]] = None

    def update_direction(self) -> None:
        """Обновляет направление движения змейки."""
        if self.next_direction:
            opposite_x = self.direction[0] * -1
            opposite_y = self.direction[1] * -1
            if not (self.next_direction[0] == opposite_x and
                    self.next_direction[1] == opposite_y):
                self.direction = self.next_direction
            self.next_direction = None

    def get_head_position(self) -> Tuple[int, int]:
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def move(self) -> None:
        """Обновляет позицию змейки на одну ячейку."""
        self.update_direction()

        self.last = self.positions[-1] if self.positions else None

        head_x, head_y = self.get_head_position()

        dir_x, dir_y = self.direction
        new_x = (head_x + (dir_x * GRID_SIZE)) % SCREEN_WIDTH
        new_y = (head_y + (dir_y * GRID_SIZE)) % SCREEN_HEIGHT
        new_position = (new_x, new_y)

        if new_position in self.positions[1:]:
            self.reset()
            return

        self.positions.insert(0, new_position)

        if len(self.positions) > self.length:
            self.positions.pop()

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает змейку на игровом поле."""
        if self.last:
            last_rect = pygame.Rect(
                (self.last[0], self.last[1]),
                (GRID_SIZE, GRID_SIZE)
            )
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, last_rect)

        for i, (x, y) in enumerate(self.positions):
            rect = pygame.Rect(
                (x, y),
                (GRID_SIZE, GRID_SIZE)
            )
            pygame.draw.rect(surface, self.body_color, rect)
            pygame.draw.rect(surface, (0, 200, 0), rect, 1)

            if i == 0:
                eye_size = GRID_SIZE // 5
                if self.direction == RIGHT:
                    eye1_pos = (x + GRID_SIZE - eye_size - 2, y + 5)
                    eye2_pos = (x + GRID_SIZE - eye_size - 2,
                                y + GRID_SIZE - 5 - eye_size)
                elif self.direction == LEFT:
                    eye1_pos = (x + 2, y + 5)
                    eye2_pos = (x + 2, y + GRID_SIZE - 5 - eye_size)
                elif self.direction == UP:
                    eye1_pos = (x + 5, y + 2)
                    eye2_pos = (x + GRID_SIZE - 5 - eye_size, y + 2)
                else:
                    eye1_pos = (x + 5, y + GRID_SIZE - eye_size - 2)
                    eye2_pos = (x + GRID_SIZE - 5 - eye_size,
                                y + GRID_SIZE - eye_size - 2)

                pygame.draw.rect(
                    surface,
                    (255, 255, 255),
                    (eye1_pos[0], eye1_pos[1], eye_size, eye_size)
                )
                pygame.draw.rect(
                    surface,
                    (255, 255, 255),
                    (eye2_pos[0], eye2_pos[1], eye_size, eye_size)
                )


def handle_keys(snake: Snake) -> None:
    """Обрабатывает нажатия клавиш для управления змейкой."""
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == KEYDOWN:
            if event.key == K_UP:
                snake.next_direction = UP
            elif event.key == K_DOWN:
                snake.next_direction = DOWN
            elif event.key == K_LEFT:
                snake.next_direction = LEFT
            elif event.key == K_RIGHT:
                snake.next_direction = RIGHT
            elif event.key == K_ESCAPE:
                pygame.quit()
                raise SystemExit


def main() -> None:
    """Основная функция игры."""
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Изгиб Питона - Змейка')

    snake = Snake()
    apple = Apple()

    clock = pygame.time.Clock()

    font = pygame.font.Font(None, 36)

    while True:
        handle_keys(snake)

        snake.update_direction()

        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position()

            while apple.position in snake.positions:
                apple.randomize_position()

        screen.fill(BOARD_BACKGROUND_COLOR)

        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(screen, (40, 40, 40), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(screen, (40, 40, 40), (0, y), (SCREEN_WIDTH, y))

        apple.draw(screen)
        snake.draw(screen)

        score_text = font.render(
            f'Длина: {snake.length}', True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        instructions_text = 'Управление: стрелки, ESC - выход'
        instructions = font.render(instructions_text, True, (200, 200, 200))
        screen.blit(instructions, (10, SCREEN_HEIGHT - 40))

        pygame.display.update()

        clock.tick(10)


if __name__ == '__main__':
    main()