import threading

import cv2
import cvzone
import numpy as np
from cvzone.FaceMeshModule import FaceMeshDetector
from collections import deque
import time
import pygame


# Function to play video in a separate thread
def play_video(video_path, stop_event):
    cap_video = cv2.VideoCapture(video_path)
    while cap_video.isOpened() and not stop_event.is_set():
        ret, frame = cap_video.read()
        if not ret:
            break
        frame = cv2.resize(frame, (640, 360))
        cv2.imshow("Media", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap_video.release()
    if cv2.getWindowProperty("Media", cv2.WND_PROP_VISIBLE) > 0:
        cv2.destroyWindow("Media")


def screen_shake(img, shake_intensity=5):
    height, width = img.shape[:2]
    x_offset = int(shake_intensity * (1 if time.time() % 0.1 < 0.05 else -1))
    y_offset = int(shake_intensity * (1 if time.time() % 0.1 < 0.05 else -1))

    M = np.float32([[1, 0, x_offset], [0, 1, y_offset]])
    shaken_img = cv2.warpAffine(img, M, (width, height))

    return shaken_img

def one_player_mode():
    cap = cv2.VideoCapture(0)
    detector = FaceMeshDetector(maxFaces=1)

    # Get the FPS (frame rate) of the camera
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"Camera FPS: {fps}")

    # Using deque for a fixed-size list for blink ratio
    ratioListLeft = deque(maxlen=5)
    ratioListRight = deque(maxlen=5)
    blinkCounter = 0
    counter = 0
    color = (255, 50, 50)
    maxBlinks = 5  # Maximum number of blinks before losing
    startTime = time.time()  # Record the start time

    # Load images and videos to be displayed
    images = [cv2.imread(f'image{1}.jpg'), cv2.imread(f'image{2}.jpg'), cv2.imread(f'image{3}.jpg')]
    videos = [f'video{1}.mp4', f'video{2}.mp4', f'video{3}.mp4']
    mediaIndex = 0
    imageDisplayTime = 3  # Display each image for 3 seconds
    nextMediaTime = time.time() + 5  # Start displaying the first media after 5 seconds
    showImage = True  # Start with image
    mediaWindowName = "Media"  # Window name for media display
    currentVideoThread = None
    stop_event = threading.Event()
    eyesClosed = False

    def close_all_windows():
        stop_event.set()
        if currentVideoThread is not None:
            currentVideoThread.join()
        if cv2.getWindowProperty(mediaWindowName, cv2.WND_PROP_VISIBLE) > 0:
            cv2.destroyWindow(mediaWindowName)
        cv2.destroyAllWindows()

    while True:
        success, img = cap.read()
        if not success:
            break

        img, faces = detector.findFaceMesh(img, draw=False)

        if faces:
            face = faces[0]
            # Left Eye
            leftUp = face[386]
            leftDown = face[374]
            leftLeft = face[263]
            leftRight = face[362]
            lengthVerLeft, _ = detector.findDistance(leftUp, leftDown)
            lengthHorLeft, _ = detector.findDistance(leftLeft, leftRight)

            ratioLeft = int((lengthVerLeft / lengthHorLeft) * 100)
            ratioListLeft.append(ratioLeft)
            ratioAvgLeft = sum(ratioListLeft) / len(ratioListLeft)

            # Right Eye
            rightUp = face[159]
            rightDown = face[23]
            rightLeft = face[130]
            rightRight = face[243]
            lengthVerRight, _ = detector.findDistance(rightUp, rightDown)
            lengthHorRight, _ = detector.findDistance(rightLeft, rightRight)

            ratioRight = int((lengthVerRight / lengthHorRight) * 100)
            ratioListRight.append(ratioRight)
            ratioAvgRight = sum(ratioListRight) / len(ratioListRight)

            # Average ratio for both eyes
            ratioAvg = (ratioAvgLeft + ratioAvgRight) / 2

            if ratioAvg < 25:
                if not eyesClosed:  # Only count the blink if eyes were open before
                    blinkCounter += 1
                    color = (50, 50, 255)
                    eyesClosed = True  # Set the flag to indicate that eyes are closed

                    # Apply screen shake
                    img = screen_shake(img, shake_intensity=15)

            else:
                # If the eyes are open (ratio is above the threshold), reset the flag
                eyesClosed = False
                color = (255, 50, 50)

            # Display blink count
            cvzone.putTextRect(img, f'Blink Count: {blinkCounter}', (50, 50), colorR=color)

            # Check if blink count exceeds max blinks
            if blinkCounter >= maxBlinks:
                cvzone.putTextRect(img, 'You Lose!', (200, 180), colorR=(0, 0, 255))
                cv2.imshow("Don't Blink", img)
                cv2.waitKey(3000)
                cap.release()
                close_all_windows()
                break

            img = cv2.resize(img, (640, 360))
        else:
            img = cv2.resize(img, (640, 360))

        # Display the timer
        elapsedTime = int(time.time() - startTime)
        cvzone.putTextRect(img, f'Time: {elapsedTime}s', (50, 300), colorR=(0, 255, 0))

        cv2.imshow("Don't Blink", img)

        # Manage media display and hiding
        currentTime = time.time()
        if currentTime >= nextMediaTime:
            # Check if the current media window exists before destroying
            if cv2.getWindowProperty(mediaWindowName, cv2.WND_PROP_VISIBLE) > 0:
                stop_event.set()
                if currentVideoThread is not None:
                    currentVideoThread.join()
                cv2.destroyWindow("Media")
                stop_event.clear()

            # Show the next media (image or video)
            if showImage:
                mediaToShow = images[mediaIndex % len(images)]
                mediaToShow = cv2.resize(mediaToShow, (640, 360))
                cv2.imshow(mediaWindowName, mediaToShow)
                nextMediaTime = currentTime + imageDisplayTime
            else:
                videoPath = videos[mediaIndex % len(videos)]
                # Use threading to play video
                currentVideoThread = threading.Thread(target=play_video, args=(videoPath, stop_event))
                currentVideoThread.start()
                nextMediaTime = currentTime + cv2.VideoCapture(videoPath).get(cv2.CAP_PROP_FRAME_COUNT) / cv2.VideoCapture(videoPath).get(cv2.CAP_PROP_FPS)

            showImage = not showImage
            mediaIndex += 1

        if cv2.waitKey(1) & 0xFF == 27:
            close_all_windows()
            break

        # Check if the window has been closed
        if cv2.getWindowProperty("Don't Blink", cv2.WND_PROP_VISIBLE) < 1:
            close_all_windows()
            break

    cap.release()
    close_all_windows()

# /////////////////////////////////////////////////////////////////////////////


def two_players_mode():
    pygame.init()
    cap = cv2.VideoCapture(0)

    width = 1280
    height = 720

    # Set the video capture frame size
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Blink Game')

    # Create a button
    button = pygame.Rect(width - 180, height - 80, 150, 50)

    detector = FaceMeshDetector(maxFaces=2)

    # Using deque for a fixed-size list for blink ratio
    ratioListLeft1 = deque(maxlen=5)
    ratioListRight1 = deque(maxlen=5)
    ratioListLeft2 = deque(maxlen=5)
    ratioListRight2 = deque(maxlen=5)

    blinkCounter1 = 0
    blinkCounter2 = 0
    color1 = (255, 0, 0)
    color2 = (0, 0, 255)
    color = (0, 0, 255)
    startTime = time.time()  # Record the start time

    maxBlinks = 5  # Maximum number of blinks before losing
    game_over = False
    winner = None

    button_enabled = True
    video_index = 0
    videos = [f'video{1}.mp4', f'video{2}.mp4', f'video{3}.mp4']
    stop_event = threading.Event()
    eyes1_Closed = False
    eyes2_Closed = False
    running = True

    while running:
        current_time = time.time()  # Get the current time for each frame

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_enabled and button.collidepoint(event.pos):
                    button_enabled = False
                    video_path = videos[video_index % len(videos)]
                    currentVideoThread = threading.Thread(target=play_video, args=(video_path, stop_event))
                    currentVideoThread.start()
                    video_index += 1
                    pygame.time.set_timer(pygame.USEREVENT, 50)

        if not button_enabled:
            if not pygame.time.get_ticks() % 50:  # Check video completion status
                button_enabled = True

        success, img = cap.read()
        if not success:
            break

        img, faces = detector.findFaceMesh(img, draw=False)

        if faces and len(faces) == 2:
            for i, face in enumerate(faces):
                if i == 0:  # First face (Player 1)
                    ratioListLeft = ratioListLeft1
                    ratioListRight = ratioListRight1
                    color = color1
                else:  # Second face (Player 2)
                    ratioListLeft = ratioListLeft2
                    ratioListRight = ratioListRight2
                    color = color2

                # Left Eye
                leftUp = face[386]
                leftDown = face[374]
                leftLeft = face[263]
                leftRight = face[362]
                lengthVerLeft, _ = detector.findDistance(leftUp, leftDown)
                lengthHorLeft, _ = detector.findDistance(leftLeft, leftRight)

                ratioLeft = int((lengthVerLeft / lengthHorLeft) * 100)
                ratioListLeft.append(ratioLeft)
                ratioAvgLeft = sum(ratioListLeft) / len(ratioListLeft)

                # Right Eye
                rightUp = face[159]
                rightDown = face[23]
                rightLeft = face[130]
                rightRight = face[243]
                lengthVerRight, _ = detector.findDistance(rightUp, rightDown)
                lengthHorRight, _ = detector.findDistance(rightLeft, rightRight)

                ratioRight = int((lengthVerRight / lengthHorRight) * 100)
                ratioListRight.append(ratioRight)
                ratioAvgRight = sum(ratioListRight) / len(ratioListRight)

                # Average ratio for both eyes
                ratioAvg = (ratioAvgLeft + ratioAvgRight) / 2

                if ratioAvg < 25:
                    # Only count the blink if the eyes were open before
                    if i == 0 and not eyes1_Closed:  # Player 1
                        blinkCounter1 += 1
                        eyes1_Closed = True  # Set the flag to indicate that eyes are closed
                        img = screen_shake(img, shake_intensity=15)  # Apply screen shake

                    if i == 1 and not eyes2_Closed:  # Player 2
                        blinkCounter2 += 1
                        eyes2_Closed = True
                        img = screen_shake(img, shake_intensity=15)

                else:
                    # If the eyes are open (ratio is above the threshold), reset the flag
                    if i == 0:
                        eyes1_Closed = False
                    if i == 1:
                        eyes2_Closed = False

            # Display blink counts for both players
            cvzone.putTextRect(img, f'Player 1: {blinkCounter1}', (50, 70), scale=2, colorR=(255, 0, 0))
            cvzone.putTextRect(img, f'Player 2: {blinkCounter2}', (1050, 70), scale=2, colorR=(0, 0, 255))

            # Check for game over
            if blinkCounter1 >= maxBlinks and not game_over:
                winner = "Player 2"
                game_over = True
                color = color2
            elif blinkCounter2 >= maxBlinks and not game_over:
                winner = "Player 1"
                game_over = True
                color = color1

        # Display the timer
        elapsedTime = int(current_time - startTime)
        cvzone.putTextRect(img, f'Time: {elapsedTime}s', (550, 650), colorR=(0, 255, 0))

        if game_over:
            # Display result text and wait for 3 seconds
            cvzone.putTextRect(img, f"{winner} Wins!", (width // 2 - 150, height // 2), colorR=color)
            # Convert the OpenCV image to Pygame surface
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = img.swapaxes(0, 1)
            surf = pygame.surfarray.make_surface(img)

            screen.blit(surf, (0, 0))
            pygame.display.flip()  # Update the display with the result text

            time.sleep(3)  # Wait for 3 seconds

            break  # Exit the loop after displaying the result for 3 seconds

        if not game_over:
            # Convert the OpenCV image to Pygame surface
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = img.swapaxes(0, 1)
            surf = pygame.surfarray.make_surface(img)

            screen.blit(surf, (0, 0))

            # Draw button
            pygame.draw.rect(screen, (0, 255, 0), button)
            font = pygame.font.Font(None, 36)
            text = font.render('Run Video', True, (255, 255, 255))
            text_rect = text.get_rect(center=button.center)
            screen.blit(text, text_rect.topleft)

            pygame.display.flip()

        if cv2.waitKey(1) & 0xFF == 27:
            cv2.destroyWindow("Blink Game")
            cv2.destroyAllWindows()
            break

    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()

# code for button *******************************************

import tkinter as tk
from tkinter import messagebox


def one_player():
    response = messagebox.askokcancel("1 Player", "You are moving now to play, then we will open the camera")
    if response:
        one_player_mode()


def two_players():
    response = messagebox.askokcancel("2 Players", "You are moving now to play, then we will open the camera")
    if response:
        two_players_mode()


# Create the main window
window = tk.Tk()
window.title("Don't Blink Game")
window.geometry("600x500")  # Set the window size
window.config(bg="lightblue")  # Set the window background color

# Create a label with the welcome text and center it
welcome_label = tk.Label(window, text="Welcome to Don't Blink Game", font=("Helvetica", 24), bg="lightblue")
welcome_label.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

# Create another label with the additional text and center it below the first text
additional_label = tk.Label(window, text="Please select an option below", font=("Helvetica", 16), bg="lightblue")
additional_label.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

# Create the "1 Player" button and place it at the bottom left
one_player_button = tk.Button(window, text="1 Player", command=one_player, font=("Helvetica", 18), bg="green")
one_player_button.place(relx=0.2, rely=0.8, anchor=tk.CENTER)

# Create the "2 Players" button and place it at the bottom right
two_players_button = tk.Button(window, text="2 Players", command=two_players, font=("Helvetica", 18), bg="red")
two_players_button.place(relx=0.8, rely=0.8, anchor=tk.CENTER)

# Run the application
window.mainloop()

