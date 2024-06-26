# mpdcron-sleep-enabler
This uses the amazing mpdcron application to monitor a Music Player Daemon (MPD) installation and automatically enable sleep mode on play on a linux machine. I've used it on a Raspberry Pi 3 Debian buster image, but it may run on other linux systems too. I've had it running for quite a few days and it works seamlessly.

My Volumio setup only used to play audio-books to my son as he falls asleep. So I don't want it playing all night! 

**This worked for me when doing it on a fresh installation  using the Feb 2024 release of Volumio. I don't take any responsibility for any damage you do to anything from following my instructions. Everything is pretty clearly documented inside the files and in here, with lots of print/echo statements and it's always a good idea to look inside any script files before downloading and running them!**

Everything here requires you to use the linux terminal - either on the machine or remotely over ssh. You can use [Putty](https://www.putty.org/) if you're using a Windows machine. First, you need to install [mpdcron](https://github.com/alip/mpdcron) - this is included in most standard linux repositories and it monitors the [mpd](https://www.musicpd.org/) service and triggers scripts on different events from the hooks directory. We are only interested in the player events (really only the play event, but player responds to play, pause and stop). I have been using this on a Raspberry Pi running the Debian buster [Volumio 3](https://volumio.com/) image, so the installation and setup of mpd was already done for me!
```
sudo apt-get install mpdcron
```

Then, you need to create a couple of files and folders and download a few files BEFORE running mpdcron or you will get permission errors. Do NOT use sudo/root. The cd ~ goes into the user's home folder
```
cd ~
mkdir .mpdcron
cd .mpdcron
touch mpdcron.pid
wget https://raw.githubusercontent.com/SANGERA2/mpdcron-sleep-enabler/main/mpdcron_in_home/mpdcron.conf
mkdir hooks
cd hooks
wget https://raw.githubusercontent.com/SANGERA2/mpdcron-sleep-enabler/main/mpdcron_in_home/hooks/player
sudo chmod +x player
```

Now, you need to edit the player file to set the text after `SLEEP_TIME_FILE=` to a path where you will store an easily accessible text file that allows you to modify the amount of time to sleep for (the one I've provided is set to 120 minutes by default. If you set the value to 0 or the file doesn't exist, the sleep will not be activated. I stored it in the root of a USB key I have my music on and that's shared using samba by Volumio so I can easily access it from anywhere.
Once you have modified the file path using the nano editor, you quit and save using `Ctrl + x`, `y`, `enter` and you'll be returned to the console. 
```
nano player
```

Then you need to download and  and edit that file using nano to contain a number of your choosing or leave it at 90 minutes.
```
cd /folder_of_your_choosing
wget https://raw.githubusercontent.com/SANGERA2/mpdcron-sleep-enabler/main/mpd_sleep_time.txt
nano mpd_sleep_time.txt
```

If you're planning to edit this file over samba, you should also check you can view and make changes to that file. If you can't, then you may need to modify it's permissions using chmod.
```
sudo chmod 0777 /folder_of_your_choosing/mpd_sleep_time.txt
```

Now, you need to download the python program that will activate the sleep on mpd and when you run the last line to edit it: set the path to the sleep time file to be the same as in the player file except that this time, the path must be surrounded by speech-marks `SLEEP_TIME_FILE="/folder_of_your_choosing/mpd_sleep_time.txt"` so Python can use it. Also, you can choose whether the system will stop playing and stay turned on or power itself off when the sleep triggers by changing which of the ACTION= lines has a # in front of it (the line with the # in front of it is the action that will NOT be taken).
```
cd /usr/local/bin
sudo wget https://raw.githubusercontent.com/SANGERA2/mpdcron-sleep-enabler/main/usr/local/bin/activate_sleep.py
sudo chmod 0777 activate_sleep.py
sudo nano activate_sleep.py
```

Then install a simple script in the same folder to see all of the mpdcron service status as it produces a lot of text, but only shows you the last 5 or so lines if you use `sudo systemctl status mpdcron.service`. You won't be able to test this until after installing the service.
```
sudo wget https://raw.githubusercontent.com/SANGERA2/mpdcron-sleep-enabler/main/usr/local/bin/mpdcron_status
sudo chmod 0777 mpdcron_status
```

You need Python 3 installed. If you don't, it's easy to get. Mine already had Python 3.7.3 so that definitely works!
```
sudo apt-get install python3
```

If you don't already have pip3 installed (I'm using 18.1), then you will need that to install the socket.io client.
```
sudo apt-get install python3-pip
```

You need to install this Python [socket.io client](https://pypi.org/project/socketIO-client/). It works great for me for this use-case. Possibly try it without the -U option if it looks like Python can't find it!
```
sudo pip3 install -U socketIO-client
```

Now, you need to see if you can enable sleep on the mpd server. Make sure sleep is not already enabled before trying this as it only activates when sleep is not currently enabled. It's designed to run on the same device as the mpd installation, but if you're running it on a different device, change `localhost` to be the device hostname (or possibly IP address may work too).
```
./activate_sleep.py
```

Next we want mpdcron to run on boot automatically. **Do not restart your device until you've made sure this works correctly or it may hang.** You can easily disable it again at any point using `systemctl disable mpdcron.service`. Below is how to download, enable and test out the service. If your user is not called "volumio", you need to edit the path `MPDCRON_DIR=/home/volumio/.mpdcron` to be `MPDCRON_DIR=/home/your_username/.mpdcron` instead. If you modify the .service file after enabling it, you have to run `sudo systemctl daemon-reload` to get it to read the file again and accept the new changes.
```
cd /lib/systemd/system
sudo wget https://raw.githubusercontent.com/SANGERA2/mpdcron-sleep-enabler/main/lib/systemd/system/mpdcron.service
sudo nano mpdcron.service
sudo systemctl enable /lib/systemd/system/mpdcron.service
sudo systemctl start mpdcron.service
sudo systemctl status mpdcron.service
```

Next, turn off sleep again using the web-interface or however you control mpd and check that the player script activates and runs the python program correctly by playing/pausing and skipping on the mpd device. Make sure you disable the sleep again before each test. You can check the service output by using my script.
```
mpdcron_status
```

All that's left is to restart your device and test it all out. You can then enable/disable/change the sleep value using the text file whenever you want.

If you have any problems, please open them as issues here and post detailed console output and I'll do my best to help you solve them.
