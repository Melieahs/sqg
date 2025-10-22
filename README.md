#install for Windows 
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm https://raw.githubusercontent.com/Melieahs/sqg/main/install.ps1 | iex

#install for macOS
curl -o sqg https://raw.githubusercontent.com/<your-username>/sqg/main/sqg
chmod +x sqg
sudo mv sqg /usr/local/bin/


