
# Creating A Desktop Application Launcher

The pip installation process does not automatically create a desktop application launcher for PyGPSClient, but this can be done manually.

The illustrations below assume PyGPSClient has been installed into a virtual environment named `pygpsclient` in the user's home directory.

## Windows

To create an application launcher for Windows, create a new Shortcut named `PyGPSClient` with the following properties (*adapted for your particular environment*):

- Target type: Application
- Target location: Scripts
- Target: `C:\Users\myuser\pygpsclient\Scripts\pygpsclient.exe`
- Start in: `C:\Users\myuser`
- Run: Minimized

and place this in the `C:\Users\myuser\AppData\Roaming\Microsoft\Windows\Start Menu\Programs` directory (*you may need Administrator privileges to do this*). To assign an icon to this shortcut, select Change Icon.. and Browse to the pygpsclient.ico file in the site_packages folder (e.g.`C:\Users\myuser\pygpsclient\Lib\site-packages\pygpsclient\resources\pygpsclient.ico`)

## MacOS

To create an application launcher for MacOS, use MacOS's Automator tool to create a "Run Shell Script" application and save this as `PyGPSClient.app`, e.g.

Shell: /bin/zsh
```
/Users/myuser/pygpsclient/bin/pygpsclient
```

To assign an icon to this shortcut, right-click on the `PyGPSClient` entry in the Applications folder, select "Get Info" and drag-and-drop the pygpsclient.ico image file from the site-packages folder (e.g. `/Users/myuser/pygpsclient/lib/python3.11/site-packages/pygpsclient/resources/pygpsclient.ico`) to the default application icon at the top left of the "Get Info" panel.

## Linux

To create an application launcher for most Linux distributions, create a text file named `pygpsclient.desktop` with the following content (*adapted for your particular environment*) and copy this to the `/home/myuser/.local/share/applications` folder, e.g.

```
[Desktop Entry]
Type=Application
Terminal=false
Name=PyGPSClient
Icon=/home/myuser/pygpsclient/lib/python3.11/site-packages/pygpsclient/resources/pygpsclient.ico
Exec=/home/myuser/pygpsclient/bin/pygpsclient
```

You will need to logout and login for the launcher to take effect.
