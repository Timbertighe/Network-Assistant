# Junos Plugin Changelog
## 0.8
### Agent
    Renamed the agent script to agent.py
    Added better error handling
    Added a top() function to get the four highest CPU processes
    If high-cpu information is relevant, it sends it to the chatbot along with the regular messages

### Netconf
    Added netconf.py
    Enables the chatbot to communicate with Junos devices over NETCONF
    
### Config - junos-config.yaml
    Added 'ftp_server' and 'ftp_dir'
    Removed some old categories to clean up the file
    
### NLP
    Added a phrase list to the class
        There is only one phrase right now
    This is used to talk to the chatbot, and request it to do things with this plugin
    
### Generate Logs
    Can now ask the chatbot to get a junos device to generate logs
    These are archived, and uploaded to an FTP location
    
### Reboot devices
    Can ask the chatbot to reboot devices
    This can be immediately, in a relative, or at an absolute time
    
### Retart processes
    Can ask for a process to be restarted
    Add 'immediately' to force it to happen immediately (SIGKILL)


&nbsp;<br>
## 0.7
### Changed
    Moved the SQL table name into the config file, rather than hardcoding in the plugin

