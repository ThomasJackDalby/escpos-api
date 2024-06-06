# escpos-api

A REST API to sit in front of an escpos thermal receipt printer. Originally developed for EMF 2024.



## Getting Started

This was developed to run on a Raspberry PI Zero W (v1) plugged into a POE Ethernet hat at EMF 2024.

First, the PI was flashed using the <https://www.raspberrypi.com/documentation/computers/getting-started.html#install-using-imager> with the lightweight (non-desktop environrment) version of debian. At the time of flashing, SSH was enabled and a suitable username/password selected.

Then, we got the code onto the PI by plugging into the Ethernet and going in over ssh. Navigating to the home directory (if not already there) and cloning via:

``` bash
cd ~
git clone https://github.com/ThomasJackDalby/escpos-api.git
```

Navigate to the code folder:

``` bash
cd ./escpos-api
```

Create a virtual environment and install the python dependencies:
``` bash
python -m venv .venv
.venv/bin/pip install -r ./requirements.txt
```

> [!NOTE]  
> Depending on which version of linux is installed on the pi, you may need to install some additional dependencies such as python3-venv

At this stage, as the api is written using FastAPI, you can start it up with either:

``` bash
.venv/bin/fastapi run main.py
.venv/bin/fastapi dev main.py # will launch in dev mode, e.g. will detect code changes and re-launch
```

## Configuring the auto-launcher

Make the launch.sh an exe:

``` bash
chmod 755 launcher.sh
```

Edit the crontab so that it starts on boot

``` bash
# open the crontab to edit (as current user)
crontab -e

# add this line to the crontab
@reboot sh ~/emfcamp-2024/server/launch.sh > ~/emfcamp-2024/server/logs/cronlog.log 2>&1

# restart the pi
sudo reboot
```

## Future (Potential) Features

- need some kind of rate limit/token based auth such that the machine isn't spammed.
  - whitelist seems overkill.
- index site to allow messages to be sent to camp.

## References

- <https://www.instructables.com/Raspberry-Pi-Launch-Python-script-on-startup/>
- <https://aschmelyun.com/blog/i-built-a-receipt-printer-for-github-issues/>