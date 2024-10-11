# Dont-Blink-Game

The "Do Not Blink" game is a computer vision-based game designed to detect and count blinks using a webcam. It provides a challenging experience where players compete by trying not to blink, and the first player to blink a specified number of times loses. The game utilizes Python libraries such as OpenCV, cvzone, and Pygame for face detection, blink detection, and providing an interactive gaming experience.
This game has both a single-player mode, where the player competes against time, and a two-player mode, where players face off against each other. The game also incorporates multimedia elements like images and videos to enhance the user experience, providing distractions to make the game more challenging.

# Methodology:
The game is implemented using Python, leveraging the following technologies:
-	OpenCV: Used for capturing real-time video from the webcam and performing image processing tasks.
-	FaceMesh from cvzone: A pre-trained face mesh detector is used to identify key facial landmarks, particularly around the eyes, to detect blinks.
-	Pygame: For creating a graphical user interface (GUI) in two-player mode, which includes the display of blink counts, video playbacks, and game-ending conditions.
-	Tkinter: A GUI library for creating the main menu and player mode selection interface.
-	Multimedia Integration: Images and videos are periodically shown to the player during the game, adding to the difficulty by acting as distractions.

# Game Mechanics:
1)	Blink Detection:
The game captures real-time video from the webcam and processes the images to detect the player's facial landmarks. The key points around the eyes are used to calculate the aspect ratio of the eye. If the aspect ratio falls below a certain threshold, a blink is detected.
2)	Single-player Mode:
In this mode, the player is challenged to last as long as possible without blinking more than a predefined number of times. If the player exceeds the blink limit, they lose. The game also displays images and plays videos to distract the player and make the challenge harder.
3)	Two-player Mode:
In the two-player mode, both players are detected using a shared webcam feed. Each player's blinks are tracked, and the player who blinks more times first loses the game. This mode includes a graphical interface using Pygame, which displays the players' scores, timer, and other information.
4)	Media Playback:
Both modes feature image and video distractions that appear at regular intervals. This is implemented using threading to ensure that videos play smoothly while blink detection continues in the background.
5)	Screen Shaking Effect:
To add more intensity when a blink is detected, a screen-shake effect is applied, disorienting the player momentarily.

# Additional Features or Enhancements:
- Music or Sound Effects: Adding background music or sound effects when a blink is detected could enhance the gaming experience.-
- Dynamic Difficulty: You can modify the difficulty by changing the blink threshold or adding new distractions over time (e.g., faster media switching or more intense screen shaking).
- Game Statistics: You can extend the game by tracking statistics such as total game time or average blink intervals and displaying them at the end.

# Conclusion:
The "Do Not Blink" game successfully demonstrates the application of computer vision in gaming. By using real-time blink detection, the game offers a unique challenge that engages players in both single and multiplayer modes. The project highlights how Python libraries like OpenCV and cvzone can be used to build interactive and entertaining applications.
The game could be further improved by integrating additional modes, enhancing the GUI, and expanding the distractions to make the game even more challenging.
