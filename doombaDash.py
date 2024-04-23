import pygame
import math

# Initialize Pygame and Joystick
pygame.init()
pygame.joystick.init()

# Set up display
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Doomba Dashboard V1.0")

# Constants
max_rpm = 1300
max_speed = 100  # Maximum speed
deadband = 0.1  # Deadband threshold
wheel_conversion_factor = 8 / 2  # Wheel size to robot size conversion factor

# Variables for FPS calculation
frames = 0
start_time = pygame.time.get_ticks()
fps = 0  # Initialize FPS variable


# Function to apply deadband
def apply_deadband(value, threshold):
    if abs(value) < threshold:
        return 0
    return value

# Function to rotate a surface around its center
def rotate_surface(surface, angle, center_pos):
    rotated_surface = pygame.transform.rotate(surface, angle)
    rotated_rect = rotated_surface.get_rect(center=center_pos)
    return rotated_surface, rotated_rect.topleft


# Function to get wheel RPMs
def get_wheel_rpms(speed, heading, target_rpm, imu_data, conversion_factor):
    right_wheel_rpm = (
        speed * max_speed * math.cos(math.radians(heading) * imu_data)
        + target_rpm * conversion_factor
    )
    left_wheel_rpm = (
        -speed * max_speed * math.cos(math.radians(heading) * imu_data)
        + target_rpm * conversion_factor
    )
    return right_wheel_rpm, left_wheel_rpm

def rpm_to_accelerometer_data_to_rpm(rpm):
    acc_out = (rpm**2)*8*(1.118*(10**-5))
    acc_to_rpm = math.sqrt(acc_out/(8*(1.118*(10**-5))))
    return acc_to_rpm

print(rpm_to_accelerometer_data_to_rpm(1000))

def fake_accelerometer_data(rpm, elapsed_time):
    # Convert RPM to rotations per second
    rpm = rpm_to_accelerometer_data_to_rpm(rpm)
    rps = rpm / 60
    # Calculate radians over elapsed time
    total_rotation = rps * elapsed_time * 2 * math.pi
    # Normalize and clamp to stay within 0 and 2π
    normalized_angle = max(0, total_rotation % (2 * math.pi))
    return normalized_angle


print(2 * math.pi)

# Create the robot surface
robot_surface = pygame.Surface((500, 500), pygame.SRCALPHA)  # Transparent support

# Running loop
running = True
old_heading = 0

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    frames += 1
    current_time = pygame.time.get_ticks()
    frame_time = (current_time - start_time) / 1000

    # Joystick initialization
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
    else:
        raise Exception("No joystick detected")

    # Apply deadband to joystick axes
    x_axis = apply_deadband(-joystick.get_axis(3), deadband)
    y_axis = apply_deadband(joystick.get_axis(2), deadband)

    # Calculate heading with deadband
    heading = math.degrees(math.atan2(y_axis, x_axis))
    if heading == 0:
        heading = 360

    # Calculate speed and RPM
    speed = min(math.sqrt(x_axis**2 + y_axis**2), 1)  # Cap speed at 1
    target_rpm = ((joystick.get_axis(4) + 1) / 2) * max_rpm

    # Clear surfaces
    screen.fill((0, 0, 0))  # Black background
    robot_surface.fill((0, 0, 0, 0))  # Transparent fill

    # Draw robot components
    pygame.draw.circle(robot_surface, (255, 255, 255), (250, 250), 250)  # Robot base
    pygame.draw.rect(robot_surface, (0, 0, 0), (50, 200, 50, 100))  # Left wheel
    pygame.draw.rect(robot_surface, (0, 0, 0), (400, 200, 50, 100))  # Right wheel

    # Get wheel RPMs and fake IMU data
    imu_data = fake_accelerometer_data(target_rpm, current_time)
    right_wheel_rpm, left_wheel_rpm = get_wheel_rpms(
        speed, heading, target_rpm, imu_data, wheel_conversion_factor
    )

    # Draw oscillation rectangles and speed rect
    pygame.draw.rect(
        robot_surface, (255, 0, 0), (50, 200, 50, (abs(right_wheel_rpm) / max_rpm) * 20)
    )  # Right wheel osc.
    pygame.draw.rect(
        robot_surface, (255, 0, 0), (400, 200, 50, (abs(left_wheel_rpm) / max_rpm) * 20)
    )  # Left wheel osc.
    pygame.draw.rect(
        robot_surface, (255, 0, 0), (250, 250, 10, speed * 100)
    )  # Speed bar

    # Rotate and blit robot surface
    rotation_angle = heading
    rotated_surf, new_pos = rotate_surface(robot_surface, rotation_angle, (400, 300))
    old_heading = heading
    screen.blit(rotated_surf, new_pos)

    # Update frame count and calculate FPS
    if frame_time >= 1:  # Calculate FPS every second
        fps = round(frames / frame_time, 2)  # Calculate FPS
        frames = 0  # Reset frames for the next period
        start_time = current_time  # Update the start time for the next period

    # Display FPS, title, heading, and RPM data
    font = pygame.font.Font(pygame.font.get_default_font(), 36)
    fps_text = font.render(str(fps), True, (255, 0, 0))  # Red FPS text
    title_text = font.render(
        "Doomba Dashboard V1.0", True, (255, 255, 255)
    )  # White title text
    heading_text = font.render(f"{int(heading)}", True, (255, 0, 0))  # Red heading text

    # Display RPM and IMU data
    right_rpm_text = font.render(str(round(right_wheel_rpm)), True, (255, 0, 0))
    left_rpm_text = font.render(str(round(left_wheel_rpm)), True, (255, 0, 0))
    imu_text = font.render(str(round(imu_data, 2)), True, (255, 0, 0))

    # Blit texts and data to the screen
    screen.blit(fps_text, (650, 550))  # Bottom-right for FPS
    screen.blit(title_text, (200, 5))  # Top-center for title
    screen.blit(
        heading_text, (screen.get_width() // 2, screen.get_height() // 2)
    )  # Center for heading
    screen.blit(right_rpm_text, (10, 450))  # Right RPM text
    screen.blit(left_rpm_text, (10, 550))  # Left RPM text
    screen.blit(imu_text, (10, 350))  # IMU data

    # Refresh the screen
    pygame.display.flip()  # Update display
    pygame.display.update()  # Refresh screen

# End of program
pygame.quit()  # Quit Pygame when finished
