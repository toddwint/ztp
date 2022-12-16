#!/usr/bin/env bash
echo '
  Welcome to the '"$APPNAME"' docker image.

  This application uses tmux to manage the windows/panes.
  Some useful tmux keyboard shortcuts are:
  Command                   | Function
  :-------------------------|:------------------
  Ctrl + b then [           | Enter copy/scroll mode
  Ctrl + b then Esc         | Exit copy/scroll mode
  Ctrl + b then q then 0-9  | Focus on pane number
  Ctrl + b then x           | Close current pane
  Ctrl + b then d           | Detach from tmux session
  Ctrl + b then c           | Create a new window
  Ctrl + b then n           | Move to the next window
  Ctrl + b then p           | Move to the previous window
  Ctrl + b then w           | Show window list
  Ctrl + b then ?           | Show shortcuts
'
read -p 'Press `enter` to continue'
if [[ $(tmux list-session -f "$APPNAME" 2> /dev/null) ]]; then
    tmux new-session -A -s "$APPNAME"
else
    tmux new-session -AD -d -s "$APPNAME"
    tmux send-keys -t 1 "tail -n 500 -F /opt/$APPNAME/logs/$APPNAME.log" Enter
    tmux new-window
    tmux send-keys -t 1 "tail -n 500 -F /opt/$APPNAME/logs/vsftpd_xfers.log" Enter
    tmux new-window
    tmux send-keys -t 1 "tail -n 500 -F /opt/$APPNAME/logs/$APPNAME.log | grep 'vsftpd'" Enter
    tmux new-window
    tmux send-keys -t 1 "tail -n 500 -F /opt/$APPNAME/logs/$APPNAME.log | grep 'in.tftpd'" Enter
    tmux new-window
    tmux select-window -t 1
    #tmux selectp -t 1 -d #disable user input in pane
    #tmux selectp -t 1 -e #enable user input in pane
    tmux new-session -A -s "$APPNAME"
fi
