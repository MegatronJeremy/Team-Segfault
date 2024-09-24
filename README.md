# Team-Segfault

### Video demonstration 

https://github.com/user-attachments/assets/c6e6debf-fd8e-4370-8b6a-e7b8b22585e5

### Presentation in Serbian

[Vuk Đorđević - Prezentacija diplomskog rada.pptx](https://github.com/user-attachments/files/17104345/Vuk.Dordevic.-.Prezentacija.diplomskog.rada.pptx)


### Game description

The game can have local bot players, remote players from other machines connected to the main server, and observers.
It is a turn-based strategy game played on a hexagonal map, with each player being assigned five different tanks.
Other than tanks, each game can have unique powerups and obstacles placed on the map to be interacted with by the tanks. 
Each game is uniquely identified by its name, and the same goes for each player joining that game.
When starting the game you will be greeted by a menu screen where you can change the game configuration as you wish.
After starting the game and waiting for all the players to join, a simulation will play out in which the different
players will battle each other, until the game ends in a draw or a winner is determined.

### Running

Set the project workspace to the folder which contains main.py, start the Python virtual environment (if you are using an IDE), or just start the game by running the command `py .\main.py` with the project root as your current directory, and follow the on-screen instructions!

Python 3.11 <= is required.

Make sure to install all the required packages in **requirements.txt**.

### Running without the menu/debugging

For testing remote games run the remote_game_create and remote_game_join modules separately, with the same project
workspace as for the previously named.
For other tests configure the parameters and run the wanted modules separately.

### Project structure

A simplified version of the project structure can be seen here:
![VLNBZjim3BpxAuIS-a0EFVGI5CMsoVO1D6YnIO5U6Oj8XBLbGw8sS1__tbYCL2iqcfk6mo5jpJXtdi1HQ9lgP3GgR7iQL8lj0Pslghe1xzN6-Bw1OGiMZkZKhqfTVY-FIDyzki-s3_JiEMDHx2Eqc03juBohqOx0dwGt4bY5ErBxClGQ27S4X0dwTXcCxZhwdqJKP0qUaWREI4Jkvi91ny0Ux2EVovtMZK5BQJ6qUj_jq3sXIqfyMdVMOas](https://user-images.githubusercontent.com/81580576/235599494-7ad24e7b-8dc7-41f0-ac29-f94e90c7aa61.png)


The DisplayManager is the top-level entry point of the program, but the Game class can be run and configured itself
without it, in which case no window will be rendered, and only console output can be seen.

### Assets

[Tank classes icons](https://icon-library.com/icon/world-of-tanks-icon-12.html)

[Tank icon](https://www.freeiconspng.com/img/19109)

[Explosion](https://www.pngwing.com/en/free-png-xiyem)

[Explosion sound](https://pixabay.com/sound-effects/explosion-6055/)

[Gunshot sound](https://pixabay.com/sound-effects/shotgun-firing-3-14483/)

[Projectile](https://www.freepnglogos.com/images/bullet-8545.html)

[Tank icon for pygame window](https://www.flaticon.com/free-icon/tank_3111508)

[Tank tracks](https://www.dreamstime.com/tank-tracks-set-track-treads-isolated-white-various-caterpillar-impressed-heavy-vehicles-like-tractors-bulldozers-image198577121)

### Team members:

- [Vuk Đorđević](https://github.com/MegatronJeremy)
- [Ricardo Suarez del Valle](https://github.com/RicardoSdV)
- [Jovan Milanović](https://github.com/wanjoh)
