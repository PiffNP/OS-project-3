osascript -e 'tell app "Terminal"
    do script "cd Documents/THU/OS/lab/OS-project-3;python3 server.py"
    end tell'
osascript -e 'tell app "Terminal"
    do script "cd Documents/THU/OS/lab/OS-project-3;python3 bak_server.py"
    end tell'
sleep 2
osascript -e 'tell app "Terminal"
    do script "cd Documents/THU/OS/lab/OS-project-3;python3 test.py"
    end tell'
